from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import sqlite3

evaluation = Blueprint('newDevice', __name__)
cors = CORS(evaluation, origins='*')

database_path = '/home/kali/Desktop/project/eval/ZTA_main_2/main/new_devices.db'

@evaluation.route("/api/newDeviceIp", methods=["GET"])
def get_users():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT ip_address, mac_adress, device_name FROM new_devices')
        devices = [{"ip_address": row[0], "mac_address": row[1], "device_name": row[2]} for row in c.fetchall()]
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(devices)

def notify_clients():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT ip_address, mac_adress, device_name FROM new_devices')
        devices = [{"ip_address": row[0], "mac_address": row[1], "device_name": row[2]} for row in c.fetchall()]
        socketio = current_app.extensions['socketio']
        socketio.emit('update', devices)
    except sqlite3.Error as e:
        print("Error fetching data:", e)
    finally:
        if conn:
            conn.close()

@evaluation.route("/api/add_device", methods=["POST"])
def add_device():
    data = request.get_json()
    ip_address = data.get('ip_address')
    mac_address = data.get('mac_address')
    device_name = data.get('device_name')
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('INSERT INTO new_devices (ip_address, mac_adress, device_name) VALUES (?, ?, ?)', 
                  (ip_address, mac_address, device_name))
        conn.commit()
        notify_clients()  # Notify clients after inserting new data
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

