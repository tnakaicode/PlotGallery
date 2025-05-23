import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
                             QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)


class Second:
    def __init__(self, parent=None):
        self.w = QDialog(parent)
        self.parent = parent
        # Setting a title, locating and sizing the window
        self.title = 'My Second Window'
        self.left = 200
        self.top = 200
        self.width = 500
        self.height = 500
        self.w.setWindowTitle(self.title)
        self.w.setGeometry(self.left, self.top, self.width, self.height)
        self.pushButton = QtWidgets.QPushButton("Close Me")
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        # self.pushButton.move(120,120)
        layout1 = QHBoxLayout()
        layout1.addWidget(self.pushButton)
        self.w.setLayout(layout1)

    def on_pushButton_clicked(self):
        self.w.close()

    def show(self):
        self.w.exec_()


class First(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(First, self).__init__(parent)
        self.title = 'My First Window'
        self.left = 100
        self.top = 100
        self.width = 500
        self.height = 500
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.pushButton = QtWidgets.QPushButton("Open Me", self)
        self.pushButton2 = QtWidgets.QPushButton("close", self)
        # self.pushButton.move(120,120)
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        self.pushButton2.clicked.connect(self.on_pushButton2_clicked)

        layout1 = QHBoxLayout()
        layout1.addWidget(self.pushButton)
        layout1.addWidget(self.pushButton2)

        self.setLayout(layout1)

    def on_pushButton_clicked(self):
        self.newWindow = Second(self)
        self.newWindow.show()

    def on_pushButton2_clicked(self):
        self.newWindow = Second(self)
        self.newWindow.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = First()
    main.show()
    sys.exit(app.exec_())
