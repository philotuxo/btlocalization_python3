from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import Qt
import pyqtgraph
import sys, os, time
sys.path.append("..")
from lib.btRadioMap_multi_ui import Ui_btRadioMap
from lib.btImageScene import *
from lib.histograms import *
from lib.parsers import *
from lib.paths import *
from lib.btCommon import *

DATA_TO_HSV_RSSI = (-90, -40)
DATA_TO_HSV_FREQ = (0, 10)

class btRadioMapImageScene(btImageScene):
    def __init__(self, btRadioMapGui):
        btImageScene.__init__(self, btRadioMapGui)
        self.circleRadius = 3
        self.latestPoint = [ None, None ]
        self.latestPointVisual = None
        self.parent = btRadioMapGui
        self.pointColor = QtGui.QColor(100,100,0, 30)
        self.lineColor = QtGui.QColor(255,0,0,30)
        self.latestColor = QtGui.QColor(150,150,150,200)
        self.coeffs = DATA_TO_HSV_RSSI

    def addDeviceVisuals(self):
        for dongle in self.parent.dongles:
            if self.parent.dongles[dongle][0]:
                if self.parent.dongles[dongle][1]:
                    item = self.addPoint(
                        real2pix(self.parent.params,
                                 self.parent.dongles[dongle][0]),
                        color=self.parent.dongles[dongle][1],
                        penColor = QtGui.QColor(0, 0, 100),
                        penWeight = 2,
                        radius = 5,
                        eventTrigger= True
                    )
                else:
                    item = self.addPoint(
                        real2pix(self.parent.params,
                                 self.parent.dongles[dongle][0]),
                        penColor = QtGui.QColor(0,0,0),
                        penWeight = 2,
                        radius = 5,
                        eventTrigger=True
                    )
                item.setData(QtCore.Qt.UserRole, dongle)
                self.dongleVisuals.append(item)

    def addFingerprintVisuals(self):
        for each in self.parent.listPointItems:
            point = each.data(QtCore.Qt.UserRole, QtCore.Qt.UserRole)
            coord = real2pix(self.parent.params, point)

            item = self.addRect(
                Qt.QRectF(coord.x() - self.parent.sizeGridPx / 2,
                          coord.y() - self.parent.sizeGridPx / 2,
                          self.parent.sizeGridPx,
                          self.parent.sizeGridPx)
            )
            item.setData(QtCore.Qt.UserRole, point)
            color = QtGui.QColor()
            color.setAlpha(50)
            item.setPen(QtGui.QPen(color))
            # item.setData(QtCore.Qt.UserRole, each.data(QtCore.Qt.UserRole))
            self.fingerprintVisuals.append(item)

    def pointOverride(self, point, text = "", color = 0, data = None):
        counter = 0
        for visual in self.fingerprintVisuals:
            if not data is None:
                if not self.parent.selectedBeacon is None:
                    rssi = self.parent.data_grid[visual.data(
                        QtCore.Qt.UserRole)][data][
                        self.parent.selectedBeacon][0]
                    scale = 255/(self.coeffs[1] - self.coeffs[0])

                    colorRssi = int((rssi - self.coeffs[0])* scale)


                    color = QtGui.QColor()
                    color.setHsv(255,
                                 0,
                                 255 - colorRssi,
                                 alpha = 240)
                    visual.setBrush(QtGui.QBrush(color))
                    visual.setPen(QtGui.QPen(color))
                else:
                    if counter == 0:
                        self.parent.log("Select a beacon first.", -1)
                        counter += 1

        for visual in self.dongleVisuals:
            visual.changeSize(5)

    def updateImage(self, imageFile, imageTrigger = False):
        btImageScene.updateImage(self, imageFile, imageTrigger = False)

class btRadioMapGui(QtWidgets.QMainWindow):
    def __init__(self,configFile):
        self.qt_app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QWidget.__init__(self, None)

        # create the main ui
        self.ui = Ui_btRadioMap()
        self.ui.setupUi(self)
        self.imageScene = btRadioMapImageScene(self)
        self.pixMap = None
        self.desiredWidth = 640

        self.grids = False

        # parameters
        self.params = {}
        self.params["parity"] = None
        self.params["origin"] = None
        self.params["direction"] = None
        self.params["limits"] = None
        self.params["points"] = [ None, None ]

        # ui extras
        self.ui.dataTreeWidget.header().resizeSection(0, 175)

        # data retreiving
        self.data_grid = {}
        self.beacons = {}
        self.dongles = {}
        self.listPointItems = []
        self.listSelectedItems = []

        ## data signals
        self.ui.actionRead_GRD_File.triggered.connect(self.readGrdPressed)

        # images manipulation
        self.ui.actionLoadImage.triggered.connect(self.loadImagePressed)
        self.ui.actionRefresh.triggered.connect(self.refreshImage)
        self.imageFile = None

        # image save
        self.ui.actionSave.triggered.connect(self.saveImagePressed)

        # read extras
        self.ui.actionLoadParameters.triggered.connect(self.loadParametersPressed)
        self.ui.actionLoadDevices.triggered.connect(self.loadDevicesPressed)

        # data triggers
        self.ui.comboBoxBeacon.currentIndexChanged.connect(
            self.beaconSelectionPressed)

        self.ui.buttonRefresh.pressed.connect(self.refreshLists)

        # rssi vs freq change
        self.ui.freqBox.clicked.connect(self.coeffsChanged)

        # plot selectors
        self.plotSelection = []
        for i in range(4):
            self.plotSelection.append([None, None])

        if configFile:
            self.readConfigFile(configFile)

        if len(self.beacons) > 0:
            self.prepareBeacons()

    def readConfigFile(self, configFile):
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
            if "grd" in config.keys():
                self.readGrdPressed(config["grd"])
            self.log("Config file loaded: " + configFile, 1)

    def log(self, logThis, type = 0):
        if type == -1:
            self.ui.logBrowser.append("<font ""color=red>%s</font>" % (logThis))
            return
        if type == 1:
            self.ui.logBrowser.append("<font ""color=green>%s</font>" % (
                logThis))
            return
        self.ui.logBrowser.append(logThis)

    def run(self):
        self.show()
        sys.exit(self.qt_app.exec_())

    def resetImagePressed(self):
        self.imageFile = None
        self.updateImage()
        self.ui.noImageLabel.setVisible(True)

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

    def coeffsChanged(self):
        if self.ui.freqBox.isChecked():
            self.imageScene.coeffs = DATA_TO_HSV_FREQ
        else:
            self.imageScene.coeffs = DATA_TO_HSV_RSSI

    def saveImagePressed(self):
        self.imageScene.setSceneRect(self.imageScene.itemsBoundingRect())
        img = Qt.QImage(self.imageScene.sceneRect().size().toSize(),
                        Qt.QImage.Format_ARGB32)
        img.fill(QtCore.Qt.transparent)
        ptr = Qt.QPainter(img)
        self.imageScene.render(ptr)
        img.save("image.png")
        ptr.end()

    def updateImage(self):
        self.imageScene.updateImage(self.imageFile)
        self.ui.imageView.setScene(self.imageScene)
        if self.imageFile:
            self.ui.noImageLabel.setVisible(False)

    def prepareBeacons(self):
        self.ui.comboBoxBeacon.addItem('Select a beacon',None)
        for beacon in self.beacons.keys():
            self.ui.comboBoxBeacon.addItem(beacon, beacon)

    def beaconSelectionPressed(self):
        self.selectedBeacon = self.ui.comboBoxBeacon.currentData()

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
            self.refreshLists()
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
            self.refreshLists()

    def readGrdPressed(self, grdFiles = None):
        if not self.params["limits"]:
            self.log("Please read parameters first!", -1)
            return
        if not grdFiles:
            grdFiles, dummy = QtWidgets.QFileDialog.getOpenFileNames(self,
                                                        'Open file',
                                                        pathData,
                                                        'Grid Data ('
                                                        '*.grd)')

        if grdFiles:
            print("Preparing grids.")
            self.grids = True
            for grdFile in grdFiles:
                # try:
                    self.data_grid, self.gridParams = \
                        parse_grids_multi(grdFile, self.data_grid)
                    sizeGrid = self.gridParams['size_grid']
                    self.sizeGridPx = int(sizeGrid / self.params["parity"])

                    self.log("File loaded: %s." % (grdFile))
                # except AttributeError and IndexError:
                #     self.log("Invalid grd file.", -1)
                # finally:
                    print("Grids imported from %s." % grdFile)
                    self.refreshLists()
                    self.updateImage()

    def refreshLists(self):
        self.ui.dataTreeWidget.clear()
        self.listPointItems.clear()
        for point in self.data_grid.keys():
            treeItem1 = QtWidgets.QTreeWidgetItem(0)
            treeItem1.setText(0,str(point))
            treeItem1.name = point
            # treeItem1.setFlags(treeItem1.flags() & ~1)
            if self.params["origin"] \
                    and self.params["parity"]:
                treeItem1.setData(QtCore.Qt.UserRole,QtCore.Qt.UserRole,
                                  point)
                self.listPointItems.append(treeItem1)

            for dongle in self.data_grid[point].keys():
                treeItem2 = QtWidgets.QTreeWidgetItem(0)
                treeItem2.setText(0, dongle)
                treeItem2.name = dongle
                if self.dongles and self.dongles[dongle][1]:
                    treeItem2.setForeground(0, QtGui.QBrush(QtGui.QColor(
                        self.dongles[dongle][1])))
                # treeItem2.setFlags(treeItem2.flags() & ~1)
                for beacon in self.data_grid[point][dongle].keys():
                    treeItem3 = QtWidgets.QTreeWidgetItem(0)
                    treeItem3.setText(0, beacon)
                    treeItem3.name = beacon
                    if self.beacons and self.beacons[beacon][1]:
                        treeItem3.setForeground(0, QtGui.QBrush(QtGui.QColor(
                            self.beacons[beacon][1])))
                    treeItem2.addChild(treeItem3)
                treeItem1.addChild(treeItem2)
            self.ui.dataTreeWidget.addTopLevelItem(treeItem1)
        self.listSelectedItems.clear()


def main():

    if len(sys.argv) > 1:
        configFile = sys.argv[1]
    else:
        configFile = None

    app = btRadioMapGui(configFile)
    app.run()

if __name__ == '__main__':
    main()
