import os


class Agent():
# Atributes will be defined through the database
    def __init__(self, name, id, key, path, config):
        self.name = name
        self.id = id
        self.key = key
        self.path =  path
        self.config = config 
          
        if not os.path.exists (self.path):
            os.makedirs(self.path)

    def get_task_file(self):
        return f"data/agents/{self.name}/task"
    


#finish this
 #   def change_config(self, config_path):
  #      with open (config_path, "w") as f:
   #         f.write(data)


    def read_task(self):
        task_file = self.get_task_file()

        if os.path.exists(task_file):    
            with open (task_file, "r") as f:   
                task = f.read()

                if task.strip() != "0":        #After reading the task, clear if it hasn't been cleared
                    self.clear_task(task_file) 

            return (task, 200)
        else:
            return ('', 204)
        

    def clear_task(self, task_file):
        with open (task_file, "w") as f:
            f.write("0")


    def write_task(self, task):
        task_file = self.get_task_file()
        reflected_output = f"{self.name} has tasked to execute {task}"

        if os.path.exists(task_file):
            with open (task_file, "w") as f:
                f.write(task)

        return reflected_output


    def register_agent():
        name = ""
        remote_ip = ""
        remote_hostname = ""
        #write_database()     #Define the function later to save data in DB
        return (name, 200)
    
