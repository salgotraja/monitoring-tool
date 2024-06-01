import paramiko
import time
from pymongo import MongoClient


class MongoDBTunnel:
    def __init__(self, ssh_config):
        self.local_bind = None
        self.ssh_config = ssh_config
        self.tunnel = None

    def start_tunnel(self):
        self.tunnel = paramiko.SSHClient()
        self.tunnel.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.tunnel.connect(
            self.ssh_config['remote_host'],
            port=self.ssh_config['remote_port'],
            username=self.ssh_config['username'],
            password=self.ssh_config['password']
        )
        transport = self.tunnel.get_transport()
        self.local_bind = transport.open_channel(
            "direct-tcpip",
            ("localhost", self.ssh_config['remote_bind_port']),
            ("localhost", self.ssh_config['local_bind_port'])
        )
        time.sleep(1)

    def stop_tunnel(self):
        if self.tunnel:
            self.tunnel.close()


def check_mongodb(ssh_config):
    ssh_tunnel = MongoDBTunnel(ssh_config)
    try:
        ssh_tunnel.start_tunnel()
        client = MongoClient('localhost', ssh_config['local_bind_port'])
        client.admin.command('ping')
        client.close()
        return 'running'
    except Exception as e:
        print(f"Error checking MongoDB status: {e}")
        return 'down'
    finally:
        ssh_tunnel.stop_tunnel()
