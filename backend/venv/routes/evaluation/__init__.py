from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import sqlite3
import json
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta


evaluation = Blueprint('evaluation', __name__)
cors = CORS(evaluation, origins='*')
database_path = '/home/kali/Desktop/project/eval/ZTA_main_2/main/new_devices.db'

   
@evaluation.route("/api/get_evaluation/<mac_address>", methods=["GET"])
def get_evaluation(mac_address):
    try: 
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT ip_address, mac_address, open_ports, password_status FROM evaluation WHERE mac_address = ?', (mac_address,))
        row = c.fetchone()
        if row:
            evaluation = {"ip_address": row[0], "mac_address": row[1], "open_ports": row[2], "password_status": row[2]}
            return jsonify(evaluation), 200
        else:
            return jsonify({"error": "Evaluation not found"}), 404
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


############ update evaluation ####################
def handle_evaluation(device_mac, target_ip, open_ports, result):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Check if the device exists in the database
    cursor.execute("SELECT mac_address FROM evaluation WHERE mac_address = ?", (device_mac,))
    mac = cursor.fetchone()

    if mac:
        # Update the existing device
        cursor.execute("UPDATE evaluation SET open_ports = ?, password_status = ? WHERE mac_address = ?",
                       (open_ports, result, device_mac))
        conn.commit()
        conn.close()
        return "Device updated in the database"
    else:
        # Insert a new device into the database
        cursor.execute("INSERT INTO evaluation (ip_address, mac_address, open_ports, password_status) VALUES (?, ?, ?, ?)",
                       (target_ip, device_mac, open_ports, result))
        conn.commit()
        conn.close()
        return "Data added to the database"

# Create an API endpoint for handling the device information
@evaluation.route('/api/update_evaluation', methods=['POST'])
def update_device():
    # Extract data from the POST request
    data = request.get_json()
    device_mac = data.get('mac_address')
    target_ip = data.get('target_ip')
    open_ports = data.get('open_ports')
    result = data.get('result')

    # Call the function to handle the device logic
    response = handle_evaluation(device_mac, target_ip, json.dumps(open_ports), result)

    # Return a JSON response
    return jsonify({"message": response})

#######################################################


############## re-evaluation ##################
def re_evaluate_device(app, device_ip, device_mac, hostname, interface_description):
    # print("re evaluate !!!!!!!!!! : " + device_ip)
    with app.app_context():
        socketio = current_app.extensions['socketio']
        socketio.emit('re_evaluate', {
            'device_ip': device_ip,
            'device_mac': device_mac,
            'hostname': hostname,
            'interface_description': interface_description
        })
        print(f"Scheduled re-evaluation triggered for device IP: {device_ip}")


# Schedule the evaluation job
# def schedule_evaluation(device_ip, device_mac, hostname, interface_description):
#     app = current_app._get_current_object()
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(lambda: re_evaluate_device(app, device_ip, device_mac, hostname, interface_description), 'interval', minutes=1)  # Re-evaluate every 30 minutes
#     scheduler.start()

def schedule_evaluation(device_ip, device_mac, hostname, interface_description):
    app = current_app._get_current_object()
    scheduler = BackgroundScheduler()
    run_time = datetime.now() + timedelta(minutes=1)  # Schedule the task to run after 1 minute
    scheduler.add_job(lambda: re_evaluate_device(app, device_ip, device_mac, hostname, interface_description), 'date', run_date=run_time)  # Run once at the specified time
    scheduler.start()

# Sample route to simulate device connection
@evaluation.route('/api/re_evaluate', methods=['POST'])
def connect_device():
    data = request.get_json()
    device_ip = data.get('ip_address')
    device_mac = data.get('mac_address')
    hostname = data.get('hostname')
    interface_description = data.get('interface_description')
    # Logic to handle initial connection
    schedule_evaluation(device_ip, device_mac, hostname, interface_description)  # Schedule recurring evaluation for this device
    return jsonify({"message": "Device connected and scheduled for evaluation."})
###############################################

