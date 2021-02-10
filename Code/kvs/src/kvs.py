from clock import VectorClock
from orset import ORSet
import json
import socket

class Store():
  def __init__(self):
    self.kvs = {}
    self.node_id = socket.getfqdn(socket.gethostname())+ "_kvs"

  def acc_exists(self, user_id):
    uids = [k for k in self.kvs.keys()]
    return user_id in uids

  def create(self, user_id):
    kart_obj = ORSet(id=user_id)
    version = VectorClock()
    version.update(self.node_id,0)
    self.kvs[kart_obj.id] = (kart_obj, version)

  def update(self, com, key, item, tag=None):
    if com == 'ADD':
      self.kvs[key][0].add(item, tag)
    elif com == 'DELETE':
      self.kvs[key][0].remove(item)
    print((com, self.kvs[key][0].display()))

    v = self.kvs[key][1].clock[self.node_id]
    self.kvs[key][1].update(self.node_id, v+1)
    print("clock" + str(self.kvs[key][1].clock))
    return self.kvs[key]

  def overwrite(self, key, cart, vc):
    self.kvs[key] = (cart, vc)

  def get(self,key):
    return self.kvs[key]
