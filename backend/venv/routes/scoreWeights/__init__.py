from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import sqlite3
import json


scoreWeights = Blueprint('scoreWeights', __name__)
cors = CORS(scoreWeights, origins='*')
database_path = '/home/kali/Desktop/project/eval/ZTA_main_2/main/score_model.db'


############## update weight #####################
@scoreWeights.route('/api/update_weights', methods=['PUT'])
def update_weights():
    data = request.json  # Get the JSON data from the request body
    
    # Extract the weight values from the request
    ml_weight = data.get('ml_weight')
    ea_weight = data.get('ea_weight')
    cr_weight = data.get('cr_weight')
    st_weight = data.get('st_weight')
    
    # Get a connection to the database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Prepare the SQL update statement based on provided values
    update_fields = []
    values = []
    
    if ml_weight is not None:
        update_fields.append("ml_weight = ?")
        values.append(ml_weight)
    if ea_weight is not None:
        update_fields.append("ea_weight = ?")
        values.append(ea_weight)
    if cr_weight is not None:
        update_fields.append("cr_weight = ?")
        values.append(cr_weight)
    if st_weight is not None:
        update_fields.append("st_weight = ?")
        values.append(st_weight)
    
    # Update only if there's something to update
    if update_fields:
        query = f"UPDATE weights SET {', '.join(update_fields)} WHERE id = 1"
        cursor.execute(query, values)
        conn.commit()
    
    # Close the connection
    conn.close()
    
    return jsonify({'message': 'Weights updated successfully'}), 200
#############################################

########### get weights ##############
@scoreWeights.route("/api/get_weights", methods=["GET"])
def get_users():
    try:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('SELECT ml_weight, ea_weight, cr_weight, st_weight FROM weights')
        devices = [{"ml_weight": row[0], "ea_weight": row[1], "cr_weight": row[2], "st_weight": row[3]} for row in c.fetchall()]
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(devices)
######################################

