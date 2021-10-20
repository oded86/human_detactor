# pip install urllib
# pip install m3u8
# pip install streamlink
from datetime import datetime, timedelta, timezone
import urllib
import m3u8
import streamlink
import cv2  # openCV
import time
import os

def get_stream(url):
    """
    Get upload chunk url
    input: youtube URL
    output: m3u8 object segment
    """
    # Try this line tries number of times, if it doesn't work,
    # then show the exception on the last attempt
    # Credit, theherk, https://stackoverflow.com/questions/2083987/how-to-retry-after-exception
    tries = 1
    for i in range(tries):
        try:
            streams = streamlink.streams(url)
        except:
            if i < tries - 1:  # i is zero indexed
                print(f"Attempt {i + 1} of {tries}")
                time.sleep(0.1)  # Wait half a second, avoid overload
                continue
            else:
                raise
                break

    stream_url = streams["360p"]  # Alternate, use '360p','best'

    m3u8_obj = m3u8.load(stream_url.args['url'])
    return m3u8_obj.segments[0]  # Parsed stream


def dl_stream(url, filename, chunks):
    """
    Download each chunk to file
    input: url, filename, and number of chunks (int)
    output: saves file at filename location
    returns none.
    """
    pre_time_stamp = datetime(1, 1, 1, 0, 0, tzinfo=timezone.utc)

    # Repeat for each chunk
    # Needs to be in chunks because
    #  1) it's live
    #  2) it won't let you leave the stream open forever
    i = 1
    while i <= chunks:

        # Open stream
        stream_segment = get_stream(url)

        # Get current time on video
        cur_time_stamp = stream_segment.program_date_time
        # Only get next time step, wait if it's not new yet
        if cur_time_stamp <= pre_time_stamp:
            # Don't increment counter until we have a new chunk
            print("NO   pre: ", pre_time_stamp, "curr:", cur_time_stamp)
            time.sleep(0.5)  # Wait half a sec
            pass
        else:
            print("YES: pre: ", pre_time_stamp, "curr:", cur_time_stamp)
            print(f'#{i} at time {cur_time_stamp}')
            # Open file for writing stream
            file = open(filename, 'ab+')  # ab+ means keep adding to file
            # Write stream to file
            with urllib.request.urlopen(stream_segment.uri) as response:
                html = response.read()
                file.write(html)

            # Update time stamp
            pre_time_stamp = cur_time_stamp
            time.sleep(stream_segment.duration)  # Wait duration time - 1

            i += 1  # only increment if we got a new chunk

    return None


def detect(frame):
    bounding_box_cordinates, weights = HOGCV.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.03)

    person = 1
    for x, y, w, h in bounding_box_cordinates:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f'person {person}', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        person += 1

    # cv2.putText(frame, 'Status : Detecting ', (40, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 0, 0), 2)
    cv2.putText(frame, f'Total Persons : {person - 1}', (40, 70), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 0, 0), 2)
    # cv2.imshow('output', frame)
    print(f'Total Persons : {person - 1}')

    return frame


def openCVProcessing(saved_video_file):
    '''View saved video with openCV
    Add your other steps here'''
    capture = cv2.VideoCapture(saved_video_file)

    while capture.isOpened():
        grabbed, frame = capture.read()  # read in single frame
        if grabbed == False:
            break

        # openCV processing goes here
        #
        cv2.imshow('frame', frame)  # Show the frame
        frame1 = detect(frame)
        frameId = int(round(capture.get(1)))
        if frameId % 10 == 0:
            cv2.imshow('frame', frame1)  # Show the frame

        # Shown in a new window, To exit, push q on the keyboard
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()  # close the windows automatically
    #os.remove(saved_video_file)


tempFile = "temp.ts"  # files are format ts, open cv can view them
videoURL = "https://www.youtube.com/watch?v=Wi26Wkk6_S0"
HOGCV = cv2.HOGDescriptor()
HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
dl_stream(videoURL, tempFile, 3)
openCVProcessing(tempFile)
