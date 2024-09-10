from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
cors = CORS(app, origins='*')

@app.route("/api/users", methods=["GET"])
def result():
    try:
        conn = sqlite3.connect('new_devices.db')
        c = conn.cursor()
        c.execute('SELECT device_name FROM new_devices')
        users = [row[0] for row in c.fetchall()]
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True, port=2000)
