import sys
import time
import os
sys.path.append("..")
from lib.arCommon import *

error_num = 0

if len(sys.argv) < 2:
    print("Video file not given!")
    sys.exit(-1)

scale_percent = .4  # percent of original size

videoFile = sys.argv[1]
fullPath = os.path.realpath(videoFile)

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_100)
board = cv2.aruco.CharucoBoard_create(charucoWidth,
                                      charucoHeight,
                                      charucoSquareSize,
                                      charucoMarkerSize,
                                      dictionary)

cap = cv2.VideoCapture(fullPath)

allCorners = []
allIds = []
pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)

while cap.isOpened():
    ret,img = cap.read()
    if ret:
        error_num = 0
        width = int(img.shape[1] * scale_percent)
        height = int(img.shape[0] * scale_percent)
        dim = (width, height)

        pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        markerCorners, markerIds, rejectedMarkers = \
            cv2.aruco.detectMarkers(gray,dictionary)

        cv2.aruco.drawDetectedMarkers(gray, markerCorners)

        resized = cv2.resize(gray, dim, interpolation = cv2.INTER_AREA)

        cv2.putText(resized, 'Total = ' + str(len(allCorners)),
                    (20,30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255,255,255),
                    2)

        cv2.putText(resized, 'Detected = ' + str(len(markerCorners)),
                    (20, 55),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2)

        cv2.imshow('frame',resized)
        if pos_frame == 1:
            cv2.moveWindow('frame',0,0)

        key = cv2.waitKey()

        if key == 13: # Enter pressed
            retVal, corners, ids = cv2.aruco.interpolateCornersCharuco(
                markerCorners, markerIds, gray, board)
            allCorners.append(corners)
            allIds.append(ids)
            # time.sleep(.001)

        if key == 82: # up pressed
            for i in range(20):
                ret, img = cap.read()

        if key & 0xFF == ord('q'):
            print("Quitting.")
            break
    else:
        pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
        print(str(pos_frame) + " not ready")
        error_num +=1
        if error_num > 50:
            break

cap.release()
cv2.destroyAllWindows()

imsize = gray.shape

#Calibration fails for lots of reasons. Release the video if we do
try:
    cal = cv2.aruco.calibrateCameraCharuco(
        allCorners,allIds,board,imsize,None,None)
    print("cameraZart = ", repr(cal[0]))
    print("cameraMatrix = ", repr(cal[1]))
    print("distCoeffs = ", repr(cal[2]))

    # np.save("logitech_calibration.npz", cal)

except:
    print("Not done.")
    cap.release()

