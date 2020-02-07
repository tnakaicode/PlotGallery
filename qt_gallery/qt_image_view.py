import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QLabel, QAction, QMainWindow, QApplication


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(100, 100, 500, 300)
        self.setWindowTitle("PyQT Show Image")

        openFile = QAction("&File", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip("Open File")
        openFile.triggered.connect(self.file_open)

        self.statusBar()

        mainMenu = self.menuBar()

        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openFile)

        self.lbl = QLabel(self)
        self.setCentralWidget(self.lbl)

        self.home()

    def home(self):
        self.show()

    def file_open(self):
        name = QFileDialog.getOpenFileName(self, 'Open File')
        print(name)
        pixmap = QtGui.QPixmap(name[0])
        self.lbl.setPixmap(pixmap.scaled(self.lbl.size()))


def run():
    app = QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())


run()
