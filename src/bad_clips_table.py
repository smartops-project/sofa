from PyQt5.QtWidgets import (QLabel, QDialog, QFormLayout, QGroupBox,
        QPushButton, QSizePolicy, QStyle, QVBoxLayout, QWidget, QLineEdit,
        QTableWidget, QTableWidgetItem, QAction, QAbstractScrollArea, QFrame,
        QDialogButtonBox)
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QColor

from utils import format_time

class BadClipsWidget(QWidget):

    def __init__(self):
        super(BadClipsWidget, self).__init__()
        self.title = 'Removed clips'
        self.default_color = None
        self.initUI()
        self.currentRow = 0

    def initUI(self):
        self.setWindowTitle(self.title)
        self.createTable()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)

    def createTable(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setSizeAdjustPolicy(
                QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setHorizontalHeaderLabels(['begin', 'end', 'duration',
            ''])
        self.tableWidget.resizeColumnsToContents()

    def new_mark(self, time, mode):
        index = self.currentRow
        if not mode:
            start_or_stop = 0
            index = self.tableWidget.rowCount()-1
            self.tableWidget.setItem(index, 1, QTableWidgetItem('...'))
            duration = '...'
            if not self.default_color:
                self.default_color = \
                        self.tableWidget.item(index, 1).background()
            self.tableWidget.insertRow(index+1)
        else:
            start_or_stop = 1
            self.currentRow += 1
            duration = 'eita'
        timeItem = QTableWidgetItem(format_time(time))
        self.tableWidget.setItem(index, start_or_stop, timeItem)
        self.tableWidget.setItem(index, 2, QTableWidgetItem(duration))
        delButton = QPushButton()
        delButton.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        delButton.clicked.connect(self.deleteRow)
        self.tableWidget.setCellWidget(index, 3, delButton)
        self.tableWidget.scrollToItem(timeItem)
        self.tableWidget.resizeColumnsToContents()
        self.set_row_color(index, mode)

    @pyqtSlot()
    def deleteRow(self):
        button = self.sender()
        if button:
            row = self.tableWidget.indexAt(button.pos()).row()
            self.tableWidget.removeRow(row)
            self.currentRow -= 1

    def set_row_color(self, index, mode):
        t = self.tableWidget
        if not mode:
            self.__row_colors(index, QColor(64, 249, 107))
        else:
            self.__row_colors(index, self.default_color)

    def get_marks(self):
        t = self.tableWidget
        marks = [[self.get_item_marks(i, j) for j in range(t.columnCount()-1)]\
                for i in range(t.rowCount()-1)]
        return marks

    def get_item_marks(self, i, j):
        try:
            return self.tableWidget.item(i, j).text()
        except:
            return 'ERROR_INVALID_VALUE'

    def __row_colors(self, i, color):
        for ii in range(self.tableWidget.columnCount()-1):
            self.tableWidget.item(i, ii).setBackground(color)


