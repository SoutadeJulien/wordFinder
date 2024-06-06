import sys
import os

from PySide2 import QtWidgets
from PySide2.QtGui import QPalette, QColor
from PySide2.QtCore import Qt

import core

wordFinderPath = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

def isPathAppended():
    for modulePath in sys.path:
        if modulePath == wordFinderPath:
            return True
    return False

if not isPathAppended():
    sys.path.append(wordFinderPath)

from wordFinder import wordFinderUi

qApp = QtWidgets.QApplication()
qApp.setStyle("Fusion")

palette = QPalette()
palette.setColor(QPalette.Window, QColor(53, 53, 53))
palette.setColor(QPalette.WindowText, Qt.white)
palette.setColor(QPalette.Base, QColor(25, 25, 25))
palette.setColor(QPalette.AlternateBase, QColor(255, 255, 255))
palette.setColor(QPalette.ToolTipBase, Qt.black)
palette.setColor(QPalette.ToolTipText, Qt.white)
palette.setColor(QPalette.Text, Qt.white)
palette.setColor(QPalette.Button, QColor(53, 53, 53))
palette.setColor(QPalette.ButtonText, Qt.white)
palette.setColor(QPalette.BrightText, Qt.red)
palette.setColor(QPalette.Link, QColor(42, 130, 218))
palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
palette.setColor(QPalette.HighlightedText, Qt.black)
qApp.setPalette(palette)


# Set default configuration if previous configuration is not found.
if not core.getConfig():
    print("Configuration not found. Base configuration is applied")
    core.makeDefaultConfig()

wfUi = wordFinderUi.WordFinder()


wfUi.show()
qApp.exec_()

def testing():
    pass
