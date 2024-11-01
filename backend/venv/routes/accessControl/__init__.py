from flask import Blueprint, jsonify, request, current_app
from flask_cors import CORS
import sqlite3
import json
import subprocess
import os


accessControl = Blueprint('accessControl', __name__)
cors = CORS(accessControl, origins='*')
database_path = '/home/kali/Desktop/project/eval/ZTA_main_2/main/score_model.db'

# Endpoint to run script1.sh with MAC address as parameter
@accessControl.route('/api/block_access/<mac_address>', methods=['GET'])
def run_script1(mac_address):
    try:
        # Path to script1.sh
        script_path = "/home/kali/Desktop/project/ZTA_backend/backend/venv/routes/accessControl/Scripts/blockAccess.sh"
        
        # Run the bash script with MAC address as an argument
        result = subprocess.run(['sudo', 'bash', script_path, mac_address], capture_output=True, text=True)
        
        # Return the result of the script execution
        if result.returncode == 0:
            return jsonify({"message": "Script 1 executed successfully", "output": result.stdout})
        else:
            return jsonify({"message": "Script 1 execution failed", "error": result.stderr}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


# Endpoint to run script2.sh with MAC address as parameter
@accessControl.route('/api/allow_access/<mac_address>', methods=['GET'])
def run_script2(mac_address):
    try:
        # Path to script2.sh
        script_path = "/home/kali/Desktop/project/ZTA_backend/backend/venv/routes/accessControl/Scripts/allowAccess.sh"
        
        # Run the bash script with MAC address as an argument
        result = subprocess.run(['sudo', 'bash', script_path, mac_address], capture_output=True, text=True)
        
        # Return the result of the script execution
        if result.returncode == 0:
            return jsonify({"message": "Script 2 executed successfully", "output": result.stdout})
        else:
            return jsonify({"message": "Script 2 execution failed", "error": result.stderr}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500