import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
                             QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)


class Second(QtWidgets.QWidget):
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
        self.pushButton1 = QtWidgets.QPushButton("Close Me", self)
        self.lineTextEd1 = QtWidgets.QLineEdit("1.0", self)

        layout1 = QVBoxLayout()
        layout1.addWidget(self.pushButton1)
        layout1.addWidget(self.lineTextEd1)
        self.setLayout(layout1)

    def on_pushButton_clicked(self):
        self.close()


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
        self.pushButton1 = QtWidgets.QPushButton("Open Me", self)
        self.pushButton2 = QtWidgets.QPushButton("close", self)
        self.lineTextEd1 = QtWidgets.QLineEdit("1.0", self)
        self.pushButton1.clicked.connect(self.on_pushButton1_clicked)
        self.pushButton2.clicked.connect(self.on_pushButton2_clicked)

        layout1 = QHBoxLayout()
        layout1.addWidget(self.pushButton1)
        layout1.addWidget(self.pushButton2)
        layout1.addWidget(self.lineTextEd1)

        self.setLayout(layout1)

    def new_widget(self):
        self.newWindow = Second(None)
        self.newWindow.pushButton1.clicked.connect(self.new_widget_update)
        self.newWindow.pushButton1.clicked.connect(self.newWindow.close)

    def new_widget_update(self):
        self.lineTextEd1.setText(self.newWindow.lineTextEd1.text())

    def on_pushButton1_clicked(self):
        self.new_widget()
        self.newWindow.show()

    def on_pushButton2_clicked(self):
        #self.newWindow = Second(self)
        self.newWindow.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = First()
    main.show()
    sys.exit(app.exec_())
