from PyQt5 import QtWidgets,QtCore

class btListWidget(QtWidgets.QListWidget):
    def __init__(self, parent):
        QtWidgets.QListWidget.__init__(self, parent)
        self.parent = parent

    def selectionChanged(self, selected, deselected):
        for item in selected.indexes():
            pos = item.data(QtCore.Qt.UserRole)[1]
            self.parent.parent().imageScene.highlightVisual(pos)
        for item in deselected.indexes():
            pos = item.data(QtCore.Qt.UserRole)[1]
            self.parent.parent().imageScene.dehighlightVisual(pos)

