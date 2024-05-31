from PyQt5.Qt import *
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem
from PyQt5 import QtWidgets, QtCore

from Model.database import session
from Model.model import Branch, Department, Inf_System, SziType
from View.main_container.setting_view import Ui_Form
from ViewModel.Helper_all import Helper_all
from config_helper import config


class Setting_view(QtWidgets.QDialog):
    def __init__(self, container):
        QDialog.__init__(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.s = session()

        self.first_boot = True

        self.ui.checkB_branch.stateChanged.connect(self.stateChanged_checkB_branch)
        self.ui.checkB_department.stateChanged.connect(self.stateChanged_checkB_department)
        self.ui.checkB_system.stateChanged.connect(self.stateChanged_checkB_system)
        self.ui.checkB_szi.stateChanged.connect(self.stateChanged_checkB_szi)

        self.ui.btn_cancel.clicked.connect(self.close)

        def user(self):
            self.create_tW_branch()
            self.create_tW_department()
            self.create_tW_system()
            self.create_tW_szi()

            self.load_tW_branch()
            self.load_tW_department()
            self.load_tW_system()
            self.load_tW_szi()

            self.load_checkBoks_branch()
            self.load_checkBox_department()
            self.load_checkBox_system()
            self.load_checkB_szi()
            self.load_status()

            self.ui.btn_save.clicked.connect(self.clicked_btn_saveUser)



        if container=='user':
            self.ui.label_name.setText('Сортировка и фильтр.')
            self.ui.label_nameStatus.setText('Статус работника:')

            user(self)

            current_indexPage = config['User']['current_indexPage']
            # self.ui.tabWidget.setCurrentIndex(int(current_indexPage))
            self.ui.tabWidget.setCurrentIndex(1)
        self.first_boot = False

    def stateChanged_checkBox_row(self, name_checkBox, name_table):
        '''Изменение состояние чекбоксов в таблицах'''

        def checked_unchecked_all_row(name_table, checkB_checket: bool):
            '''Изменяет состояние чекбоксов в таблице в зависисости включен ли верхний чекбокс или нет'''
            for i in range(name_table.rowCount()):
                if checkB_checket==False:
                    name_table.item(i, 1).setCheckState(QtCore.Qt.Unchecked)
                else:
                    name_table.item(i, 1).setCheckState(QtCore.Qt.Checked)

        if name_checkBox.isChecked():
            name_checkBox.setChecked(True)
            name_table.setEnabled(False)
        else:
            name_checkBox.setChecked(False)
            name_table.setEnabled(True)

        if self.first_boot == False:
            checked_unchecked_all_row(name_table, name_checkBox.isChecked())

    def stateChanged_checkB_branch(self):
        self.stateChanged_checkBox_row(self.ui.checkB_branch, self.ui.tW_branch)

    def stateChanged_checkB_department(self):
        self.stateChanged_checkBox_row(self.ui.checkB_department, self.ui.tW_department)

    def stateChanged_checkB_system(self):
        self.stateChanged_checkBox_row(self.ui.checkB_system, self.ui.tW_system)

    def stateChanged_checkB_szi(self):
        self.stateChanged_checkBox_row(self.ui.checkB_szi, self.ui.tW_szi)

    def create_tW_branch(self):
        numrows = 0
        numcols = 2

        self.ui.tW_branch.setColumnCount(numcols)
        self.ui.tW_branch.setRowCount(numrows)

        self.ui.tW_branch.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        self.ui.tW_branch.verticalHeader().setVisible(False)
        self.ui.tW_branch.horizontalHeader().setVisible(False)

        self.ui.tW_branch.setColumnHidden(0, True)

        header = self.ui.tW_branch.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

    def load_tW_branch(self):
        branches = self.s.query(Branch.id, Branch.name).order_by(Branch.name)
        checked_branch = config['User']['checked_branch']
        self.cheked_row_in_table(self.ui.tW_branch, branches, checked_branch)

    def create_tW_department(self):
        numrows = 0
        numcols = 2

        self.ui.tW_department.setColumnCount(numcols)
        self.ui.tW_department.setRowCount(numrows)

        self.ui.tW_department.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        self.ui.tW_department.verticalHeader().setVisible(False)
        self.ui.tW_department.horizontalHeader().setVisible(False)

        self.ui.tW_department.setColumnHidden(0, True)

        header = self.ui.tW_department.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

    def load_tW_department(self):
        department = self.s.query(Department.id, Department.name).order_by(Department.name)
        checked_department = config['User']['checked_department']
        self.cheked_row_in_table(self.ui.tW_department, department, checked_department)

    def create_tW_system(self):
        numrows = 0
        numcols = 2

        self.ui.tW_system.setColumnCount(numcols)
        self.ui.tW_system.setRowCount(numrows)

        self.ui.tW_system.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        self.ui.tW_system.verticalHeader().setVisible(False)
        self.ui.tW_system.horizontalHeader().setVisible(False)

        self.ui.tW_system.setColumnHidden(0, True)

        header = self.ui.tW_system.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

    def load_tW_system(self):
        system = self.s.query(Inf_System.id, Inf_System.inf_system).order_by(Inf_System.inf_system)
        checked_system = config['User']['checked_system']
        self.cheked_row_in_table(self.ui.tW_system, system, checked_system)

    def create_tW_szi(self):
        numrows = 0
        numcols = 2

        self.ui.tW_szi.setColumnCount(numcols)
        self.ui.tW_szi.setRowCount(numrows)

        self.ui.tW_szi.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        self.ui.tW_szi.verticalHeader().setVisible(False)
        self.ui.tW_szi.horizontalHeader().setVisible(False)

        self.ui.tW_szi.setColumnHidden(0, True)

        header = self.ui.tW_szi.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

    def load_tW_szi(self):
        sziType = self.s.query(SziType.id, SziType.name).order_by(SziType.name)
        checked_szi = config['User']['checked_szi']
        self.cheked_row_in_table(self.ui.tW_szi, sziType, checked_szi)

    def load_checkBoks_branch(self):
        checkBox_branch = config['User']['checkBox_branch']
        self.ui.checkB_branch.setChecked(Helper_all.convert_bool(checkBox_branch))
        self.stateChanged_checkBox_row(self.ui.checkB_branch, self.ui.tW_branch)

    def load_checkBox_department(self):
        checkBox_department = config['User']['checkBox_department']
        self.ui.checkB_department.setChecked(Helper_all.convert_bool(checkBox_department))
        self.stateChanged_checkBox_row(self.ui.checkB_department, self.ui.tW_department)

    def load_checkBox_system (self):
        checkBox_system = config['User']['checkBox_system']
        self.ui.checkB_system.setChecked(Helper_all.convert_bool(checkBox_system))
        self.stateChanged_checkBox_row(self.ui.checkB_system, self.ui.tW_system)

    def load_checkB_szi(self):
        checkBox_szi = config['User']['checkBox_szi']
        self.ui.checkB_szi.setChecked(Helper_all.convert_bool(checkBox_szi))
        self.stateChanged_checkBox_row(self.ui.checkB_szi, self.ui.tW_szi)

    def load_status(self):
        self.ui.checkB_statusOn.setChecked(Helper_all.convert_bool(config['User']['checkB_statusOn']))
        self.ui.checkB_statusOff.setChecked(Helper_all.convert_bool(config['User']['checkB_statusOff']))

    def get_Checked_id_tW(self, name_tW):
        '''Получаем список отмеченных id на подаваемой таблицы'''
        list_check_id = []
        for i in range(name_tW.rowCount()):
            if name_tW.item(i, 1).checkState() == Qt.CheckState.Checked:
                id = name_tW.item(i, 0).text()
                list_check_id.append(id)
        return list_check_id

    def clicked_btn_saveUser(self):
        config['User']['checked_branch'] = self.get_Checked_id_tW(self.ui.tW_branch)
        config['User']['checked_department'] = self.get_Checked_id_tW(self.ui.tW_department)
        config['User']['checked_system'] = self.get_Checked_id_tW(self.ui.tW_system)
        config['User']['checked_szi'] = self.get_Checked_id_tW(self.ui.tW_szi)

        config['User']['current_indexPage'] = self.ui.tabWidget.currentIndex()
        config['User']['checkBox_branch'] = self.ui.checkB_branch.isChecked()
        config['User']['checkBox_department'] = self.ui.checkB_department.isChecked()
        config['User']['checkBox_system'] = self.ui.checkB_system.isChecked()
        config['User']['checkBox_szi'] = self.ui.checkB_szi.isChecked()

        config['User']['checkB_statusOn'] = self.ui.checkB_statusOn.isChecked()
        config['User']['checkB_statusOff'] = self.ui.checkB_statusOff.isChecked()

        config.write()
        self.close()


    def cheked_row_in_table(self, name_table: QTableWidget, data, checked_item: list):
        '''Функция заполняет таблицу данными (data-Query), с отмеченными chekBox'''
        for i in data:

            if i[1] == '' or i[0] is None:
                continue

            rowPosition = name_table.rowCount()
            name_table.insertRow(rowPosition)

            name_table.setItem(rowPosition, 0, QTableWidgetItem(str(i[0])))

            chkBoxItem = QTableWidgetItem(i[1])
            chkBoxItem.setText(i[1])
            chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

            if str(i[0]) in checked_item:
                chkBoxItem.setCheckState(QtCore.Qt.Checked)
            else:
                chkBoxItem.setCheckState(QtCore.Qt.Unchecked)

            name_table.setItem(rowPosition, 1, chkBoxItem)
            name_table.setRowHeight(rowPosition, 8)