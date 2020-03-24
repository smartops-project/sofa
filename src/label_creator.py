from PyQt5.QtWidgets import (QLabel, QDialog, QFormLayout, QGroupBox,
        QPushButton, QSizePolicy, QStyle, QVBoxLayout, QWidget, QLineEdit,
        QTableWidget, QTableWidgetItem, QAction, QAbstractScrollArea, QFrame,
        QDialogButtonBox, QKeySequenceEdit, QAbstractItemView)
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon, QIntValidator

from signals import SignalBus


class LabelCreatorWidget(QWidget):

    def __init__(self):
        super(LabelCreatorWidget, self).__init__()
        self.title = 'Label Creator'
        self.comm = SignalBus.instance()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        self.createTable()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.show()

    @pyqtSlot()
    def deleteRow(self):
        button = self.sender()
        if button:
            row = self.tableWidget.indexAt(button.pos()).row()
            keySeqStr = self.tableWidget.item(row, 2).text()
            self.comm.delLabelSignal.emit(keySeqStr)
            self.tableWidget.removeRow(row)

    def createTable(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setSizeAdjustPolicy(
                QAbstractScrollArea.AdjustToContents)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.setHorizontalHeaderLabels(['id', 'label',
            'shortcut', ''])
        newButton = self._create_newButton()
        self.tableWidget.setCellWidget(0, 3, newButton)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

    @pyqtSlot()
    def addLabel(self):
        newLabelDialog = NewLabelDialog()
        if newLabelDialog.exec_():
            label = newLabelDialog.label.text()
            keySeq = newLabelDialog.shortcut.keySequence()
            index = self.tableWidget.rowCount() - 1
            self.tableWidget.setItem(index, 0, QTableWidgetItem(
                newLabelDialog.lid.text()))
            self.tableWidget.setItem(index, 1, QTableWidgetItem(label))
            keyItem = QTableWidgetItem(keySeq.toString())
            self.tableWidget.setItem(index, 2, keyItem)
            delButton = QPushButton()
            delButton.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
            delButton.clicked.connect(self.deleteRow)
            self.tableWidget.setCellWidget(index, 3, delButton)
            self.tableWidget.scrollToItem(keyItem)
            self.comm.newLabelSignal.emit(keySeq, label)
            self.tableWidget.insertRow(index+1)
            newButton = self._create_newButton()
            self.tableWidget.setCellWidget(index+1, 3, newButton)
            self.tableWidget.resizeColumnsToContents()

    def _create_newButton(self):
        newButton = QPushButton()
        newButton.setIcon(self.style().standardIcon(
            QStyle.SP_FileDialogNewFolder))
        newButton.clicked.connect(self.addLabel)
        return newButton


class NewLabelDialog(QDialog):

    def __init__(self):
        super(NewLabelDialog, self).__init__()
        self.title = 'Add New Label'
        self.initUI()

    def initUI(self):
        self.createFormGroupBox()
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | \
                QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        dialogLayout = QVBoxLayout()
        dialogLayout.addWidget(self.formGroupBox)
        dialogLayout.addWidget(buttonBox)
        self.setLayout(dialogLayout)
        self.setWindowTitle(self.title)

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox('Label form')
        self.lid = QLineEdit()
        self.lid.setValidator(QIntValidator())
        self.label = QLineEdit()
        self.shortcut = QKeySequenceEdit()
        layout = QFormLayout()
        layout.addRow(QLabel('id:'), self.lid)
        layout.addRow(QLabel('label:'), self.label)
        layout.addRow(QLabel('shortcut:'), self.shortcut)
        self.formGroupBox.setLayout(layout)


