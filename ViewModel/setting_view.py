from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt5 import QtWidgets, Qt, QtCore

from Model.database import session
from Model.model import SziType, Inf_System, Branch, Department
from View.main_container.setting_view import Ui_Form
from Model.newTab_sortView import NewTab_sortView
from ViewModel.Helper_all import Helper_all
from config_helper import config
from stylesheet import style


class Setting_view(QtWidgets.QDialog):
    def __init__(self, container):
        QDialog.__init__(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.s = session()

        self.setStyleSheet(style)

        self.first_boot = True

    #     self.buildTabs()
    #
    # def buildTabs(self):
    #
    #     page = NewTab_sortView()
    #     text = ('TAB ')
    #     self.ui.tabWidget.addTab(page, text)
    #
    #     self.ui.checkB_branch.stateChanged.connect(self.stateChanged_checkB_branch)
    #     self.ui.checkB_department.stateChanged.connect(self.stateChanged_checkB_department)
    #     self.ui.checkB_system.stateChanged.connect(self.stateChanged_checkB_system)
    #     self.ui.checkB_szi.stateChanged.connect(self.stateChanged_checkB_szi)
    #
    #     self.ui.btn_cancel.clicked.connect(self.close)

        def user(self):
            self.create_tW_branch()
            self.create_tW_department()
            self.create_tW_system()
            self.create_tW_szi()

            self.load_tW_branch('User')
            self.load_tW_department('User')
            self.load_tW_system('User')
            self.load_tW_szi('User')

            self.load_checkBoks_branch('User')
            self.load_checkBox_department('User')
            self.load_checkBox_system('User')
            self.load_checkB_szi('User')
            self.load_status('User')

            self.ui.btn_save.clicked.connect(self.clicked_btn_saveUser)

        def skr(self):
            self.ui.tabWidget.setTabVisible(2, False)
            self.ui.tabWidget.setTabVisible(3, False)

            self.create_tW_branch()
            self.create_tW_department()

            self.load_tW_branch('Skr')
            self.load_tW_department('Skr')

            self.load_checkBoks_branch('Skr')
            self.load_checkBox_department('Skr')
            self.load_status('Skr')

            self.ui.btn_save.clicked.connect(self.clicked_btn_saveSkr)

        def equipment(self):
            self.ui.tabWidget.setTabVisible(2, False)
            self.ui.tabWidget.setTabVisible(3, False)

            self.create_tW_branch()
            self.create_tW_department()

            self.load_tW_branch('Equipment')
            self.load_tW_department('Equipment')

            self.load_checkBoks_branch('Equipment')
            self.load_checkBox_department('Equipment')
            self.load_status('Equipment')

            self.ui.btn_save.clicked.connect(self.clicked_btn_saveEquipment)

        def szi(self):

            self.buildTabs(self, 8)

            self.ui.tabWidget.setTabVisible(2, False)
            self.ui.tabWidget.setTabVisible(3, False)

            self.create_tab_sziType()

            self.create_tW_branch()
            self.create_tW_department()

            self.load_tW_branch('Szi')
            self.load_tW_department('Szi')

            self.load_checkBoks_branch('Szi')
            self.load_checkBox_department('Szi')
            self.load_status('Szi')

            self.ui.btn_save.clicked.connect(self.clicked_btn_saveSzi)

        def usb(self):
            self.ui.tabWidget.setTabVisible(2, False)
            self.ui.tabWidget.setTabVisible(3, False)

            self.create_tW_branch()
            self.create_tW_department()

            self.load_tW_branch('Usb')
            self.load_tW_department('Usb')

            self.load_checkBoks_branch('Usb')
            self.load_checkBox_department('Usb')
            self.load_status('Usb')

            self.ui.btn_save.clicked.connect(self.clicked_btn_saveUsb)

        if container == 'user':
            self.ui.label_name.setText('Сортировка и фильтр.')
            self.ui.label_nameStatus.setText('Статус работника:')

            user(self)
            self.load_indexPage('User')

        elif container == 'usb':
            self.ui.label_name.setText('Сортировка и фильтр.')
            self.ui.label_nameStatus.setText('Статус USB устройства:')
            self.ui.checkB_statusOn.setText('Исправен')
            self.ui.checkB_statusOff.setText('Не исправен')

            usb(self)
            self.load_indexPage('Usb')

        elif container == 'equipment':
            self.ui.label_name.setText('Сортировка и фильтр.')
            self.ui.label_nameStatus.setText('Статус оргтехники:')
            self.ui.checkB_statusOn.setText('Исправен')
            self.ui.checkB_statusOff.setText('Не исправен')

            equipment(self)
            self.load_indexPage('Equipment')

        elif container == 'skr':
            self.ui.label_name.setText('Сортировка и фильтр.')
            self.ui.label_nameStatus.setText('Статус пломбы - наклейки:')
            self.ui.checkB_statusOn.setText('Актуален')
            self.ui.checkB_statusOff.setVisible(False)

            skr(self)
            self.load_indexPage('Skr')

        elif container == 'szi':
            self.ui.label_name.setText('Сортировка и фильтр.')
            self.ui.label_nameStatus.setText('Статус СЗИ:')
            self.ui.checkB_statusOn.setText('Актуален')
            self.ui.checkB_statusOff.setText('Удален')

            szi(self)
            self.load_indexPage('Szi')


        self.first_boot = False

    def create_tab_sziType(self):

        def stateChanged_checkBox_typeSzi():
            self.stateChanged_checkBox_row(self.checkBox_typeSzi, self.tW_sziType)

        def create_sziTab():
            self.szi_tab = QtWidgets.QWidget()
            self.ui.tabWidget.addTab(self.szi_tab, 'СЗИ')

        def create_checkBox_typeSzi():
            self.checkBox_typeSzi = QtWidgets.QCheckBox('Все СЗИ')
            self.checkBox_typeSzi.stateChanged.connect(stateChanged_checkBox_typeSzi)

        def create_tW_sziType():
            '''Создаем табицу инфо szi_type'''
            self.tW_sziType = QtWidgets.QTableWidget()
            self.tW_sziType.setWordWrap(True)
            self.tW_sziType.setCornerButtonEnabled(True)
            self.tW_sziType.viewport().installEventFilter(self)
            self.tW_sziType.setAcceptDrops(True)
            self.tW_sziType.setShowGrid(False)

            numrows = 0
            numcols = 2

            self.tW_sziType.setColumnCount(numcols)
            self.tW_sziType.setRowCount(numrows)

            self.tW_sziType.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
            self.tW_sziType.verticalHeader().setVisible(False)
            self.tW_sziType.horizontalHeader().setVisible(False)

            self.tW_sziType.setColumnHidden(0, True)

            header = self.tW_sziType.horizontalHeader()
            header.setSectionResizeMode(1, QHeaderView.Stretch)

        def addWidget_layout():
            self.szi_tab_layout = QtWidgets.QVBoxLayout()
            self.szi_tab.setLayout(self.szi_tab_layout)

            self.szi_tab.layout().addWidget(self.checkBox_typeSzi)
            self.szi_tab_layout.addWidget(self.tW_sziType)

        def load_tW_szi_type():
            szi_types = self.s.query(SziType.id, SziType.name).order_by(SziType.name).filter(SziType.name != '')
            checked_sziType = config['Szi']['checked_sziType']
            self.cheked_row_in_table(self.tW_sziType, szi_types, checked_sziType)

        create_sziTab()
        create_checkBox_typeSzi()
        create_tW_sziType()
        addWidget_layout()
        load_tW_szi_type()

        self.checkBox_typeSzi.setChecked(Helper_all.convert_bool(config['Szi']['checkBox_typeSzi']))


    def clicked_btn_saveSzi(self):
        config['Szi']['checked_branch'] = self.get_Checked_id_tW(self.ui.tW_branch)
        config['Szi']['checked_department'] = self.get_Checked_id_tW(self.ui.tW_department)
        config['Szi']['checked_sziType'] = self.get_Checked_id_tW(self.tW_sziType)

        config['Szi']['current_indexPage'] = self.ui.tabWidget.currentIndex()
        config['Szi']['checkBox_branch'] = self.ui.checkB_branch.isChecked()
        config['Szi']['checkBox_department'] = self.ui.checkB_department.isChecked()
        config['Szi']['checkBox_typeSzi'] = self.checkBox_typeSzi.isChecked()

        config['Szi']['checkB_statusOn'] = self.ui.checkB_statusOn.isChecked()
        config['Szi']['checkB_statusOff'] = self.ui.checkB_statusOff.isChecked()

        config.write()
        self.close()



    def load_indexPage(self, modul):
        current_indexPage = config[modul]['current_indexPage']
        if current_indexPage == '':
            current_indexPage = 0
        self.ui.tabWidget.setCurrentIndex(int(current_indexPage))

    def stateChanged_checkBox_row(self, name_checkBox, name_table):
        '''Изменение состояние чекбоксов в таблицах'''

        def checked_unchecked_all_row(name_table, checkB_checket: bool):
            '''Изменяет состояние чекбоксов в таблице в зависисости включен ли верхний чекбокс или нет'''
            for i in range(name_table.rowCount()):
                if checkB_checket == False:
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

    def load_tW_branch(self, modul):
        branches = self.s.query(Branch.id, Branch.name).order_by(Branch.name)
        checked_branch = config[modul]['checked_branch']
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

    def load_tW_department(self, modul):
        department = self.s.query(Department.id, Department.name).order_by(Department.name)
        checked_department = config[modul]['checked_department']
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

    def load_tW_system(self, modul):
        system = self.s.query(Inf_System.id, Inf_System.inf_system).order_by(Inf_System.inf_system)
        checked_system = config[modul]['checked_system']
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

    def load_tW_szi(self, modul):
        sziType = self.s.query(SziType.id, SziType.name).order_by(SziType.name)
        checked_szi = config[modul]['checked_szi']
        self.cheked_row_in_table(self.ui.tW_szi, sziType, checked_szi)

    def load_checkBoks_branch(self, modul):
        checkBox_branch = config[modul]['checkBox_branch']
        self.ui.checkB_branch.setChecked(Helper_all.convert_bool(checkBox_branch))
        self.stateChanged_checkBox_row(self.ui.checkB_branch, self.ui.tW_branch)

    def load_checkBox_department(self, modul):
        checkBox_department = config[modul]['checkBox_department']
        self.ui.checkB_department.setChecked(Helper_all.convert_bool(checkBox_department))
        self.stateChanged_checkBox_row(self.ui.checkB_department, self.ui.tW_department)

    def load_checkBox_system(self, modul):
        checkBox_system = config[modul]['checkBox_system']
        self.ui.checkB_system.setChecked(Helper_all.convert_bool(checkBox_system))
        self.stateChanged_checkBox_row(self.ui.checkB_system, self.ui.tW_system)

    def load_checkB_szi(self, modul):
        checkBox_szi = config[modul]['checkBox_szi']
        self.ui.checkB_szi.setChecked(Helper_all.convert_bool(checkBox_szi))
        self.stateChanged_checkBox_row(self.ui.checkB_szi, self.ui.tW_szi)

    def load_status(self, modul):
        self.ui.checkB_statusOn.setChecked(Helper_all.convert_bool(config[modul]['checkB_statusOn']))
        self.ui.checkB_statusOff.setChecked(Helper_all.convert_bool(config[modul]['checkB_statusOff']))

    def get_Checked_id_tW(self, name_tW):
        '''Получаем список отмеченных id на подаваемой таблицы'''
        list_check_id = []
        for i in range(name_tW.rowCount()):
            if name_tW.item(i, 1).checkState() == Qt.CheckState.Checked:
                id = name_tW.item(i, 0).text()
                list_check_id.append(id)
        return list_check_id

    def clicked_btn_saveSkr(self):
        config['Skr']['checked_branch'] = self.get_Checked_id_tW(self.ui.tW_branch)
        config['Skr']['checked_department'] = self.get_Checked_id_tW(self.ui.tW_department)

        config['Skr']['current_indexPage'] = self.ui.tabWidget.currentIndex()
        config['Skr']['checkBox_branch'] = self.ui.checkB_branch.isChecked()
        config['Skr']['checkBox_department'] = self.ui.checkB_department.isChecked()

        config['Skr']['checkB_statusOn'] = self.ui.checkB_statusOn.isChecked()
        config['Skr']['checkB_statusOff'] = self.ui.checkB_statusOff.isChecked()

        config.write()
        self.close()

    def clicked_btn_saveEquipment(self):
        config['Equipment']['checked_branch'] = self.get_Checked_id_tW(self.ui.tW_branch)
        config['Equipment']['checked_department'] = self.get_Checked_id_tW(self.ui.tW_department)

        config['Equipment']['current_indexPage'] = self.ui.tabWidget.currentIndex()
        config['Equipment']['checkBox_branch'] = self.ui.checkB_branch.isChecked()
        config['Equipment']['checkBox_department'] = self.ui.checkB_department.isChecked()

        config['Equipment']['checkB_statusOn'] = self.ui.checkB_statusOn.isChecked()
        config['Equipment']['checkB_statusOff'] = self.ui.checkB_statusOff.isChecked()

        config.write()
        self.close()



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

    def clicked_btn_saveUsb(self):
        config['Usb']['checked_branch'] = self.get_Checked_id_tW(self.ui.tW_branch)
        config['Usb']['checked_department'] = self.get_Checked_id_tW(self.ui.tW_department)

        config['Usb']['current_indexPage'] = self.ui.tabWidget.currentIndex()
        config['Usb']['checkBox_branch'] = self.ui.checkB_branch.isChecked()
        config['Usb']['checkBox_department'] = self.ui.checkB_department.isChecked()

        config['Usb']['checkB_statusOn'] = self.ui.checkB_statusOn.isChecked()
        config['Usb']['checkB_statusOff'] = self.ui.checkB_statusOff.isChecked()

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


style = '''

    QTableWidget{
        background-color: white;
        border: 0px solid #3873d9;
    }
'''
