from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import sqlite3
import json


reEvaluation = Blueprint('reEvaluation', __name__)
cors = CORS(evaluation, origins='*')
database_path = '/home/kali/Desktop/project/eval/ZTA_main_2/main/new_devices.db'

#########################################
def evaluate_device(device_id):
    # Replace this logic with actual evaluation code
    device = get_device_from_db(device_id)  # Fetch device from DB
    evaluation_result = perform_evaluation(device)  # Perform evaluation

    if evaluation_result:
        device['permission_granted'] = True  # Update permission
        device['next_evaluation'] = datetime.utcnow() + timedelta(minutes=30)  # Set next evaluation time
    else:
        device['permission_granted'] = False  # Deny permission

    update_device_in_db(device)  # Save updates to DB
    print(f"Device {device_id} re-evaluated and updated.")

# Schedule the evaluation job
def schedule_evaluation(device_id):
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: evaluate_device(device_id), 'interval', minutes=30)  # Re-evaluate every 30 minutes
    scheduler.start()

# Sample route to simulate device connection
@reEvaluation.route('/connect_device/<int:device_id>', methods=['POST'])
def connect_device(device_id):
    # Logic to handle initial connection
    schedule_evaluation(device_id)  # Schedule recurring evaluation for this device
    return jsonify({"message": "Device connected and scheduled for evaluation."})
#########################################

