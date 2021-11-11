# importing the required libraries

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # set the title
        self.setWindowTitle("Python")

        # setting geometry
        self.setGeometry(100, 100, 600, 400)

        # creating a push button
        self.button = QPushButton("Toggle", self)

        # setting geometry of button
        self.button.setGeometry(200, 150, 100, 40)

        # setting checkable to true
        self.button.setCheckable(True)

        # setting calling method by button
        self.button.clicked.connect(self.changeColor)

        # setting default color of button to light-grey
        self.button.setStyleSheet("background-color : lightgrey")

        # show all the widgets
        self.update()
        self.show()

    # method called by button
    def changeColor(self):

        # if button is checked
        if self.button.isChecked():

            # setting background color to light-blue
            self.button.setStyleSheet("background-color : lightblue")

        # if it is unchecked
        else:

            # set background color back to light-grey
            self.button.setStyleSheet("background-color : lightgrey")


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# start the app
sys.exit(App.exec())
