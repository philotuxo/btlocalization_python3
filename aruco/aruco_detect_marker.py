import cv2
import numpy as np
import time
import sys
sys.path.append("..")
from lib.arCommon import *



dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)

#Start capturing images for calibration
# cap = cv2.VideoCapture(2)
cap = cv2.VideoCapture(0)
cap.set(3,800)
cap.set(4,600)

# time.sleep(2)

# cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, 0)
# cap.set(cv2.CAP_PROP_WHITE_BALANCE_RED_V, 0)
# for i in range(20):
#     print(cap.get(i))

# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)

# cap.open("data/video_test_800x600_m0.298.mkv")
# cap.open("data/video_test_netlab_800x600_m0.298.mkv")

old_usec = time.time()
frameCount = 1
paused = False

while True:
    if not paused:
        ret,frame = cap.read()
        if not ret:
            break
        new_usec = time.time()
        fps = 1.0 / (new_usec - old_usec)
        old_usec = new_usec


        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        markerCorners, markerIds, rejectedCorners = \
            cv2.aruco.detectMarkers(gray, dictionary)
        cv2.aruco.drawDetectedMarkers(frame, markerCorners, ids=markerIds,
                                      borderColor=(255,255,255))
        # os.system("v4l2-ctl -d /dev/video1 -l | grep -i white")
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
                rvec, tvec, a = cv2.aruco.estimatePoseSingleMarkers(
                    corners, markerSize, cameraMatrix, distCoeffs)


                cv2.aruco.drawAxis(frame,cameraMatrix, distCoeffs, rvec,
                                   tvec, markerSize/2)
                dst, jacob = cv2.Rodrigues(rvec)
            # print(locations)
            #     print(id, np.round(tvec,2), dst )
            print(id)

        cv2.imshow('frame',frame)
    a = cv2.waitKey(1)
    if a == ord('q'):
        break
    if a == ord('p'):
        if paused == False:
            paused = True
        else:
            paused = False
    # time.sleep(30)

#Calibration fails for lots of reasons. Release the video if we do
cap.release()
cv2.destroyAllWindows()
