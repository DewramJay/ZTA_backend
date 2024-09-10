from routes import create_app
from flask_socketio import SocketIO

# app = create_app()

# if __name__ == '__main__':
#     app.run(debug=True, port=2000)



app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=2000, debug=True)