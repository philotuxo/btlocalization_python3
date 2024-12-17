from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import Qt
import pyqtgraph
import sys, os, time
sys.path.append("..")
from lib.btInterpolate_multi_ui import Ui_btInterpolate
from lib.btImageScene import *
from lib.histograms import *
from lib.parsers import *
from lib.paths import *
from lib.btCommon import *
import pyqtgraph as pg

class btInterpolateImageScene(btImageScene):
    def __init__(self, btInterpolateGui):
        btImageScene.__init__(self, btInterpolateGui)
        self.circleRadius = 3
        self.latestPoint = [ None, None ]
        self.latestPointVisual = None
        self.pairs = []
        self.pairVisuals = []
        self.parent = btInterpolateGui
        self.pairColor1 = QtGui.QColor(0,255,255,100)
        self.pairColor2 = QtGui.QColor(255,0,255,100)
        self.pointColor = QtGui.QColor(100,100,0, 30)
        self.lineColor = QtGui.QColor(255,0,0,30)
        self.latestColor = QtGui.QColor(150,150,150,200)

    def putTempCircle(self):
        # tempCircle to delete when needed
        self.tempCircle = self.addPoint(self.latestPoint,"",color =
        QtGui.QColor(255,0,0))

    def addMouseVisuals(self):
        if self.latestPoint[0]:
            self.latestPointVisual = self.addPoint(
                self.latestPoint[0],"", self.latestColor)

        for pair in self.pairs:
            pairVisual = [ None, None, None]
            pairPix0 = real2pix(self.parent.params, pair[0])
            pairPix1 = real2pix(self.parent.params, pair[1])

            # colorize the selected pair (compared with the first pair)
            if pair[0] == self.pairs[0][0]:
                pairVisual[0] = self.addPoint(
                    pairPix0, "",
                    self.pairColor1)
            elif pair[0] == self.pairs[0][1]:
                pairVisual[0] = self.addPoint(
                    pairPix0, "",
                    self.pairColor2)
            else:
                pairVisual[0] = self.addPoint(
                    pairPix0, "",
                    self.pointColor)

            if pair[1] == self.pairs[0][0]:
                pairVisual[1] = self.addPoint(
                    pairPix0, "",
                    self.pairColor1)

            elif pair[1] == self.pairs[0][1]:
                pairVisual[1] = self.addPoint(
                    pairPix0, "",
                    self.pairColor2)
            else:
                pairVisual[1] = self.addPoint(
                    pairPix0, "",
                    self.pointColor)

            pen = QtGui.QPen(self.lineColor)

            pairVisual[2] = self.addLine(pairPix0.x(), pairPix0.y(),
                                         pairPix1.x(), pairPix1.y(),
                                         pen)

            self.pairVisuals.append(pairVisual)

    def removeMouseVisuals(self):
        if self.latestPointVisual:
            self.removeItem(self.latestPointVisual)
            self.latestPointVisual = None

        for pairVisual in self.pairVisuals:
            self.removeItem(pairVisual[0])
            self.removeItem(pairVisual[1])
            self.removeItem(pairVisual[2])

        self.pairVisuals.clear()

    def updateMouseVisuals(self):
        self.removeMouseVisuals()
        self.addMouseVisuals()

    def addFingerprintVisuals(self):
        pen = Qt.QPen(Qt.QColor(0,0,0,100))
        for each in self.parent.listPointItems:
            coord = each.data(QtCore.Qt.UserRole, QtCore.Qt.UserRole)
            if self.parent.grids:
                item = self.addRect(
                    Qt.QRectF(coord.x() - self.parent.sizeGridPx / 2,
                              coord.y() - self.parent.sizeGridPx / 2,
                              self.parent.sizeGridPx,
                              self.parent.sizeGridPx),
                    pen=pen
                )
            else:

                if each.isSelected():
                    item = self.addPoint(coord,
                                         "",
                                         QtGui.QColor(0,0,0)
                                         ,radius=5
                    )
                else:
                    item = self.addPoint(coord,
                                         "",
                                         QtGui.QColor(200,200,200)
                                         ,radius=5)

            self.fingerprintVisuals.append(item)

    def pointOverride(self, point, text="", color=0, data=None):
        self.latestPoint[0] = point
        self.latestPoint[1] = pix2real(self.parent.params, self.latestPoint[0])

        if self.parent.params["limits"]:
            points, self.pairs = find_best_pair(
                self.latestPoint[1],
                list(self.parent.dataHist.keys()),
                self.parent.ori,
                self.parent.ui.sliderR.value() / 100.0 * round(
                    math.sqrt(
                        (self.parent.params["limits"][1][0]
                         - self.parent.params["limits"][0][0]) ** 2 +
                        (self.parent.params["limits"][1][1]
                         - self.parent.params["limits"][0][1]) ** 2
                    ), 2)
            )

        if len(self.pairs) > 0:
            self.parent.plotHist(self.pairs[0][0], 1)
            self.parent.plotHist(self.pairs[0][1], 2)

        if self.latestPoint[0]:
            if len(self.pairs) > 0:
                t = calculate_t(self.latestPoint[1],
                                self.pairs[0][0],
                                self.pairs[0][1])
                self.parent.plotMidHist(
                    self.pairs[0][0],
                    self.pairs[0][1],
                    t)

        self.updateMouseVisuals()

    def updateImage(self, imageFile):
        self.removeMouseVisuals()
        btImageScene.updateImage(self, imageFile)
        self.addMouseVisuals()

class btInterpolateGui(QtWidgets.QMainWindow):
    def __init__(self,configFile):
        self.qt_app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QWidget.__init__(self, None)

        # create the main ui
        self.ui = Ui_btInterpolate()
        self.ui.setupUi(self)
        self.imageScene = btInterpolateImageScene(self)
        self.pixMap = None
        self.desiredWidth = 640

        self.grids = False

        # parameters
        self.ori = None
        self.params = {}
        self.params["parity"] = None
        self.params["origin"] = None
        self.params["direction"] = None
        self.params["limits"] = None
        self.params["points"] = [ None, None ]

        # ui extras
        self.ui.dataTreeWidget.header().resizeSection(0, 175)

        # data retreiving
        self.dataValue = {}
        self.dataHist = {}
        self.dataTime = {}
        self.dataBins = []
        self.beacons = {}
        self.dongles = {}
        self.rssiRange = np.arange(rssi_start, rssi_end, 1)
        self.listPointItems = []
        self.listSelectedItems = []

        ## data signals
        self.ui.actionRead_HST_File.triggered.connect(self.readHstPressed)
        self.ui.actionRead_GRD_File.triggered.connect(self.readGrdPressed)
        self.ui.actionDelete_Data.triggered.connect(self.deleteDataPressed)

        # images manipulation
        self.ui.actionLoadImage.triggered.connect(self.loadImagePressed)
        self.ui.actionRefresh.triggered.connect(self.refreshImage)
        self.imageFile = None

        # read extras
        self.ui.actionLoadParameters.triggered.connect(self.loadParametersPressed)
        self.ui.actionLoadDevices.triggered.connect(self.loadDevicesPressed)

        # data triggers
        self.ui.dataTreeWidget.itemSelectionChanged.connect(
            self.selectionChanged)

        self.ui.buttonRefresh.pressed.connect(self.refreshLists)

        self.ui.sliderBeta.valueChanged.connect(self.updateSliders)
        self.ui.sliderR.valueChanged.connect(self.updateSliders)
        self.ui.sliderT.valueChanged.connect(self.updateSliders)
        self.ui.sliderTheta.valueChanged.connect(self.updateSliders)
        self.ui.sliderTheta.setDisabled(True)
        self.ui.thetaBox.toggled.connect(self.updateTheta)
        self.ui.sliderR.setValue(50)


        # plot selectors
        self.plotSelection = []
        for i in range(4):
            self.plotSelection.append([None, None])

        self.dongleBoxes = []
        self.dongleBoxes.append(self.ui.dongleBox1)
        self.dongleBoxes.append(self.ui.dongleBox2)
        self.dongleBoxes.append(self.ui.dongleBox3)
        self.dongleBoxes.append(self.ui.dongleBox4)

        self.beaconBoxes = []
        self.beaconBoxes.append(self.ui.beaconBox1)
        self.beaconBoxes.append(self.ui.beaconBox2)
        self.beaconBoxes.append(self.ui.beaconBox3)
        self.beaconBoxes.append(self.ui.beaconBox4)

        # plotting
        self.hl1 = []
        self.hl1.append(self.ui.histView1_1)
        self.hl1.append(self.ui.histView2_1)
        self.hl1.append(self.ui.histView3_1)
        self.hl1.append(self.ui.histView4_1)

        self.hl2 = []
        self.hl2.append(self.ui.histView1_2)
        self.hl2.append(self.ui.histView2_2)
        self.hl2.append(self.ui.histView3_2)
        self.hl2.append(self.ui.histView4_2)

        self.hl0 = []
        self.hl0.append(self.ui.histView1_int)
        self.hl0.append(self.ui.histView2_int)
        self.hl0.append(self.ui.histView3_int)
        self.hl0.append(self.ui.histView4_int)

        if configFile:
            self.readConfigFile(configFile)

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
                if "hst" in config.keys():
                    self.readHstPressed(
                        os.path.join(pathConf, config["hst"])
                    )
                self.log("Config file loaded: " + configFile, 1)
        # except:
        #     self.log("Problem with the config file: " + configFile)

    def deviceChanged(self):
        for i in range(0,4):
            adapter = None
            beacon = None
            if self.dongleBoxes[i].currentIndex() > 0:
                adapter = self.dongleBoxes[i].currentData()
            if self.beaconBoxes[i].currentIndex() > 0:
                beacon = self.beaconBoxes[i].currentData()
            self.plotSelection[i] = [adapter, beacon]

    def setBoxActions(self):
        for index in range(len(self.dongleBoxes)):
            self.dongleBoxes[index].currentIndexChanged.connect(
                self.deviceChanged)
            self.beaconBoxes[index].currentIndexChanged.connect(
                self.deviceChanged)

    def generateBoxes(self):
        if len(self.dongles.keys()) > 0:
            for box in self.dongleBoxes:
                box.clear()
                box.addItem("Select Dongle")
                model = box.model()
                for dongle in self.dongles.keys():
                    item = QtGui.QStandardItem(self.dongles[dongle][2])
                    item.setData(dongle,QtCore.Qt.UserRole)
                    item.setForeground(QtGui.QColor(self.dongles[dongle][1]))
                    model.appendRow(item)

        if len(self.beacons.keys()) > 0:
            for box in self.beaconBoxes:
                box.clear()
                box.addItem("Select Beacon")
                model = box.model()
                for beacon in self.beacons.keys():
                    item = QtGui.QStandardItem(self.beacons[beacon][2])
                    item.setData(beacon,QtCore.Qt.UserRole)
                    item.setForeground(QtGui.QColor(self.beacons[beacon][1]))
                    model.appendRow(item)

        self.setBoxActions()

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

    def updateImage(self):
        self.imageScene.updateImage(self.imageFile)
        self.ui.imageView.setScene(self.imageScene)
        if self.imageFile:
            self.ui.noImageLabel.setVisible(False)


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
            self.generateBoxes()

    def readHstPressed(self, hstFile = None):
        if not hstFile:
            hstFile, dummy = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        'Open file',
                                                        pathData,
                                                        'Histogram Data ('
                                                        '*.hst)')

        if hstFile:
            try:
                self.dataHist, self.dataBins, self.beacons, self.dongles = \
                    parse_hist_multi(hstFile)
                self.log("File loaded: %s." % (hstFile))
            except AttributeError:
                self.log("Invalid hst file.", -1)
            finally:
                self.refreshLists()
                self.updateImage()
                self.generateBoxes()

        if not hstFile:
            self.log("No data loaded.", -1 )

    def readGrdPressed(self, files_grid = None):
        if not self.params["limits"]:
            self.log("Please read parameters first!", -1)
            return

        if not files_grid:
            files_grid, dummy = QtWidgets.QFileDialog.getOpenFileNames(self,
                                                        'Open file',
                                                                       pathData,
                                                        'Grid Data ('
                                                        '*.grd)')
        if files_grid:
            self.data_grid = {}
            self.grids = True
            for file_grid in files_grid:
                try:
                    self.data_grid, self.params_grid = \
                        parse_grids_multi(file_grid, self.data_grid)
                    size_grid = self.params_grid['size_grid']
                    self.sizeGridPx = int(size_grid / self.params[ "parity"])

                    for point in self.data_grid.keys():
                        for dongle in self.data_grid[point].keys():
                            for beacon in self.data_grid[point][dongle].keys():
                                if not point in self.dataHist.keys():
                                    self.dataHist[point] = {}
                                if not dongle in self.dataHist[point].keys():
                                    self.dataHist[point][dongle] = {}
                                if not beacon in self.dataHist[point][dongle].keys():
                                    self.dataHist[point][dongle][beacon] = \
                                        self.data_grid[point][dongle][beacon]

                    self.log("File loaded: %s." % (file_grid))
                except AttributeError and IndexError:
                    self.log("Invalid hst file.", -1)
                finally:
                    self.refreshLists()
                    self.updateImage()
                    self.generateBoxes()


    def deleteDataPressed(self):
        for item in self.listSelectedItems:
            point = item.text(0)
            point = literal_eval(point)
            del self.dataHist[point]
            self.ui.dataTreeWidget.removeItemWidget(item,0)
            # self.ui.dataTreeWidget.takeItem(
            #     self.ui.dataTreeWidget.row(self.listPointItems[point])
            # )
            self.listPointItems.remove(item)
        self.refreshLists()

    def selectionChanged(self):
        self.listSelectedItems.clear()
        for item in self.listPointItems:
            if item.isSelected():
                self.listSelectedItems.append(item)
        self.updateImage()

    def refreshLists(self):
        self.ui.dataTreeWidget.clear()
        self.listPointItems.clear()
        for point in self.dataHist.keys():
            treeItem1 = QtWidgets.QTreeWidgetItem(0)
            treeItem1.setText(0,str(point))
            treeItem1.name = point
            # treeItem1.setFlags(treeItem1.flags() & ~1)
            if self.params["origin"] \
                    and self.params["parity"]:
                pixCoord = real2pix(self.params, point)
                treeItem1.setData(QtCore.Qt.UserRole,QtCore.Qt.UserRole,
                                  pixCoord)
                self.listPointItems.append(treeItem1)

            for dongle in self.dataHist[point].keys():
                treeItem2 = QtWidgets.QTreeWidgetItem(0)
                treeItem2.setText(0, dongle)
                treeItem2.name = dongle
                if self.dongles and self.dongles[dongle][1]:
                    treeItem2.setForeground(0, QtGui.QBrush(QtGui.QColor(
                        self.dongles[dongle][1])))
                # treeItem2.setFlags(treeItem2.flags() & ~1)
                for beacon in self.dataHist[point][dongle].keys():
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

    def updateSliders(self):
        self.ui.t.setText("t: %s" % (self.ui.sliderT.value()/100.0))
        self.ui.beta.setText("%s: %s" % ("B",
                                      self.ui.sliderBeta.value()/ 100.0))
        self.ui.theta.setText("%s: %s" % ("T",
                          (self.ui.sliderTheta.value()-50.0) / 50.0))
        if self.params["limits"]:
            self.ui.r.setText("r: %s" % (
                self.ui.sliderR.value()/ 100.0 *
                (round(math.sqrt(
                    self.params["limits"][1][0]**2 +
                    self.params["limits"][1][1]**2
                ),2)
            )))

        if self.ui.sliderTheta.isEnabled():
            self.ori = (self.ui.sliderTheta.value()-50.0)/ 50.0


    def updateTheta(self):
        if self.ui.thetaBox.isChecked():
            self.ui.sliderTheta.setDisabled(False)
            self.updateSliders()
        else:
            self.ui.sliderTheta.setDisabled(True)
            self.ori = None


    def plotHist(self, point, p_int):

        for index in range(len(self.dongleBoxes)):
            dongle = self.plotSelection[index][0]
            beacon = self.plotSelection[index][1]

            if beacon and dongle:
                if not dongle in self.dataHist[point].keys():
                    self.log("Dongle not loaded: " + dongle, -1)
                    continue

                color = QtGui.QColor(self.beacons[beacon][1])
                # color.setAlpha(80)
                bg = pg.BarGraphItem(
                    x=self.dataBins[:-1],
                    height=self.dataHist[point][dongle][beacon],
                    width=(self.dataBins[1] - self.dataBins[0]),
                    pen={'color': color},
                    brush=color)

                if p_int == 1:
                    self.hl1[index].clear()
                    self.hl1[index].addItem(bg)
                    c1 = QtGui.QColor(self.imageScene.pairColor1)
                    c1.setAlpha(25)
                    self.hl1[index].setBackgroundBrush(QtGui.QBrush(c1))

                    # self.ui.histView1_1

                if p_int == 2:
                    self.hl2[index].clear()
                    self.hl2[index].addItem(bg)
                    c2 = QtGui.QColor(self.imageScene.pairColor2)
                    c2.setAlpha(25)
                    self.hl2[index].setBackgroundBrush(QtGui.QBrush(c2))

    def plotMidHist(self, point1, point2, t):
        for index in range(len(self.dongleBoxes)):
            dongle = self.plotSelection[index][0]
            beacon = self.plotSelection[index][1]


            if beacon and dongle:

                if not dongle in self.dataHist[point1].keys():
                    self.log("Dongle not loaded: " + dongle, -1)
                    continue

                beta = self.ui.sliderBeta.value() / 100.0
                W, mapping = hist_wasserstein(
                    self.dataHist[point1][dongle][beacon],
                    self.dataHist[point2][dongle][beacon]
                )
                midhist = hist_wasserstein_interpolation(
                    mapping, t, beta, self.dataBins
                )

                color = QtGui.QColor(self.beacons[beacon][1])
                # color.setAlpha(75)

                bg = pg.BarGraphItem(
                    x=self.dataBins[:-1],
                    height=midhist,
                    width=(self.dataBins[1] - self.dataBins[0]),
                    pen={'color': color},
                    brush=color)
                self.hl0[index].clear()
                self.hl0[index].addItem(bg)
                c0 = QtGui.QColor(self.imageScene.latestColor)
                c0.setAlpha(25)
                self.hl0[index].setBackgroundBrush(QtGui.QBrush(c0))


def main():

    if len(sys.argv) > 1:
        configFile = sys.argv[1]
    else:
        configFile = None

    app = btInterpolateGui(configFile)
    app.run()

if __name__ == '__main__':
    main()
