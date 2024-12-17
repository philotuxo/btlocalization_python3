import cv2
import numpy as np
import time
import sys
import os
sys.path.append("..")
from lib.arCommon import *

cameraMatrix = np.array(camParameters["GoPro Linear"][0])
distCoeffs = np.array(camParameters["GoPro Linear"][1])

if len(sys.argv) < 2:
    print("Video file not given!")
    sys.exit(-1)

videoFile = sys.argv[1]
fullPath = os.path.realpath(videoFile)

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)

#Start capturing images for calibration
cap = cv2.VideoCapture()
cap.open(fullPath)

old_usec = time.time()
frameCount = 1
paused = False

while cap.isOpened():
    if not paused:
        ret,frame = cap.read()
        if ret:
            new_usec = time.time()
            fps = 1.0 / (new_usec - old_usec)
            old_usec = new_usec


            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            markerCorners, markerIds, rejectedCorners = \
                cv2.aruco.detectMarkers(gray, dictionary)
            cv2.aruco.drawDetectedMarkers(frame, markerCorners, ids=markerIds,
                                          borderColor=(255,255,255))
            markers = readMarkerConfiguration("data/markerConfiguration.dat")

            if len(markerCorners) > 0:
                if not ( markerCorners is not None and markerIds is not None):
                    continue
                # print(markerCorners)
                # print()
                locations = []
                for index in range(len(markerCorners)):
                    id = markerIds[index][0]
                    corners = markerCorners[index]
                    rvec, tvec, objPoints = cv2.aruco.estimatePoseSingleMarkers(
                        corners, markerSize, cameraMatrix, distCoeffs)


                    cv2.aruco.drawAxis(frame,cameraMatrix, distCoeffs, rvec,
                                       tvec, markerSize/2)
                    dst, jacob = cv2.Rodrigues(rvec)
                # print(locations)
                    print(id, np.round(tvec,2), dst )

            frame_scaled = cv2.resize(frame, (frame.shape[1]//2,frame.shape[
                0]//2))
            cv2.imshow('frame',frame_scaled)
        else:
            pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            # print(str(pos_frame) + " not ready")

    a = cv2.waitKey(1)
    if a == ord('q'):
        break
    if a == ord('p'):
        if paused == False:
            paused = True
        else:
            paused = False
    if a == ord('f'):
        for i in range(30):
            ret, frame = cap.read()

    # time.sleep(30)

#Calibration fails for lots of reasons. Release the video if we do
cap.release()
cv2.destroyAllWindows()
