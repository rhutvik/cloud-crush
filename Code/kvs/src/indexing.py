class SecondaryIndex():
    def __init__(self):
        self.sec = {}
        self.sec['pname'] = {}
        self.sec['price'] = {}

    def update(self, com, key, item):
        if com == 'ADD':
            if item[1] not in self.sec['pname']:
                self.sec['pname'][item[1]] = set([])
            self.sec['pname'][item[1]].add(key)
            
            if item[2] not in self.sec['price']:
                self.sec['price'][item[2]] = set([])
            self.sec['price'][item[2]].add(key)
        
        elif com == 'DELETE':
            if item[1] not in self.sec['pname']:
                self.sec['pname'][item[1]] = set([])
            try:
                self.sec['pname'][item[1]].remove(key)
            except KeyError:
                pass
            
            if item[2] not in self.sec['price']:
                self.sec['price'][item[2]] = set([])
            try:
                self.sec['price'][item[2]].remove(key)
            except KeyError:
                pass
            
        return
        
    def get_sec_index(self, key, value):
        if value not in self.sec[key]:
            self.sec[key][value] = set([])
        return list(self.sec[key][value])
                
    def get_dict(self):
        return self.sec

