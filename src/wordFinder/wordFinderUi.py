import os
import logging
from PySide2 import QtWidgets, QtCore, QtGui
from typing import Mapping, List
import re

import constants
import widgets
import core

from utils import wordFinderUtils
from wordFinder import resources
from wordFinder.gitHub import auth


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(20)
logging.basicConfig(filename='./utils/wordFinder.log', level=logging.INFO)


class WordFinder(QtWidgets.QDialog):

    closed = QtCore.Signal()

    """Main ui class."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.searchPath = core.getConfigValueByName(constants.SEARCH_PATH)

        self._buildUi()
        self._setupUi()
        self._connectUi()

        # Add modules.
        self.stackedModulesWidget.setModulesWidgetSearchPath(self.searchPath)
        self.stackedModulesWidget.addLocalModules()
        self.stackedModulesWidget.addGitHubModules()

    def _buildUi(self) -> None:
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.searchModeLayout = QtWidgets.QHBoxLayout()
        self.searchPathLayout = QtWidgets.QHBoxLayout()
        self.checkButtonLayout = QtWidgets.QHBoxLayout()
        self.optionLayout = QtWidgets.QHBoxLayout()

        self.menuBar = QtWidgets.QMenuBar()

        self.uiSetup = self.menuBar.addMenu('Options')
        self.githubSetup = self.menuBar.addMenu('Github')

        # Ui setup.
        self.devModeAction = self.uiSetup.addAction('Dev mode')
        self.devModeAction.setCheckable(True)

        if core.getConfigValueByName(constants.DEV_MODE):
            self.devModeAction.setChecked(True)

        self.layoutAction = self.uiSetup.addAction('Layout')

        self.syntaxAction = self.uiSetup.addAction('Syntax highlighting')
        self.syntaxAction.setCheckable(True)
        self.syntaxAction.setChecked(True)

        # Github setup.
        self.githubTokenAction = self.githubSetup.addAction("Set Github personal access tokens ")

        self.searchPathLabel = QtWidgets.QLabel()
        self.moduleToCheckLabel = QtWidgets.QLabel("Modules to check")
        self.stackedModulesWidget = widgets.StackModulesWidget(self.searchPath)

        self.searchModeGroup = QtWidgets.QGroupBox()
        self.radioSearchModeLayout = QtWidgets.QHBoxLayout(self.searchModeGroup)

        self.literalCheckBox = QtWidgets.QRadioButton("Classic")
        self.regexCheckBox = QtWidgets.QRadioButton("Regex")

        self.radioSearchModeLayout.addWidget(self.literalCheckBox)
        self.radioSearchModeLayout.addWidget(self.regexCheckBox)

        self.showCommentCheckBox = QtWidgets.QCheckBox("Show comments")
        self.showCommentCheckBox.setChecked(True)

        self.showContextCheckBox = QtWidgets.QCheckBox("Show context")
        self.contextNumberComboBox = QtWidgets.QComboBox()
        self.checkButton = widgets.PushButton('check')
        self.wordToSearch = QtWidgets.QLineEdit()
        self.output = widgets.OutputWidget()
        self.setSearchPathButton = widgets.PushButton("Set local search path")
        self.checkAllButton = widgets.PushButton("Check all")
        self.uncheckAllButton = widgets.PushButton("Uncheck all")
        self.separatorOne = widgets.SunkenHSeparator()
        self.separatorTwo = widgets.SunkenHSeparator()

    def _setupUi(self) -> None:
        self.mainLayout.addWidget(self.menuBar)
        self.mainLayout.addLayout(self.searchPathLayout)
        self.searchPathLayout.addWidget(self.setSearchPathButton)
        self.searchPathLayout.addWidget(self.searchPathLabel)
        self.mainLayout.addWidget(self.separatorOne)
        self.mainLayout.addLayout(self.optionLayout)
        self.optionLayout.addWidget(self.showCommentCheckBox)
        self.optionLayout.addWidget(self.showContextCheckBox)
        self.optionLayout.addWidget(self.contextNumberComboBox)
        self.mainLayout.addWidget(self.separatorTwo)
        self.mainLayout.addWidget(self.moduleToCheckLabel)
        self.mainLayout.addWidget(self.stackedModulesWidget)
        self.mainLayout.addLayout(self.checkButtonLayout)
        self.checkButtonLayout.addWidget(self.checkAllButton)
        self.checkButtonLayout.addWidget(self.uncheckAllButton)
        self.mainLayout.addWidget(self.searchModeGroup)

        self.mainLayout.addWidget(self.wordToSearch)
        self.mainLayout.addWidget(self.output)
        self.mainLayout.addWidget(self.checkButton)

        self.checkButtonLayout.addStretch()

        self.searchModeGroup.setTitle("Search mode")
        self.radioSearchModeLayout.addStretch()

        self.optionLayout.addStretch()
        self.searchPathLayout.addStretch()

        self.searchPathLabel.setText("Search path: {}".format(self.searchPath))

        self.checkAllButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.uncheckAllButton.setFocusPolicy(QtCore.Qt.NoFocus)

        self.setSearchPathButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setSearchPathButton.setFixedWidth(100)

        self.moduleToCheckLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.wordToSearch.setPlaceholderText('Search')

        self.output.setFont(QtGui.QFont('Arial', 13))
        self.output.setReadOnly(True)

        self.contextNumberComboBox.setFixedWidth(60)
        
        # Add numbers to context number comboBox.
        for i in range(1, 10):
            self.contextNumberComboBox.addItem(str(i))
        self.contextNumberComboBox.setCurrentIndex(3)

        self.literalCheckBox.setChecked(True)

        # Main window.
        self.mainLayout.setMargin(5)
        self.resize(1300, 800)
        self.setWindowTitle("Word finder")
        self.setWindowIcon(QtGui.QIcon("wfIcons:w.png"))
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)

    def _connectUi(self) -> None:
        self.closed.connect(self.saveLocalCheckedModules)
        self.closed.connect(self.saveGitHubCheckedModules)
        self.devModeAction.triggered.connect(self._devMode)
        self.layoutAction.triggered.connect(self.onLayoutActionTriggered)
        self.syntaxAction.triggered.connect(self.onSyntaxActionTriggered)
        self.githubTokenAction.triggered.connect(self.onGithubTokenActionTriggered)
        self.setSearchPathButton.clicked.connect(self.setSearchPath)
        self.checkButton.clicked.connect(self.searchWord)
        self.checkAllButton.clicked.connect(self.checkAllCheckBoxes)
        self.uncheckAllButton.clicked.connect(self.uncheckAllCheckBoxes)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        event.accept()
        self.closed.emit()

    @wordFinderUtils.storeConfig(constants.LOCAL_CHECKED_MODULES)
    def saveLocalCheckedModules(self) -> List[str]:
        """Gets the checked checkBoxes and save them within the config file."""
        return [checkBox.text() for checkBox in self.stackedModulesWidget.allLocalCheckBoxes if checkBox.isChecked()]

    @wordFinderUtils.storeConfig(constants.GIT_HUB_CHECKED_MODULES)
    def saveGitHubCheckedModules(self) -> List[str]:
        """Gets the checked checkBoxes and save them within the config file."""
        return [checkBox.text() for checkBox in self.stackedModulesWidget.allGitHubCheckBoxes if checkBox.isChecked()]

    @wordFinderUtils.storeConfig(constants.DEV_MODE)
    def _devMode(self) -> bool:
        """This method handle the dev mode.

        Basically, the dev mode will activate the :func:`wordFinderUtils.devMode` decorator and set to DEBUG the :const:LOGGER logger.

        Returns:
            The dev mode state.
        """
        wordFinderUtils.DEV_MODE = self.devModeAction.isChecked()

        if wordFinderUtils.DEV_MODE:
            self.devModeAction.setIcon(QtGui.QIcon("wfIcons:check.png"))
            LOGGER.setLevel(10)

        else:
            self.devModeAction.setIcon(QtGui.QIcon(""))
            LOGGER.setLevel(20)

        self.devModeAction.setChecked(wordFinderUtils.DEV_MODE)

        LOGGER.debug("Dev mode: {}".format(wordFinderUtils.DEV_MODE))

        return self.devModeAction.isChecked()

    def onLayoutActionTriggered(self) -> None:
        """Opens a window to manage the module's layout."""
        layoutWindow = widgets.ModuleLayoutWindow(self)
        layoutWindow.exec_()

        # Set the modules with the new layout configuration.
        self.stackedModulesWidget.addLocalModules()

    def onSyntaxActionTriggered(self) -> None:
        """Sets the syntax action icon"""
        if self.syntaxAction.isChecked():
            self.syntaxAction.setIcon(QtGui.QIcon("wfIcons:check.png"))
            return

        self.syntaxAction.setIcon(QtGui.QIcon(""))

    @wordFinderUtils.storeConfig(constants.GIT_HUB_HEY)
    def onGithubTokenActionTriggered(self):
        githubWindow = widgets.GitHubWindow()
        githubWindow.exec_()

        self.refreshModules()

        return githubWindow.gitHubToken()

    def setSearchPath(self) -> None:
        """Opens a new window to let the user write the path where to query the modules."""
        pathWindow = widgets.SearchPathWindow()
        pathWindow.exec_()

        # Set the new search path.
        self.searchPath = pathWindow.newPath()
        self.refreshModules()

        LOGGER.debug("Search path: {}".format(self.searchPath))

    def refreshModules(self) -> None:
        """Reset the module path in the module widget and this class, adds the new module's checkBoxes to this window."""
        self.searchPathLabel.setText("Search path: {}".format(self.searchPath))
        self.stackedModulesWidget.setModulesWidgetSearchPath(self.searchPath)
        self.stackedModulesWidget.addLocalModules()
        self.stackedModulesWidget.addGitHubModules()
        
    def checkAllCheckBoxes(self) -> None:
        """Checks all checkBoxes"""
        LOGGER.debug("All checkboxes from module widget: {}".format(self.stackedModulesWidget.allCheckBoxes))

        for checkBox in self.stackedModulesWidget.allCheckBoxes:
            checkBox.setChecked(True)

    def uncheckAllCheckBoxes(self) -> None:
        """Unchecks all checkBoxes"""
        for checkBox in self.stackedModulesWidget.allCheckBoxes:
            checkBox.setChecked(False)

    def searchWord(self) -> None:
        if not self.stackedModulesWidget.currentIndex():
            self.searchWordInLocal()
            return

        self.searchWordInGitHub()

    @wordFinderUtils.devMode(wordFinderUtils.timed)
    def searchWordInLocal(self) -> None:
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
                        if self.wordInLine(word, line):
                            modulesWithPrints.append(module)

                            if self.showContextCheckBox.isChecked():
                                self.displayPreviousLines(modulePath, lineNumber)

                            # Colorize the line dependent on the syntax.
                            colorizedLine = core.colorizeLine(line, word) if self.syntaxAction.isChecked() else line

                            self.output.appendHtml("<font color=#5de856>{}</font> <span>&#8594;</span> <font color=#dae63e>line {}</font> <span>&#8594;</span> {}".format(' <span>&#8594;</span> '.join(modulePath.split(os.sep)[-3:]), lineNumber, colorizedLine))

                            if self.showContextCheckBox.isChecked():
                                self.displayNextLines(modulePath, lineNumber)

                    # Don't show the comment characters.
                    else:
                        if self.wordInLine(word, line):
                            if self.isLineValid(line):
                                modulesWithPrints.append(module)

                                if self.showContextCheckBox.isChecked():
                                    self.displayPreviousLines(modulePath, lineNumber)

                                # Colorize the line dependent on the syntax.
                                colorizedLine = core.colorizeLine(line, word) if self.syntaxAction.isChecked() else line

                                self.output.appendHtml("<font color=#5de856>{}</font> <span>&#8594;</span> <font color=#dae63e>line {}</font> <span>&#8594;</span> {}".format(' <span>&#8594;</span> '.join(modulePath.split(os.sep)[-3:]), lineNumber, colorizedLine))

                                if self.showContextCheckBox.isChecked():
                                    self.displayNextLines(modulePath, lineNumber)

        if not modulesWithPrints:
            self.output.appendPlainText('The word [{}] is not found'.format(word))


    def searchWordInGitHub(self):
        for checkBox in self.stackedModulesWidget.allGitHubCheckBoxes:
            if not checkBox.isChecked():
                continue

    def wordInLine(self, word: str, line: str) -> bool:
        """Gets if the provided line contains the provided word.

        There is two way to search the word, with a simple check or with a regex.

        Parameters:
            word: The word to search.
            line: The line that is used to search for the word.

        Returns:
            True if the line contains the word, else False.
        """
        if self.literalCheckBox.isChecked():
            if word in line:
                return True

        if self.regexCheckBox.isChecked():
            pattern = r"\b" + re.escape(word) + r"\b"

            if re.search(pattern, line):
                return True

        return False

    @staticmethod
    def isLineValid(line: str) -> bool:
        """Checks if the provided word or sentence contains an excluded character.

        This method is used to get if the tool can output a line that contains a comment or a docstring.

        Parameters:
            line: The line to check.

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

        for checkBox in self.stackedModulesWidget.allLocalCheckBoxes:
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
                    self.output.appendHtml("<font color='grey'>{}</font> <span>&#8594;</span> <font color='grey'>line {}</font> <span>&#8594;</span> <font color' -> ''>{}</font>".format(" <span>&#8594;</span> ".join(modulePath.split(os.sep)[-3:]), number, line))
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
                    self.output.appendHtml("<font color='grey'>{}</font> <span>&#8594;</span> <font color='grey'>line {}</font> <span>&#8594;</span> <font color' -> ''>{}</font>".format(" <span>&#8594;</span> ".join(modulePath.split(os.sep)[-3:]), number, line))
                    index += 1

                    if index == int(self.contextNumberComboBox.currentText()) + 1:
                        self.output.appendHtml('')
                        break
