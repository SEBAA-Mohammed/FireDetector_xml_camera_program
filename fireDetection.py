import cv2         # Library for openCV
import threading   # Library for threading allowing code to run in the background
import playsound   # Library for playing alarm sound
import smtplib     # Library for sending emails

# To access xml file which includes positive and negative images of fire.
# (Trained images) File is also provided with the code.
fire_cascade = cv2.CascadeClassifier('fire_detection_cascade_model.xml')

# To start camera this command is used '0' for laptop built-in camera
# and '1' for USB attached camera
video = cv2.VideoCapture(0)
runOnce = False  # To ensure some actions are performed once only


def play_alarm_sound():
    """Defined function to play alarm post fire detection using threading"""
    # To play alarm mp3 audio file is also provided with the code.
    playsound.playsound('alarm-sound.mp3', True)
    print('Fire alarm end')


def send_mail():
    """Defined function to send e-mail post fire detection using threading"""
    recipient_mail = 'add recipients mail'  # recipients mail
    recipient_mail = recipient_mail.lower()  # To lower case mail

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        # Performs an EHLO greeting to the server
        server.ehlo()
        # Initiates TLS encryption for secure communication
        server.starttls()
        # Senders mail ID and password
        server.login('add senders mail', 'add senders password')
        # Recipients mail with mail message
        server.sendmail('add recipients mail', recipient_mail,
                        'Warning fire accident has been reported')
        # To print in consol to whom mail is sent
        print("Alert mail sent successfully to {}".format(recipient_mail))
        server.close()  # To close SMTP server

    except Exception as e:
        print(e)  # Print error if there is any


while (True):
    alarm_status = False
    # Continuously captures frames from the video as long as ret is True
    ret, frame = video.read()
    # Converts each frame to grayscale for better processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detects fire using the cascade classifier with provided frame resolution
    fire = fire_cascade.detectMultiScale(frame, 1.2, 5)

    # To highlight fire with square
    for (x, y, w, h) in fire:
        # Draws rectangle around detected fire region
        cv2.rectangle(frame, (x-20, y-20), (x+w+20, y+h+20), (255, 0, 0), 2)
        # Extracts region of interest (ROI)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

        if runOnce == False:
            # print('Mail send initiated')
            # To call alarm thread
            # threading.Thread(target=send_mail).start()

            print('Fire alarm initiated')
            # To call alarm thread
            threading.Thread(target=play_alarm_sound).start()

            runOnce = True
        if runOnce == True:
            # print('Mail is already sent once')
            print('Fire alarm is already triggered once')
            runOnce = True

    # Displays the original frame with detected fire regions
    cv2.imshow('frame', frame)

    key = cv2.waitKey(1)  # Wait for a key press for 1 millisecond

    # Check if the pressed key is 'q' or the escape key (27 ASCII value)
    if key == ord('q') or key == 27:
        break  # Break out of the loop and exit the program


cv2.destroyAllWindows()
video.release()
