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
        c.execute('SELECT id, src_mac, dst_mac FROM illegal_connection_alerts')
        devices = [{"id": row[0], "src_mac": row[1], "dst_mac": row[2]} for row in c.fetchall()]
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(devices)

# def notify_alerts():
#     try:
#         conn = sqlite3.connect(database_path)
#         c = conn.cursor()
#         c.execute('SELECT mac_address, blacklist_mac  FROM url_alerts')
#         alerts = [{"mac_address": row[0], "blacklist_mac": row[1]} for row in c.fetchall()]
#         socketio = current_app.extensions['socketio']
#         socketio.emit('alert', alerts)
#     except sqlite3.Error as e:
#         print("Error fetching data:", e)
#     finally:
#         if conn:
#             conn.close()

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
        # notify_alerts()  # Notify clients after inserting new data
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

