import os
from PySide2 import QtWidgets, QtCore
from typing import Optional

import constants
from wordFinder.utils import wordFinderUtils


class SunkenHSeparator(QtWidgets.QFrame):
    """A simple separator"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class SearchPathWindow(QtWidgets.QDialog):
    """A simple window with a QLineEdit where to write a path."""
    searchPathAdded = QtCore.Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._setupUi()
        self._connectUi()

    def _setupUi(self) -> None:
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

    def newPath(self) -> None:
        """Gets if the path wrote in the LineEdit is valid, then, adds the new search path in the config.json.

        Returns:
            The path wrote by the user.
        """
        newPath = self.searchPathLineEdit.text()
        if os.path.isdir(newPath):
            wordFinderUtils.addSearchPath(newPath)
            self.accept()

            # Emit signal to refresh the ui.
            self.searchPathAdded.emit(newPath)

            return self.searchPathLineEdit.text()


class CheckBox(QtWidgets.QCheckBox):
    """A checkbox with a path attribute where to store the module path."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)

        self.path = None


class ModulesWidget(QtWidgets.QWidget):
    """This widget manages the modules to read."""
    def __init__(self, searchPath: str, parent: Optional[QtWidgets.QWidget]=None):
        """ModulesWidget initialisation.

        Parameters:
            searchPath, the path where to retrieve the modules.
            parent: The parent widget.
        """
        super().__init__(parent)

        self.searchPath = searchPath
        self.allCheckBoxes = []

        self.mainLayout = QtWidgets.QGridLayout(self)

        self.addModules()

    def addModules(self) -> None:
        """Adds the modules within the :attr:`searchPath` to the main layout."""
        self.clearLayout()

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

    def clearLayout(self) -> None:
        """Clears the main layout."""
        self.allCheckBoxes.clear()
        if self.mainLayout.count():
            for index in range(self.mainLayout.count()):
                item = self.mainLayout.itemAt(index)
                if item:
                    item.widget().deleteLater()

    def modules(self) -> str:
        """Yields the module name within the :attr:`searchPath` folder."""
        if not self.searchPath:
            return None

        for module in os.listdir(self.searchPath):
            yield module
