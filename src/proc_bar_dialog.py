import os
import sys
import time
from threading import Thread

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QProgressBar, QPushButton, QVBoxLayout

from signals import SignalBus
from face_recog import UltraLightFaceRecog


class ProcVideoDialog(QDialog):

    def __init__(self, rawFileName, fileName, parent=None):
        super(ProcVideoDialog, self).__init__(parent)
        self.comm = SignalBus.instance()
        self.comm.updProgress.connect(self.updProgress)
        self.fileName = fileName
        self.faceRecog = UltraLightFaceRecog()
        self.procThread = Thread(target=self.faceRecog.blur_faces,
                args=(rawFileName, self.fileName,))
        self.procThread.start()
        self.done = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Processing video')
        self.progress = QProgressBar(self)
        self.progress.setMaximum(100)
        self.cancelButton = QPushButton('cancel', self)
        self.cancelButton.clicked.connect(self.close)
        layout = QVBoxLayout()
        layout.addWidget(self.progress)
        layout.addWidget(self.cancelButton)
        self.setLayout(layout)
        self.show()

    def closeEvent(self, event):
        if not self.done:
            self.faceRecog.stop()
            self.procThread.join()
            if os.path.isfile(self.fileName):
                os.remove(self.fileName)

    @pyqtSlot(float)
    def updProgress(self, prog: float):
        self.progress.setValue(prog)
        if prog == 100.0:
            self.done = True
            self.close()


