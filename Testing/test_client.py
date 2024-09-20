import requests
import json
import time

while True:
    data = input("Enter task to send: ")
    response = requests.post("http://localhost:5000/c2/write_task", json={"beacon_id": "test", "task": data})
    print(response.text)
    time.sleep(1)
