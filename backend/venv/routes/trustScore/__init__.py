from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import sqlite3
import json
import requests


trustScore = Blueprint('trustScore', __name__)
cors = CORS(trustScore, origins='*')
database_path = '/home/kali/Desktop/project/eval/ZTA_main_2/main/score_model.db'


def notify_score():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT mac_address, ml, ea, cr, st, total, check_status  FROM trust_score')
        scores = [{"mac_address": row[0], "ml": row[1], "ea": row[2], "cr": row[3], "st": row[4], "total": row[5],  "check_status": row[6]} for row in c.fetchall()]
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
        cursor.execute('SELECT ml, ea, cr, st, check_status FROM trust_score WHERE mac_address = ?', (mac_address,))
        row = cursor.fetchone()

        if row:
            ml, ea, cr, st, check_status = row

            # Calculate the new total by subtracting ml, ea, cr, and st from the previous total
            new_total = 0.4379 * ml + 0.1879 * ea + 0.3126 * cr + 0.06275 * st  
            
            if new_total < 0.6 and check_status == 0 :
                update_status_in_db(1, mac_address)
                block_mac(mac_address)
            elif new_total >= 0.6 and check_status == 1 :
                update_status_in_db(0, mac_address)
                allow_mac(mac_address)

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
        response = requests.get(f'http://localhost:2000/api/block_access/{mac_address}')
        if response.status_code == 200:
            print(f"Successfully blocked MAC address {mac_address}")
        else:
            print(f"Failed to block MAC address {mac_address}: {response.text}")
    except Exception as e:
        print(f"Error blocking MAC address: {e}")

########## allow access #################
def allow_mac(mac_address):
    """ Function to block the MAC address by calling the block-mac endpoint """
    try:
        # Make a GET request to the block-mac endpoint
        response = requests.get(f'http://localhost:2000/api/allow_access/{mac_address}')
        if response.status_code == 200:
            print(f"Successfully allowed MAC address {mac_address}")
        else:
            print(f"Failed to allow MAC address {mac_address}: {response.text}")
    except Exception as e:
        print(f"Error allowing MAC address: {e}")


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
            existing_record = {'mac_address': row[0], 'ml': row[1], 'ea': row[2], 'cr': row[3], 'st': row[4], 'total': row[5], 'check_status': row[6]}
        else:
            existing_record = None

        if existing_record:
            # If record exists, update only the provided fields
            ml = data.get('ml', existing_record['ml'])
            ea = data.get('ea', existing_record['ea'])
            cr = data.get('cr', existing_record['cr'])
            st = data.get('st', existing_record['st'])
            total = data.get('total', existing_record['total'])
            check_status = data.get('check_status', existing_record['check_status'])

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
            check_status = data.get('check_status', 0)

            cursor.execute('''
                INSERT INTO trust_score (mac_address, ml, ea, cr, st, total, check_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (mac_address, ml, ea, cr, st, total, check_status))        

        conn.commit()
        conn.close()
        calculate_and_update_total(mac_address)
        notify_score()

        return jsonify({'message': 'Data inserted/updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
################################################



########### get scores ##############
@trustScore.route("/api/get_score", methods=["GET"])
def get_users():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT mac_address, ml, ea, cr, st, total, check_status FROM trust_score')
        scores = [{"mac_address": row[0], "ml": row[1], "ea": row[2], "cr": row[3], "st": row[4], "total": row[5], "check_status": row[6]} for row in c.fetchall()]
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(scores)
######################################

############ get score ###############
@trustScore.route('/api/trust_score/<mac_address>', methods=['GET'])
def get_trust_score(mac_address):
    try:
        # Connect to the database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Retrieve the record based on mac_address
        cursor.execute('SELECT * FROM trust_score WHERE mac_address = ?', (mac_address,))
        row = cursor.fetchone()

        # Check if a record was found
        if row:
            # Map the row to a dictionary
            trust_score = {
                'mac_address': row[0],
                'ml': row[1],
                'ea': row[2],
                'cr': row[3],
                'st': row[4],
                'total': row[5],
                'check_status': row[6]
            }
            conn.close()
            return jsonify(trust_score), 200
        else:
            conn.close()
            return jsonify({'message': 'No record found for this MAC address'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

######################################

########### update check status ##########
def update_status_in_db(new_status, mac_address):
    # Connect to the database
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    # SQL query to update the status column
    if mac_address is not None:
        query = "UPDATE trust_score SET check_status = ? WHERE mac_address = ?"
        cursor.execute(query, (new_status, mac_address))
    else:
        conn.close()
        return jsonify({'message': 'mac address is required'}), 400
    
    # Commit the transaction and close the connection
    connection.commit()
    connection.close()

@trustScore.route('/api/update_check_status', methods=['POST'])
def update_status():
    # Get the new status and optional row_id from the request JSON data
    data = request.json
    new_status = data.get("status")
    mac_address = data.get("mac_address")  # Optional row ID to update specific row
    
    if new_status is None:
        return jsonify({"error": "Status value is required"}), 400
    
    try:
        # Call function to update the status in the database
        update_status_in_db(new_status, mac_address)
        return jsonify({"message": "Status updated successfully"}), 200
        notify_score()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

##########################################

