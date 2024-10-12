from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import sqlite3
import json


trustScore = Blueprint('trustScore', __name__)
cors = CORS(trustScore, origins='*')
database_path = '/home/kali/Desktop/project/eval/ZTA_main_2/main/score_model.db'


# def notify_score_weights():
#     try:
#         conn = sqlite3.connect(database_path)
#         c = conn.cursor()
#         c.execute('SELECT ml_weight, ea_weight, cr_weight, st_weight FROM weights')
#         weights = [{"ml_weight": row[0], "ea_weight": row[1], "cr_weight": row[2], "st_weight": row[3]} for row in c.fetchall()]
#         socketio = current_app.extensions['socketio']
#         socketio.emit('weights', weights)
#     except sqlite3.Error as e:
#         print("Error fetching data:", e)
#     finally:
#         if conn:
#             conn.close()


################ update trust score ###################
@trustScore.route('/api/trust_score', methods=['POST'])
def add_or_update_trust_score():
    try:
        # Extract data from request
        data = request.json
        mac_address = data.get('mac_address')
        
        # Check if mac_address is provided
        if not mac_address:
            return jsonify({'error': 'mac_address is required'}), 400
        
        # Connect to the database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Check if the mac_address already exists
        cursor.execute('SELECT * FROM trust_score WHERE mac_address = ?', (mac_address,))
        # existing_record = cursor.fetchone()
        row = cursor.fetchone()  # Fetch the single row
        
        if row:
            # If a record exists, map it to a dictionary
            existing_record = {'mac_address': row[0], 'ml': row[1], 'ea': row[2], 'cr': row[3], 'st': row[4], 'total': row[5]}
        else:
            existing_record = None

        if existing_record:
            # If record exists, update only the provided fields
            ml = data.get('ml', existing_record['ml'])
            ea = data.get('ea', existing_record['ea'])
            cr = data.get('cr', existing_record['cr'])
            st = data.get('st', existing_record['st'])
            total = data.get('total', existing_record['total'])

            cursor.execute('''
                UPDATE trust_score
                SET ml = ?, ea = ?, cr = ?, st = ?, total = ?
                WHERE mac_address = ?
            ''', (ml, ea, cr, st, total, mac_address))
        else:
            # If record doesn't exist, insert new data with provided values, set missing fields to NULL
            ml = data.get('ml', 0)
            ea = data.get('ea', 0)
            cr = data.get('cr', 0)
            st = data.get('st', 0)
            total = data.get('total', 0)

            cursor.execute('''
                INSERT INTO trust_score (mac_address, ml, ea, cr, st, total)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (mac_address, ml, ea, cr, st, total))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Data inserted/updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
################################################



# ########### get weights ##############
# @trustScore.route("/api/get_weights", methods=["GET"])
# def get_users():
#     try:
#         conn = sqlite3.connect(database_path)
#         c = conn.cursor()
#         c.execute('SELECT ml_weight, ea_weight, cr_weight, st_weight FROM weights')
#         devices = [{"ml_weight": row[0], "ea_weight": row[1], "cr_weight": row[2], "st_weight": row[3]} for row in c.fetchall()]
#     except sqlite3.Error as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         if conn:
#             conn.close()
#     return jsonify(devices)
# ######################################

