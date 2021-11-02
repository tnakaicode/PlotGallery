#!/usr/bin/env python3

import os
import sys
import numpy

sys.path.append(os.path.join("../"))
from base import plot2d
# https://github.com/pyinstaller/pyinstaller/issues/2560

from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)

b1 = QtWidgets.QPushButton('Button 1')
b2 = QtWidgets.QPushButton('Button 2')
b3 = QtWidgets.QPushButton('Button 3')

b1.clicked.connect(lambda: b2.setVisible(not b2.isVisible()))
# b1.clicked.connect(lambda: QtCore.QTimer.singleShot(10, lambda: b2.setVisible(not b2.isVisible())))

layout = QtWidgets.QVBoxLayout()
layout.addWidget(b1)
layout.addWidget(b2)
layout.addWidget(b3)
layout.addStretch()

dialog = QtWidgets.QDialog()
dialog.setLayout(layout)
dialog.show()

app.exec_()

plot2d()
