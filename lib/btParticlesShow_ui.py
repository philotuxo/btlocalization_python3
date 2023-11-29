# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'btParticlesShow.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_btParticleShow(object):
    def setupUi(self, btParticleShow):
        btParticleShow.setObjectName("btParticleShow")
        btParticleShow.resize(772, 749)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(btParticleShow.sizePolicy().hasHeightForWidth())
        btParticleShow.setSizePolicy(sizePolicy)
        btParticleShow.setMaximumSize(QtCore.QSize(975, 749))
        btParticleShow.setMouseTracking(True)
        self.centralwidget = QtWidgets.QWidget(btParticleShow)
        self.centralwidget.setObjectName("centralwidget")
        self.imageView = QtWidgets.QGraphicsView(self.centralwidget)
        self.imageView.setGeometry(QtCore.QRect(10, 10, 751, 731))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageView.sizePolicy().hasHeightForWidth())
        self.imageView.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setKerning(False)
        self.imageView.setFont(font)
        self.imageView.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.imageView.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.imageView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.imageView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.imageView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.imageView.setAlignment(QtCore.Qt.AlignCenter)
        self.imageView.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.imageView.setViewportUpdateMode(QtWidgets.QGraphicsView.MinimalViewportUpdate)
        self.imageView.setObjectName("imageView")
        self.info = QtWidgets.QLabel(self.centralwidget)
        self.info.setGeometry(QtCore.QRect(120, 680, 551, 41))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.info.setFont(font)
        self.info.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.info.setObjectName("info")
        btParticleShow.setCentralWidget(self.centralwidget)
        self.actionRead_HST_File = QtWidgets.QAction(btParticleShow)
        self.actionRead_HST_File.setObjectName("actionRead_HST_File")
        self.actionRead_Directory = QtWidgets.QAction(btParticleShow)
        self.actionRead_Directory.setObjectName("actionRead_Directory")
        self.actionRead_Files = QtWidgets.QAction(btParticleShow)
        self.actionRead_Files.setObjectName("actionRead_Files")
        self.actionExport_HST_File = QtWidgets.QAction(btParticleShow)
        self.actionExport_HST_File.setObjectName("actionExport_HST_File")
        self.actionClear_Image = QtWidgets.QAction(btParticleShow)
        self.actionClear_Image.setObjectName("actionClear_Image")
        self.actionLoad_Parameters = QtWidgets.QAction(btParticleShow)
        self.actionLoad_Parameters.setObjectName("actionLoad_Parameters")
        self.actionLoad_Conversion = QtWidgets.QAction(btParticleShow)
        self.actionLoad_Conversion.setObjectName("actionLoad_Conversion")
        self.actionClear_Beacons = QtWidgets.QAction(btParticleShow)
        self.actionClear_Beacons.setObjectName("actionClear_Beacons")
        self.actionLoadBeacons = QtWidgets.QAction(btParticleShow)
        self.actionLoadBeacons.setObjectName("actionLoadBeacons")
        self.actionSaveBeacons = QtWidgets.QAction(btParticleShow)
        self.actionSaveBeacons.setObjectName("actionSaveBeacons")
        self.actionLoadImage = QtWidgets.QAction(btParticleShow)
        self.actionLoadImage.setObjectName("actionLoadImage")
        self.actionClearImage = QtWidgets.QAction(btParticleShow)
        self.actionClearImage.setObjectName("actionClearImage")
        self.actionSaveParams = QtWidgets.QAction(btParticleShow)
        self.actionSaveParams.setObjectName("actionSaveParams")
        self.actionLoadParams = QtWidgets.QAction(btParticleShow)
        self.actionLoadParams.setObjectName("actionLoadParams")
        self.actionLoadConversion = QtWidgets.QAction(btParticleShow)
        self.actionLoadConversion.setObjectName("actionLoadConversion")
        self.actionClearConversion = QtWidgets.QAction(btParticleShow)
        self.actionClearConversion.setObjectName("actionClearConversion")
        self.actionSaveConversion = QtWidgets.QAction(btParticleShow)
        self.actionSaveConversion.setObjectName("actionSaveConversion")
        self.actionRead_Trajectory = QtWidgets.QAction(btParticleShow)
        self.actionRead_Trajectory.setObjectName("actionRead_Trajectory")
        self.actionReadTrajectory = QtWidgets.QAction(btParticleShow)
        self.actionReadTrajectory.setObjectName("actionReadTrajectory")
        self.actionOverlayTrajectory = QtWidgets.QAction(btParticleShow)
        self.actionOverlayTrajectory.setObjectName("actionOverlayTrajectory")
        self.actionRemoveTrajectories = QtWidgets.QAction(btParticleShow)
        self.actionRemoveTrajectories.setObjectName("actionRemoveTrajectories")
        self.actionLoadDevices = QtWidgets.QAction(btParticleShow)
        self.actionLoadDevices.setObjectName("actionLoadDevices")
        self.actionRefresh = QtWidgets.QAction(btParticleShow)
        self.actionRefresh.setObjectName("actionRefresh")
        self.actionDelete_Data = QtWidgets.QAction(btParticleShow)
        self.actionDelete_Data.setObjectName("actionDelete_Data")

        self.retranslateUi(btParticleShow)
        QtCore.QMetaObject.connectSlotsByName(btParticleShow)

    def retranslateUi(self, btParticleShow):
        _translate = QtCore.QCoreApplication.translate
        btParticleShow.setWindowTitle(_translate("btParticleShow", "Particle Filter for Sensor-Beacon Pair"))
        self.info.setText(_translate("btParticleShow", "Starting..."))
        self.actionRead_HST_File.setText(_translate("btParticleShow", "&Read HST File"))
        self.actionRead_Directory.setText(_translate("btParticleShow", "Read &Directory"))
        self.actionRead_Files.setText(_translate("btParticleShow", "Read &MBD Files"))
        self.actionExport_HST_File.setText(_translate("btParticleShow", "&Export HST File"))
        self.actionClear_Image.setText(_translate("btParticleShow", "&Clear Image"))
        self.actionLoad_Parameters.setText(_translate("btParticleShow", "Load Parameters"))
        self.actionLoad_Conversion.setText(_translate("btParticleShow", "Load Conversion"))
        self.actionClear_Beacons.setText(_translate("btParticleShow", "Clear Beacons"))
        self.actionLoadBeacons.setText(_translate("btParticleShow", "&Load"))
        self.actionSaveBeacons.setText(_translate("btParticleShow", "&Save"))
        self.actionLoadImage.setText(_translate("btParticleShow", "&Load"))
        self.actionClearImage.setText(_translate("btParticleShow", "&Clear"))
        self.actionSaveParams.setText(_translate("btParticleShow", "&Save"))
        self.actionLoadParams.setText(_translate("btParticleShow", "&Load"))
        self.actionLoadConversion.setText(_translate("btParticleShow", "&Load"))
        self.actionClearConversion.setText(_translate("btParticleShow", "&Clear"))
        self.actionSaveConversion.setText(_translate("btParticleShow", "&Save"))
        self.actionRead_Trajectory.setText(_translate("btParticleShow", "Read Trajectory"))
        self.actionReadTrajectory.setText(_translate("btParticleShow", "&Read Trajectory File"))
        self.actionOverlayTrajectory.setText(_translate("btParticleShow", "&Overlay Trajectory"))
        self.actionRemoveTrajectories.setText(_translate("btParticleShow", "R&emove Trajectories"))
        self.actionLoadDevices.setText(_translate("btParticleShow", "&Load"))
        self.actionRefresh.setText(_translate("btParticleShow", "&Refresh"))
        self.actionDelete_Data.setText(_translate("btParticleShow", "&Delete Data"))
