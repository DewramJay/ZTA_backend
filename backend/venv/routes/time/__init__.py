from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import sqlite3
import json


time = Blueprint('time', __name__)
cors = CORS(time, origins='*')
database_path = '/home/kali/Desktop/project/eval/ZTA_main_2/main/new_devices.db'

#########################################
@time.route("/api/add_time", methods=["POST"])
def add_device():
    data = request.get_json()
    time = data.get('time')
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('INSERT INTO timesr1 (time) VALUES (?)', 
                  (time,))
        conn.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
#########################################

