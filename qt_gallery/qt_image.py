import sys
import os

import numpy as np
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import glob
from PIL import Image


class Application(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.root = '../pic_color/'
        self.ext = 'bmp'

        self.set_FileList()
        self.FileName = self.FileList.item(0).text()
        self.load_ImageFile()

        self.initFigure()
        self.FileList.itemSelectionChanged.connect(self.FileList_Changed)

    def initUI(self):
        self.FigureWidget = QtWidgets.QWidget(self)
        self.FigureLayout = QtWidgets.QVBoxLayout(self.FigureWidget)
        self.FigureLayout.setContentsMargins(0, 0, 0, 0)

        self.FileList = QtWidgets.QListWidget(self)
        self.setGeometry(0, 0, 900, 600)
        self.FigureWidget.setGeometry(200, 0, 700, 600)
        self.FileList.setGeometry(0, 0, 200, 600)

    def initFigure(self):
        self.Figure = plt.figure()
        self.FigureCanvas = FigureCanvas(self.Figure)
        self.FigureLayout.addWidget(self.FigureCanvas)

        self.axis = self.Figure.add_subplot(1, 1, 1)
        self.axis_image = self.axis.imshow(self.image, cmap='gray')
        plt.axis('off')

    def set_FileList(self):
        Files = glob.glob(self.root + '*.' + self.ext)
        self.Files = sorted(Files)
        for file in self.Files:
            self.FileList.addItem(os.path.basename(file))

    def FileList_Changed(self):
        self.FileName = self.FileList.selectedItems()[0].text()
        self.load_ImageFile()
        self.update_Figure()

    def load_ImageFile(self):
        image = Image.open(self.root + self.FileName)
        self.image = np.asarray(image)

    def update_Figure(self):
        self.axis_image.set_data(self.image)
        self.FigureCanvas.draw()


QApp = QtWidgets.QApplication(sys.argv)
app = Application()
app.show()
sys.exit(QApp.exec_())
