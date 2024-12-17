import sys
import time
sys.path.append("..")
from lib.arCommon import *

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_100)
board = cv2.aruco.CharucoBoard_create(charucoWidth,
                                      charucoHeight,
                                      charucoSquareSize,
                                      charucoMarkerSize,
                                      dictionary)

cap = cv2.VideoCapture(1)
cap.set(3,640)
cap.set(4,480)

allCorners = []
allIds = []
decimator = 0
while True:
    ret,img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    markerCorners, markerIds, rejectedMarkers = \
        cv2.aruco.detectMarkers(gray,dictionary)

    cv2.aruco.drawDetectedMarkers(gray, markerCorners)

    cv2.imshow('frame',gray)

    k = cv2.waitKey(1)
    if len(markerCorners) > 0:
        print("Capturing.")
        retVal, corners, ids = cv2.aruco.interpolateCornersCharuco(
            markerCorners, markerIds, gray, board)
        if corners is not None and ids is not None and len(
                corners) > 3 and decimator % 3 == 0:
            allCorners.append(corners)
            allIds.append(ids)
        time.sleep(.5)
    decimator+=1

    if k == ord('q'):
        print("Quitting.")
        break


imsize = gray.shape

#Calibration fails for lots of reasons. Release the video if we do
try:
    cal = cv2.aruco.calibrateCameraCharuco(allCorners,allIds,board,imsize,
                                           None,None)
    print(cal)
    # np.save("logitech_calibration.npz", cal)

except:
    print("Not done.")
    cap.release()

cap.release()
cv2.destroyAllWindows()
