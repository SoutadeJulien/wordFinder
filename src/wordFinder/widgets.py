import os
from PySide2 import QtWidgets

import constants


class CheckBox(QtWidgets.QCheckBox):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self.path = None

        self._state = False

        self.stateChanged.connect(self.state)

    def state(self):
        self._state = not self._state


class ModulesWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.mainLayout = QtWidgets.QGridLayout(self)
        self.allCheckBoxes = []

        self.addModules()

    def addModules(self):
        row = 0
        column = 0

        for module in self.modules():
            checkBox = CheckBox(module)
            checkBox.path = os.path.join(constants.MODULES_PATH, module)
            self.mainLayout.addWidget(checkBox, row, column)

            self.allCheckBoxes.append(checkBox)

            column += 1
            if column == 5:
                column = 0
                row += 1

    def modules(self):
        for module in os.listdir(constants.MODULES_PATH):
            yield module