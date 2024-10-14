from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import sqlite3

illegalConnection = Blueprint('illegalConnection', __name__)
cors = CORS(illegalConnection, origins='*')

database_path = '/home/kali/Desktop/project/eval/ZTA_main_2/main/new_devices.db'

@illegalConnection.route("/api/get_illegal_connection", methods=["GET"])
def get_users():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        # c.execute('SELECT id, src_mac, dst_mac FROM illegal_connection_alerts')
        # devices = [{"id": row[0], "src_mac": row[1], "dst_mac": row[2]} for row in c.fetchall()]

        query = '''
            SELECT DISTINCT ia.src_mac, nd1.device_name AS src_device_name,
                    ia.dst_mac, nd2.device_name AS dst_device_name
            FROM illegal_connection_alerts ia
            LEFT JOIN new_devices nd1 ON ia.src_mac = nd1.mac_adress
            LEFT JOIN new_devices nd2 ON ia.dst_mac = nd2.mac_adress
        '''

        c.execute(query)

        # Fetch results including both device names
        devices = [{"src_mac": row[0], 
                    "src_device_name": row[1], 
                    "dst_mac": row[2], 
                    "dst_device_name": row[3]} for row in c.fetchall()]
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(devices)

def notify_illegal_alerts():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        query = '''
            SELECT DISTINCT ia.src_mac, nd1.device_name AS src_device_name,
                            ia.dst_mac, nd2.device_name AS dst_device_name
            FROM illegal_connection_alerts ia
            LEFT JOIN new_devices nd1 ON ia.src_mac = nd1.mac_adress
            LEFT JOIN new_devices nd2 ON ia.dst_mac = nd2.mac_adress
        '''

        c.execute(query)
        alerts = [{"src_mac": row[0], 
                    "src_device_name": row[1], 
                    "dst_mac": row[2], 
                    "dst_device_name": row[3]} for row in c.fetchall()]
        socketio = current_app.extensions['socketio']
        socketio.emit('illegal_connection', alerts)
    except sqlite3.Error as e:
        print("Error fetching data:", e)
    finally:
        if conn:
            conn.close()

@illegalConnection.route("/api/add_illegal_connection", methods=["POST"])
def add_alert():
    data = request.get_json()
    src_mac = data.get('src_mac')
    dst_mac = data.get('dst_mac')
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('INSERT INTO illegal_connection_alerts (src_mac, dst_mac) VALUES (?, ?)', 
                  (src_mac, dst_mac))
        conn.commit()
        notify_illegal_alerts()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@illegalConnection.route("/api/delete_illegal_connections", methods=["DELETE"])
def delete_alert():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute("DELETE FROM illegal_connection_alerts ")
        conn.commit()
        return jsonify({"status": "success"})

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return set()
    except Exception as e:
        print(f"Exception in delete_alerts: {e}")
        return set()
    finally:
        conn.close()


################# get blacklist ip count ###################
@illegalConnection.route("/api/get_illegal_connection_count", methods=["GET"])
def get_blacklist_mac_count():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(DISTINCT dst_mac) FROM illegal_connection_alerts')
        count = c.fetchone()[0]
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify({"illegal_connection_count": count})

############################################################

@illegalConnection.route("/api/delete_specific_alert", methods=["DELETE"])
def delete_specific_alert():
    data = request.get_json()
    src_mac = data.get('src_mac')
    dst_mac = data.get('dst_mac')
    
    if not src_mac or not dst_mac:
        return jsonify({"error": "src_mac and dst_mac are required"}), 400
    
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        # Delete the specific row based on src_mac and dst_mac
        c.execute("DELETE FROM illegal_connection_alerts WHERE src_mac = ? AND dst_mac = ?", 
                  (src_mac, dst_mac))
        conn.commit()
        notify_illegal_alerts()
        
        if c.rowcount == 0:
            return jsonify({"error": "No matching row found"}), 404

        return jsonify({"status": "success"}), 200

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


################# get blacklist ip count for specific mac ###################
@illegalConnection.route("/api/get_related_mac_count", methods=["GET"])
def get_related_mac_count():
    data = request.get_json()
    mac_address = data.get('mac_address')
    
    if not mac_address:
        return jsonify({"error": "MAC address is required"}), 400
    
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()

        # Get distinct dst_mac where given mac is in src_mac
        c.execute('''
            SELECT DISTINCT dst_mac 
            FROM illegal_connection_alerts 
            WHERE src_mac = ?
        ''', (mac_address,))
        unique_macs = set(row[0] for row in c.fetchall())

        # # Get distinct src_mac where given mac is in dst_mac
        # c.execute('''
        #     SELECT DISTINCT src_mac 
        #     FROM illegal_connection_alerts 
        #     WHERE dst_mac = ?
        # ''', (mac_address,))
        # src_macs_from_dst = set(row[0] for row in c.fetchall())

        # Combine both sets to get unique MAC addresses
        # unique_macs = dst_macs_from_src.union(src_macs_from_dst)

        mac_count = len(unique_macs)

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
    
    return jsonify({"related_mac_count": mac_count})

#############################################################################

@illegalConnection.route("/api/delete_alerts_by_src_mac", methods=["DELETE"])
def delete_alerts_by_src_mac():
    data = request.get_json()
    src_mac = data.get('src_mac')
    
    if not src_mac:
        return jsonify({"error": "src_mac is required"}), 400
    
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        # Delete all rows where src_mac matches the given value
        c.execute("DELETE FROM illegal_connection_alerts WHERE src_mac = ?", (src_mac,))
        conn.commit()
        notify_illegal_alerts()
        
        if c.rowcount == 0:
            return jsonify({"error": "No matching rows found"}), 404

        return jsonify({"status": "success"}), 200

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
