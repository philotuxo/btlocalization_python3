import json
import time
import cv2
import cv2.aruco as A
import numpy as np
import sys

id = int(sys.argv[1])

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
img = cv2.aruco.drawMarker(dictionary, id, 200)
# cv2.imshow("frame", img)
cv2.imwrite("marker-%s.png" % (id), img)
# cv2.waitKey()

#Start capturing images for calibration
