from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import sqlite3
import json


device = Blueprint('device', __name__)
cors = CORS(device, origins='*')
database_path = '/home/kali/Desktop/project/eval/ZTA_main_2/main/new_devices.db'


@device.route("/api/users", methods=["GET"])
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

@device.route("/api/get_active_devices", methods=["GET"])
def get_active_devices():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT ip_address, mac_adress, device_name FROM new_devices WHERE status = "active"')
        devices = [{"ip_address": row[0], "mac_address": row[1], "device_name": row[2]} for row in c.fetchall()]
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(devices)

def notify_clients(new_mac_address=None):
    try:
        print(new_mac_address)
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT ip_address, mac_adress, device_name FROM new_devices WHERE status = "active"')
        devices = [{"ip_address": row[0], "mac_address": row[1], "device_name": row[2]} for row in c.fetchall()]
        socketio = current_app.extensions['socketio']
        socketio.emit('update', {'devices': devices, 'new_mac_address': new_mac_address})
    except sqlite3.Error as e:
        print("Error fetching data:", e)
    finally:
        if conn:
            conn.close()

@device.route("/api/add_device", methods=["POST"])
def add_device():
    data = request.get_json()
    ip_address = data.get('ip_address')
    mac_address = data.get('mac_address')
    device_name = data.get('device_name')
    status = data.get('status')
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('INSERT INTO new_devices (ip_address, mac_adress, device_name, status) VALUES (?, ?, ?, ?)', 
                  (ip_address, mac_address, device_name, status))
        conn.commit()
        notify_clients(new_mac_address=mac_address)  # Notify clients after inserting new data
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

def update_ip_address(mac_address, ip_address, status):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE new_devices SET ip_address = ?, status = ? WHERE mac_adress = ?", (ip_address, status, mac_address))
        conn.commit()
        notify_clients(new_mac_address=mac_address)  # Notify clients after inserting new data
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

@device.route('/api/update_ip', methods=['POST'])
def update_ip():
    data = request.get_json()
    mac_address = data.get('mac_address')
    ip_address = data.get('ip_address')
    status = data.get('status')
    
    if not mac_address or not ip_address:
        return jsonify({'error': 'MAC address and IP address are required'}), 400
    
    if update_ip_address(mac_address, ip_address, status):
        return jsonify({'message': 'IP address updated successfully'}), 200
    else:
        return jsonify({'error': 'Failed to update IP address'}), 500
    
@device.route("/api/get_device/<mac_address>", methods=["GET"])
def get_device(mac_address):
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT ip_address, mac_adress, device_name FROM new_devices WHERE mac_adress = ?', (mac_address,))
        row = c.fetchone()
        if row:
            device = {"ip_address": row[0], "mac_address": row[1], "device_name": row[2]}
            return jsonify(device), 200
        else:
            return jsonify({"error": "Device not found"}), 404
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


############ update device name #################
def update_device_name(mac_address, device_name):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE new_devices SET device_name = ? WHERE mac_adress = ?", (device_name, mac_address))
        conn.commit()
        notify_clients(new_mac_address=mac_address)  # Notify clients after inserting new data
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

@device.route('/api/update_device_name', methods=['POST'])
def device_name():
    data = request.get_json()
    mac_address = data.get('mac_address')
    device_name = data.get('device_name')
    
    if not mac_address or not device_name:
        return jsonify({'error': 'MAC address and device name are required'}), 400
    
    if update_device_name(mac_address, device_name):
        return jsonify({'message': 'device name updated successfully'}), 200
    else:
        return jsonify({'error': 'Failed to update deivce name'}), 500

####################################################

############ update device status #################
def update_device_status(mac_address, status):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE new_devices SET status = ? WHERE mac_adress = ?", (status, mac_address))
        conn.commit()
        notify_clients(new_mac_address=mac_address)  # Notify clients after inserting new data
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

@device.route('/api/update_device_status', methods=['POST'])
def device_status():
    data = request.get_json()
    mac_address = data.get('mac_address')
    status = data.get('status')
    
    if not mac_address or not status:
        return jsonify({'error': 'MAC address and device status are required'}), 400
    
    if update_device_status(mac_address, status):
        return jsonify({'message': 'device status updated successfully'}), 200
    else:
        return jsonify({'error': 'Failed to update deivce status'}), 500

####################################################

############ update connected devices ####################
def update_connected_devices(mac_address, connected_device):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE new_devices SET connected_devices = ? WHERE mac_adress = ?",
                       (json.dumps(connected_device), mac_address))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

    

@device.route('/api/update_connected_devices', methods=['POST'])
def update_device():
    # Extract data from the POST request
    data = request.get_json()
    mac_address = data.get('device_mac')
    connected_device = data.get('connected_device')

    if not mac_address or not connected_device:
        return jsonify({'error': 'MAC address and connected devices are required'}), 400
    
    if update_connected_devices(mac_address, connected_device):
        return jsonify({'message': 'connected devices updated successfully'}), 200
    else:
        return jsonify({'error': 'Failed to update connected devices'}), 500

#######################################################

################# get connected devices ###############
def connected_devices(device_mac):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        # Query to get the connected devices for the given MAC address
        cursor.execute("SELECT connected_devices FROM new_devices WHERE mac_adress=?", (device_mac,))
        row = cursor.fetchone()

        if row and row[0]:
            # Load the allowed devices from JSON string
            allowed_devices = json.loads(row[0])
            return set(allowed_devices)  # Return as a set for easy comparison

        return set()  # Return an empty set if no devices are found

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return set()
    except Exception as e:
        print(f"Exception in get_allowed_devices: {e}")
        return set()
    finally:
        conn.close()



@device.route("/api/get_connected_devices/<mac_address>", methods=["GET"])
def get_connected_devices(mac_address):
    allowed = connected_devices(mac_address)
    return jsonify({'allowed_devices': list(allowed)}), 200 
    
#######################################################

############## check device status ####################
@device.route("/api/check_device_status", methods=["GET"])
def check_device_status():
    data = request.get_json()
    ip_address = data.get('ip_address')
    mac_address = data.get('mac_address')
    
    if not ip_address and not mac_address:
        return jsonify({"error": "Please provide either IP address or MAC address"}), 400
    
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        
        if ip_address:
            c.execute('SELECT status FROM new_devices WHERE ip_address = ?', (ip_address,))
        elif mac_address:
            c.execute('SELECT status FROM new_devices WHERE mac_adress = ?', (mac_address,))
        
        result = c.fetchone()
        if result:
            status = result[0]
            return jsonify({"device_status": status}), 200
        else:
            return jsonify({"error": "Device not found"}), 404
    
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if conn:
            conn.close()


#######################################################

################ set all devices inactive ##############

# Function to update the status of all devices to 'inactive'
def update_all_devices_status():
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE new_devices SET status = ?", ('inactive',))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

# Route to update all devices' status to 'inactive'
@device.route('/api/update_all_devices_status', methods=['POST'])
def set_all_devices_inactive():
    if update_all_devices_status():
        return jsonify({'message': 'All devices updated to inactive successfully'}), 200
    else:
        return jsonify({'error': 'Failed to update device status'}), 500

########################################################

############# check connected device status #############
def check_status(mac_address):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Query to check if the new_column equals 1 for the given MAC address
    cursor.execute("SELECT connected_device_status FROM new_devices WHERE mac_adress = ?", (mac_address,))
    result = cursor.fetchone()

    conn.close()

    # Check if we found a result and if the new_column is 1
    if result and result[0] == 1:
        return True
    else:
        return False



@device.route('/api/check_connected_device_status', methods=['GET'])
def check_connected_device_status():
    data = request.get_json()
    mac_address = data.get('mac_address')
    
    if not mac_address:
        return jsonify({'error': 'MAC address is required'}), 400

    # Call the function to check the status
    status = check_status(mac_address)

    return jsonify({'mac_address': mac_address, 'status': status})

#########################################################

############ update connected device status #################
def update_connected_device_status(mac_address, connected_device_status):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE new_devices SET connected_device_status = ? WHERE mac_adress = ?", (connected_device_status, mac_address))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

@device.route('/api/update_connected_device_status', methods=['POST'])
def connected_device_status():
    data = request.get_json()
    mac_address = data.get('mac_address')
    connected_device_status = data.get('connected_device_status')
    
    if not mac_address or not device_name:
        return jsonify({'error': 'MAC address and connected_device_status are required'}), 400
    
    if update_connected_device_status(mac_address, connected_device_status):
        return jsonify({'message': 'connected_device_status updated successfully'}), 200
    else:
        return jsonify({'error': 'Failed to update connected_device_status'}), 500

####################################################


############ add a connected device ##############
def add_connected_device(mac_address, device_to_add):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Retrieve the current connected devices for the given MAC address
        cursor.execute("SELECT connected_devices FROM new_devices WHERE mac_adress = ?", (mac_address,))
        result = cursor.fetchone()
        if result is None:
            return False, 'MAC address not found'

        # Load the connected devices JSON string into a Python list
        connected_devices = json.loads(result[0])

        # Add the specified device if it's not already in the list
        if device_to_add in connected_devices:
            return False, 'Device is already in the connected devices list'
        
        connected_devices.append(device_to_add)

        # Update the connected_devices in the database
        cursor.execute("UPDATE new_devices SET connected_devices = ? WHERE mac_adress = ?",
                       (json.dumps(connected_devices), mac_address))
        conn.commit()
        return True, 'Device added successfully'

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False, 'Database error'
    finally:
        conn.close()

    

@device.route('/api/add_connected_device', methods=['POST'])
def connected_device():
    # Extract data from the POST request
    data = request.get_json()
    mac_address = data.get('device_mac')
    device_to_add = data.get('connected_device')

    if not mac_address or not device_to_add:
        return jsonify({'error': 'MAC address and device to add are required'}), 400
    
    success, message = add_connected_device(mac_address, device_to_add)
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'error': message}), 500
#####################################################


