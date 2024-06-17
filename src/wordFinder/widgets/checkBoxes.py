import os
import logging
from typing import Optional, List, Mapping
from functools import partial

from PySide2 import QtCore, QtWidgets, QtGui

from wordFinder import constants

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(20)


class ModuleCheckBox(QtWidgets.QCheckBox):
    def __init__(self, text, path):
        super().__init__()

        self.path = path
        self.setText(text)


class CheckBox(QtWidgets.QCheckBox):
    """A checkbox with a path attribute where to store the module path."""

    onRightClick = QtCore.Signal()

    STYLESHEET = \
        """
        QCheckBox {
            background-color: #565656;
            spacing: 10px;
            padding: 8px;
            color: white;
            border: 0px hidden, black;
            border-radius: 5
        }
        QCheckBox[hover=true] {
            spacing: 10px;
            padding: 7px;
            border: 1px ridge #5e5e5c;
        }
        """

    def __init__(self, text: str, path, parent=None):
        super().__init__(text, parent)

        self.path = path
        self.modules = []

        self._connectUi()
        self.getModules(self.path)
        print(self.modules)

        self.setStyleSheet(self.STYLESHEET)

    def _connectUi(self):
        self.onRightClick.connect(self.openModuleWindow)

    def getModules(self, path):
        for item in os.listdir(path):
            itemPath = os.path.join(self.path, item)

            if os.path.isdir(itemPath):
                if item not in constants.EXCLUDED_DIRECTORIES:
                    self.getModules(itemPath)

            if item.partition('.')[-1] == 'py' and item not in constants.EXCLUDED_MODULES:
                self.modules.append(itemPath)

    def enterEvent(self, event):
        self.setProperty('hover', True)
        self.style().polish(self)
        event.accept()

    def leaveEvent(self, event):
        self.setProperty('hover', False)
        self.style().polish(self)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() is QtCore.Qt.LeftButton:
            self.setChecked(not self.isChecked())
            event.accept()

        if event.button() is QtCore.Qt.RightButton:
            self.onRightClick.emit()
            event.accept()

    def minimumSizeHint(self):
        return QtCore.QSize(100, 25)

    def openModuleWindow(self):
        globalPos = QtGui.QCursor.pos()
        self.moduleWindow = CheckBoxModulesWindow(self.path)
        self.moduleWindow.move(globalPos)
        self.moduleWindow.show()
        self.modules = self.moduleWindow.modulesPaths


class CheckBoxModulesWindow(QtWidgets.QWidget):
    STYLESHEET = \
    """
    {
    background-color: rgb(70, 70, 70);
    margin: 1em;
    padding: 1em;
    }
    """
    def __init__(self, modulePath, parent=None):
        super().__init__(parent=parent)

        self.modulePath = modulePath
        self.modulesPaths = []

        self._buildWindow()

    def _buildWindow(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.getModule(self.modulePath)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def getModule(self, path):
        self.modulesPaths.clear()

        for item in os.listdir(path):
            itemPath = os.path.join(path, item)

            if os.path.isdir(itemPath):
                if item not in constants.EXCLUDED_DIRECTORIES:
                    self.getModule(itemPath)

            if item.partition('.')[-1] == 'py' and item not in constants.EXCLUDED_MODULES:
                newCheckBox = ModuleCheckBox(item, itemPath)
                newCheckBox.path = itemPath
                newCheckBox.setChecked(True)

                self.mainLayout.addWidget(newCheckBox)
                self.modulesPaths.append(itemPath)
                newCheckBox.clicked.connect(partial(self.updateModuleList, newCheckBox))

    def updateModuleList(self, module):
        if module.isChecked():
            self.modulesPaths.append(module.path)
            return

        self.modulesPaths.remove(module.path)

    def leaveEvent(self, event):
        self.deleteLater()
