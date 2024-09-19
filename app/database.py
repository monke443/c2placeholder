from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Beacon(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    ip = db.Column(db.String(50))
    hostname = db.Column(db.String(100))
    permissions = db.Column(db.String(20))
    registration_time = db.Column(db.DateTime, default=datetime.utcnow)
    alive = db.Column(db.Boolean, default=True)

class Task(db.Model):
    task_id = db.Column(db.String(36), primary_key=True)
    beacon_id = db.Column(db.String(36), db.ForeignKey('beacon.id'), nullable=False)
    task = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    beacon = db.relationship('Beacon', backref='tasks')

class Result(db.Model):
    result_id = db.Column(db.String(36), primary_key=True)
    task_id = db.Column(db.String(36), db.ForeignKey('task.task_id'), nullable=False)
    output = db.Column(db.Text, nullable=False)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)

class Agent(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100))
    path = db.Column(db.Text)
    key = db.Column(db.Text)
    config = db.Column(db.Text)
