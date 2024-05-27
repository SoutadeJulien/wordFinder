import os
from PySide2 import QtWidgets, QtCore

import constants
from wordFinder.utils import wordFinderUtils


class SunkenHSeparator(QtWidgets.QFrame):
    """A simple separator"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class SearchPathWindow(QtWidgets.QDialog):
    searchPathAdded = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._setupUi()
        self._connectUi()

    def _setupUi(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.buttonLayout = QtWidgets.QHBoxLayout()

        self.searchPathLineEdit = QtWidgets.QLineEdit()
        self.acceptButton = QtWidgets.QPushButton('Ok')
        self.cancelButton = QtWidgets.QPushButton('Cancel')

        self.mainLayout.addWidget(self.searchPathLineEdit)
        self.mainLayout.addLayout(self.buttonLayout)
        self.buttonLayout.addWidget(self.acceptButton)
        self.buttonLayout.addWidget(self.cancelButton)

        self.setWindowTitle("Add new search path")

    def _connectUi(self):
        self.acceptButton.clicked.connect(self.newPath)
        self.cancelButton.clicked.connect(self.reject)

    def newPath(self):
        newPath = self.searchPathLineEdit.text()
        if os.path.isdir(newPath):
            wordFinderUtils.addSearchPath(newPath)
            self.accept()
            self.searchPathAdded.emit(newPath)
            return self.searchPathLineEdit.text()


class CheckBox(QtWidgets.QCheckBox):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self.path = None

        self._state = False

        self.stateChanged.connect(self.state)

    def state(self):
        self._state = not self._state


class ModulesWidget(QtWidgets.QWidget):
    def __init__(self, searchPath, parent=None):
        super().__init__(parent)

        self.searchPath = searchPath
        self.allCheckBoxes = []

        self.mainLayout = QtWidgets.QGridLayout(self)

        self.addModules()

    def addModules(self):
        self.allCheckBoxes.clear()
        if self.mainLayout.count():
            for index in range(self.mainLayout.count()):
                item = self.mainLayout.itemAt(index)
                if item:
                    item.widget().deleteLater()


        row = 0
        column = 0

        if not self.modules():
            return

        for module in self.modules():
            checkBox = CheckBox(module)
            checkBox.path = os.path.join(self.searchPath, module)
            self.mainLayout.addWidget(checkBox, row, column)

            self.allCheckBoxes.append(checkBox)

            column += 1
            if column == 5:
                column = 0
                row += 1


    def modules(self):
        if not self.searchPath:
            return None

        for module in os.listdir(self.searchPath):
            yield module
