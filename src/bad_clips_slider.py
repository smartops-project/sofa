import sys
from PyQt5.QtWidgets import (QWidget, QSlider, QApplication,
                             QHBoxLayout, QVBoxLayout)
from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QFont, QColor, QPen


class HlightRmClipsWidget(QWidget):

    def __init__(self):
        super(HlightRmClipsWidget, self).__init__()
        self.video_len = 8
        self.isRemoved = False
        self.initUI()

    def initUI(self):
        self.setMinimumSize(170, 30)
        self.value = 0

    def setValue(self, value: int):
        self.value = value
        self.repaint()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def setRange(self, r):
        self.video_len = r
        self.repaint()

    def toggleRm(self):
        self.isRemoved = not self.isRemoved

    def drawWidget(self, qp):
        MAX_CAPACITY = 8
        OVER_CAPACITY = self.video_len
        font = QFont('Serif', 7, QFont.Light)
        qp.setFont(font)
        size = self.size()
        w = size.width()
        h = size.height()
        step = int(round(w / 5))
        till = int(((w / OVER_CAPACITY) * self.value))
        full = int(((w / OVER_CAPACITY) * MAX_CAPACITY))
        if self.isRemoved:
            qp.setPen(QColor(255, 255, 255))
            qp.setBrush(QColor(255, 255, 184))
            qp.drawRect(0, 0, full, h)
            qp.setPen(QColor(255, 175, 175))
            qp.setBrush(QColor(255, 175, 175))
            qp.drawRect(full, 0, till-full, h)
        else:
            qp.setPen(QColor(255, 255, 255))
            qp.setBrush(QColor(255, 255, 184))
            qp.drawRect(0, 0, till, h)
        pen = QPen(QColor(20, 20, 20), 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.setBrush(Qt.NoBrush)
        qp.drawRect(0, 0, w-1, h-1)
        j = 0


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        OVER_CAPACITY = 10
        sld = QSlider(Qt.Horizontal, self)
        sld.setFocusPolicy(Qt.NoFocus)
        sld.setRange(0, OVER_CAPACITY)
        sld.setValue(2)

        self.c = Communicate()
        self.wid = BurningWidget()

        self.c.updateBW[int].connect(self.wid.setValue)
        sld.valueChanged[int].connect(self.changeValue)

        hbox = QHBoxLayout()
        hbox.addWidget(self.wid)
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(sld)

        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.setGeometry(500, 300, 390, 210)
        self.setWindowTitle('Burning widget')

    def changeValue(self, value):
        self.c.updateBW.emit(value)
        self.wid.repaint()


