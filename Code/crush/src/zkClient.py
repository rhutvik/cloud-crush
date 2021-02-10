import socket,sys
from kazoo.client import KazooClient

class zkClient():
    def __init__(self):
        self.zk = KazooClient(hosts='10.0.0.2:2181')
        self.zk.start()
        
    def get_hostname_ip(self):
        host_name = socket.getfqdn(socket.gethostname())
        host_ip = socket.gethostbyname(host_name)
        return "/" + host_name + "_gateway", host_ip

    def register(self):
        name,ip = self.get_hostname_ip()
        if not self.zk.exists(name): 
            self.zk.create(name,bytes(ip,'utf-8'))
        else:
            self.zk.set(name,bytes(ip,'utf-8'))
    
    def get_kvs_ips(self):
        device_ips = []
        for device_name in self.zk.get_children('/'):
            if device_name.endswith('_kvs'):
                data, stat = self.zk.get(device_name)
                device_ips.append(data.decode("utf-8"))
        return device_ips
    
    def get_nodes_list(self):
        device_names = []
        for device_name in self.zk.get_children('/'):
            if device_name.endswith('_kvs'):
                device_names.append(device_name)
        return device_names