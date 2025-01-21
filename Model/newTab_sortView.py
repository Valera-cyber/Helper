from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableWidgetItem, QWidget
from PyQt5 import QtWidgets, QtCore
from ViewModel.Helper_all import Helper_all
from config_helper import config

class NewTab_sortView(QtWidgets.QWidget):
    def __init__(self, title, ui, helper_module, data):
        super(NewTab_sortView, self).__init__()

        self.layout = QtWidgets.QVBoxLayout(self)

        index = list(helper_module.keys())
        self.module = index[0]  # Получили ключ словаря
        self.module1 = helper_module[self.module]  # Получили значение по ключу

        self.data = data

        self.title = title
        self.ui = ui

        self.first_boot = False

        self.create_tW_item()
        self.create_chekBox_all()

        self.print_cheked_row_tW_item()

    def color_titele(self):
        if self.checkBox_all.isChecked():
            self.ui.tabWidget.tabBar().setTabTextColor(self.ui.tabWidget.currentIndex(), QColor("gray"))
        else:
            self.ui.tabWidget.tabBar().setTabTextColor(self.ui.tabWidget.currentIndex(), QColor("black"))

    def create_chekBox_all(self):
        self.checkBox_all = QtWidgets.QCheckBox(self.title)
        self.layout.insertWidget(0, self.checkBox_all)
        self.checkBox_all.stateChanged.connect(self.stateChanged_checkBox_row)

        status_checkBox_all = Helper_all.convert_bool(config[self.module]['checkBox_all_' + self.module1])
        self.checkBox_all.setChecked(status_checkBox_all)

    def create_tW_item(self):
        '''Создаем табицу'''
        self.tW_item = QtWidgets.QTableWidget()
        self.tW_item.setWordWrap(True)
        self.tW_item.setCornerButtonEnabled(True)
        self.tW_item.viewport().installEventFilter(self)
        self.tW_item.setAcceptDrops(True)
        self.tW_item.setShowGrid(False)

        numrows = 0
        numcols = 2

        self.tW_item.setColumnCount(numcols)
        self.tW_item.setRowCount(numrows)

        self.tW_item.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        self.tW_item.verticalHeader().setVisible(False)
        self.tW_item.horizontalHeader().setVisible(False)

        self.tW_item.setColumnHidden(0, True)

        header = self.tW_item.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.layout.insertWidget(1, self.tW_item)

    def print_cheked_row_tW_item(self):
        '''Функция заполняет таблицу данными (data-Query), с отмеченными chekBox'''

        checked_item = config[self.module]['checked_item_' + self.module1]

        for i in self.data:

            if i[1] == '' or i[0] is None:
                continue

            rowPosition = self.tW_item.rowCount()
            self.tW_item.insertRow(rowPosition)

            self.tW_item.setItem(rowPosition, 0, QTableWidgetItem(str(i[0])))

            chkBoxItem = QTableWidgetItem(i[1])
            chkBoxItem.setText(i[1])
            chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

            if str(i[0]) in checked_item:
                chkBoxItem.setCheckState(QtCore.Qt.Checked)
            else:
                chkBoxItem.setCheckState(QtCore.Qt.Unchecked)

            self.tW_item.setItem(rowPosition, 1, chkBoxItem)
            self.tW_item.setRowHeight(rowPosition, 8)

    def stateChanged_checkBox_row(self):
        '''Изменение состояние чекбоксов в таблицах'''

        def checked_unchecked_all_row(name_table, checkB_checket: bool):
            '''Изменяет состояние чекбоксов в таблице в зависисости включен ли верхний чекбокс или нет'''
            for i in range(name_table.rowCount()):
                if checkB_checket == False:
                    name_table.item(i, 1).setCheckState(QtCore.Qt.Unchecked)
                else:
                    name_table.item(i, 1).setCheckState(QtCore.Qt.Checked)

        if self.checkBox_all.isChecked():
            self.checkBox_all.setChecked(True)
            self.tW_item.setEnabled(False)
        else:
            self.checkBox_all.setChecked(False)
            self.tW_item.setEnabled(True)

        if self.first_boot == False:
            checked_unchecked_all_row(self.tW_item, self.checkBox_all.isChecked())

            self.color_titele()
