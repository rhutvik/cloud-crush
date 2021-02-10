import socket,sys
from kazoo.client import KazooClient

class zkClient():
    def __init__(self):
        self.zk = KazooClient(hosts='10.0.0.2:2181')
        self.zk.start()

    def get_hostname_ip(self):
        host_name = socket.getfqdn(socket.gethostname())
        host_ip = socket.gethostbyname(host_name)
        return "/" + host_name + "_kvs", host_ip

    def register(self):
        name,ip = self.get_hostname_ip()
        if not self.zk.exists(name): 
            self.zk.create(name,bytes(ip,'utf-8'))
        else:
            self.zk.set(name,bytes(ip,'utf-8'))