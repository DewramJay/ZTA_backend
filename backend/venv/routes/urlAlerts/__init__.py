from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import sqlite3

urlAlert = Blueprint('urlAlert', __name__)
cors = CORS(urlAlert, origins='*')

database_path = '/home/kali/Desktop/project/eval/ZTA_main_2/main/new_devices.db'

@urlAlert.route("/api/get_url_alert", methods=["GET"])
def get_users():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
         # Join the url_alerts with new_devices to get device_name
        query = '''
            SELECT ua.mac_address, ua.blacklist_mac, nd.device_name
            FROM url_alerts ua
            LEFT JOIN new_devices nd ON ua.mac_address = nd.mac_adress
        '''
        
        c.execute(query)
        
        # Fetch results and include device_name
        devices = [{"mac_address": row[0], "blacklist_mac": row[1], "device_name": row[2]} for row in c.fetchall()]
    
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(devices)

def notify_alerts():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
         # Join the url_alerts with new_devices to get device_name
        query = '''
            SELECT ua.mac_address, ua.blacklist_mac, nd.device_name
            FROM url_alerts ua
            LEFT JOIN new_devices nd ON ua.mac_address = nd.mac_adress
        '''
        
        c.execute(query)
        
        # Fetch results and include device_name
        alerts = [{"mac_address": row[0], "blacklist_mac": row[1], "device_name": row[2]} for row in c.fetchall()]
        socketio = current_app.extensions['socketio']
        socketio.emit('alert', alerts)
    except sqlite3.Error as e:
        print("Error fetching data:", e)
    finally:
        if conn:
            conn.close()

@urlAlert.route("/api/add_url_alert", methods=["POST"])
def add_alert():
    data = request.get_json()
    mac_address = data.get('mac_address')
    blacklist_mac = data.get('blacklist_mac')
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('INSERT INTO url_alerts (mac_address, blacklist_mac) VALUES (?, ?)', 
                  (mac_address, blacklist_mac))
        conn.commit()
        notify_alerts()  # Notify clients after inserting new data
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@urlAlert.route("/api/delete_all_alert", methods=["DELETE"])
def delete_alert():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute("DELETE FROM url_alerts")
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
@urlAlert.route("/api/get_blacklist_mac_count", methods=["GET"])
def get_blacklist_mac_count():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(DISTINCT blacklist_mac) FROM url_alerts')
        count = c.fetchone()[0]
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify({"anomaly_count": count})

############################################################


######################## get distinct blacklist ip count #########################
@urlAlert.route("/api/get_blacklist_mac_count_by_mac", methods=["GET"])
def get_blacklist_mac_count_by_mac():
    data = request.get_json()
    mac_address = data.get('mac_address')
    
    if not mac_address:
        return jsonify({"error": "MAC address parameter is missing"}), 400
    
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(DISTINCT blacklist_mac) FROM url_alerts WHERE mac_address = ?', (mac_address,))
        count = c.fetchone()[0]
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
    
    return jsonify({"anomaly_count": count})



#################### delete specific alerts ######################
@urlAlert.route("/api/delete_specific_alert", methods=["DELETE"])
def delete_specific_alert():
    try:
        data = request.get_json()
        mac_address = data.get('mac_address')

        conn = sqlite3.connect(database_path)
        c = conn.cursor()

        if mac_address:
            c.execute("DELETE FROM url_alerts WHERE mac_address = ?", (mac_address,))
        else:
            print("mac address is needed")

        conn.commit()
        return jsonify({"status": "success"})

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"status": "error", "message": "Database error"})

    except Exception as e:
        print(f"Exception in delete_alerts: {e}")
        return jsonify({"status": "error", "message": "Exception occurred"})

    finally:
        conn.close()
##################################################################


@urlAlert.route("/api/delete_alert_by_mac/<mac_address>", methods=["DELETE"])
def delete_alert_by_mac(mac_address):
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        # Use parameterized query to prevent SQL injection
        c.execute("DELETE FROM url_alerts WHERE mac_address = ?", (mac_address,))
        conn.commit()
        
        return jsonify({"status": "success"})

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"status": "failure", "error": str(e)}), 500
    except Exception as e:
        print(f"Exception in delete_alert: {e}")
        return jsonify({"status": "failure", "error": str(e)}), 500
    finally:
        conn.close()