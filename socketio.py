import cv2
import numpy as np
import smtplib
import threading
import matplotlib.pyplot as plt
import requests
import socketio
#import server_socketio
from flask import Flask
from flask_cors import CORS
from flask import request


# this for socket.io server
# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Socket.IO server with eventlet
sio = socketio.Server(cors_allowed_origins='http://localhost:3000', async_mode='eventlet')

# Function to send a message to the client
def send_message_to_client(message):
    sio.emit('message', message)  # Send message to all clients

# Attach Socket.IO server to Flask app
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

if __name__ == '__main__':
    # Run the server using eventlet
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('localhost', 5001)), app)

# -------------------------------------------------------------------------------------------------------------------------

fire_cascade = cv2.CascadeClassifier('fire_detection_cascade_model.xml')
video = cv2.VideoCapture(0)
runOnce = False


def play_alarm_sound():
    """Defined function to play alarm post fire detection using threading"""
    print('Fire alarm end')


def send_location():
    url = 'http://localhost:5001/send-message'
    coordinates = [33.98785020929, -5.020268935320675]

    message = {'coordinates': coordinates}

    response = requests.post(url, json=message)

    if response.status_code == 200:
        print('Message sent successfully.')
    else:
        print('Failed to send message.')

x_coordinates = []
y_coordinates = []
fig, ax = plt.subplots()
while (True):
    alarm_status = False
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fire = fire_cascade.detectMultiScale(frame, 1.2, 5)

    for (x, y, w, h) in fire:
        cv2.rectangle(frame, (x-20, y-20), (x+w+20, y+h+20), (255, 0, 0), 2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

        # Add detected coordinates to the lists
        x_coordinates.append(x + w / 2)  # Use the center of the bounding box
        y_coordinates.append(y + h / 2)  # Use the center of the bounding box

        ax.clear()

        # Plot the coordinates
        ax.scatter(x_coordinates, y_coordinates)
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.set_title('Detected Fire Object Positions')
        ax.set_xlim(0, frame.shape[1])  # Limit x-axis to frame width
        ax.set_ylim(frame.shape[0], 0)  # Limit y-axis to frame height
        ax.grid(True)

        # Display the plot
        plt.pause(0.01)  # Pause to update the plot

        if runOnce == False:
            # send the coordinates of the camera
            # send_location()
            send_message_to_client([33.98785020929, -5.020268935320675])

            threading.Thread(target=play_alarm_sound).start()
            runOnce = True
        if runOnce == True:
            print('Fire alarm is already triggered once')
            runOnce = True

    cv2.imshow('frame', frame)

    key = cv2.waitKey(1)

    if key == ord('q') or key == 27:
        break

cv2.destroyAllWindows()
video.release()