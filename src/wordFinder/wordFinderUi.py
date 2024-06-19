import logging
from PySide2 import QtWidgets, QtCore, QtGui
from typing import List

from wordFinder import resources
import constants
from wordFinder.widgets import widgets, checkBoxes
import core

from utils import wordFinderUtils


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(20)
logging.basicConfig(filename='utils/wordFinder.log', level=logging.INFO)


class WordFinder(QtWidgets.QDialog):

    closed = QtCore.Signal()

    """Main ui class."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        # Get if a search path has been stored.
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
        self.optionLayout = QtWidgets.QHBoxLayout()

        self.menuBar = QtWidgets.QMenuBar()

        self.uiSetup = self.menuBar.addMenu('Options')
        self.githubSetup = self.menuBar.addMenu('GitHub')

        # Ui setup.
        self.devModeAction = self.uiSetup.addAction('Dev mode')

        self.layoutAction = self.uiSetup.addAction('Layout')

        self.syntaxAction = self.uiSetup.addAction('Syntax highlighting')

        # GitHub setup.
        self.githubTokenAction = self.githubSetup.addAction("Set GitHub personal access token")

        self.searchPathLabel = QtWidgets.QLabel()
        self.moduleToCheckLabel = QtWidgets.QLabel("Modules to check")
        self.stackedModulesWidget = widgets.StackModulesWidget(self.searchPath)

        self.searchModeGroup = QtWidgets.QGroupBox()
        self.radioSearchModeLayout = QtWidgets.QHBoxLayout(self.searchModeGroup)

        self.literalCheckBox = QtWidgets.QRadioButton("Classic")
        self.regexCheckBox = QtWidgets.QRadioButton("Regex")

        self.radioSearchModeLayout.addWidget(self.literalCheckBox)
        self.radioSearchModeLayout.addWidget(self.regexCheckBox)

        self.showContextCheckBox = QtWidgets.QCheckBox("Show context")
        self.contextNumberComboBox = QtWidgets.QComboBox()
        self.checkButton = widgets.PushButton('check')
        self.wordToSearch = QtWidgets.QLineEdit()
        self.setSearchPathButton = widgets.PushButton("Set local search path")
        self.separatorOne = widgets.SunkenHSeparator()
        self.separatorTwo = widgets.SunkenHSeparator()

    def _setupUi(self) -> None:
        self.mainLayout.addWidget(self.menuBar)
        self.mainLayout.addLayout(self.searchPathLayout)
        self.searchPathLayout.addWidget(self.setSearchPathButton)
        self.searchPathLayout.addWidget(self.searchPathLabel)
        self.mainLayout.addWidget(self.separatorOne)
        self.mainLayout.addLayout(self.optionLayout)
        self.optionLayout.addWidget(self.showContextCheckBox)
        self.optionLayout.addWidget(self.contextNumberComboBox)
        self.mainLayout.addWidget(self.separatorTwo)
        self.mainLayout.addWidget(self.moduleToCheckLabel)
        self.mainLayout.addWidget(self.stackedModulesWidget)
        self.mainLayout.addWidget(self.searchModeGroup)

        self.mainLayout.addWidget(self.wordToSearch)
        self.mainLayout.addWidget(self.checkButton)

        self.searchModeGroup.setTitle("Search mode")
        self.radioSearchModeLayout.addStretch()

        # Get if the dev mode has been set.
        if core.getConfigValueByName(constants.DEV_MODE):
            self.devModeAction.setChecked(True)

        self.devModeAction.setCheckable(True)
        self.syntaxAction.setCheckable(True)
        self.syntaxAction.setChecked(True)


        self.optionLayout.addStretch()
        self.searchPathLayout.addStretch()

        self.searchPathLabel.setText("Search path: {}".format(self.searchPath))

        self.setSearchPathButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setSearchPathButton.setFixedWidth(100)

        self.moduleToCheckLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.wordToSearch.setPlaceholderText('Search')

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

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Emits a signal when the ui is closed to store the method decorated by @wordFinderUtils.storeConfig"""
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

        Basically, the dev mode will activate the :func:`wordFinderUtils.devMode` decorator and set to DEBUG all the LOGGERS.

        Returns:
            The dev mode state.
        """
        wordFinderUtils.DEV_MODE = self.devModeAction.isChecked()

        widgetLogger = logging.getLogger(widgets.__name__)
        checkBoxLogger = logging.getLogger(checkBoxes.__name__)

        if wordFinderUtils.DEV_MODE:
            self.devModeAction.setIcon(QtGui.QIcon("wfIcons:check.png"))
            widgetLogger.setLevel(10)
            checkBoxLogger.setLevel(10)
            LOGGER.setLevel(10)

        else:
            self.devModeAction.setIcon(QtGui.QIcon(""))
            widgetLogger.setLevel(20)
            checkBoxLogger.setLevel(20)
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
        self.stackedModulesWidget.addGitHubModules()

    def onSyntaxActionTriggered(self) -> None:
        """Sets the syntax action icon"""
        if self.syntaxAction.isChecked():
            self.syntaxAction.setIcon(QtGui.QIcon("wfIcons:check.png"))
            return

        self.syntaxAction.setIcon(QtGui.QIcon(""))

    @wordFinderUtils.storeConfig(constants.GIT_HUB_HEY)
    def onGithubTokenActionTriggered(self):
        """Opens a window to allow the user to store an GitHub developer token to grant access to the repositories"""
        githubWindow = widgets.GitHubWindow()
        githubWindow.exec_()

        self.refreshModules()

        return githubWindow.gitHubToken()

    def setSearchPath(self) -> None:
        """Opens a new window to allow the user write the path where to query the modules."""
        pathWindow = widgets.SearchPathWindow()
        pathWindow.exec_()

        self.searchPath = pathWindow.newPath()
        self.refreshModules()

        LOGGER.debug("Search path: {}".format(self.searchPath))

    def refreshModules(self) -> None:
        """Refresh the modules checkboxes."""
        self.searchPathLabel.setText("Search path: {}".format(self.searchPath))
        self.stackedModulesWidget.setModulesWidgetSearchPath(self.searchPath)
        self.stackedModulesWidget.addLocalModules()
        self.stackedModulesWidget.addGitHubModules()
        
    def checkAllCheckBoxes(self) -> None:
        """Checks all checkBoxes"""
        for checkBox in self.stackedModulesWidget.allCheckBoxes:
            checkBox.setChecked(True)

    def uncheckAllCheckBoxes(self) -> None:
        """Unchecks all checkBoxes"""
        for checkBox in self.stackedModulesWidget.allCheckBoxes:
            checkBox.setChecked(False)

    def searchWord(self) -> None:
        """Search a word in the local or GitHub widget"""
        if not self.stackedModulesWidget.currentIndex():
            self.stackedModulesWidget.searchWordInLocal(
                self.wordToSearch.text(),
                self.showContextCheckBox.isChecked(),
                self.literalCheckBox.isChecked(),
                self.syntaxAction.isChecked(),
                self.contextNumberComboBox.currentText()
            )
            return

        self.stackedModulesWidget.searchWordInGitHub(
            self.wordToSearch.text(),
            self.showContextCheckBox.isChecked(),
            self.literalCheckBox.isChecked(),
            self.syntaxAction.isChecked(),
            self.contextNumberComboBox.currentText()
        )
