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

