import sys
from PyQt5.QtWidgets import (QWidget, QSlider, QApplication, QSizePolicy,
                             QHBoxLayout, QVBoxLayout)
from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QFont, QColor, QPen


class HlightSliderTipsWidget(QWidget):

    def __init__(self):
        super(HlightSliderTipsWidget, self).__init__()
        self.video_len = 8
        self.useYellow = False
        self.initUI()

    def initUI(self):
        self.setMinimumSize(170, 30)
        self.colorsArray = []
        self.value = 0
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def setColorsArray(self, colorsArray, useYellow=False):
        self.colorsArray = colorsArray
        self.setRange(len(colorsArray))
        self.useYellow = useYellow

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

    def drawWidget(self, qp):
        # initializing
        MAX_CAPACITY = self.video_len
        OVER_CAPACITY = self.video_len
        font = QFont('Serif', 7, QFont.Light)
        qp.setFont(font)
        size = self.size()
        w = size.width()
        h = size.height()
        step = 1

        # setting background
        pen = QPen(QColor(20, 20, 20), 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.setBrush(Qt.NoBrush)
        qp.drawRect(0, 0, w-1, h-1)

        if (not self.useYellow):
            for curr, diff_value in enumerate(self.colorsArray):
                till = curr+step
                # red - requires attention
                if (diff_value != 0):
                    qp.setPen(QColor(184, 0, 0))
                    qp.setBrush(QColor(184, 0, 0))
                else:
                    qp.setPen(QColor(80, 80, 80))
                    qp.setBrush(QColor(80, 80, 80))

                # drawRect(x1,y1,w,h), which here is...
                qp.drawRect(curr, 0, till, h)
                if (diff_value != 0):
                    pen = QPen(QColor(255, 0, 0), 1, Qt.SolidLine)
                else:
                    pen = QPen(QColor(80, 80, 80), 1, Qt.SolidLine)

                qp.setPen(pen)
        else:
            for curr, diff_value in enumerate(self.colorsArray):
                till = curr+step
                # yellow - no register by one of the (or both) algorithms
                if (diff_value == 2):
                    qp.setPen(QColor(255, 255, 184))
                    qp.setBrush(QColor(255, 255, 184))
                 # red
                elif (diff_value == 1):
                    qp.setPen(QColor(184, 0, 0))
                    qp.setBrush(QColor(184, 0, 0))

                # drawRect(x1,y1,w,h), which here is...
                qp.drawRect(curr, 0, till, h)
                if (diff_value == 2):
                    pen = QPen(QColor(255, 255, 0), 1, Qt.SolidLine)
                elif (diff_value == 1):
                    pen = QPen(QColor(255, 0, 0), 1, Qt.SolidLine)
                qp.setPen(pen)


class HlightRmClipsWidget(QWidget):

    def __init__(self):
        super(HlightRmClipsWidget, self).__init__()
        self.video_len = 8
        self.isRemoved = False
        self.initUI()

    def initUI(self):
        self.setMinimumSize(170, 30)
        self.value = 0
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

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


