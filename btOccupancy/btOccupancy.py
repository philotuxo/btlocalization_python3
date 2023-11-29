from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import Qt
import sys, os, time
sys.path.append("..")
from lib.btOccupancy_ui import Ui_btOccupancy
from lib.btImageScene import *
from lib.histograms import *
from lib.parsers import *
from lib.paths import *
from lib.btCommon import *

visualColorSelected = QtGui.QColor(200, 0, 0, 150)
visualColorNormal = QtGui.QColor(0, 0, 0, 0)
trkColorNormal = QtGui.QColor(0,0,0,5)

class btOccupancyPixmapItem(btPixmapItem):
    def __init__(self, parent):
        super(btOccupancyPixmapItem, self).__init__(parent)
        self.parent = parent

    def mousePressEvent(self,event):
        # QGraphicsScene cannot receive the points properly,
        # thus QGraphicsPixmapItem hands them over
        self.parent.pointOverride(event.pos(), data = None)

    def mouseReleaseEvent(self, event):
        self.parent.pointOverrideRelease(event.pos(), data = None)

    def mouseMoveEvent(self, event):
        self.parent.pointOverrideMove(event.pos(), data = None)


class btOccupancyScene(btImageScene):
    def __init__(self, btOccupancyGui):
        btImageScene.__init__(self, btOccupancyGui)
        self.circleRadius = 1
        self.parent = btOccupancyGui
        self.pointColor = QtGui.QColor(100,100,0, 30)
        self.lineColor = QtGui.QColor(255,0,0,30)
        self.latestColor = QtGui.QColor(150,150,150,200)
        self.oldClicked = None
        self.tempEllipse = None
        self.rectTopLeft = None
        self.rectBottomRight = None
        self.tempRect = None

    def pointOverride(self,
                      pixCoord,
                      visual=None,
                      data=None):
        if self.tempEllipse:
            self.removeItem(self.tempEllipse)
        self.tempEllipse = self.addPoint(pixCoord)
        reaCoord = pix2real(self.parent.params,pixCoord)
        self.rectTopLeft = [ pixCoord, reaCoord ]

    def pointOverrideRelease(self,
                      pixCoord,
                      visual=None,
                      data=None):
        reaCoord = pix2real(self.parent.params,pixCoord)
        self.rectBottomRight = [ pixCoord, reaCoord ]
        if self.tempRect:
            self.removeItem(self.tempRect)
        self.tempRect = QtWidgets.QGraphicsRectItem(
            self.rectTopLeft[0].x(),
            self.rectTopLeft[0].y(),
            self.rectBottomRight[0].x() - self.rectTopLeft[0].x(),
            self.rectBottomRight[0].y() - self.rectTopLeft[0].y())
        self.addItem(self.tempRect)

        x_begin = np.ceil(self.rectTopLeft[1][0]/self.parent.params_grid[
            'size_grid']) * self.parent.params_grid['size_grid']
        y_begin = np.ceil(self.rectTopLeft[1][1]/self.parent.params_grid[
            'size_grid']) * self.parent.params_grid['size_grid']

        x_end = np.ceil(self.rectBottomRight[1][0]/self.parent.params_grid[
            'size_grid']) * self.parent.params_grid['size_grid']
        y_end = np.ceil(self.rectBottomRight[1][1]/self.parent.params_grid[
            'size_grid']) * self.parent.params_grid['size_grid']

        # rounded limits for control, see forloop below
        rounded_limits = (
                           ( np.floor(self.parent.params["limits"][0][0] /
                        self.parent.params_grid["size_grid"]) * \
                  self.parent.params_grid["size_grid"],
                         np.floor(self.parent.params["limits"][0][1] /
                                  self.parent.params_grid["size_grid"]) * \
                         self.parent.params_grid["size_grid"] ),
                           ( np.ceil(self.parent.params["limits"][1][0] /
                        self.parent.params_grid["size_grid"]) * \
                  self.parent.params_grid["size_grid"],
                    np.ceil(self.parent.params["limits"][1][1] /
                            self.parent.params_grid["size_grid"]) * \
                    self.parent.params_grid["size_grid"])
                           )

        for i in np.arange(
                x_begin, x_end + self.parent.params_grid['size_grid'],
                    self.parent.params_grid['size_grid']):
            for j in  np.arange(
                y_begin, y_end+ self.parent.params_grid['size_grid'],
                    self.parent.params_grid['size_grid']):

                # respect the limits
                if round(i,1) < rounded_limits[0][0] or \
                    round(i,1) > rounded_limits[1][0]:
                    continue
                if round(j,1) < rounded_limits[0][1] or \
                    round(j,1) > rounded_limits[1][1]:
                    continue

                if self.parent.ui.checkAddSelect.isChecked():
                    self.parent.fingerprintVisuals[(round(i,1), round(j,1))].data(
                        QtCore.Qt.UserRole).setSelected(True)
                else:
                    self.parent.fingerprintVisuals[(round(i, 1), round(j, 1))].data(
                        QtCore.Qt.UserRole).setSelected(False)

    def pointOverrideMove(self,
                          pixCoord,
                          visual=None,
                          data=None):
        self.rectBottomRight = [ pixCoord, None ]
        if self.tempRect:
            self.removeItem(self.tempRect)
        self.tempRect = QtWidgets.QGraphicsRectItem(
            self.rectTopLeft[0].x(),
            self.rectTopLeft[0].y(),
            self.rectBottomRight[0].x() - self.rectTopLeft[0].x(),
            self.rectBottomRight[0].y() - self.rectTopLeft[0].y())
        self.addItem(self.tempRect)

    def addRect(self, point, color=QtGui.QColor(0, 0, 0),
                 radius=None, penColor=None, penWeight=None,
                 eventTrigger=False):
        if not radius:
            radius = self.circleRadius
        color = QtGui.QColor(color)
        pn = QtGui.QPen()

        if penWeight:
            pn.setWidth(penWeight)
        if penColor:
            pn.setColor(penColor)
        else:
            pn.setColor(color)

        br = QtGui.QBrush()
        br.setStyle(1)
        br.setColor(color)
        newRect = QtWidgets.QGraphicsRectItem(
            point.x() - radius,
            point.y() - radius,
            2 * radius,
            2 * radius)
        newRect.setBrush(br)
        newRect.setPen(pn)

        self.addItem(newRect)
        return newRect

    def addFingerprintVisuals(self):
        for i in range(self.parent.ui.listData.count()):
            listItem = self.parent.ui.listData.item(i)
            pixCoord = listItem.data(QtCore.Qt.UserRole)[0]
            reaCoord = listItem.data(QtCore.Qt.UserRole)[1]
            # visualItem data: corresponding listWidgetItem
            visualItem = self.addRect(
                Qt.QRectF(pixCoord.x() - self.parent.sizeGridPx / 2,
                          pixCoord.y() - self.parent.sizeGridPx / 2,
                          self.parent.sizeGridPx,
                          self.parent.sizeGridPx),
                          color = QtGui.QColor(0,0,0,0),
                          penColor= QtGui.QColor(0,0,0,200),
                          eventTrigger=False,
                          radius=self.parent.sizeGridPx/2
            )
            visualItem.setData(QtCore.Qt.UserRole, listItem)
            # visualItem.setVisible(False)
            self.parent.fingerprintVisuals[reaCoord] = visualItem

    def dehighlightVisual(self, key):
        visual = self.parent.fingerprintVisuals[key]
        brSelected = QtGui.QBrush(visualColorNormal)
        visual.setBrush(brSelected)

    def highlightVisual(self, key):
        visual = self.parent.fingerprintVisuals[key]
        brSelected = QtGui.QBrush(visualColorSelected)
        visual.setBrush(brSelected)

    def updateImage(self, imageFile, imageTrigger = True):
        # self.printAllVisuals()
        self.removeVisuals()
        self.clear()

        if not imageFile:
            return

        if not self.frame or not imageFile == self.imageFile:
            self.frame = QtGui.QImage(imageFile)
            # check image size and save if necessary
            if self.frame.width() > self.desiredWidth:
                if not self.imagePopup(imageFile):
                    self.log("Image too large!")
                    return

            self.frame = self.setOpacity(.5)
            self.log("Image loaded: %s." % (imageFile))
            self.imageFile = imageFile

        self.pixMap = btPixmap().fromImage(self.frame)
        self.pixItem = btOccupancyPixmapItem(self)
        self.pixItem.setPixmap(self.pixMap)
        self.addPixItem(self.pixItem)

        self.setImageSize(self.frame.size())
        self.update()
        self.addVisuals()

class btOccupancyGui(QtWidgets.QMainWindow):
    def __init__(self,configFile):
        self.qt_app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QWidget.__init__(self, None)

        # create the main ui
        self.ui = Ui_btOccupancy()
        self.ui.setupUi(self)
        self.imageScene = btOccupancyScene(self)
        self.pixMap = None
        self.desiredWidth = 640
        self.data = []

        self.grids = False

        # parameters
        self.ori = None
        self.params = {}
        self.params["parity"] = None
        self.params["origin"] = None
        self.params["direction"] = None
        self.params["limits"] = None
        self.params["points"] = [ None, None ]

        # data retreiving
        self.dataValue = {}
        self.dataHist = {}
        self.dataTime = {}
        self.dataBins = []
        self.beacons = {}
        self.dongles = {}
        self.rssiRange = np.arange(rssi_start, rssi_end, 1)
        self.listPointItems = []

        # occupancy data holder
        self.data_occ = {}

        # fingerprints
        # key: real coordinate, value: visualitem(rect)
        self.fingerprintVisuals = {}

        ## data signals
        self.ui.actionRead_GRD_File.triggered.connect(self.read_grd_pressed)
        self.ui.actionRead_GRD_File.triggered.connect(self.read_grd_dir_pressed)
        self.ui.actionExport_OCC_File.triggered.connect(self.export_occ_pressed)
        self.ui.actionRead_OCC_File.triggered.connect(self.read_occ_pressed)
        self.ui.actionExport_View.triggered.connect(self.saveMapVisual)

        # selection is set to default
        self.ui.checkAddSelect.setChecked(True)

        # images manipulation
        self.ui.actionLoadImage.triggered.connect(self.loadImagePressed)
        self.ui.actionRefresh.triggered.connect(self.refreshImage)
        self.imageFile = None

        # read extras
        self.ui.actionLoadParameters.triggered.connect(self.loadParametersPressed)
        self.ui.actionLoadDevices.triggered.connect(self.loadDevicesPressed)

        # toggle check box
        self.ui.checkAddSelect.stateChanged.connect(self.checkboxChanged)

        # listWidgetSelection
        # self.ui.listData.selectionChanged.connect(self.selectionChanged)

        if configFile:
            self.readConfigFile(configFile)

    def checkboxChanged(self):
        if self.ui.checkAddSelect.isChecked():
            self.ui.checkAddSelect.setText("Adding")
        else:
            self.ui.checkAddSelect.setText("Removing")

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
                if "grd" in config.keys():
                    self.read_grd_pressed(
                        [ os.path.join(pathConf, config["grd"] )]
                    )
                if "grddir" in config.keys():
                    self.read_grd_dir_pressed(
                        os.path.join(pathConf, config["grddir"])
                    )
                self.log("Config file loaded: " + configFile, 1)
        # except:
        #     self.log("Problem with the config file: " + configFile)

    def log(self, logThis, type = 0):
        if type == -1:
            # self.ui.logBrowser.append("<font ""color=red>%s</font>" % (logThis))
            return
        if type == 1:
            # self.ui.logBrowser.append("<font ""color=green>%s</font>" % (
            #     logThis))
            return
        # self.ui.logBrowser.append(logThis)
        print(logThis)

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
                self.updateImage()

        if not hstFile:
            self.log("No data loaded.", -1 )


    def read_occ_pressed(self, file_occ = None):
        if not file_occ:
            file_occ, dummy = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        'Open file',
                                                        pathData,
                                                        'Occupancy Data ('
                                                        '*.occ)')

        if file_occ:
            self.data_occ, self.params_grid = parse_occupancy(file_occ,
                                                              self.data_occ)

        # update visuals
        for point in self.data_occ:
            if self.data_occ[point] == 1:
                self.fingerprintVisuals[point].data(
                    QtCore.Qt.UserRole).setSelected(True)
            else:
                self.fingerprintVisuals[point].data(
                    QtCore.Qt.UserRole).setSelected(False)

    def export_occ_pressed(self, file_occ = None):
        if not self.params["limits"]:
            self.log("Please read parameters first!", -1)
            return
        if not file_occ:
            file_occ, dummy = QtWidgets.QFileDialog.getSaveFileName(self,
                                                    'Save file',
                                                    pathData,
                                                    'Occupancy Data '
                                                    '(*.occ)')

        # synchronize occupancy data holder
        if file_occ:
            for point in self.data_occ.keys():
                self.data_occ[point] = int(
                    self.fingerprintVisuals[point].data(
                        QtCore.Qt.UserRole).isSelected())

        write_occupancy_file(file_occ, self.data_occ,self.params_grid)



    def read_grd_pressed(self, files_grid = None):
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
            for file_grid in files_grid:
                self.grids = True

                self.dataHist, self.params_grid = \
                    parse_grids_multi(file_grid, self.dataHist)
                size_grid = self.params_grid['size_grid']
                self.sizeGridPx = int(size_grid / self.params[ "parity"])

                self.log("File loaded: %s." % (file_grid))

            for key in self.dataHist.keys():
                self.data_occ[key] = 0
            self.refreshLists()
            self.updateImage()

    def read_grd_dir_pressed(self, grid_dir = None):
        if not self.params["limits"]:
            self.log("Please read parameters first!", -1)
            return

        if not grid_dir:
            grid_dir, dummy = QtWidgets.QFileDialog.getOpenFileNames(self,
                                                        'Open file',
                                                        pathData,
                                                        'Grid Data ('
                                                        '*.grd)')

        if grid_dir:
            self.dataHist, self.params_grid = parse_grids_dir_multi(
                grid_dir,
                default_pattern_multi_data_grid)
            size_grid = self.params_grid['size_grid']
            self.sizeGridPx = int(size_grid / self.params["parity"])
            self.grids = True

        for key in self.dataHist.keys():
            self.data_occ[key] = 0

        self.log("Directory loaded: %s." % (grid_dir))

        self.refreshLists()
        self.updateImage()

    def refreshLists(self):
        self.ui.listData.clear()
        for point in self.dataHist.keys():
            item = QtWidgets.QListWidgetItem()
            item.setText(str(point[0]) + ", " + str(point[1]))
            # treeItem1.name = point
            # treeItem1.setFlags(treeItem1.flags() & ~1)
            if self.params["origin"] \
                    and self.params["parity"]:
                pixCoord = real2pix(self.params, point)
                # listWidgetItem data: (pixCoord, reaCoord) of the visual
                item.setData(QtCore.Qt.UserRole, (pixCoord, point))
                self.ui.listData.addItem(item)

    def saveMapVisual(self, imageFile = None):

        if not imageFile:
            imageFile, dummy = QtWidgets.QFileDialog.getSaveFileName(self,
                                                    'Save file',
                                                    '../../maps',
                                                    'Images '
                                                    ' (*.png *.xpm *.jpg)')
        if not imageFile:
            return

        self.imageScene.saveImage(imageFile)

def main():

    if len(sys.argv) > 1:
        configFile = sys.argv[1]
    else:
        configFile = None

    app = btOccupancyGui(configFile)
    app.run()

if __name__ == '__main__':
    main()

