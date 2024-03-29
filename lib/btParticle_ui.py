# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../ui/btParticle.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_btParticle(object):
    def setupUi(self, btParticle):
        btParticle.setObjectName("btParticle")
        btParticle.resize(900, 720)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(btParticle.sizePolicy().hasHeightForWidth())
        btParticle.setSizePolicy(sizePolicy)
        btParticle.setMinimumSize(QtCore.QSize(900, 720))
        btParticle.setMaximumSize(QtCore.QSize(900, 720))
        self.loadImageButton = QtWidgets.QPushButton(btParticle)
        self.loadImageButton.setGeometry(QtCore.QRect(220, 10, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.loadImageButton.setFont(font)
        self.loadImageButton.setObjectName("loadImageButton")
        self.imageView = QtWidgets.QGraphicsView(btParticle)
        self.imageView.setGeometry(QtCore.QRect(190, 30, 701, 681))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageView.sizePolicy().hasHeightForWidth())
        self.imageView.setSizePolicy(sizePolicy)
        self.imageView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.imageView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.imageView.setObjectName("imageView")
        self.noImageLabel = QtWidgets.QLabel(btParticle)
        self.noImageLabel.setGeometry(QtCore.QRect(490, 280, 121, 20))
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
        self.resetImageButton = QtWidgets.QPushButton(btParticle)
        self.resetImageButton.setGeometry(QtCore.QRect(260, 10, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.resetImageButton.setFont(font)
        self.resetImageButton.setObjectName("resetImageButton")
        self.label = QtWidgets.QLabel(btParticle)
        self.label.setGeometry(QtCore.QRect(190, 12, 31, 16))
        self.label.setObjectName("label")
        self.resetDataButton = QtWidgets.QPushButton(btParticle)
        self.resetDataButton.setGeometry(QtCore.QRect(70, 10, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.resetDataButton.setFont(font)
        self.resetDataButton.setObjectName("resetDataButton")
        self.beaconsAvailable = QtWidgets.QListWidget(btParticle)
        self.beaconsAvailable.setGeometry(QtCore.QRect(10, 370, 171, 161))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(8)
        self.beaconsAvailable.setFont(font)
        self.beaconsAvailable.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.beaconsAvailable.setObjectName("beaconsAvailable")
        self.pointsAvailable = QtWidgets.QListWidget(btParticle)
        self.pointsAvailable.setGeometry(QtCore.QRect(10, 60, 171, 291))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(8)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.pointsAvailable.setFont(font)
        self.pointsAvailable.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.pointsAvailable.setObjectName("pointsAvailable")
        self.readDataButton = QtWidgets.QPushButton(btParticle)
        self.readDataButton.setGeometry(QtCore.QRect(10, 10, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.readDataButton.setFont(font)
        self.readDataButton.setObjectName("readDataButton")
        self.loadParametersButton = QtWidgets.QPushButton(btParticle)
        self.loadParametersButton.setGeometry(QtCore.QRect(400, 10, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.loadParametersButton.setFont(font)
        self.loadParametersButton.setObjectName("loadParametersButton")
        self.label_3 = QtWidgets.QLabel(btParticle)
        self.label_3.setGeometry(QtCore.QRect(320, 13, 81, 16))
        self.label_3.setObjectName("label_3")
        self.dataFile = QtWidgets.QLabel(btParticle)
        self.dataFile.setGeometry(QtCore.QRect(10, 40, 161, 16))
        self.dataFile.setObjectName("dataFile")
        self.buttonStart = QtWidgets.QPushButton(btParticle)
        self.buttonStart.setGeometry(QtCore.QRect(770, 10, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.buttonStart.setFont(font)
        self.buttonStart.setObjectName("buttonStart")
        self.buttonStop = QtWidgets.QPushButton(btParticle)
        self.buttonStop.setGeometry(QtCore.QRect(830, 10, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.buttonStop.setFont(font)
        self.buttonStop.setObjectName("buttonStop")
        self.collectDataShow = QtWidgets.QListWidget(btParticle)
        self.collectDataShow.setGeometry(QtCore.QRect(10, 560, 171, 141))
        font = QtGui.QFont()
        font.setFamily("Andale Mono")
        font.setPointSize(6)
        self.collectDataShow.setFont(font)
        self.collectDataShow.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.collectDataShow.setObjectName("collectDataShow")
        self.inputComboBox = QtWidgets.QComboBox(btParticle)
        self.inputComboBox.setGeometry(QtCore.QRect(581, 10, 191, 21))
        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        font.setPointSize(8)
        self.inputComboBox.setFont(font)
        self.inputComboBox.setObjectName("inputComboBox")
        self.dps = QtWidgets.QLabel(btParticle)
        self.dps.setGeometry(QtCore.QRect(10, 540, 161, 16))
        self.dps.setObjectName("dps")
        self.label_4 = QtWidgets.QLabel(btParticle)
        self.label_4.setGeometry(QtCore.QRect(460, 13, 51, 16))
        self.label_4.setObjectName("label_4")
        self.loadDevicesButton = QtWidgets.QPushButton(btParticle)
        self.loadDevicesButton.setGeometry(QtCore.QRect(510, 10, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.loadDevicesButton.setFont(font)
        self.loadDevicesButton.setObjectName("loadDevicesButton")

        self.retranslateUi(btParticle)
        QtCore.QMetaObject.connectSlotsByName(btParticle)

    def retranslateUi(self, btParticle):
        _translate = QtCore.QCoreApplication.translate
        btParticle.setWindowTitle(_translate("btParticle", "Particle Filter"))
        self.loadImageButton.setText(_translate("btParticle", "Load"))
        self.noImageLabel.setText(_translate("btParticle", "No Image Loaded"))
        self.resetImageButton.setText(_translate("btParticle", "Clear"))
        self.label.setText(_translate("btParticle", "Map:"))
        self.resetDataButton.setText(_translate("btParticle", "Reset"))
        self.readDataButton.setText(_translate("btParticle", "Add Files"))
        self.loadParametersButton.setText(_translate("btParticle", "Load"))
        self.label_3.setText(_translate("btParticle", "Parameters:"))
        self.dataFile.setText(_translate("btParticle", "File:"))
        self.buttonStart.setText(_translate("btParticle", "Start"))
        self.buttonStop.setText(_translate("btParticle", "Stop"))
        self.dps.setText(_translate("btParticle", "DPS:"))
        self.label_4.setText(_translate("btParticle", "Devices:"))
        self.loadDevicesButton.setText(_translate("btParticle", "Load"))

