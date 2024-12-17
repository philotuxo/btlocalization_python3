import cv2
import sys, os
sys.path.append("..")
from lib.arCommon import *

dictionary = cv2.aruco.getPredefinedDictionary(arucoDict)
board = cv2.aruco.CharucoBoard_create(charucoWidth,
                                      charucoHeight,
                                      charucoSquareSize,
                                      charucoMarkerSize,
                                      dictionary)
img = board.draw((500,700))

#Dump the calibration board to a file
cv2.imwrite('charuco.png',img)
