import sys
sys.path.append("..")
from aruco.arCommon import *
import time
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread

def rot2d(theta):
    return np.matrix([[np.cos(theta),  -np.sin(theta)],
                      [np.sin(theta), np.cos(theta)]])

def axisBasedRemoval(distances):
    return np.argsort(distances).tolist()[:2]

def naiveOutlierRemoval(coordlist):
    # get the cluster center
    m = np.mean(coordlist, 0)

    dist = []

    # find the residuals
    for pts in coordlist:
        dist.append(np.linalg.norm(m - pts))

    # return indices
    return np.argsort(dist)[:2]

class DetectThread(QThread):

    def __init__(self, name, inQueue, outQueue, markers, video):
        QThread.__init__(self)
        self.name = name
        self.outQueue = outQueue
        self.inQueue = inQueue
        self.markers = markers
        self.sendImg = True
        self.video = video

    def run(self):
        # time.sleep(5)
        # cv2.namedWindow(self.windowName)

        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)

        # Start capturing images for calibration
        cap = cv2.VideoCapture()
        cap.set(3, 800)
        cap.set(4, 600)

        # v4l2-ctl --device=/dev/video0 -c exposure_absolute=300

        # cap.open("data/video_test_netlab_800x600_m0.298.mkv")
        # bunun dışarıdan verilmesi gerekiyor
        # cap.open("/home/serhan/my_video-6.mkv")
        cap.open(self.video)
        time.sleep(.05)

        errPosQ = 0.05
        errOriQ = np.pi/72
        errPosR = 20
        errOriR = np.pi

        # kalman filter parameters
        A = np.matrix(np.diag([1,1,1,1,1,1])) # dimensions are independent
        H = np.matrix(np.diag([1,1,1,1,1,1])) # observation dimensions are
        # independent
        P = np.matrix(np.ones(shape=[6,6])) # error covariance initial value

        # transition error (process noise covariance)
        Q = np.matrix(np.diag([errPosQ,
                               errPosQ,
                               errPosQ,
                               errOriQ,
                               errOriQ,
                               errOriQ]))
        # observation error (sensor noise covariance)
        R = np.matrix(np.diag([errPosR,
                               errPosR,
                               errPosR,
                               errOriR,
                               errOriR,
                               errOriR]))

        X = None
        arrowEnd = None
        # if first run
        first = True
        paused = False
        kalman = True

        self.outQueue.put(['I', 'S'])
        while True:
            if self.inQueue.qsize() > 0:
                # flush inQueue
                msg = self.inQueue.get()
                if msg == 'S':
                    break
                if msg == 'P':
                    if paused:
                        paused = False
                    else:
                        paused = True
                if msg == 'T':
                    self.sendImg = True
                if msg == 'F':
                    self.sendImg = False
                if msg == 'K':
                    kalman = True
                if msg == 'M':
                    kalman = False
            if paused:
                time.sleep(0.05)
                continue
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            markerCorners, markerIds, rejectedCorners = \
                cv2.aruco.detectMarkers(gray, dictionary)
            cv2.aruco.drawDetectedMarkers(frame, markerCorners, ids=markerIds,
                                          borderColor=(255, 255, 255))
            # os.system("v4l2-ctl -d /dev/video1 -l | grep -i white")

            if len(markerCorners) > 0:
                if not (markerCorners is not None and markerIds is not None):
                    continue

                listPos = []
                listOri = []
                listArr = []
                listWeights = []
                listIds = []

                for index in range(len(markerCorners)):
                    # check if marker ID is defined in the configuration
                    if not index in self.markers.keys():
                        continue
                    id = markerIds[index][0]
                    corners = markerCorners[index]
                    rvec, tvec = cv2.aruco.estimatePoseSingleMarkers(
                        corners, markerSize, cameraMatrix, distCoeffs)

                    posCamera2Marker = np.matrix(tvec[0][0])

                    # rotation for camera coords w.r.t. marker frame
                    rotCamera2Marker, Jacob = cv2.Rodrigues(
                        np.matrix(rvec[0][0]))

                    # rotate w.r.t. world coords
                    rotWorld2Marker = invRotMat(self.markers[id][1])

                    # final rotation matrix
                    rotWorld2Camera = rotCamera2Marker * rotWorld2Marker

                    # - for translating origin of the camera to the origin of
                    #  the marker
                    posMarker2Camera = -posCamera2Marker * rotWorld2Camera

                    # translate to world coords
                    posWorld2Camera = self.markers[id][0] + posMarker2Camera

                    # orientation line end coordinates
                    arrowEnd = (
                        -np.matrix(tvec[0][0]) - np.matrix([0,0,-.5]))\
                               * rotWorld2Camera + self.markers[id][0]

                    listPos.append(posWorld2Camera.tolist()[0])
                    listArr.append(arrowEnd.tolist()[0])

                    # get absolute of x
                    listWeights.append(abs(posCamera2Marker[0,0]))
                    # print(listWeights)

                    listIds.append(id)

                    # get rotation matrix
                    ori3D, jacob = cv2.Rodrigues(rotWorld2Camera)
                    listOri.append(np.transpose(ori3D).tolist()[0])

                    if self.sendImg:
                        cv2.aruco.drawAxis(frame,
                                       cameraMatrix,
                                       distCoeffs,
                                       rvec,
                                       tvec,
                                       markerSize/2)

                if kalman:
                    if len(listPos) >= 2:
                        # indices = naiveOutlierRemoval(listCoords)
                        indices = axisBasedRemoval(listWeights)
                        selectedPos = [listPos[i] for i in indices]
                        selectedOri = [listOri[i] for i in indices]
                        meanPos = np.mean(selectedPos, 0)
                        meanOri = np.mean(selectedOri, 0)
                    else:
                        meanPos = listPos[0]
                        meanOri = listOri[0]

                    Z = np.matrix(np.append(meanPos, meanOri)).transpose()

                    if first:
                        # initialization
                        X = np.copy(Z)
                    else:
                        # kalman filtering
                        # prediction
                        Xpre = A*X
                        # print(Xpre)
                        Ppre = A*P*np.transpose(A) + Q

                        # update
                        K = Ppre * H * np.linalg.inv(H* Ppre* np.transpose(H) + R)
                        # gain
                        X = Xpre + K * (Z - H*X )
                        P = (np.identity(6) - K * H) * Ppre

                        # calculate the arrow end ????
                        rotEstimation, jacob = cv2.Rodrigues(X[3:])

                        arrowEnd = X[0:3].transpose() + np.matrix([0, 0, .5])\
                                                   * rotEstimation

                    if not first:
                        self.outQueue.put([ 'K', [
                                         np.round(X.transpose(),2).tolist()[0],
                                         np.round(arrowEnd,2).tolist()[0] ]])
                    first = False
                else:
                    # Not kalman
                    self.outQueue.put([ 'M', [listIds,
                                              listPos,
                                              listArr,
                                              listOri]])


            if self.sendImg:
                frame = cv2.resize(frame, (400,300))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, bytesPerLine = frame.data.shape
                cameraMap = QPixmap(
                    QImage(frame.data, width, height, bytesPerLine * width,
                                 QImage.Format_RGB888))
                # self.scene.addPixmap(cameraMap)

                self.outQueue.put([ 'F', cameraMap])

        self.outQueue.put(['I', 'E'])
        cap.release()
