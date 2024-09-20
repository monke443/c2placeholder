from flask import jsonify
from werkzeug.exceptions import BadRequest
from database import db, Beacon, Task, Result
import uuid
import datetime

def handle_register_beacon(request):
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
            permissions=current_permission,
            alive=True
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

def handle_read_task(request):
    beacon_id = request.args.get('beacon_id')

    if not beacon_id:
        return f"Wrong, debugg : {beacon_id}"

    beacon = Beacon.query.filter_by(id=beacon_id).first()
    if not beacon:
        return jsonify({"status": "failure", "message": "Invalid beacon ID", "data": {}}), 404

    if not beacon.alive:
        return jsonify({"status": "failure", "message": "Beacon is not alive", "data": {}}), 404

    tasks = Task.query.filter_by(beacon_id=beacon_id).order_by(Task.task_order).all()     # is this even necesary?
    task_list = [{"task": task.task_content, "task_order": task.task_order} for task in tasks]


# This should return something like this
    """{
  "status": "success",
  "message": "Tasks fetched successfully",
  "data": {
    "tasks": [
      {"task": "First task for the beacon", "task_order": 1},
      {"task": "Second task for the beacon", "task_order": 2},
      {"task": "Third task for the beacon", "task_order": 3}
    ]
  }
}
"""

    return jsonify({
        "status": "success",
        "message": "Tasks fetched successfully",
        "data": {"tasks": task_list}
    }), 200

def handle_write_task(request):
    try:
        data = request.json
        if not data:
            return jsonify({"status": "failure", "message": "No JSON data provided", "data": {}}), 400

        beacon_id = data.get('beacon_id')
        task_content = data.get('task')

        if not beacon_id or not task_content:
            return jsonify({"status": "failure", "message": "Beacon ID or task is missing", "data": {}}), 400

        beacon = Beacon.query.filter_by(id=beacon_id).first()
        if not beacon:
            return jsonify({"status": "failure", "message": "Invalid beacon ID", "data": {}}), 404

        if not beacon.alive:
            return jsonify({"status": "failure", "message": "Beacon is not alive", "data": {}}), 404

        highest_task_order = db.session.query(db.func.max(Task.task_order)).filter_by(beacon_id=beacon_id).scalar()
        next_task_order = (highest_task_order or 0) + 1
        

        task_id = str(uuid.uuid4())
        new_task = Task(
            task_id=task_id,
            beacon_id=beacon_id,
            task=task_content,
            status="pending",
            task_order= next_task_order
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

def handle_return_beacon_data(request):
    try:
        data = request.json
        if not data:
            return jsonify({"status": "failure", "message": "No JSON data provided", "data": {}}), 400

        beacon_id = data.get('beacon_id')
        output = data.get('output')

        if not beacon_id or not output:
            return jsonify({"status": "failure", "message": "Beacon ID or output is missing", "data": {}}), 400

        beacon = Beacon.query.filter_by(id=beacon_id).first()
        if not beacon:
            return jsonify({"status": "failure", "message": "Invalid beacon ID", "data": {}}), 404

        if not beacon.alive:
            return jsonify({"status": "failure", "message": "Beacon is not alive", "data": {}}), 404

        result_id = str(uuid.uuid4())
        new_result = Result(
            result_id=result_id,
            task_id=beacon_id,
            output=output
        )
        db.session.add(new_result)
        db.session.commit()

        task = Task.query.filter_by(task_id=beacon_id).first()
        if task:
            task.status = "completed"
            task.completed_at = datetime.datetime.utcnow()
            db.session.commit()

            completed_task_order = task.task_order
            remaining_task = Task.query.filter(Task.beacon_id==beacon_id, Task.task_order > completed_task_order).all()

            for remaining_task in remaining_task:
                remaining_task.task_order -= 1

        beacon.alive = True
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Result saved successfully",
            "data": {"result_id": result_id}
        }), 200

    except Exception as e:
        return jsonify({"status": "failure", "message": f"Failed to save result: {str(e)}", "data": {}}), 500

def handle_delete_beacon_from_db(request):
    try:
        data = request.json
        if not data:
            return jsonify({"status": "failure", "message": "No JSON data provided", "data": {}}), 400

        beacon_ids = data.get('beacon_id')
        if not beacon_ids:
            return jsonify({"status": "failure", "message": "Beacon IDs not provided", "data": {}}), 400

        for beacon_id in beacon_ids:
            beacon = Beacon.query.filter_by(id=beacon_id).first()
            if not beacon:
                return jsonify({"status": "failure", "message": "Invalid beacon ID", "data": {}}), 404

            db.session.delete(beacon)
            db.session.query(Task).filter_by(beacon_id=beacon_id).delete()
            db.session.commit()

        return jsonify({"status": "success", "message": "Beacons deleted successfully", "data": {}}), 200

    except Exception as e:
        return jsonify({"status": "failure", "message": f"Failed to clear beacons: {str(e)}", "data": {}}), 500

