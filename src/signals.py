from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QKeySequence


class SignalBus(QObject):
    __instance = None
    newLabelSignal = pyqtSignal(QKeySequence, str)
    delLabelSignal = pyqtSignal(str)
    uptLabelSlicer = pyqtSignal(int, str)

    @staticmethod
    def instance():
        if not SignalBus.__instance:
            SignalBus.__instance = SignalBus()
        return SignalBus.__instance


