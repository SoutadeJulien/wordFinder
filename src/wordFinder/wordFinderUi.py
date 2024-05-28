import os
import logging
from PySide2 import QtWidgets, QtCore, QtGui
from typing import Mapping

import constants
import widgets
from utils import wordFinderUtils
from wordFinder import resources


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(20)
logging.basicConfig(filename='./utils/wordFinder.log', level=logging.INFO)


class WordFinder(QtWidgets.QDialog):
    """Main ui class."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.searchPath = wordFinderUtils.searchPath()

        self._buildUi()
        self._setupUi()
        self._connectUi()

    def _buildUi(self) -> None:
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.devModeLayout = QtWidgets.QHBoxLayout()
        self.searchPathLayout = QtWidgets.QHBoxLayout()
        self.checkButtonLayout = QtWidgets.QGridLayout()
        self.optionLayout = QtWidgets.QHBoxLayout()

        self.menuBar = QtWidgets.QMenuBar()

        self.searchPathLabel = QtWidgets.QLabel()
        self.moduleToCheckLabel = QtWidgets.QLabel("Modules to check")
        self.modulesWidget = widgets.ModulesWidget(self.searchPath)
        self.devModeCheckBox = QtWidgets.QCheckBox("Dev mode")
        self.showCommentCheckBox = QtWidgets.QCheckBox("Show comments")
        self.showContextCheckBox = QtWidgets.QCheckBox("Show context")
        self.contextNumberComboBox = QtWidgets.QComboBox()
        self.checkButton = QtWidgets.QPushButton('check')
        self.wordToSearch = QtWidgets.QLineEdit()
        self.output = QtWidgets.QPlainTextEdit()
        self.setSearchPathButton = QtWidgets.QPushButton("Change search path")
        self.checkAllButton = QtWidgets.QPushButton("Check all")
        self.uncheckAllButton = QtWidgets.QPushButton("Uncheck all")
        self.separatorOne = widgets.SunkenHSeparator()
        self.separatorTwo = widgets.SunkenHSeparator()

    def _setupUi(self) -> None:
        self.mainLayout.addWidget(self.menuBar)
        self.mainLayout.addLayout(self.devModeLayout)
        self.devModeLayout.addWidget(self.devModeCheckBox)
        self.mainLayout.addLayout(self.searchPathLayout)
        self.searchPathLayout.addWidget(self.setSearchPathButton)
        self.searchPathLayout.addWidget(self.searchPathLabel)
        self.mainLayout.addWidget(self.separatorOne)
        self.mainLayout.addLayout(self.checkButtonLayout)
        self.checkButtonLayout.addWidget(self.checkAllButton, 0, 0)
        self.checkButtonLayout.addWidget(self.uncheckAllButton, 0, 1)
        self.mainLayout.addLayout(self.optionLayout)
        self.optionLayout.addWidget(self.showCommentCheckBox)
        self.optionLayout.addWidget(self.showContextCheckBox)
        self.optionLayout.addWidget(self.contextNumberComboBox)
        self.mainLayout.addWidget(self.separatorTwo)
        self.mainLayout.addWidget(self.moduleToCheckLabel)
        self.mainLayout.addWidget(self.modulesWidget)
        self.mainLayout.addWidget(self.wordToSearch)
        self.mainLayout.addWidget(self.output)
        self.mainLayout.addWidget(self.checkButton)

        self.devModeLayout.insertStretch(0)
        self.optionLayout.addStretch()
        self.searchPathLayout.addStretch()

        self.uiSetup = self.menuBar.addMenu('Options')
        self.devModeAction = self.uiSetup.addAction('Dev mode')
        self.devModeAction.setData(False)
        self.layoutAction = self.uiSetup.addAction('Layout')

        self.showCommentCheckBox.setChecked(True)
        self.searchPathLabel.setText("Search path: {}".format(self.searchPath))
        self.moduleToCheckLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.setSearchPathButton.setFixedWidth(100)
        self.wordToSearch.setPlaceholderText('Search')
        self.output.setFont(QtGui.QFont('Arial', 13))
        self.output.setReadOnly(True)

        self.contextNumberComboBox.setFixedWidth(60)
        
        # Add numbers to context number comboBox.
        for i in range(1, 10):
            self.contextNumberComboBox.addItem(str(i))
        self.contextNumberComboBox.setCurrentIndex(3)

        # Window.
        self.resize(1300, 800)
        self.setWindowTitle("Word finder")
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)

    def _connectUi(self) -> None:
        self.devModeAction.triggered.connect(self._devMode)
        self.layoutAction.triggered.connect(self.onLayoutActionTriggered)
        self.setSearchPathButton.clicked.connect(self.setSearchPath)
        self.checkButton.clicked.connect(self.searchWord)
        self.checkAllButton.clicked.connect(self.checkAllCheckBoxes)
        self.uncheckAllButton.clicked.connect(self.uncheckAllCheckBoxes)

    def _devMode(self) -> None:
        """This method handle the dev mode.

        Basically, the dev mode will activate the @wordFinderUtils.devMode decorator and set to DEBUG the :const:LOGGER logger.
        """
        wordFinderUtils.DEV_MODE = not self.devModeAction.data()

        if wordFinderUtils.DEV_MODE:
            self.devModeAction.setIcon(QtGui.QIcon("wfIcons:check.png"))
            LOGGER.setLevel(10)
        else:
            self.devModeAction.setIcon(QtGui.QIcon(""))
            LOGGER.setLevel(20)

        self.devModeAction.setData(wordFinderUtils.DEV_MODE)

        LOGGER.debug("Dev mode: {}".format(wordFinderUtils.DEV_MODE))

    def onLayoutActionTriggered(self) -> None:
        """Opens a window to manage the module's layout."""
        layoutWindow = widgets.ModuleLayoutWindow(self)
        layoutWindow.exec_()
        self.modulesWidget.addModules(layoutWindow.getColumnSliderValue())

    def setSearchPath(self) -> None:
        """Opens a new window to let the user write the path where to query the modules."""
        pathWindow = widgets.SearchPathWindow()
        pathWindow.searchPathAdded.connect(self.refreshModules)
        pathWindow.exec_()
        self.searchPath = pathWindow.newPath()

        LOGGER.debug("Search path: {}".format(self.searchPath))

    def refreshModules(self, modulePath: str) -> None:
        """Reset the module path in the module widget and this class, adds the new module's checkBoxes to this window.

        Parameters:
            modulePath: The new module path where to get the modules.
        """
        self.modulesWidget.searchPath = modulePath
        self.searchPath = modulePath
        self.searchPathLabel.setText("Search path: {}".format(self.searchPath))
        self.modulesWidget.addModules(5)
        
    def checkAllCheckBoxes(self) -> None:
        """Checks all checkBoxes"""
        LOGGER.debug("All checkboxes from module widget: {}".format(self.modulesWidget.allCheckBoxes))

        for checkBox in self.modulesWidget.allCheckBoxes:
            checkBox.setChecked(True)

    def uncheckAllCheckBoxes(self) -> None:
        """Unchecks all checkBoxes"""
        for checkBox in self.modulesWidget.allCheckBoxes:
            checkBox.setChecked(False)

    @wordFinderUtils.devMode(wordFinderUtils.timed)
    def searchWord(self) -> None:
        """Search the typed word or sentence in the checked modules."""
        self.output.clear()

        word = self.wordToSearch.text()
        modulesWithPrints = []

        for module, modulePath in self.filteredModules.items():
            with open(modulePath, 'r', encoding='utf-8') as reader:
                lines = reader.readlines()
                for lineNumber, line in enumerate(lines, start=1):
                    # Show the comment characters.
                    if self.showCommentCheckBox.isChecked():
                        if word in line:
                            modulesWithPrints.append(module)

                            if self.showContextCheckBox.isChecked():
                                self.displayPreviousLines(modulePath, lineNumber)

                            self.output.appendHtml("<font color='green'>{}</font> <span>&#8594;</span> <font color='yellow'>line {}</font> <span>&#8594;</span> <font color='white'>{}</font>".format(module, lineNumber, line))

                            if self.showContextCheckBox.isChecked():
                                self.displayNextLines(modulePath, lineNumber)

                    # Don't show the comment characters.
                    else:
                        if word in line:
                            if self.isLineValid(line):
                                modulesWithPrints.append(module)

                                if self.showContextCheckBox.isChecked():
                                    self.displayPreviousLines(modulePath, lineNumber)

                                self.output.appendHtml("<font color='green'>{}</font> <span>&#8594;</span> <font color='yellow'>line {}</font> <span>&#8594;</span> <font color='white'>{}</font>".format(module, lineNumber, line))

                                if self.showContextCheckBox.isChecked():
                                    self.displayNextLines(modulePath, lineNumber)

        if not modulesWithPrints:
            self.output.appendPlainText('The word [{}] is not found'.format(word))

    @staticmethod
    def isLineValid(line: str) -> bool:
        """Checks if the provided word or sentence contains an excluded character.

        Returns:
            True if the :param:`line` does not contain any excluded characters, else, False.
        """
        for char in constants.EXCLUDED_CHARACTERS:
            if char in line:
                return False
        return True

    @property
    def filteredModules(self) -> Mapping[str, str]:
        """Filters the checked checkBoxes.

        Returns:
            A dictionary containing each checked module's names as key and they path as value.
        """
        allModules = {}

        for checkBox in self.modulesWidget.allCheckBoxes:
            if not checkBox.isChecked():
                continue

            if os.path.isfile(checkBox.path):
                if os.path.splitext(checkBox.path)[-1] == '.py':
                    allModules[checkBox.path.split(os.sep)[-1]] = checkBox.path

            for root, dirs, files in os.walk(checkBox.path):
                for directory in dirs:
                    if directory in constants.EXCLUDED_DIRECTORIES:
                        continue

                    for file in files:
                        if os.path.splitext(file)[-1] == '.py':
                            allModules[file] = os.path.join(root, file)

        LOGGER.debug("Checked modules: {}".format(allModules))
        return allModules

    def displayPreviousLines(self, modulePath: str, lineNumber: int) -> None:
        """Opens the provided module to find the x lines before the provided line and appends them to the :var:`self.outPut` window.

        Parameters:
            modulePath: The module path.
            lineNumber: The line that contains the word to search.
        """
        with open(modulePath, 'r', encoding='utf-8') as readFile:
            lines = readFile.readlines()
            index = int(self.contextNumberComboBox.currentText())

            for number, line in enumerate(lines, start=1):
                if number == lineNumber - index:
                    self.output.appendHtml("<font color='grey'>{}</font> <span>&#8594;</span> <font color='grey'>line {}</font> <span>&#8594;</span> <font color='grey'>{}</font>".format(modulePath.split('\\')[-1], number, line))
                    index -= 1

                    if index == 0:
                        break

    def displayNextLines(self, modulePath: str, lineNumber: int) -> None:
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
                    self.output.appendHtml("<font color='grey'>{}</font> <span>&#8594;</span> <font color='grey'>line {}</font> <span>&#8594;</span> <font color='grey'>{}</font>".format(modulePath.split('\\')[-1], number, line))
                    index += 1

                    if index == int(self.contextNumberComboBox.currentText()) + 1:
                        self.output.appendHtml('')
                        break
