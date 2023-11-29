# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/btCalibrate.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_btCalibrate(object):
    def setupUi(self, btCalibrate):
        btCalibrate.setObjectName("btCalibrate")
        btCalibrate.resize(900, 900)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(btCalibrate.sizePolicy().hasHeightForWidth())
        btCalibrate.setSizePolicy(sizePolicy)
        btCalibrate.setMinimumSize(QtCore.QSize(900, 900))
        btCalibrate.setMaximumSize(QtCore.QSize(900, 900))
        self.loadImageButton = QtWidgets.QPushButton(btCalibrate)
        self.loadImageButton.setGeometry(QtCore.QRect(810, 10, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.loadImageButton.setFont(font)
        self.loadImageButton.setObjectName("loadImageButton")
        self.imageView = QtWidgets.QGraphicsView(btCalibrate)
        self.imageView.setGeometry(QtCore.QRect(190, 90, 701, 801))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageView.sizePolicy().hasHeightForWidth())
        self.imageView.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.imageView.setFont(font)
        self.imageView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.imageView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.imageView.setObjectName("imageView")
        self.noImageLabel = QtWidgets.QLabel(btCalibrate)
        self.noImageLabel.setGeometry(QtCore.QRect(480, 360, 131, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(30, 30, 40))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(20, 19, 18))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        self.noImageLabel.setPalette(palette)
        self.noImageLabel.setObjectName("noImageLabel")
        self.loadDevicesButton = QtWidgets.QPushButton(btCalibrate)
        self.loadDevicesButton.setGeometry(QtCore.QRect(810, 30, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.loadDevicesButton.setFont(font)
        self.loadDevicesButton.setObjectName("loadDevicesButton")
        self.clearDevicesButton = QtWidgets.QPushButton(btCalibrate)
        self.clearDevicesButton.setGeometry(QtCore.QRect(850, 30, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.clearDevicesButton.setFont(font)
        self.clearDevicesButton.setObjectName("clearDevicesButton")
        self.resetImageButton = QtWidgets.QPushButton(btCalibrate)
        self.resetImageButton.setGeometry(QtCore.QRect(850, 10, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.resetImageButton.setFont(font)
        self.resetImageButton.setObjectName("resetImageButton")
        self.label = QtWidgets.QLabel(btCalibrate)
        self.label.setGeometry(QtCore.QRect(730, 13, 81, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(btCalibrate)
        self.label_2.setGeometry(QtCore.QRect(730, 32, 81, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.pointSelectBox = QtWidgets.QGroupBox(btCalibrate)
        self.pointSelectBox.setGeometry(QtCore.QRect(190, 10, 81, 81))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.pointSelectBox.setFont(font)
        self.pointSelectBox.setTitle("")
        self.pointSelectBox.setFlat(False)
        self.pointSelectBox.setCheckable(False)
        self.pointSelectBox.setObjectName("pointSelectBox")
        self.point1 = QtWidgets.QRadioButton(self.pointSelectBox)
        self.point1.setGeometry(QtCore.QRect(0, 0, 71, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.point1.setFont(font)
        self.point1.setObjectName("point1")
        self.point2 = QtWidgets.QRadioButton(self.pointSelectBox)
        self.point2.setGeometry(QtCore.QRect(0, 20, 71, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.point2.setFont(font)
        self.point2.setObjectName("point2")
        self.origin = QtWidgets.QRadioButton(self.pointSelectBox)
        self.origin.setGeometry(QtCore.QRect(0, 40, 61, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.origin.setFont(font)
        self.origin.setObjectName("origin")
        self.positive = QtWidgets.QRadioButton(self.pointSelectBox)
        self.positive.setGeometry(QtCore.QRect(0, 60, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.positive.setFont(font)
        self.positive.setObjectName("positive")
        self.labelPoint1 = QtWidgets.QLabel(btCalibrate)
        self.labelPoint1.setGeometry(QtCore.QRect(280, 12, 221, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelPoint1.setFont(font)
        self.labelPoint1.setObjectName("labelPoint1")
        self.labelPoint2 = QtWidgets.QLabel(btCalibrate)
        self.labelPoint2.setGeometry(QtCore.QRect(280, 32, 221, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelPoint2.setFont(font)
        self.labelPoint2.setObjectName("labelPoint2")
        self.calibrateButton = QtWidgets.QPushButton(btCalibrate)
        self.calibrateButton.setGeometry(QtCore.QRect(450, 46, 61, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.calibrateButton.setFont(font)
        self.calibrateButton.setObjectName("calibrateButton")
        self.meterBox = QtWidgets.QDoubleSpinBox(btCalibrate)
        self.meterBox.setGeometry(QtCore.QRect(388, 45, 62, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.meterBox.setFont(font)
        self.meterBox.setObjectName("meterBox")
        self.resetDataButton = QtWidgets.QPushButton(btCalibrate)
        self.resetDataButton.setGeometry(QtCore.QRect(140, 10, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.resetDataButton.setFont(font)
        self.resetDataButton.setObjectName("resetDataButton")
        self.beaconsAvailable = QtWidgets.QListWidget(btCalibrate)
        self.beaconsAvailable.setGeometry(QtCore.QRect(10, 370, 171, 221))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(8)
        self.beaconsAvailable.setFont(font)
        self.beaconsAvailable.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.beaconsAvailable.setObjectName("beaconsAvailable")
        self.selectNoneButton = QtWidgets.QPushButton(btCalibrate)
        self.selectNoneButton.setGeometry(QtCore.QRect(50, 350, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.selectNoneButton.setFont(font)
        self.selectNoneButton.setObjectName("selectNoneButton")
        self.selectAllButton = QtWidgets.QPushButton(btCalibrate)
        self.selectAllButton.setGeometry(QtCore.QRect(10, 350, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.selectAllButton.setFont(font)
        self.selectAllButton.setObjectName("selectAllButton")
        self.pointsAvailable = QtWidgets.QListWidget(btCalibrate)
        self.pointsAvailable.setGeometry(QtCore.QRect(10, 30, 171, 321))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(8)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.pointsAvailable.setFont(font)
        self.pointsAvailable.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.pointsAvailable.setObjectName("pointsAvailable")
        self.readDataButton = QtWidgets.QPushButton(btCalibrate)
        self.readDataButton.setGeometry(QtCore.QRect(10, 10, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.readDataButton.setFont(font)
        self.readDataButton.setObjectName("readDataButton")
        self.labelOrigin = QtWidgets.QLabel(btCalibrate)
        self.labelOrigin.setGeometry(QtCore.QRect(280, 52, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelOrigin.setFont(font)
        self.labelOrigin.setObjectName("labelOrigin")
        self.labelPositive = QtWidgets.QLabel(btCalibrate)
        self.labelPositive.setGeometry(QtCore.QRect(280, 72, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelPositive.setFont(font)
        self.labelPositive.setObjectName("labelPositive")
        self.labelParity = QtWidgets.QLabel(btCalibrate)
        self.labelParity.setGeometry(QtCore.QRect(520, 12, 141, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelParity.setFont(font)
        self.labelParity.setObjectName("labelParity")
        self.saveParametersButton = QtWidgets.QPushButton(btCalibrate)
        self.saveParametersButton.setGeometry(QtCore.QRect(850, 50, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.saveParametersButton.setFont(font)
        self.saveParametersButton.setObjectName("saveParametersButton")
        self.loadParametersButton = QtWidgets.QPushButton(btCalibrate)
        self.loadParametersButton.setGeometry(QtCore.QRect(810, 50, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.loadParametersButton.setFont(font)
        self.loadParametersButton.setObjectName("loadParametersButton")
        self.label_3 = QtWidgets.QLabel(btCalibrate)
        self.label_3.setGeometry(QtCore.QRect(730, 53, 81, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.exportButton = QtWidgets.QPushButton(btCalibrate)
        self.exportButton.setGeometry(QtCore.QRect(830, 70, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.exportButton.setFont(font)
        self.exportButton.setObjectName("exportButton")
        self.setLimitsButton = QtWidgets.QPushButton(btCalibrate)
        self.setLimitsButton.setGeometry(QtCore.QRect(388, 65, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.setLimitsButton.setFont(font)
        self.setLimitsButton.setObjectName("setLimitsButton")
        self.labelLimits = QtWidgets.QLabel(btCalibrate)
        self.labelLimits.setGeometry(QtCore.QRect(470, 69, 201, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelLimits.setFont(font)
        self.labelLimits.setObjectName("labelLimits")
        self.exportBox = QtWidgets.QComboBox(btCalibrate)
        self.exportBox.setGeometry(QtCore.QRect(680, 70, 151, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.exportBox.setFont(font)
        self.exportBox.setObjectName("exportBox")
        self.deleteDataButton = QtWidgets.QPushButton(btCalibrate)
        self.deleteDataButton.setGeometry(QtCore.QRect(90, 10, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.deleteDataButton.setFont(font)
        self.deleteDataButton.setObjectName("deleteDataButton")

        self.retranslateUi(btCalibrate)
        QtCore.QMetaObject.connectSlotsByName(btCalibrate)

    def retranslateUi(self, btCalibrate):
        _translate = QtCore.QCoreApplication.translate
        btCalibrate.setWindowTitle(_translate("btCalibrate", "Map Calibrator"))
        self.loadImageButton.setText(_translate("btCalibrate", "Load"))
        self.noImageLabel.setText(_translate("btCalibrate", "No Image Loaded"))
        self.loadDevicesButton.setText(_translate("btCalibrate", "Load"))
        self.clearDevicesButton.setText(_translate("btCalibrate", "Clear"))
        self.resetImageButton.setText(_translate("btCalibrate", "Clear"))
        self.label.setText(_translate("btCalibrate", "Map Image: "))
        self.label_2.setText(_translate("btCalibrate", "Devices: "))
        self.point1.setText(_translate("btCalibrate", "Point &1"))
        self.point2.setText(_translate("btCalibrate", "Point &2"))
        self.origin.setText(_translate("btCalibrate", "Ori&gin"))
        self.positive.setText(_translate("btCalibrate", "Posi&tive"))
        self.labelPoint1.setText(_translate("btCalibrate", "Point 1:"))
        self.labelPoint2.setText(_translate("btCalibrate", "Point 2:"))
        self.calibrateButton.setText(_translate("btCalibrate", "Calibrate"))
        self.resetDataButton.setText(_translate("btCalibrate", "Reset"))
        self.selectNoneButton.setText(_translate("btCalibrate", "None"))
        self.selectAllButton.setText(_translate("btCalibrate", "All"))
        self.readDataButton.setText(_translate("btCalibrate", "Add"))
        self.labelOrigin.setText(_translate("btCalibrate", "Origin:"))
        self.labelPositive.setText(_translate("btCalibrate", "Positive:"))
        self.labelParity.setText(_translate("btCalibrate", "Parity:"))
        self.saveParametersButton.setText(_translate("btCalibrate", "Save"))
        self.loadParametersButton.setText(_translate("btCalibrate", "Load"))
        self.label_3.setText(_translate("btCalibrate", "Parameters: "))
        self.exportButton.setText(_translate("btCalibrate", "Export"))
        self.setLimitsButton.setText(_translate("btCalibrate", "Set Limits"))
        self.labelLimits.setText(_translate("btCalibrate", "Limits:"))
        self.deleteDataButton.setText(_translate("btCalibrate", "Delete"))
