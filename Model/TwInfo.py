from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QTableWidget
from Model.database import session


class TwInfo(QTableWidget):
    def __init__(self, name_column:list, height_row):
        super(TwInfo, self).__init__()
        self.height_row = height_row
        self.s = session()

        self.setShowGrid(False)
        self.setWordWrap(True)
        self.setCornerButtonEnabled(True)
        self.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)

        numrows = len(name_column)
        numcols = 2

        self.setColumnCount(numcols)
        self.setRowCount(numrows)

        for i in sorted(name_column):
            self.setItem(i, 0, QTableWidgetItem(name_column[i]))

        self.set_height_qtable(numrows, self.height_row)
        self.set_style_qtable(numrows)

    def set_style_qtable(self, numrows):
        for rowPosition in range(numrows):
            self.item(rowPosition, 0).setBackground(QBrush(Qt.lightGray))  # серый фон
            self.item(rowPosition, 0).setTextAlignment(
                Qt.AlignVCenter | Qt.AlignRight)  # Выравнивание по правому краю
            self.item(rowPosition, 0).setFlags(
                Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # запрет редактирования

        header = self.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

    def update_tw_info(self, column_1: dict):
        '''Словарь ключ- номер строки значение- сама строка '''
        for i in sorted(column_1):
            self.setItem(i, 1, QTableWidgetItem(column_1[i]))

    def set_height_qtable(self, row_count, height_row):
        '''Задаем высоту таблицы от колличества строк+высота заголовка'''
        height_heder = 24
        height_tW = ((row_count * height_row) + height_heder)

        vh = self.verticalHeader()
        vh.setDefaultSectionSize(height_row)

        self.setMaximumHeight(height_tW - 22)
        self.setMinimumHeight(height_tW - 22)
