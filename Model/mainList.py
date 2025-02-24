from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QTableWidget
from Model.database import session

class MainList(QTableWidget):
    dataSignal = pyqtSignal(str)
    def __init__(self, sql_data, setColumnHidden: bool):
        super(MainList, self).__init__()

        self.s = session()
        self.sql_data=sql_data

        self.setColumnCount(2)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.setColumnHidden(0, setColumnHidden)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # select all row
        self.setShowGrid(False)

        self.itemSelectionChanged.connect(self.item_selection_changed)

        self.update_mainList(self.sql_data, 0)



    def update_mainList(self, sql_data, selectRow_id):

        selectRow = 0
        self.setRowCount(0)

        for i in sql_data:
            rowPosition = self.rowCount()
            self.insertRow(rowPosition)

            self.setItem(rowPosition, 0, QTableWidgetItem(str(i[0])))
            self.setItem(rowPosition, 1, QTableWidgetItem(i[1]))

            if (i[0])==selectRow_id:
                selectRow = rowPosition
                self.selectRow(rowPosition)

            if selectRow==0:
                self.selectRow(0)

    def item_selection_changed(self):
        if self.item(self.currentRow(),0) is not None:
            self.current_id = self.item(self.currentRow(), 0).text()
            self.dataSignal.emit(self.current_id)
        else:
            self.current_id=''
            self.dataSignal.emit(self.current_id)

    def get_id(self):
        '''Получаем id выделенной ячейки'''
        if self.item(self.currentRow(), 0) is None:
            return None
        else:
            return self.item(self.currentRow(), 0).text()