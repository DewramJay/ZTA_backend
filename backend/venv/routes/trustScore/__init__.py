from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import sqlite3
import json


trustScore = Blueprint('trustScore', __name__)
cors = CORS(trustScore, origins='*')
database_path = '/home/kali/Desktop/project/eval/ZTA_main_2/main/score_model.db'


def notify_score():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT mac_address, ml, ea, cr, st, total FROM trust_score')
        scores = [{"mac_address": row[0], "ml": row[1], "ea": row[2], "cr": row[3], "st": row[4], "total": row[5]} for row in c.fetchall()]
        socketio = current_app.extensions['socketio']
        socketio.emit('scores', scores)
    except sqlite3.Error as e:
        print("Error fetching data:", e)
    finally:
        if conn:
            conn.close()


def calculate_and_update_total(mac_address):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Fetch the current values of ml, ea, cr, st
        cursor.execute('SELECT ml, ea, cr, st FROM trust_score WHERE mac_address = ?', (mac_address,))
        row = cursor.fetchone()

        if row:
            ml, ea, cr, st = row

            # Calculate the new total by subtracting ml, ea, cr, and st from the previous total
            new_total = 0.4379 * ml + 0.1879 * ea + 0.3126 * cr + 0.06275 * st  # Modify this logic as per your requirement

            # Update the total in the database
            cursor.execute('UPDATE trust_score SET total = ? WHERE mac_address = ?', (new_total, mac_address))
            conn.commit()
            notify_score()

        conn.close()

    except Exception as e:
        print(f"Error calculating and updating total: {e}")

########## block access #################
def block_mac(mac_address):
    """ Function to block the MAC address by calling the block-mac endpoint """
    try:
        # Make a GET request to the block-mac endpoint
        response = requests.get(f'http://localhost:2000/block_access/{mac_address}')
        if response.status_code == 200:
            print(f"Successfully blocked MAC address {mac_address}")
        else:
            print(f"Failed to block MAC address {mac_address}: {response.text}")
    except Exception as e:
        print(f"Error blocking MAC address: {e}")


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
            ml = data.get('ml', 1)
            ea = data.get('ea', 1)
            cr = data.get('cr', 1)
            st = data.get('st', 1)
            total = data.get('total', 1)

            cursor.execute('''
                INSERT INTO trust_score (mac_address, ml, ea, cr, st, total)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (mac_address, ml, ea, cr, st, total))        

        conn.commit()
        conn.close()
        calculate_and_update_total(mac_address)
        notify_score()

        return jsonify({'message': 'Data inserted/updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
################################################



########### get score ##############
@trustScore.route("/api/get_score", methods=["GET"])
def get_users():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT mac_address, ml, ea, cr, st, total FROM trust_score')
        scores = [{"mac_address": row[0], "ml": row[1], "ea": row[2], "cr": row[3], "st": row[4], "total": row[5]} for row in c.fetchall()]
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(scores)
######################################

