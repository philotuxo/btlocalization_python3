import sys
import time
import os
sys.path.append("..")
from lib.arCommon import *

if len(sys.argv) < 2:
    print("Video file not given!")
    sys.exit(-1)

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
decimator = 0
pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)

while cap.isOpened():
    ret,img = cap.read()
    if ret:
        pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        markerCorners, markerIds, rejectedMarkers = \
            cv2.aruco.detectMarkers(gray,dictionary)

        cv2.aruco.drawDetectedMarkers(gray, markerCorners)

        cv2.imshow('frame',gray)

        if len(markerCorners) > 0:
            retVal, corners, ids = cv2.aruco.interpolateCornersCharuco(
                markerCorners, markerIds, gray, board)
            if corners is not None and ids is not None and len(
                    corners) > 10 and decimator % 2 == 0:
                print(str(pos_frame), len(corners))
                allCorners.append(corners)
                allIds.append(ids)
            # time.sleep(.001)
        decimator+=1
    else:
        pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
        print(str(pos_frame) + " not ready")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Quitting.")
        break

cap.release()
cv2.destroyAllWindows()

imsize = gray.shape

#Calibration fails for lots of reasons. Release the video if we do
try:
    cal = cv2.aruco.calibrateCameraCharuco(allCorners,allIds,board,imsize,
                                           None,None)
    print("cameraZart =", cal[0])
    print("cameraMatrix =np.", cal[1])
    print("distCoeffs =np.", cal[2])

    # np.save("logitech_calibration.npz", cal)

except:
    print("Not done.")
    cap.release()

