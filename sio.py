import socketio
from flask import Flask
from flask_cors import CORS
from flask import request

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Socket.IO server with eventlet
sio = socketio.Server(cors_allowed_origins='http://localhost:3000', async_mode='eventlet')

# Function to send a message to the client
def send_message_to_client(message):
    sio.emit('message', message)  # Send message to all clients

# Define endpoint for receiving messages from the user
@app.route('/send-message', methods=['POST'])
def send_message():
    message = request.json.get('coordinates')
    send_message_to_client(message)  # Send message to client(s)
    return 'Message sent to clients'

# Attach Socket.IO server to Flask app
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

if __name__ == '__main__':
    # Run the server using eventlet
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('localhost', 5001)), app)
