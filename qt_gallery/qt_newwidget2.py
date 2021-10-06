import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
                             QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)


class Second(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Second, self).__init__(parent)
        # Setting a title, locating and sizing the window
        self.title = 'My Second Window'
        self.left = 200
        self.top = 200
        self.width = 500
        self.height = 500
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.pushButton = QtWidgets.QPushButton("Close Me", self)
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        self.pushButton.move(120, 120)

    def on_pushButton_clicked(self):
        self.close()


class First(QtWidgets.QMainWindow):
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
        self.pushButton.move(120, 120)
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        self.pushButton2 = QtWidgets.QPushButton("Close Me", self)
        self.pushButton2.move(120, 150)
        self.pushButton2.clicked.connect(self.on_pushButton2_clicked)
        self.newWindow = Second(self)

    def on_pushButton_clicked(self):
        self.newWindow.show()

    def on_pushButton2_clicked(self):
        self.newWindow.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = First()
    main.show()
    sys.exit(app.exec_())
