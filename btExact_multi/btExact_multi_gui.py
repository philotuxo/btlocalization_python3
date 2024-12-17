import sys, os, time, re
sys.path.append("..")
from btHmmShow_ui import Ui_btHmmShow
from lib.btImageScene import *
from lib.parsers import *
from lib.paths import *
import queue

HmmQueue = queue.Queue()
SEC_SLEEP = 0.0001
groundColor = QtGui.QColor(0,200,0)
meanColor = QtGui.QColor(180,0,0)

class btEllipseItem(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, point, radius = 2, color = None):
        super(btEllipseItem, self).__init__(
            point.x()-radius,
            point.y()-radius,
            2 * radius,
            2 * radius
        )
        self.x = point.x()
        self.y = point.y()
        self.radius = radius

        if not color == None:
            # color = QtGui.QColor(color)
            pn = QtGui.QPen()
            pn.setColor(color)

            br = QtGui.QBrush()
            br.setStyle(1) # RadialGradient pattern
            br.setColor(color)
            # brText = QtGui.QBrush()
            # brText.setStyle(1) # RadialGradient pattern
            # brText.setColor(QtGui.QColor(96,96,96))
            self.setBrush(br)
            self.setPen(pn)

    def changeAlpha(self, alpha):
        br = self.brush()
        pn = self.pen()
        color = br.color()
        color.setAlpha(alpha)
        br.setColor(color)
        pn.setColor(color)
        self.setBrush(br)
        self.setPen(pn)


    def changePos(self, point):
        self.x = point.x() - self.radius
        self.y = point.y() - self.radius
        self.w = 2 * self.radius
        self.h = 2 * self.radius
        self.setRect(self.x,
                     self.y,
                     self.w,
                     self.h)

    def changeSize(self, newRadius):
        self.w = newRadius * 2
        self.h = newRadius * 2
        self.x = self.x + int(self.w / 2) - newRadius
        self.y = self.y + int(self.h / 2) - newRadius
        self.setRect(self.x,
                     self.y,
                     self.w,
                     self.h)


class btHmmImageScene(btImageScene):
    def __init__(self, btParticleGui):
        btImageScene.__init__(self, btParticleGui)
        self.circleRadius = 2
        self.latestPoint = [ None, None ]
        self.latestPointVisual = None
        self.pairs = []
        self.pairVisuals = []
        self.parent = btParticleGui
        self.pairColor1 = QtGui.QColor(0,255,255,100)
        self.pairColor2 = QtGui.QColor(255,0,255,100)
        self.pointColor = QtGui.QColor(100,100,0, 30)
        self.lineColor = QtGui.QColor(255,0,0,30)
        self.latestColor = QtGui.QColor(150,150,150,200)

    def putTempCircle(self):
        # tempCircle to delete when needed
        self.tempCircle = self.addPoint(self.latestPoint,"",color =
        QtGui.QColor(255,0,0))

    def pointOverride(self, point, text="", color=0, data=None):
        pass

    def updateImage(self, imageFile):
        btImageScene.updateImage(self, imageFile)

class btHmm_viewer(QtWidgets.QMainWindow):
    def __init__(self, name, configFile, hmmQueue = None, logQueue = None):
        self.qt_app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QWidget.__init__(self, None)

        # create the main ui
        self.ui = Ui_btHmmShow()
        self.ui.setupUi(self)
        self.imageScene = btHmmImageScene(self)
        self.pixMap = None
        self.desiredWidth = 640

        self.lQueue = logQueue
        self.hmmQueue = hmmQueue
        self.shower_running = False

        # placeholders
        self.name = name
        self.data = {}
        self.beacons = {}
        self.dongles = {}

        self.params = {}
        self.params["parity"] = None
        self.params["origin"] = None
        self.params["direction"] = None
        self.params["limits"] = None
        self.params["points"] = [ None, None ]

        self.particle_visuals = []
        self.particles = None
        self.weights = None
        self.mean = None
        self.ground_visuals = []
        self.mean_visuals = []
        self.visuals_size = 5000
        self.ground = None
        self.discarded = 0

        if configFile:
            self.readConfigFile(configFile)

        self.timer = Qt.QTimer()
        self.timer.timeout.connect(self.timerTrigger)
        self.timer.start(100)

    def log(self, logThis):
        msg = self.name + ": " + str(logThis)
        if not self.lQueue == None:
            self.lQueue.put(msg)
        else:
            print(msg)

    def timerTrigger(self):
        # avoid running multiple instances simultaneously
        if self.shower_running:
            return
        # self.log("Discarded particle sets = " + str(self.discarded))
        self.shower_running = True

        if self.hmmQueue.qsize() > 0:
            data = self.hmmQueue.get()

            if data[0] == 'Q':
                pass
                # sys.exit(self.qt_app.exec_())

            if data[0] == 'P':
                self.particles = data[1]
                self.weights = data[2]
                self.ground = (data[3][0], data[3][1])
                self.mean = data[4][0], data[4][1]
                self.info = data[5]

                self.log("Prepared Particles")
            if data[0] == 'P':
                # (x, y, w)
                # ground visualization
                ground_point = real2pix(self.params, self.ground)

                while len(self.ground_visuals) >= self.visuals_size:
                    item = self.ground_visuals.pop(0)
                    self.imageScene.removeItem(item)
                if len(self.ground_visuals) > 0:
                    self.ground_visuals[-1].changeSize(2)
                    self.ground_visuals[-1].changeAlpha(200)
                item = btEllipseItem(ground_point ,color=groundColor,
                                     radius=4)
                self.imageScene.addItem(item)
                self.ground_visuals.append(item)

                # mean point visualization
                mean_point = real2pix(self.params, self.mean)
                while len(self.mean_visuals) >= self.visuals_size:
                    item = self.mean_visuals.pop(0)
                    self.imageScene.removeItem(item)
                if len(self.mean_visuals) > 0:
                    self.mean_visuals[-1].changeSize(2)
                    self.mean_visuals[-1].changeAlpha(200)
                item = btEllipseItem(mean_point ,color=meanColor,
                                     radius=4)
                self.imageScene.addItem(item)
                self.mean_visuals.append(item)

                # put info
                self.ui.info.setText(self.info)

                # put particles
                counter = 0
                for particle in self.particles:
                    point = real2pix(self.params, particle[0:2])
                    alpha = min(self.weights[counter] * 3000,255)

                    self.particle_visuals[counter].changeAlpha(alpha)
                    self.particle_visuals[counter].changePos(point)

                    counter +=1

        # flush area
        # discard the rest of the queue
        while self.hmmQueue.qsize() > 0:
            discard = self.hmmQueue.get()
            self.discarded += 1

        self.shower_running = False

    def readConfigFile(self, configFile):
        # try:
            with open(configFile, 'r') as f:
                config = json.load(f)
                if "map" in config.keys():
                    self.loadImagePressed(os.path.join(pathMap, config["map"]))
                if "par" in config.keys():
                    self.loadParametersPressed(
                        os.path.join(pathConf, config["par"]))
                if "dev" in config.keys():
                    self.loadDevicesPressed(
                        os.path.join(pathConf, config["dev"]))
                self.log("Config file loaded: " + configFile)
        # except:
        #     self.log("Problem with the config file: " + configFile)

    def resetImagePressed(self):
        self.imageFile = None
        self.updateImage()

    def refreshImage(self):
        self.imageScene.updateImage(self.imageFile)

    def loadImagePressed(self, imageFile = None):
        if not imageFile:
            imageFile, dummy = QtWidgets.QFileDialog.getOpenFileName(self,
                                                      'Open file',
                                                      pathMap,
                                                      'Images (*.png *.xpm '
                                                      '*.jpg)' )
        if not imageFile:
            return
        self.imageFile = imageFile
        self.updateImage()

    def updateImage(self):
        self.imageScene.updateImage(self.imageFile)
        self.ui.imageView.setScene(self.imageScene)

    def loadImageButtonPressed(self, imageFile = None):
        imageFile, stuff = QtWidgets.QFileDialog.getOpenFileName(self,
                                              'Open file',
                                              pathMap,
                                              'Images (*.png *.xpm '
                                              '*.jpg)')
        if imageFile:
            with open(imageFile, 'r') as f:
                # try:
                    self.imageFile = imageFile
                    self.updateImage()
                    self.log("Image loaded: %s." % (imageFile))
                    f.close()

    def loadParametersPressed(self, parFile = None):
        if not parFile:
            parFile, dummy = QtWidgets.QFileDialog.getOpenFileName(self,
                                                  'Open file',
                                                  pathConf,
                                                  'Parameters (*.par)')

        if not parFile:
            return
        try:
            self.params = parseParameters(parFile, self.params)
            self.log("Parameters loaded: " + parFile)
        except:
            self.log("Incompatible File: " + parFile)
        finally:
            self.updateImage()

    def loadDevicesPressed(self, devFile = None):
        if not devFile:
            devFile, dummy = QtWidgets.QFileDialog.getOpenFileName(self,
                                                  'Open file',
                                                  pathConf,
                                                  'Devices (*.dev)')

        if not devFile:
            return
        try:
            self.beacons, self.dongles = parseDevices(devFile)
            self.log("Devices loaded: " + devFile)
        except:
            self.log("Incompatible File: " + devFile)
        finally:
            self.updateImage()

    def run(self):
        self.show()
        # print("hello")
        sys.exit(self.qt_app.exec_())

def main():
    if len(sys.argv) > 1:
        config_gui = sys.argv[1]
    else:
        config_gui = None
        print("HMM Filter: Not enough parameters.")

    hmm_queue = queue.Queue()
    app = btHmm_viewer("Particle_Viewer_Widget",
                            config_gui,
                            hmm_queue)
    app.run()

if __name__ == '__main__':
    main()
