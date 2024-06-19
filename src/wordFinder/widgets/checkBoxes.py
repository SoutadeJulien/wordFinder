import os
import logging
from typing import Mapping, Union, Any
from functools import partial

from PySide2 import QtCore, QtWidgets, QtGui

from wordFinder import constants


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(20)


class ModuleCheckBox(QtWidgets.QCheckBox):
    """This is a basic checkBox witch can be store a path, used for modules"""
    def __init__(self, text, path):
        super().__init__()

        self.path = path
        self.setText(text)


class AbstractPackageCheckBox(QtWidgets.QCheckBox):

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
        self.modules = {}

        self._connectUi()
        self.getModules(self.path)

        self.setStyleSheet(self.STYLESHEET)

    def _connectUi(self):
        self.onRightClick.connect(self.openModuleWindow)

    def enterEvent(self, event: QtCore.QEvent) -> None:
        self.setProperty('hover', True)
        self.style().polish(self)
        event.accept()

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        self.setProperty('hover', False)
        self.style().polish(self)
        event.accept()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() is QtCore.Qt.LeftButton:
            self.setChecked(not self.isChecked())
            event.accept()

        if event.button() is QtCore.Qt.RightButton:
            self.onRightClick.emit()
            event.accept()

    def minimumSizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(100, 25)

    def openModuleWindow(self) -> None:
        """Pops up a window to display the modules, then, copy the modules that have a check state into the :attr:`modules`"""
        globalPos = QtGui.QCursor.pos()

        # Reset the modules.
        self.getModules(self.path)

        self.moduleWindow = CheckBoxModulesWindow(self.modules)
        self.moduleWindow.move(globalPos)
        self.moduleWindow.show()

        # Copy the checked modules to update the list.
        self.modules = self.moduleWindow.activatedModules


class LocalPackageCheckBox(AbstractPackageCheckBox):

    def getModules(self, path: str) -> None:
        """Get the module within the provided path.

        Parameters:
            path: The path where to search the modules.
        """
        for module in os.listdir(path):
            modulePath = os.path.join(path, module)

            if os.path.isdir(modulePath) and module not in constants.EXCLUDED_DIRECTORIES:
                self.getModules(modulePath)

            if module.rpartition('.')[-1] == 'py' and module not in constants.EXCLUDED_MODULES:
                self.modules[module] = modulePath

        LOGGER.debug("Modules from PackageCheckBox: {}".format(self.modules))


class GitHubPackageCheckBox(AbstractPackageCheckBox):
    """This class handle the Git part."""
    def getModules(self, path: str) -> None:
        """Get the module within the provided path.

        Parameters:
            path: The path where to search the modules.

        Notes:
            WIP, this feature is not implemented yet.
        """
        ...


class CheckBoxModulesWindow(QtWidgets.QWidget):
    def __init__(self, innerModules: Mapping[Union[str, Any], Union[str, Any]], parent=None):
        """This is the window that pops when the user left-click on a packageCheckBox

        Parameters:
            innerModules: The modules to display.
        """
        super().__init__(parent=parent)

        self.innerModules = innerModules
        self.activatedModules = {}

        self._buildWindow()

    def _buildWindow(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        for module, modulePath in self.innerModules.items():
            newCheckBox = ModuleCheckBox(module, modulePath)
            self.activatedModules[module] = modulePath
            newCheckBox.setChecked(True)
            newCheckBox.stateChanged.connect(partial(self.updateActivatedModules, module, modulePath))
            self.mainLayout.addWidget(newCheckBox)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def updateActivatedModules(self, moduleName: str, modulePath: str, state: bool) -> None:
        """Updates the :attr:`activatedModules` depending on the state of the provided moduleName.

        Parameters:
            moduleName: The name of the module.
            modulePath: The path of the module.
            state: if true, the module will be appended to the :attr:`activatedModules`, otherwise, this module will be removed.
        """
        if state:
            self.activatedModules[moduleName] = modulePath
            return

        self.activatedModules.pop(moduleName)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """Unchecks the moduleCheckBox under the cursor."""
        mousePov = event.pos()
        if self.childAt(mousePov):
            self.childAt(mousePov).setChecked(False)

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        """Delete the window when the user move the cursor outside this window."""
        self.deleteLater()
