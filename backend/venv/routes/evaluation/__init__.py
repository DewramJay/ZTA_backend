from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import sqlite3

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
                       (json.dumps(open_ports), result, device_mac))
        conn.commit()
        conn.close()
        return "Device updated in the database"
    else:
        # Insert a new device into the database
        cursor.execute("INSERT INTO evaluation (ip_address, mac_address, open_ports, password_status) VALUES (?, ?, ?, ?)",
                       (target_ip, device_mac, json.dumps(open_ports), result))
        conn.commit()
        conn.close()
        return "Data added to the database"

# Create an API endpoint for handling the device information
@evaluation.route('/update_evaluation', methods=['POST'])
def update_device():
    # Extract data from the POST request
    data = request.get_json()
    device_mac = data.get('device_mac')
    target_ip = data.get('target_ip')
    open_ports = data.get('open_ports')
    result = data.get('result')

    # Call the function to handle the device logic
    response = handle_evaluation(device_mac, target_ip, open_ports, result)

    # Return a JSON response
    return jsonify({"message": response})

#######################################################

