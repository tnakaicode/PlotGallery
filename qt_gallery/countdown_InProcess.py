import random
import sys
import time
from threading import Thread
import pandas as pd
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QLabel, QStyleFactory, QMainWindow
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.uic import loadUi
parametros = [['Area', 0, 5]]


def generar_aleatorio():
    return random.uniform(*parametros[0][1:])


def area(x1):
    area = 3.1416 * x1 ** 2
    return area


class Helper(QObject):
    send_signal = pyqtSignal(str)
    data_signal = pyqtSignal(list)


helper = Helper()


def estado(starttime, last_print, contador, n, area):
    acttime = time.time()
    if acttime - last_print <= 2:
        avg_time_per_run = (acttime - starttime) / (contador + 1)
        timestr = time.strftime("%H:%M:%S", time.gmtime(
            round(avg_time_per_run * (n - (contador + 1)))))
        text = 'Simulacion %i de %i - Tiempo estimado restante: %s\n' % (contador, n, timestr) \
               + 'Area = %5.3f\n\n' % area
        helper.send_signal.emit(text)


def montecarlo(n):
    data = []
    text = 'Iniciando iteraciones con {} repeticiones...\n\n'.format(n)
    helper.send_signal.emit(text)
    ult_print = time.time()
    starttime = time.time()
    for contador in range(n):
        z = generar_aleatorio()
        y = area(z)
        estado(starttime, ult_print, contador + 1, n, y)
        ult_print = time.time()
        time.sleep(0.001)
        data.append([z, y])
    helper.data_signal.emit(data)


class simulacion(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        #loadUi('simulacion.ui', self)
        self.setStyle(QStyleFactory.create('Fusion'))
        self.numsim = 10000000
        
        self.pushButton = QPushButton("Start", self)
        self.pushButton.clicked.connect(self.calibracion)

        #self.pushButton_2 = QPushButton("Start2", self)
        #self.pushButton_2.clicked.connect(self.save)
        
        #self.textEdit = QLabel("")

    def calibracion(self):
        thread = Thread(target=montecarlo, args=(self.numsim,))
        helper.send_signal.connect(self.textEdit.append, Qt.QueuedConnection)
        helper.data_signal.connect(self.obtener_resultados)
        thread.start()

    def obtener_resultados(self, data):
        self.data = data

    def save(self, data):
        file, _ = QFileDialog.getSaveFileName(
            self, 'Guardar Archivo de Simulación', '', '(*.csv)')
        if file:
            df = pd.DataFrame(self.data)
            df.to_csv(file, sep=';', index=False, encoding='utf-8')


app = QApplication(sys.argv)
w = simulacion()
w.show()
sys.exit(app.exec_())
