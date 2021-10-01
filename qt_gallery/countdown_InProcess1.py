import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import time

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        # Set up an example ui
        qbtn = QPushButton('Click', self)
        qbtn.clicked.connect(self.changeLabels)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(100, 50)
        # Add labels
        self.labels = list()
        self.labels.append(QLabel("Lbl1", self))
        self.labels[-1].setFixedSize(50, 20)
        self.labels.append(QLabel("Lbl2", self))
        self.labels[-1].setFixedSize(50, 20)
        self.labels[-1].move(0, 20)
        self.labels.append(QLabel("Lbl3", self))
        self.labels[-1].setFixedSize(50, 20)
        self.labels[-1].move(0, 40)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Test')
        self.show()

    #def changeLabels(self):
    #    # Loop over all labels. For each label a function will be executed that will take some time. In this case
    #    # I represent that with a dummy function to just take time. While the function is running the label should say
    #    # "running" and when its finished it should say "done".
    #    for lbl in self.labels:
    #        orgTxt = lbl.text()
    #        lbl.setText("%s Running" % orgTxt)
    #        self.dummyFunction()
    #        lbl.setText("%s Done" % orgTxt)

    def dummyFunction(self):
        time.sleep(1)

    def changeLabels(self):
        for lbl in self.labels:
            orgTxt = lbl.text()
            lbl.setText("%s Running" % orgTxt)
            thread = DummyThread(self)
            thread.start()
            thread.finished.connect(lambda txt=orgTxt, lbl=lbl : lbl.setText("%s Done" % txt))

class DummyThread(QThread):
    finished = pyqtSignal()
    def run(self):
        time.sleep(1)
        self.finished.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())