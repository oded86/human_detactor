import cv2
from datetime import datetime
import os.path
from telegram.ext import Updater
import paramiko

# Configuration
host = "incontrol-sys.com"  # hard-coded
port = 22


VIDEO_URL = "https://stream.cawamo.com/hof/hof1.m3u8"
LAT = "31.9702383"
LON = "34.8145154"
# SFTP
THEUSERNAME = ""
THEPASSWORD = ""

# Path to XML

file_to_open = os.path.join("hog_xml", "haarcascade_fullbody.xml")
body_classifier = cv2.CascadeClassifier(file_to_open)
# Number of allowed People

maxVal = 1


def upload_to_server(img_to_upload):
    transport = paramiko.Transport((host, port))
    transport.connect(username=THEUSERNAME, password=THEPASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    path = './human_detactor/' + img_to_upload  # hard-coded
    sftp.put(img_to_upload,path)
    sftp.close()
    transport.close()
    return 'Done'


def send_message_pedestrians(message_text, pic1):
    pic = "https://incontrol-sys.com/human_detactor/" + pic1
    print("starting sendMessage func..................")
    print(LAT)
    print(LON)
    # send message to telegram
    updater = Updater(
        token='1702864193:AAGj_J3ipAQ3wS0P1a2GEoEnnaAXOx9f9FY', use_context=True)
    updater.bot.sendPhoto(
        chat_id='-519827084', photo='https://incontrol-sys.com/images/alert.jpg')
    updater.bot.sendMessage(chat_id='-519827084',
                            text='the details: ' + message_text + ' in the location:')
    # updater.bot.sendMessage(chat_id='-519827084', text=address)
    updater.bot.sendLocation(chat_id='-519827084',
                             latitude=float(LAT),
                             longitude=float(LON))
    updater.bot.send_photo(chat_id='-519827084', photo=pic)


# Initiate video capture for video file
cap = cv2.VideoCapture(VIDEO_URL)
datetime_start = datetime.now()

while cap.isOpened():
    # Read first frame
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Pass frame to our body classifier
    bodies = body_classifier.detectMultiScale(gray, 1.1, 1)
    i = len(bodies)
    # Extract bounding boxes for any bodies identified
    person = 1
    for (x, y, w, h) in bodies:
        cv2.rectangle(gray, (x, y), (x + w, y + h), (0, 255, 255), 2)
        cv2.putText(gray, f'person {person}', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        person += 1
    if i <= maxVal:
        datetime_start = datetime.now()
        print(f'start time: {datetime_start}')
    if i > maxVal:
        datetime_end = datetime.now()
        minutes_diff = (datetime_end - datetime_start).total_seconds() / 60.0
        message = f'found {i} pedestrians, allowed max of {maxVal} pedestrians'
        if minutes_diff > 1:
            print(message)
            img_name = 'hof1_' + datetime_end.strftime("%m-%d-%Y_%H_%M_%S") + '.jpg'
            cv2.imwrite(img_name, gray)
            uploaded = upload_to_server(img_name)
            if uploaded == 'Done':
                print(f'{minutes_diff} minutes of high pedestrians traffic has passed, sending alert')
                send_message_pedestrians(message, img_name)
                datetime_start = datetime.now()

    cv2.imshow('Pedestrians', gray)
    if cv2.waitKey(1) == 13:  # 13 is the Enter Key
        break
cap.release()
cv2.destroyAllWindows()
