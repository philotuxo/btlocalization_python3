from PyQt5 import QtGui, QtCore, QtWidgets, Qt
import sys, os
sys.path.append("..")
from lib.btImageScene import *
from lib.btCalibrate_multi_ui import Ui_btCalibrate
from lib.histograms import *
from lib.parsers import *
from lib.processing import *
from lib.colors import *
from lib.paths import *
from ast import literal_eval
import json


class btCalibrateImageScene(btImageScene):
    def __init__(self, btCalibrateGui):
        btImageScene.__init__(self, btCalibrateGui)
        self.circleRadius = 4
        self.parent = btCalibrateGui
        self.latestPoint = None
        self.terminals = [ None, None ]
        self.originPoint = None
        self.tempCircle = None
        self.tempLine = None

    def pointOverride(self, point, text = "", color = 0, data = None):
        # abstract method
        if self.parent.selectionType == 0:
            # no selection
            if self.tempEllipse:
                self.removeItem(self.tempEllipse)
            self.tempEllipse = self.addPoint(point)

        elif self.parent.selectionType == 1:
            # Point 1
            if self.visualMeasure[0]:
                self.removeItem(self.visualMeasure[0])
            self.parent.params["points"][0] = point
            self.visualMeasure[0] = self.addPoint(
                point, "", rgb2int((255,255,0)))

            # update Line
            if all(self.visualMeasure):
                self.addMeasureLine(self.parent.params["points"][1],
                                    self.parent.params["points"][0])

        elif self.parent.selectionType == 2:
            # Point 2
            if self.visualMeasure[1]:
                self.removeItem(self.visualMeasure[1])
            self.parent.params["points"][1] = point
            self.visualMeasure[1] = self.addPoint(
                point, "", rgb2int((255,255,0)))

            # update Line Object
            if all(self.visualMeasure):
                self.addMeasureLine(self.parent.params["points"][0],
                                    self.parent.params["points"][1])

        elif self.parent.selectionType == 3:
            # Origin
            if self.visualOrigin:
                self.removeItem(self.visualOrigin)
            self.parent.params["origin"] = point
            self.visualOrigin = self.addPoint(
                point, "", rgb2int((255,0,255)))
            self.updateImage(self.parent.imageFile)

        elif self.parent.selectionType == 4:
            # Positive
            if not self.parent.params["origin"]:
                self.parent.log("Origin not set!", -1)
                return
            for item in self.positiveVisuals:
                if item:
                    self.removeItem(item)
            try:
                self.parent.params["direction"] = (self.parent.params[
                    "direction"][0], self.parent.params["direction"][1],
                    (point.x() - self.parent.params["origin"].x()) / \
                    abs(point.x() - self.parent.params["origin"].x()),
                    (point.y() - self.parent.params["origin"].y()) / \
                    abs(point.y() - self.parent.params["origin"].y()))
            except ZeroDivisionError:
                self.parent.log("Division by zero detected.", -1)
                return

            self.updateImage(self.parent.imageFile)
        self.parent.updateParameterList()


class btCalibrateGui(QtWidgets.QMainWindow):
    def __init__(self, configFile):
        self.qt_app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QWidget.__init__(self, None)

        # create the main ui
        self.ui = Ui_btCalibrate()
        self.ui.setupUi(self)
        self.imageScene = btCalibrateImageScene(self)
        self.desiredWidth = 640

        # parameters
        self.params = {}
        self.params["parity"] = None
        self.params["origin"] = None
        self.params["direction"] = None
        self.params["limits"] = None
        self.params["points"] = [ None, None ]

        # ui extras
        self.ui.dataTreeWidget.header().resizeSection(0, 175)

        ## aliases
        self.isAliasesOn = self.ui.aliasesBox.isChecked()
        self.ui.aliasesBox.stateChanged.connect(self.updateAliasState)

        # data retreiving
        self.dataValue = {}
        self.data = self.dataValue
        self.dataPoint = {}
        self.dataPointMx = {}
        self.timePoint = {}
        self.dataTime = {}
        self.dataBins = []
        self.dataBinsMx = []
        self.dataBinsMxMd = []
        self.timeBins = []
        self.beacons = {}
        self.dongles = {}
        self.rssiRange = np.arange(rssi_start, rssi_end, 1)
        self.listPointItems = {}

        ## data signals
        self.ui.actionRead_MBD_Directory.triggered.connect(self.readDirPressed)
        self.ui.actionRead_HST_File.triggered.connect(self.readHstRssiPressed)
        self.ui.button_RSSI_histogram.pressed.connect(
            self.exportHstRssiPressed)
        self.ui.button_MxRSSI_histogram.pressed.connect(
            self.exportHstMxRssiPressed)
        self.ui.button_MxMdRSSI_histogram.pressed.connect(
            self.exportHstMxMdRssiPressed)
        self.ui.button_Freq_histogram.pressed.connect(
            self.exportHstFreqPressed)
        self.ui.actionRead_MBD_File.triggered.connect(self.readCsvPressed)
        self.ui.actionRefresh.triggered.connect(self.refreshImage)
        self.ui.button_prepare.pressed.connect(self.generateHistograms)
        self.ui.button_reset.pressed.connect(self.resetHistograms)

        # images manipulation
        self.ui.actionLoadImage.triggered.connect(self.loadImagePressed)
        self.ui.actionClearImage.triggered.connect(self.resetImagePressed)
        self.ui.actionExport_View.triggered.connect(self.saveMapVisual)
        self.imageFile = None

        # trajectory overlay
        self.trajectory = []
        self.trackColor = QtGui.QColor(0, 255, 0, 25)
        self.trackVisuals = []
        self.trackLineVisuals = []
        self.ui.actionReadTrajectory.triggered.connect(self.loadTrackFromFile)
        self.ui.actionShow_Trajectory.triggered.connect(self.showTrajectory)
        self.ui.actionHide_Trajectory.triggered.connect(self.hideTrajectories)

        self.estimations = []
        self.estimColor = QtGui.QColor(0, 0, 0, 50)
        self.estimVisuals = []
        self.ui.actionRead_Estimations.triggered.connect(self.loadEstimFromFile)
        self.ui.actionShow_Estimations.triggered.connect(self.showEstimations)
        self.ui.actionHide_Trajectory.triggered.connect(self.hideEstimations)


        # calibration
        self.updateMetricState()
        self.ui.metricBox.stateChanged.connect(self.updateParameterList)
        self.prepareItems()
        self.ui.pointTypeSelection.itemSelectionChanged.connect(
            self.pointSelectionChanged)
        self.ui.pointTypeSelection.itemChanged.connect(self.updateParameterList)
        self.ui.setParityButton.pressed.connect(self.setParityButtonPressed)
        self.ui.setLimitsButton.pressed.connect(self.setLimitsPressed)
        self.ui.actionSaveParams.triggered.connect(self.saveParametersPressed)
        self.ui.actionLoadParams.triggered.connect(self.loadParametersPressed)
        self.ui.actionLoadDevices.triggered.connect(self.loadDevicesPressed)
        self.ui.actionRemoveDevices.triggered.connect(self.removeDevicesPressed)
        self.ui.dataTreeWidget.itemSelectionChanged.connect(
            self.treeSelectionChanged)

        self.selectionType = 0 # see prepareItems() for details

        if configFile:
            self.readConfigFile(configFile)

        self.updateParameterList()

    def readConfigFile(self, configFile):
        try:
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
        except:
            self.log("Problem with the config file: " + configFile)

    def hideTrajectories(self):
        for visual in self.trackVisuals:
            self.imageScene.removeItem(visual)
        for visual in self.trackLineVisuals:
            self.imageScene.removeItem(visual)
        self.trackVisuals.clear()
        self.trackLineVisuals.clear()

    def hideEstimations(self):
        for visual in self.estimVisuals:
            self.imageScene.removeItem(visual)
        self.estimVisuals.clear()


    def showTrajectory(self):
        oldPoint = False
        for point in self.trajectory:
            itemPoint = self.imageScene.addPoint(point, '',
                                                 self.trackColor,
                                                 radius=3)

            if oldPoint is not False:
                itemLine = self.imageScene.addLine(
                    oldPoint.x(),
                    oldPoint.y(),
                    point.x(), point.y()
                )
                itemLine.setPen(QtGui.QPen(self.trackColor))
                self.trackLineVisuals.append(itemLine)
            oldPoint = point
            self.trackVisuals.append(itemPoint)

    def showEstimations(self):
        # oldPoint = False
        for point in self.estimations:
            itemPoint = self.imageScene.addPoint(point, '',
                                                 self.estimColor,
                                                 radius=3)

            # if oldPoint is not False:
            #     itemLine = self.imageScene.addLine(
            #         oldPoint.x(),
            #         oldPoint.y(),
            #         point.x(), point.y()
            #     )
            #     self.trackLineVisuals.append(itemLine)
            # oldPoint = point
            self.estimVisuals.append(itemPoint)

    def loadTrackFromFile(self):
        self.trajectory.clear()
        self.hideTrajectories()
        self.trackVisuals.clear()
        self.trackLineVisuals.clear()
        tFile, dummy = QtWidgets.QFileDialog.getOpenFileName(self,
                                                  'Open file',
                                                  pathData,
                                                  'Track Data (*.mbd *.txt)')

        if not tFile:
            return

        with open(tFile, 'r') as f:
            for line in f:
                each = line.strip().split(',')
                point = real2pix(self.params, (float(each[4]),float(each[5])))
                self.trajectory.append(point)

            self.log ("Trajectory file loaded " + tFile, 1)

    def loadEstimFromFile(self):
        self.estimations.clear()
        self.hideEstimations()
        self.estimVisuals.clear()

        tFile, dummy = QtWidgets.QFileDialog.getOpenFileName(self,
                                                  'Open file',
                                                  pathData,
                                                  'Estimation Data (*.txt)')

        if not tFile:
            return

        with open(tFile, 'r') as f:
            for line in f:
                each = line.strip().split(',')
                text_points = each[1] + ", " + each[2]
                point_real = literal_eval(text_points.strip())
                point = real2pix(self.params, (point_real))
                self.estimations.append(point)

            self.log ("Estimations file loaded " + tFile, 1)


    def resetImagePressed(self):
        self.imageFile = None
        self.updateImage()
        self.ui.noImageLabel.setVisible(True)

    def refreshImage(self):
        self.imageScene.updateImage(self.imageFile)

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
        self.refreshLists()
        self.imageScene.updateImage(self.imageFile)
        self.ui.imageView.setScene(self.imageScene)
        if self.imageFile:
            self.ui.noImageLabel.setVisible(False)

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

    def removeDevicesPressed(self):
        self.imageScene.removeDeviceVisuals()
        self.dongles.clear()
        self.updateImage()

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
            self.updateParameterList()
            self.refreshLists()
            self.updateImage()

    def deleteDataButtonPressed(self):
        for point in self.pointsSelected:
            del self.dataValue[point]
            del self.dataTime[point]
        self.refreshLists()

    def prepareItems(self):
        self.itemList = [
            [ "Point 1" ,1, None ],
            [ "Point 2" ,2, None ],
            [ "Origin"  ,3, None ],
            [ "Direction",4, None ],
            [ "Parity"  ,5, None ],
            [ "Edit"    ,6, None ],
            [ "Limits"  ,7, None ] ]
        self.ui.pointTypeSelection.clear()
        for itemKey in self.itemList:
            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.DisplayRole, itemKey[0])
            item.setData(QtCore.Qt.UserRole, itemKey[1])
            # role 3 is used for data storage
            itemKey[2] = item
            self.ui.pointTypeSelection.addItem(item)

    def updateParameterList(self):
        if self.params["points"][0]:
            if self.isMetricOn:
                real = pix2real(self.params, self.params["points"][0])
                text = "Point 1 (m): %s,%s" % (
                    round(real[0],3),
                    round(real[1],3))
            else:
                text = "Point 1 (px): %s,%s" % (
                    self.params["points"][0].x(),
                    self.params["points"][0].y())

            self.itemList[0][2].setData(QtCore.Qt.DisplayRole, text)

        if self.params["points"][1]:
            if self.isMetricOn:
                real = pix2real(self.params, self.params["points"][1])
                text = "Point 2 (m): %s,%s" % (
                    round(real[0],3),
                    round(real[1],3))
            else:
                text = "Point 2 (px): %s,%s" % (
                    self.params["points"][1].x(),
                    self.params["points"][1].y())

            self.itemList[1][2].setData(QtCore.Qt.DisplayRole, text)

        if self.params["origin"]:
            self.itemList[2][2].setData(
                QtCore.Qt.DisplayRole,
                    "Origin (px): %s,%s" % (
                        self.params["origin"].x(),
                        self.params["origin"].y()))

        if self.params["direction"]:
            self.itemList[3][2].setData(
            QtCore.Qt.DisplayRole,
            "Positive: %s,%s,%s,%s" % (
                self.params["direction"][0],
                self.params["direction"][1],
                self.params["direction"][2],
                self.params["direction"][3]))
        if self.params["parity"]:
            self.itemList[4][2].setData(QtCore.Qt.DisplayRole,
                "Parity: %s m/px" % round(self.params["parity"],4))

        if self.params["limits"]:
            self.itemList[6][2].setData(QtCore.Qt.DisplayRole,
                "Limits (m): %s,%s|%s,%s" %(
                    round(self.params["limits"][0][0],2),
                    round(self.params["limits"][0][1],2),
                    round(self.params["limits"][1][0],2),
                    round(self.params["limits"][1][1],2)
                                        ))

        # to toggle parity
        if all(self.params["points"]):
            self.ui.setParityButton.setEnabled(True)
        else:
            self.ui.setParityButton.setEnabled(False)

        # to toggle set limits
        if all(self.params["points"]) and \
                self.params["parity"] and \
                self.params["direction"]:
            self.ui.setLimitsButton.setEnabled(True)
        else:
            self.ui.setLimitsButton.setEnabled(False)

        # first call metricStatus then do the update
        self.updateMetricState()
        self.imageScene.update()

    def setParityButtonPressed(self):
        if self.params['points'][0] and self.params['points'][1]:
            self.params["parity"] =  \
                1 / math.sqrt(
                    (self.params['points'][0].x() -
                     self.params['points'][1].x())**2 + \
                    (self.params['points'][0].y() -
                     self.params['points'][1].y())**2)

            self.updateParameterList()

    def setLimitsPressed(self):
        if self.params["parity"] \
                and self.params["origin"] \
                and self.params["direction"] \
                and all(self.params["points"]):

            self.params["limits"] = (
                pix2real(self.params, self.params['points'][0]),
                pix2real(self.params, self.params['points'][1]))
            # self.imageScene.placeParameters()
            self.updateParameterList()
            self.updateImage()

    def updateMetricState(self):
        if self.params["origin"] and\
            self.params["parity"] and\
            self.params["direction"] and\
            self.ui.metricBox.isChecked():
            self.isMetricOn = True
        else:
            self.isMetricOn = False

    def pointSelectionChanged(self):
        items = self.ui.pointTypeSelection.selectedItems()
        if len(items) > 0:
            self.selectionType = items[0].data(QtCore.Qt.UserRole)
        else:
            self.selectionType = 0

    def readDirPressed(self, dataDir = None):
        if not dataDir:
            dataDir = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Select Directory",
                pathData,
                options=QtWidgets.QFileDialog.ShowDirsOnly|
                         QtWidgets.QFileDialog.DontUseNativeDialog
            )


        if dataDir:
            self.log("Parsing directory: %s." %(dataDir))

            self.dataValue, self.dataTime = parseDataDir_multi(
                dataDir, default_pattern_multi_data, quiet = True)
            self.data = self.dataValue
            self.refreshLists()

        if not dataDir:
            self.log("No data loaded.", True)

    def generateHistograms(self):
        hasRun = False
        if self.ui.checkBox_rssi.isEnabled() and \
                self.ui.checkBox_rssi.isChecked():
            hasRun = True
            if len(self.dataValue) == 0:
                self.log("Please load some data first.", type=-1)
                return
            self.dataPoint, self.dataBins = \
                rssiHistFromDataDict_multi(self.dataValue, normalized=True)
            self.log("RSSI histograms prepared.", 1)
            self.ui.checkBox_rssi.setDisabled(True)

        if self.ui.checkBox_mxrssi.isEnabled() and \
                self.ui.checkBox_mxrssi.isChecked():
            hasRun = True
            if len(self.dataValue) == 0:
                self.log("Please load some data first.", type=-1)
                return
            sec_window = self.ui.spinMxRssiWindow.value()
            self.dataPointMx, self.dataBinsMx = \
                maxRssiHistFromDataDict_multi(self.dataValue, self.dataTime, sec_window, normalized=True)
            self.log("Max RSSI histograms prepared.", 1)
            self.ui.checkBox_mxrssi.setDisabled(True)
            self.ui.spinMxRssiWindow.setDisabled(True)

        if self.ui.checkBox_mxmdrssi.isEnabled() and self.ui.checkBox_mxmdrssi.isChecked():
            hasRun = True
            if len(self.dataValue) == 0:
                if len(self.dataValue) == 0:
                    self.log("Please load some data first.", type=-1)
                    return
            sec_window = self.ui.spinMxMdRssiWindow.value()
            self.dataPointMxMd, self.dataBinsMxMd = \
                maxModeRssiDistFromDataDict_multi(self.dataValue, self.dataTime, sec_window)
            self.log("Max Mode RSSI histograms prepared.", 1)
            self.ui.checkBox_mxmdrssi.setDisabled(True)
            self.ui.spinMxMdRssiWindow.setDisabled(True)

        if self.ui.checkBox_freq.isEnabled() and \
                self.ui.checkBox_freq.isChecked():
            hasRun = True
            if len(self.dataTime) == 0:
                self.log("Please load some data first.", type=-1)
                return
            self.timePoint, self.timeBins = \
                freqHistFromDataDict_multi(self.dataTime, normalized=True)
            self.log("Frequency histograms prepared.", 1)
            self.ui.checkBox_freq.setDisabled(True)
        if not hasRun:
            self.log("Please select data to generate histograms.",type = -1)

    def resetHistograms(self):
        self.timePoint.clear()
        self.dataPoint.clear()
        self.ui.checkBox_rssi.setEnabled(True)
        self.ui.checkBox_rssi.setChecked(False)
        self.ui.checkBox_freq.setEnabled(True)
        self.ui.checkBox_freq.setChecked(False)
        self.ui.checkBox_mxrssi.setEnabled(True)
        self.ui.checkBox_mxrssi.setChecked(False)
        self.ui.checkBox_mxmdrssi.setEnabled(True)
        self.ui.checkBox_mxmdrssi.setChecked(False)

        self.ui.spinMxRssiWindow.setEnabled(True)
        self.ui.spinMxMdRssiWindow.setEnabled(True)

    def exportHstMxRssiPressed(self):
        if not len(self.dataBinsMx) > 0:
            self.log("Load data first.", True)
            return

        hstFile, dummy = QtWidgets.QFileDialog.getSaveFileName(self,
                                                    'Save file',
                                                    '../../data',
                                                    'Histogram Data '
                                                    '(*.hst)')
        if hstFile:
            write_hist_file(hstFile,
                     self.dataPointMx,
                     self.dataBinsMx,
                     self.beacons,
                     self.dongles)
            self.log("Histogram file written: %s." % (hstFile),1)
        else:
            self.log("Histogram file not written.", -1)

    def exportHstMxMdRssiPressed(self):
        if not len(self.dataBinsMxMd) > 0:
            self.log("Load data first.", True)
            return

        hstFile, dummy = QtWidgets.QFileDialog.getSaveFileName(self,
                                                    'Save file',
                                                    '../../data',
                                                    'Histogram Data '
                                                    '(*.hst)')
        if hstFile:
            write_hist_file(hstFile,
                     self.dataPointMxMd,
                     self.dataBinsMxMd,
                     self.beacons,
                     self.dongles)

            self.log("Histogram file written: %s." % (hstFile),1)
        else:
            self.log("Histogram file not written.", -1)



    def exportHstRssiPressed(self):
        if not len(self.dataBins) > 0:
            self.log("Load data first.", True)
            return

        hstFile, dummy = QtWidgets.QFileDialog.getSaveFileName(self,
                                                    'Save file',
                                                    '../../data',
                                                    'Histogram Data '
                                                    '(*.hst)')
        if hstFile:
            write_hist_file(hstFile,
                     self.dataPoint,
                     self.dataBins,
                     self.beacons,
                     self.dongles)
            self.log("Histogram file written: %s." % (hstFile),1)
        else:
            self.log("Histogram file not written.", -1)

    def exportHstFreqPressed(self):
        if not len(self.timeBins) > 0:
            self.log("Load data first.", True)
            return

        hist_file_name, dummy = QtWidgets.QFileDialog.getSaveFileName(self,
                                                    'Save file',
                                                    '../../data',
                                                    'Histogram Data '
                                                    '(*.hst)')

        if hist_file_name:
            write_hist_file(hist_file_name,
                     self.timePoint,
                     self.timeBins,
                     self.beacons,
                     self.dongles)
            self.log("Histogram file written: %s." % (hist_file_name),1)
        else:
            self.log("Histogram file not written.", -1)

    def readHstRssiPressed(self, hstFile = None):
        if not hstFile:
            hstFile, dummy = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        'Open file',
                                                        '../../data',
                                                        'Histogram Data ('
                                                        '*.hst)')

        if hstFile:
            try:
                self.dataPoint, self.dataBins, self.beacons, self.dongles = \
                    parse_hist_multi(hstFile)
                self.log("File loaded: %s." % (hstFile), 1)
                self.data = self.dataPoint
                self.refreshLists()
            except AttributeError:
                self.log("Invalid hst file.", -1)


        if not hstFile:
            self.log("No data loaded.", True)

    def readCsvPressed(self, mbdFiles = None):
        # self.log("Parsing CSV files not implemented yet.", -1)
        # return
        #

        if type(mbdFiles) == str:
            mbdFiles = [mbdFiles]

        if not mbdFiles:
            mbdFiles, dummy = QtWidgets.QFileDialog.getOpenFileNames(self,
                                                                'Open file',
                                                                pathData,
                                                                'Log File ('
                                                                '*.mbd)')

        if not len(mbdFiles) > 0:
            return

        for mbdFile in mbdFiles:
            self.dataValue, self.dataTime = parseDataFile_multi(
                mbdFile,
                self.dataValue,
                self.dataTime,
                default_pattern_multi_data,
                quiet=True)
        self.data = self.dataValue

        self.refreshLists()

    def treeSelectionChanged(self):
        self.refreshImage()

    def refreshLists(self):
        self.ui.dataTreeWidget.clear()
        self.listPointItems.clear()
        for point in self.data.keys():
            treeItem1 = QtWidgets.QTreeWidgetItem(0)
            treeItem1.setText(0,str(point))
            treeItem1.name = point
            # treeItem1.setFlags(treeItem1.flags() & ~1)
            if self.imageScene.pixMap \
                    and self.params["origin"] \
                    and self.params["parity"]:
                coord = real2pix(self.params, point)
                treeItem1.setData(QtCore.Qt.UserRole,QtCore.Qt.UserRole,coord)
                self.listPointItems[point] = treeItem1

            for dongle in self.data[point].keys():
                treeItem2 = QtWidgets.QTreeWidgetItem(0)
                treeItem2.setText(0, self.alias(dongle,self.dongles))
                treeItem2.name = dongle
                if self.dongles and self.dongles[dongle][1]:
                    treeItem2.setForeground(0, QtGui.QBrush(QtGui.QColor(
                        self.dongles[dongle][1])))
                treeItem2.setFlags(treeItem2.flags() & ~1)
                for beacon in self.data[point][dongle].keys():
                    treeItem3 = QtWidgets.QTreeWidgetItem(0)
                    treeItem3.setText(0, self.alias(beacon, self.beacons))
                    treeItem3.name = beacon
                    if self.beacons and self.beacons[beacon][1]:
                        treeItem3.setForeground(0, QtGui.QBrush(QtGui.QColor(
                            self.beacons[beacon][1])))
                    treeItem2.addChild(treeItem3)
                treeItem1.addChild(treeItem2)
            self.ui.dataTreeWidget.addTopLevelItem(treeItem1)

    def updateAliasState(self):
        self.isAliasesOn = self.ui.aliasesBox.isChecked()
        self.refreshLists()

    def alias(self, mac, devices):
        if self.isAliasesOn and\
            mac in devices.keys() and\
            devices[mac][2]:
            return devices[mac][2]
        else:
            return mac

    def saveParametersPressed(self):

        parFile, dummy = QtWidgets.QFileDialog.getSaveFileName(self,
                                                    'Save file',
                                                    pathConf,
                                                    'Parameters '
                                                    '(*.par)')

        if not parFile:
            self.log("No file given!",-1)
            return

        try:
            tempParams = dict()
            tempParams["parity"] = self.params["parity"]
            tempParams["origin"] = ( self.params["origin"].x(),
                                     self.params["origin"].y() )
            tempParams["direction"] = (self.params["direction"][0],
                                       self.params["direction"][1],
                                       self.params["direction"][2],
                                       self.params["direction"][3])

            tempParams["limits"] = (self.params["limits"][0][0],
                                    self.params["limits"][0][1],
                                    self.params["limits"][1][0],
                                    self.params["limits"][1][1])
        except AttributeError:
            self.log("Parameters not proper!", -1)
            return

        with open(parFile, 'w') as f:
            self.log("Writing to file: %s." % (parFile))
            json.dump(tempParams, f)
            self.log("Parameters saved to %s." % (os.path.basename(str(
                parFile))),1)

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
        self.qt_app.exec_()

    def closeEvent(self, QCloseEvent):
        del self.imageScene

def main():

    if len(sys.argv) > 1:
        configFile = sys.argv[1]
    else:
        configFile = None

    app = btCalibrateGui(configFile)
    app.run()

if __name__ == '__main__':
    main()
