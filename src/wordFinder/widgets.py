import os
from PySide2 import QtWidgets, QtCore
from typing import Optional, List, Tuple

import core
from constants import COLUMN_COUNT
from wordFinder.utils import wordFinderUtils
from wordFinder import constants


class SunkenHSeparator(QtWidgets.QFrame):
    """A basic separator"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        self.setLineWidth(1)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setStyleSheet("background-color: #5e5e5c;")


class PushButton(QtWidgets.QPushButton):

    STYLESHEET = \
    """
    PushButton  {
        background-color: #525050;
        color: #ededed;
        border-style: ridge ;
        border-color: rgb(93, 93, 93);
        border-width: 1px;
        border-radius: 5px;
    }
    PushButton:hover {
        background-color: #707070;
    }
    PushButton:pressed {
        background-color:#828282;
    }
    """
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet(self.STYLESHEET)
        
    def minimumSizeHint(self):
        return QtCore.QSize(200, 30)


class ModuleLayoutWindow(QtWidgets.QDialog):
    """This widget is responsible for the layout management of the modules"""
    def __init__(self, parent=None):
        super().__init__(parent)

        self._buildWindow()
        self._setupWindow()
        self._connectWindow()

    def _buildWindow(self) -> None:
        self.mainLayout = QtWidgets.QGridLayout(self)

        self.columnsLabel = QtWidgets.QLabel('Columns')
        self.columnCount = QtWidgets.QLabel()
        self.columnsSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        self.okButton = QtWidgets.PushButton('Ok')
        self.cancelButton = QtWidgets.PushButton('Cancel')

    def _setupWindow(self) -> None:
        self.mainLayout.addWidget(self.columnsLabel, 0, 0)
        self.mainLayout.addWidget(self.columnsSlider, 1, 0)
        self.mainLayout.addWidget(self.columnCount, 1, 1)
        self.mainLayout.addWidget(self.okButton, 4, 0)
        self.mainLayout.addWidget(self.cancelButton, 4, 1)

        self.columnsSlider.setMinimum(1)
        self.columnsSlider.setMaximum(10)
        self.columnsSlider.setValue(5)
        self.columnCount.setText('5')

    def _connectWindow(self) -> None:
        self.columnsSlider.valueChanged.connect(self.getColumnSliderValue)
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

    @wordFinderUtils.storeConfig(COLUMN_COUNT)
    def getColumnSliderValue(self, *args) -> int:
        """Gets the value of the :attr:`columnsSlider` and sets it to the :attr:`columnCount`.

        Returns:
            The :attr:`columnsSlider`'s value.
        """
        columnCount = self.columnsSlider.value()
        self.columnCount.setText(str(columnCount))

        return columnCount


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
        self.acceptButton = QtWidgets.PushButton('Ok')
        self.cancelButton = QtWidgets.PushButton('Cancel')

        self.mainLayout.addWidget(self.searchPathLineEdit)
        self.mainLayout.addLayout(self.buttonLayout)
        self.buttonLayout.addWidget(self.acceptButton)
        self.buttonLayout.addWidget(self.cancelButton)

        self.setWindowTitle("Add new search path")

    def _connectUi(self):
        self.acceptButton.clicked.connect(self.newPath)
        self.cancelButton.clicked.connect(self.reject)

    @wordFinderUtils.storeConfig(constants.SEARCH_PATH)
    def newPath(self) -> str:
        """Gets if the path wrote in the LineEdit is valid, then, adds the new search path in the config.json.

        Returns:
            The path wrote by the user.
        """
        newPath = self.searchPathLineEdit.text()
        if os.path.isdir(newPath):
            self.accept()

            # Emit signal to refresh the ui.
            self.searchPathAdded.emit(newPath)

            # Reset the checked modules list.
            core.storeConfig(constants.CHECKED_MODULES, None)

            return self.searchPathLineEdit.text()


class CheckBox(QtWidgets.QCheckBox):
    """A checkbox with a path attribute where to store the module path."""

    STYLESHEET = \
    """
    QCheckBox {
        spacing: 15px;
        padding: 12px;
        color: white;
        border: 0px hidden, black;
        border-radius: 5
    }
    QCheckBox[hover=true] {
        spacing: 15px;
        padding: 11px;
        border: 1px ridge #5e5e5c;
    }
    """

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)

        self.path = None

        self.setStyleSheet(self.STYLESHEET)

    def enterEvent(self, event):
        self.setProperty('hover', True)
        self.style().polish(self)
        event.accept()

    def leaveEvent(self, event):
        self.setProperty('hover', False)
        self.style().polish(self)
        event.accept()

    def mousePressEvent(self, event):
        self.setChecked(not self.isChecked())
        event.accept()

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
        self.checkedCheckBoxes = []

        self.mainLayout = QtWidgets.QGridLayout(self)
        self.mainLayout.setSpacing(8)

        self.addModules()

    def addModules(self) -> Optional[List[str]]:
        """Adds the modules within the :attr:`searchPath` to the main layout."""
        self.clearLayout()

        columnMax = core.getConfigValueByName(COLUMN_COUNT)
        row = 0
        column = 0

        if not self.modules():
            return

        for module in self.modules():
            checkBox = CheckBox(module)
            checkBox.path = os.path.join(self.searchPath, module)

            # Check the checkBox if it's previously checked.
            if self.isCheckBoxPreviouslyChecked(checkBox):
                checkBox.setChecked(True)

            self.mainLayout.addWidget(checkBox, row, column)
            self.allCheckBoxes.append(checkBox)

            column += 1
            if column == columnMax:
                column = 0
                row += 1

    @staticmethod
    def isCheckBoxPreviouslyChecked(checkBox: QtWidgets.QCheckBox) -> bool:
        """Gets if the provided checkBox is present in the config file, if it is, sets it to checked.

        Parameters:
            checkBox: The checkBox to search.

        Returns:
            True if the checkBox is present in the config file, else False.
        """
        checkedBoxes = core.getConfigValueByName(constants.CHECKED_MODULES)

        if not checkedBoxes:
            return False

        if checkBox.text() in checkedBoxes:
            return True


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
            if os.path.isdir(os.path.join(self.searchPath, module)) and module not in constants.EXCLUDED_MODULES:
                yield module
