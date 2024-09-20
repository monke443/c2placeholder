class Task:
    def __init__(self, task_id, beacon_id, task_content, status="pending", task_order=0):
        self.task_id = task_id
        self.beacon_id = beacon_id
        self.task_content = task_content
        self.status = status
        self.task_order =  task_order
