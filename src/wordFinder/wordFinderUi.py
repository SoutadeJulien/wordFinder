import os
from PySide2 import QtWidgets, QtCore, QtGui
from typing import Mapping

import constants
import widgets
from utils import wordFinderUtils


class WordFinder(QtWidgets.QDialog):
    def __init__(self, parent=None):
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

        self.searchPathLabel = QtWidgets.QLabel()
        self.moduleToCheckLabel = QtWidgets.QLabel("Modules to check")
        self.modulesWidget = widgets.ModulesWidget(self.searchPath)
        self.devModeCheckBox = QtWidgets.QCheckBox("Dev mode")
        self.showCommentCheckBox = QtWidgets.QCheckBox("Show special characters")
        self.showContextCheckBox = QtWidgets.QCheckBox("Show context")
        self.contextNumber = QtWidgets.QComboBox()
        self.checkButton = QtWidgets.QPushButton('check')
        self.wordToSearch = QtWidgets.QLineEdit()
        self.output = QtWidgets.QPlainTextEdit()
        self.setSearchPathButton = QtWidgets.QPushButton("Change search path")
        self.checkAllButton = QtWidgets.QPushButton("Check all")
        self.uncheckAllButton = QtWidgets.QPushButton("Uncheck all")
        self.separatorOne = widgets.SunkenHSeparator()
        self.separatorTwo = widgets.SunkenHSeparator()

    def _setupUi(self) -> None:
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
        self.optionLayout.addWidget(self.contextNumber)
        self.mainLayout.addWidget(self.separatorTwo)
        self.mainLayout.addWidget(self.moduleToCheckLabel)
        self.mainLayout.addWidget(self.modulesWidget)
        self.mainLayout.addWidget(self.wordToSearch)
        self.mainLayout.addWidget(self.output)
        self.mainLayout.addWidget(self.checkButton)

        self.devModeLayout.insertStretch(0)
        self.optionLayout.addStretch()
        self.searchPathLayout.addStretch()

        self.showCommentCheckBox.setChecked(True)
        self.searchPathLabel.setText("Search path: {}".format(self.searchPath))
        self.moduleToCheckLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.setSearchPathButton.setFixedWidth(100)
        self.wordToSearch.setPlaceholderText('Search')
        self.output.setFont(QtGui.QFont('Arial', 13))
        self.output.setReadOnly(True)

        self.contextNumber.setFixedWidth(60)

        for i in range(1, 10):
            self.contextNumber.addItem(str(i))
        self.contextNumber.setCurrentIndex(3)

        self.resize(1300, 800)
        self.setWindowTitle("Word finder")
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)

    def _connectUi(self) -> None:
        self.devModeCheckBox.clicked.connect(self._devMode)
        self.setSearchPathButton.clicked.connect(self.setSearchPath)
        self.checkButton.clicked.connect(self.searchWord)
        self.checkAllButton.clicked.connect(self.checkAllCheckBoxes)
        self.uncheckAllButton.clicked.connect(self.uncheckAllCheckBoxes)

    def _devMode(self):
        wordFinderUtils.DEV_MODE = self.devModeCheckBox.isChecked()

    def setSearchPath(self):
        pathWindow = widgets.SearchPathWindow()
        pathWindow.searchPathAdded.connect(self.refreshModules)
        pathWindow.exec_()
        self.searchPath = pathWindow.newPath()

    def refreshModules(self, modulePath):
        self.modulesWidget.searchPath = modulePath
        self.searchPath = modulePath
        self.searchPathLabel.setText("Search path: {}".format(self.searchPath))
        self.modulesWidget.addModules()
        
    def checkAllCheckBoxes(self) -> None:
        for checkBox in self.modulesWidget.allCheckBoxes:
            checkBox.setChecked(True)

    def uncheckAllCheckBoxes(self) -> None:
        for checkBox in self.modulesWidget.allCheckBoxes:
            checkBox.setChecked(False)

    @wordFinderUtils.devMode(wordFinderUtils.timed)
    def searchWord(self) -> None:
        self.output.clear()

        word = self.wordToSearch.text()
        modulesWithPrints = []

        for module, modulePath in self.filteredModules.items():
            with open(modulePath, 'r') as reader:
                lines = reader.readlines()
                for lineNumber, line in enumerate(lines, start=1):
                    if self.showCommentCheckBox.isChecked():
                        if word in line:
                            modulesWithPrints.append(module)

                            if self.showContextCheckBox.isChecked():
                                self.displayPreviousLines(modulePath, lineNumber)

                            self.output.appendHtml("<font color='green'>{}</font> <span>&#8594;</span> <font color='yellow'>line {}</font> <span>&#8594;</span> <font color='white'>{}</font>".format(module, lineNumber, line))

                            if self.showContextCheckBox.isChecked():
                                self.displayNextLines(modulePath, lineNumber)

                    else:
                        if word in line and constants.EXCLUDED_CHARACTERS not in line:

                            if self.showContextCheckBox.isChecked():
                                self.displayPreviousLines(modulePath, lineNumber)

                            self.output.appendHtml("<font color='green'>{}</font> <span>&#8594;</span> <font color='yellow'>line {}</font> <span>&#8594;</span> <font color='white'>{}</font>".format(module, lineNumber, line))
                            modulesWithPrints.append(module)

                            if self.showContextCheckBox.isChecked():
                                self.displayNextLines(modulePath, lineNumber)

        if not modulesWithPrints:
            self.output.appendPlainText('The word [{}] is not found'.format(word))

    @property
    def filteredModules(self) -> Mapping[str, str]:
        allModules = {}

        for checkBox in self.modulesWidget.allCheckBoxes:
            if not checkBox._state:
                continue
            for root, dirs, files in os.walk(checkBox.path):
                for directory in dirs:
                    if directory in constants.EXCLUDED_DIRECTORIES:
                        continue

                    for file in files:
                        if os.path.splitext(file)[-1] == '.py':
                            allModules[file] = os.path.join(root, file)

        return allModules


    def displayPreviousLines(self, module, lineNumber):
        with open(module, 'r') as readFile:
            lines = readFile.readlines()
            index = int(self.contextNumber.currentText())

            for number, line in enumerate(lines, start=1):
                if number == lineNumber - index:
                    self.output.appendHtml("<font color='grey'>{}</font> <span>&#8594;</span> <font color='grey'>line {}</font> <span>&#8594;</span> <font color='grey'>{}</font>".format(module.split('\\')[-1], number, line))
                    index -= 1

                    if index == 0:
                        break

    def displayNextLines(self, module, lineNumber):
        with open(module, 'r') as readFile:
            lines = readFile.readlines()
            index = 1

            for number, line in enumerate(lines, start=1):
                if number == lineNumber + index:
                    self.output.appendHtml("<font color='grey'>{}</font> <span>&#8594;</span> <font color='grey'>line {}</font> <span>&#8594;</span> <font color='grey'>{}</font>".format(module.split('\\')[-1], number, line))
                    index += 1

                    if index == int(self.contextNumber.currentText()) + 1:
                        self.output.appendHtml('')
                        break



