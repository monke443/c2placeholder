import uuid
import socket
import subprocess
import re
import requests
from app.database import Beacon as BeaconDB, Task as TaskDB, db

class Agent:
    def __init__(self, name, id, key, path, config):
        self.name = name
        self.id = id
        self.key = key
        self.path = path
        self.config = config

    def fetch_tasks(self, beacon_id):
        tasks = TaskDB.query.filter_by(beacon_id=beacon_id).all()
        return [task.task for task in tasks], 200 if tasks else 204

    def write_task(self, beacon_id, task_content):
        task_id = str(uuid.uuid4())
        new_task = TaskDB(
            task_id=task_id,
            beacon_id=beacon_id,
            task=task_content,
            status="pending"
        )
        db.session.add(new_task)
        db.session.commit()
        return f"{self.name} has tasked beacon {beacon_id} to execute: {task_content}", 200
