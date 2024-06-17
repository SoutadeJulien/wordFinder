import os
import logging
from typing import Optional, List, Mapping, Iterable, Any

from PySide2 import QtCore, QtWidgets, QtGui

import core
from wordFinder.widgets import checkBoxes
from constants import COLUMN_COUNT
from wordFinder.utils import wordFinderUtils
from wordFinder.utils import sentenceProcess
from wordFinder import constants

from wordFinder.gitHub import auth


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(20)


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
        return QtCore.QSize(200, 25)


class OutputWidget(QtWidgets.QPlainTextEdit):

    STYLESHEET = \
        """
        background-color: rgb(60, 60, 60);
        """

    def __init__(self):
        super().__init__()
        self.setStyleSheet(self.STYLESHEET)

    def minimumSizeHint(self):
        return QtCore.QSize(300, 350)


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

        self.okButton = PushButton('Ok')
        self.cancelButton = PushButton('Cancel')

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
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._setupUi()
        self._connectUi()

    def _setupUi(self) -> None:
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.buttonLayout = QtWidgets.QHBoxLayout()

        self.searchPathLineEdit = QtWidgets.QLineEdit()
        self.acceptButton = PushButton('Ok')
        self.cancelButton = PushButton('Cancel')

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

            # Reset the checked modules list.
            core.storeConfig(constants.LOCAL_CHECKED_MODULES, None)

            return newPath


class GitHubWindow(QtWidgets.QDialog):
    """A simple window with a QLineEdit where to write a path."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._setupUi()
        self._connectUi()

    def _setupUi(self) -> None:
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.buttonLayout = QtWidgets.QHBoxLayout()

        self.tokenLineEdit = QtWidgets.QLineEdit()
        self.acceptButton = PushButton('Ok')
        self.cancelButton = PushButton('Cancel')

        self.mainLayout.addWidget(self.tokenLineEdit)
        self.mainLayout.addLayout(self.buttonLayout)
        self.buttonLayout.addWidget(self.acceptButton)
        self.buttonLayout.addWidget(self.cancelButton)

        self.setWindowTitle("Add new search path")

    def _connectUi(self):
        self.acceptButton.clicked.connect(self.gitHubToken)
        self.cancelButton.clicked.connect(self.reject)

    @wordFinderUtils.storeConfig(constants.GIT_HUB_HEY)
    def gitHubToken(self):
        token = self.tokenLineEdit.text()
        self.accept()

        return token


class AbstractModuleWidget(QtWidgets.QWidget):

    STYLESHEET = \
    """
    QWidget {
        background-color: #454545;
        spacing: 2px;
    }
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget]=None):
        super().__init__(parent)

        self._searchPath = None

        self.allCheckBoxes = []
        self.checkedCheckBoxes = []

        self._buildUi()
        self._setupUi()
        self._connectUi()

        self.setStyleSheet(self.STYLESHEET)

    def _buildUi(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.moduleLayout = QtWidgets.QGridLayout()

        self.checkAllLayout = QtWidgets.QHBoxLayout()
        self.modulesWidgets = QtWidgets.QWidget()

        self.output = OutputWidget()

        self.checkAllButton = PushButton("Check all")
        self.uncheckAllButton = PushButton("Uncheck all")

    def _setupUi(self):
        self.mainLayout.addLayout(self.moduleLayout)
        self.moduleLayout.addWidget(self.modulesWidgets)

        self.mainLayout.addLayout(self.checkAllLayout)
        self.checkAllLayout.addWidget(self.checkAllButton)
        self.checkAllLayout.addWidget(self.uncheckAllButton)

        self.mainLayout.addWidget(self.output)

        self.checkAllLayout.addStretch()

        self.checkAllButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.uncheckAllButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.output.setFont(QtGui.QFont('Arial', 13))
        self.output.setReadOnly(True)

    def _connectUi(self):
        self.checkAllButton.clicked.connect(self.checkAllCheckBoxes)
        self.uncheckAllButton.clicked.connect(self.unCheckAllCheckBoxes)

    @property
    def searchPath(self):
        return self._searchPath

    @searchPath.setter
    def searchPath(self, newPath):
        if newPath and os.path.isdir(newPath):
            self._searchPath = newPath

    def addModules(self) -> Optional[List[str]]:
        columnMax = core.getConfigValueByName(COLUMN_COUNT)
        row = 0
        column = 0

        if not self.modules():
            return

        for module in self.modules():
            checkBox = checkBoxes.CheckBox(module, os.path.join(self.searchPath, module))

            # Check the checkBox if it's previously checked.
            if self.isCheckBoxPreviouslyChecked(checkBox):
                checkBox.setChecked(True)

            self.moduleLayout.addWidget(checkBox, row, column)
            self.allCheckBoxes.append(checkBox)

            column += 1
            if column == columnMax:
                column = 0
                row += 1

    def clearLayout(self) -> None:
        """Clears the main layout."""
        self.allCheckBoxes.clear()

        if self.moduleLayout.count():
            for index in range(self.moduleLayout.count()):
                item = self.moduleLayout.itemAt(index)
                if item is not None:
                    item.widget().deleteLater()

    @property
    def filteredModules(self) -> Iterable[Any]:
        """Filters the checked checkBoxes.

        Returns:
            A dictionary containing each checked module's names as key and they path as value.
        """
        allModules = []

        for checkBox in self.allCheckBoxes:
            if not checkBox.isChecked():
                continue

            allModules.append(checkBox)

        return allModules

class LocalModuleWidget(AbstractModuleWidget):

    @staticmethod
    def isCheckBoxPreviouslyChecked(checkBox: QtWidgets.QCheckBox) -> bool:
        """Gets if the provided checkBox is present in the config file, if it is, sets it to checked.

        Parameters:
            checkBox: The checkBox to search.

        Returns:
            True if the checkBox is present in the config file, else False.
        """
        checkedBoxes = core.getConfigValueByName(constants.LOCAL_CHECKED_MODULES)

        if not checkedBoxes:
            return False

        if checkBox.text() in checkedBoxes:
            return True

    def modules(self) -> str:
        """Yields the module name within the :attr:`searchPath` folder."""
        if not self._searchPath:
            return None

        for module in os.listdir(self._searchPath):
            if os.path.isdir(os.path.join(self._searchPath, module)) and module not in constants.EXCLUDED_MODULES:
                yield module

    @wordFinderUtils.devMode(wordFinderUtils.timed)
    def searchWordInLocal(self, word, showComment, showContext, isLiteral, useSyntaxColor, numberOfExtraLine) -> None:
        """Search the typed word or sentence in the checked modules."""
        self.output.clear()

        modulesWithPrints = []

        for checkBox in self.filteredModules:
            for modulePath in checkBox.modules:
                print(modulePath)
                try:
                    with open(modulePath, 'r', encoding='utf-8') as reader:
                        lines = reader.readlines()
                        for lineNumber, line in enumerate(lines, start=1):
                            # Show the comment characters.
                            if showComment:
                                if sentenceProcess.wordInLine(word, line, isLiteral):
                                    modulesWithPrints.append(modulePath)

                                    if showContext:
                                        self.displayPreviousLines(numberOfExtraLine, modulePath, lineNumber)

                                    # Colorize the line dependent on the syntax.
                                    colorizedLine = core.colorizeLine(line, word) if useSyntaxColor else line

                                    self.output.appendHtml("<font color=#5de856>{}</font> <span>&#8594;</span> <font color=#dae63e>line {}</font> <span>&#8594;</span> {}".format(' <span>&#8594;</span> '.join(modulePath.split(os.sep)[-3:]), lineNumber, colorizedLine))

                                    if showContext:
                                        self.displayNextLines(numberOfExtraLine, modulePath, lineNumber)

                            # Don't show the comment characters.
                            else:
                                if self.wordInLine(word, line, self.literalCheckBox.isChecked()):
                                    if sentenceProcess.isLineValid(line):
                                        modulesWithPrints.append(modulePath)

                                        if showContext:
                                            self.displayPreviousLines(numberOfExtraLine, modulePath, lineNumber)

                                        # Colorize the line dependent on the syntax.
                                        colorizedLine = core.colorizeLine(line, word) if self.syntaxAction.isChecked() else line

                                        self.output.appendHtml("<font color=#5de856>{}</font> <span>&#8594;</span> <font color=#dae63e>line {}</font> <span>&#8594;</span> {}".format(' <span>&#8594;</span> '.join(modulePath.split(os.sep)[-3:]), lineNumber, colorizedLine))

                                        if showContext:
                                            self.displayNextLines(numberOfExtraLine, modulePath, lineNumber)

                except PermissionError:
                    LOGGER.debug("Permission denied for {}".format(modulePath))

        if not modulesWithPrints:
            self.output.appendPlainText('The word [{}] is not found'.format(word))


    def displayPreviousLines(self, numberOfExtraLine, modulePath: str, lineNumber: int) -> None:
        """Opens the provided module to find the x lines before the provided line and appends them to the :var:`self.outPut` window.

        Parameters:
            modulePath: The module path.
            lineNumber: The line that contains the word to search.
        """
        with open(modulePath, 'r', encoding='utf-8') as readFile:
            lines = readFile.readlines()
            index = int(numberOfExtraLine)

            for number, line in enumerate(lines, start=1):
                if number == lineNumber - index:
                    self.output.appendHtml("<font color='grey'>{}</font> <span>&#8594;</span> <font color='grey'>line {}</font> <span>&#8594;</span> <font color' -> ''>{}</font>".format(" <span>&#8594;</span> ".join(modulePath.split(os.sep)[-3:]), number, line))
                    index -= 1

                    if index == 0:
                        break

    def displayNextLines(self, numberOfExtraLine, modulePath: str, lineNumber: int) -> None:
        """Same method as :meth:`displayPreviousLines` but this will append the next x lines after the provided line.

        Parameters:
            modulePath: The module path.
            lineNumber: The line that contains the word to search.
        """
        with open(modulePath, 'r', encoding='utf-8') as readFile:
            lines = readFile.readlines()
            index = 1

            for number, line in enumerate(lines, start=1):
                if number == lineNumber + index:
                    self.output.appendHtml("<font color='grey'>{}</font> <span>&#8594;</span> <font color='grey'>line {}</font> <span>&#8594;</span> <font color' -> ''>{}</font>".format(" <span>&#8594;</span> ".join(modulePath.split(os.sep)[-3:]), number, line))
                    index += 1

                    if index == int(numberOfExtraLine) + 1:
                        self.output.appendHtml('')
                        break



    @wordFinderUtils.storeConfig(constants.LOCAL_CHECKED_MODULES)
    def checkAllCheckBoxes(self):
        for checkBox in self.allCheckBoxes:
            checkBox.setChecked(True)

    @wordFinderUtils.storeConfig(constants.LOCAL_CHECKED_MODULES)
    def unCheckAllCheckBoxes(self):
        for checkBox in self.allCheckBoxes:
            checkBox.setChecked(False)

class GitHubModuleWidget(AbstractModuleWidget):

    @staticmethod
    def isCheckBoxPreviouslyChecked(checkBox: QtWidgets.QCheckBox) -> bool:
        """Gets if the provided checkBox is present in the config file, if it is, sets it to checked.

        Parameters:
            checkBox: The checkBox to search.

        Returns:
            True if the checkBox is present in the config file, else False.
        """
        checkedBoxes = core.getConfigValueByName(constants.GIT_HUB_CHECKED_MODULES)

        if not checkedBoxes:
            return False

        if checkBox.text() in checkedBoxes:
            return True


    @wordFinderUtils.storeConfig(constants.GIT_HUB_CHECKED_MODULES)
    def checkAllCheckBoxes(self):
        for checkBox in self.allCheckBoxes:
            checkBox.setChecked(True)

    @wordFinderUtils.storeConfig(constants.GIT_HUB_CHECKED_MODULES)
    def unCheckAllCheckBoxes(self):
        for checkBox in self.allCheckBoxes:
            checkBox.setChecked(False)


class StackModulesWidget(QtWidgets.QTabWidget):
    """This widget manages the modules to read."""
    def __init__(self, searchPath: str, parent: Optional[QtWidgets.QWidget]=None):
        """ModulesWidget initialisation.

        Parameters:
            searchPath, the path where to retrieve the modules.
            parent: The parent widget.
        """
        super().__init__(parent)

        self.searchPath = searchPath

        self._buildWidget()

    def _buildWidget(self):
        self.localWidget = LocalModuleWidget()
        self.githubWidget = GitHubModuleWidget()

        self.localTab = self.addTab(self.localWidget, 'Local')
        self.githubTab = self.addTab(self.githubWidget, 'Github')

    def setModulesWidgetSearchPath(self, path):
        self.localWidget.searchPath = path
        self.githubWidget.searchPath = path

    def addLocalModules(self):
        """Adds the modules within the :attr:`searchPath` to the main layout."""
        self.localWidget.clearLayout()
        self.localWidget.addModules()

    def addGitHubModules(self):
        gitHubToken = core.getConfigValueByName(constants.GIT_HUB_HEY)

        if gitHubToken:
            self.githubWidget.addModules([repo.full_name for repo in auth.gitHubRepositories()])

    @property
    def allLocalCheckBoxes(self):
        return self.localWidget.allCheckBoxes

    @property
    def allGitHubCheckBoxes(self):
        return self.githubWidget.allCheckBoxes

    def searchWordInLocal(self, word, showComment, showContext, isLiteral, useSyntaxColor, numberOfExtraLine):
        self.localWidget.searchWordInLocal(word, showComment, showContext, isLiteral, useSyntaxColor, numberOfExtraLine)

    def searchWordInGit(self, word, showComment, showContext, isLitteral, useSyntaxColor, numberOfExtraLine):
        self.githubWidget.searchWordInGit(word, showComment, showContext, isLiteral, useSyntaxColor, numberOfExtraLine)
