#Source: http://daviddrysdale.github.io/pynamo
import copy

class VectorClock(object):
    def __init__(self):
        self.clock = {}  # node => counter

    def update(self, node, counter):
        """Add a new node:counter value to a VectorClock."""
        if node in self.clock and counter <= self.clock[node]:
            raise Exception("Node %s has gone backwards from %d to %d" %
                            (node, self.clock[node], counter))
        self.clock[node] = counter
        return self  # allow chaining of .update() operations

    def __str__(self):
        return "{%s}" % ", ".join(["%s:%d" % (node, self.clock[node])
                                   for node in sorted(self.clock.keys())])

    # Comparison operations.
    # Vector clocks are partially ordered, but not totally ordered.
    def __eq__(self, other):
        return self.clock == other.clock

    def __lt__(self, other):
        for node in self.clock:
            if node not in other.clock:
                return False
            if self.clock[node] > other.clock[node]:
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def __le__(self, other):
        return (self == other) or (self < other)

    def __gt__(self, other):
        return (other < self)

    def __ge__(self, other):
        return (self == other) or (self > other)

    @classmethod
    def coalesce(cls, vcs):
        """Coalesce a container of VectorClock objects.

        The result is a list of VectorClocks; each input VectorClock is a direct
        ancestor of one of the results, and no result entry is a direct ancestor
        of any other result entry."""
        results = []
        for cvc in vcs:
            # See if this vector-clock subsumes or is subsumed by anything already present
            vc = cvc['cart']['version']['clock']
            subsumed = False
            for ii, result in enumerate(results):
                if vc <= result:  # subsumed by existing answer
                    subsumed = True
                    break
                if result < vc:  # subsumes existing answer so replace it
                    results[ii] = copy.deepcopy(vc)
                    subsumed = True
                    break
            if not subsumed:
                results.append(copy.deepcopy(vc))
        return results
