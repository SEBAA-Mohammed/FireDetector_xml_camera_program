import cv2
import numpy as np
import threading
import smtplib
import matplotlib.pyplot as plt
import requests
from PIL import Image
import io

fire_cascade = cv2.CascadeClassifier('fire_detection_cascade_model.xml')
video = cv2.VideoCapture(0)
runOnce = False


def play_alarm_sound():
    """Defined function to play alarm post fire detection using threading"""
    # playsound.playsound('alarm-sound.mp3', True)
    print('Fire alarm end')


def send_mail():
    """Defined function to send e-mail post fire detection using threading"""
    recipient_mail = 'add recipients mail'
    recipient_mail = recipient_mail.lower()

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login('add senders mail', 'add senders password')
        server.sendmail('add senders mail', recipient_mail,
                        'Warning fire accident has been reported')
        print("Alert mail sent successfully to {}".format(recipient_mail))
        server.close()

    except Exception as e:
        print(e)


def calculate_distance_and_direction(x, y, width, height, frame_width, frame_height):
    center_x = frame_width // 2
    center_y = frame_height // 2
    distance = np.sqrt((x + width/2 - center_x)**2 +
                       (y + height/2 - center_y)**2)

    return distance


def send_image_to_api(roi_bytes):
    url = 'http://localhost:5001/image'  # API endpoint for sending the image
    files = {'image': ('fire_image.jpg', roi_bytes, 'image/jpeg')}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        print('Image sent successfully to API.')
    else:
        print('Failed to send image to API.')


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
            distance = calculate_distance_and_direction(
                x, y, w, h, frame.shape[1], frame.shape[0])
            print(distance)
            url = 'http://localhost:5001/send-message'

            # Define the message you want to send
            message = {'coordinates': [33.98785020929, -5.020268935320675]}

            # Send the HTTP POST request with the message payload
            response = requests.post(url, json=message)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                print('Message sent successfully.')
            else:
                print('Failed to send message.')


            # Convert the frame to bytes
            frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
            # Send the full frame image to the API
            threading.Thread(target=send_image_to_api, args=(frame_bytes,)).start()


            # # Capture ROI and send it to the API
            # roi_bytes = cv2.imencode('.jpg', roi_color)[1].tobytes()
            # threading.Thread(target=send_image_to_api, args=(roi_bytes,)).start()

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