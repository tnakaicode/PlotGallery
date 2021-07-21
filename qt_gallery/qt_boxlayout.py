#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from PyQt5.QtWidgets import QLabel, QWidget, QApplication
from PyQt5.QtWidgets import QPushButton, QLineEdit
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, QLayout, QGridLayout


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        mainlayout = QGridLayout()

        # OKボタンとCancelボタンの作成
        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")

        # 水平なボックスを作成
        hbox1 = QHBoxLayout()
        # ボタンの大きさが変わらないようにする
        # ボタンの左側に水平方向に伸縮可能なスペースができるため、ボタンは右に寄る
        hbox1.addStretch(1)
        hbox1.addWidget(okButton)
        hbox1.addWidget(cancelButton)

        # 垂直なボックスを作成
        vbox = QVBoxLayout()
        # 垂直方向に伸縮可能なスペースを作る
        vbox.addStretch(1)
        # 右下にボタンが移る
        vbox.addLayout(hbox1)

        title = QLabel("Title")
        title_edit = QLineEdit()
        title_edit.setFixedSize(100, 20)
        hbox2 = QHBoxLayout()
        hbox2.setSpacing(25)
        hbox2.addStretch(1)
        hbox2.addWidget(title)
        hbox2.addWidget(title_edit)
        mainlayout.addLayout(hbox2, 0, 0)
        mainlayout.addLayout(vbox, 1, 2)

        # 画面に上で設定したレイアウトを加える
        self.setLayout(mainlayout)

        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Buttons')
        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
