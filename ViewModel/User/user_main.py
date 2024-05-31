import os
import subprocess, sys
import openpyxl
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QPushButton, QTableWidgetSelectionRange
from PyQt5 import QtWidgets, QtCore
from sqlalchemy import or_
from sqlalchemy.sql.functions import user, coalesce
from functools import partial
from Model.database import session
from Model.model import User, Department, Branch, User_System, SziFileInst, SziAccounting
from View.main_container.container import Ui_MainWindow
from ViewModel.Helper_all import Helper_all
from ViewModel.User.user_new import User_new
from ViewModel.setting_view import Setting_view
from config_helper import config


class User_main(QtWidgets.QMainWindow):
    def __init__(self, path_helper):
        super(User_main, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.s = session()

        self.create_table()

        self.print_tW_user()

        self.path_helper = path_helper

        self.btn_newUser()
        self.btn_editUser()
        self.btn_settingViewUser()
        self.btn_expotyExl()

        self.ui.lineEdit_searchUser.textChanged.connect(partial(self.print_tW_user, None))

        horizSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.ui.horizontalLayout_4.addItem(horizSpacer)

        width = QtWidgets.qApp.desktop().availableGeometry(self).width()
        self.ui.splitter.setSizes([width * 1 / 3, width * 2 / 3])

    def btn_newUser(self):
        btn_newUser = QPushButton('     Добавить\n пользователя')
        self.ui.horizontalLayout_4.addWidget(btn_newUser)
        btn_newUser.setIcon(QIcon(self.path_helper + '/Icons/User/add-user-male-40.png'))
        btn_newUser.setIconSize(QtCore.QSize(40, 40))
        btn_newUser.clicked.connect(self.clicked_btn_newUser)

    def btn_editUser(self):
        btn_editUser = QPushButton('Редактировать\n пользователя')
        self.ui.horizontalLayout_4.addWidget(btn_editUser)
        btn_editUser.setIcon(QIcon(self.path_helper + '/Icons/User/registration-40.png'))
        btn_editUser.setIconSize(QtCore.QSize(40, 40))
        btn_editUser.clicked.connect(self.clicked_btn_editUser)

    def btn_settingViewUser(self):
        btn_settingViewUser = QPushButton('Сортировка\n  и фильтр')
        self.ui.horizontalLayout_4.addWidget(btn_settingViewUser)
        btn_settingViewUser.setIcon(QIcon(self.path_helper + '/Icons/User/search-user-40.png'))
        btn_settingViewUser.setIconSize(QtCore.QSize(40, 40))
        btn_settingViewUser.clicked.connect(self.clicked_settingViewUser)

    def btn_expotyExl(self):
        btn_expotyExl = QPushButton(' Экспорт \n    XLSX')
        self.ui.horizontalLayout_4.addWidget(btn_expotyExl)
        btn_expotyExl.setIcon(QIcon(self.path_helper + '/Icons/User/microsoft-excel-40.png'))
        btn_expotyExl.setIconSize(QtCore.QSize(40, 40))
        btn_expotyExl.clicked.connect(self.clicked_excel)

    def clicked_excel(self):
        '''Экспорт пользователей в эксель'''
        count_row = self.ui.tW_users.rowCount()
        list_employeeId = []
        for i in range(count_row):
            list_employeeId.append(self.ui.tW_users.item(i, 0).text())
        list_export_users = []
        for i in list_employeeId:
            list_export_users.append(
                self.s.query(User.employeeId, User.fio, Department.name, User.post, User.phone, User.eMail,
                             User.address, User.login, User.dk, User.armName).select_from(User).join(Department).filter(
                    User.employeeId == i).one())

        wb = openpyxl.Workbook()
        sheet = wb.sheetnames
        lis = wb.active
        # Создание строки с заголовками
        lis.append(('Табельный номер', 'ФИО', 'Служба', 'Должность', 'Телефон', 'Почта', 'Расположение', 'Логин',
                    'Договор конфиденциальности', 'Доступные АРМ'))
        for user in list_export_users:
            lis.append(list(user))
        wb.save(filename=self.path_helper+'/'+'User_files'+'/'+'users.xlsx')
        # subprocess.Popen(self.path_helper+'/'+"users.xlsx", shell=True)
        # os.startfile(self.path_helper+'/'+"users.xlsx")
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, "users.xlsx"])

    def clicked_settingViewUser(self):
        self.settingViewUser = Setting_view('user')
        self.settingViewUser.exec_()
        self.print_tW_user()

    def clicked_btn_editUser(self):
        employeeId = self.get_employeeId()
        if employeeId is not None:
            self.new_user = User_new(employeeId)
            self.new_user.exec_()
            self.print_tW_user(int(employeeId))

    def clicked_btn_newUser(self):
        self.new_user = User_new()
        self.new_user.exec_()
        employeeId = self.get_employeeId()
        try:
            employeeId = self.new_user.employeeId
        except:
            employeeId = employeeId
        self.print_tW_user(employeeId)

    def get_employeeId(self):
        if self.ui.tW_users.item(self.ui.tW_users.currentRow(), 0) is None:
            return None
        else:
            return self.ui.tW_users.item(self.ui.tW_users.currentRow(), 0).text()

    def print_fill_user(self, employeeId):
        user = self.s.query(User, Department.name, Branch.name). \
            join(Department).join(Branch). \
            filter(User.employeeId == employeeId). \
            one()

        self.ui.item_data.setItem(0, 1, QTableWidgetItem(user[2]))
        self.ui.item_data.setItem(1, 1, QTableWidgetItem(user[1]))
        self.ui.item_data.setItem(2, 1, QTableWidgetItem(str(user[0].employeeId)))
        self.ui.item_data.setItem(3, 1, QTableWidgetItem(user[0].fio))
        self.ui.item_data.setItem(4, 1, QTableWidgetItem(user[0].post))
        self.ui.item_data.setItem(5, 1, QTableWidgetItem(user[0].eMail))
        self.ui.item_data.setItem(6, 1, QTableWidgetItem(user[0].eMail))
        self.ui.item_data.setItem(7, 1, QTableWidgetItem(user[0].address))
        self.ui.item_data.setItem(8, 1, QTableWidgetItem(user[0].login))
        self.ui.item_data.setItem(9, 1, QTableWidgetItem(user[0].dk))
        self.ui.item_data.setItem(10, 1, QTableWidgetItem(user[0].armName))
        self.checkBox_status.setChecked(user[0].statusWork)

    def changed_current_cell_user(self):
        user_id = self.get_employeeId()
        if user_id is not None:
            self.print_fill_user(user_id)
        else:
            self.ui.item_data.setItem(0, 1, QTableWidgetItem(''))
            self.ui.item_data.setItem(1, 1, QTableWidgetItem(''))
            self.ui.item_data.setItem(2, 1, QTableWidgetItem(''))
            self.ui.item_data.setItem(3, 1, QTableWidgetItem(''))
            self.ui.item_data.setItem(4, 1, QTableWidgetItem(''))
            self.ui.item_data.setItem(5, 1, QTableWidgetItem(''))
            self.ui.item_data.setItem(6, 1, QTableWidgetItem(''))
            self.ui.item_data.setItem(7, 1, QTableWidgetItem(''))
            self.ui.item_data.setItem(8, 1, QTableWidgetItem(''))
            self.ui.item_data.setItem(9, 1, QTableWidgetItem(''))
            self.ui.item_data.setItem(10, 1, QTableWidgetItem(''))
            self.ui.item_data.setItem(11, 1, QTableWidgetItem(''))

    def create_table(self):
        def create_item_data():
            numrows = 12
            numcols = 2

            self.ui.item_data.setColumnCount(numcols)
            self.ui.item_data.setRowCount(numrows)

            header = self.ui.item_data.horizontalHeader()
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            self.ui.item_data.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

            self.ui.item_data.horizontalHeader().setVisible(False)
            self.ui.item_data.verticalHeader().setVisible(False)

            self.ui.item_data.setItem(0, 0, QTableWidgetItem('Филиал:'))
            self.ui.item_data.setItem(1, 0, QTableWidgetItem('Служба:'))
            self.ui.item_data.setItem(2, 0, QTableWidgetItem('Табельный №:'))
            self.ui.item_data.setItem(3, 0, QTableWidgetItem('ФИО:'))
            self.ui.item_data.setItem(4, 0, QTableWidgetItem('Должность:'))
            self.ui.item_data.setItem(5, 0, QTableWidgetItem('Телефон:'))
            self.ui.item_data.setItem(6, 0, QTableWidgetItem('Почта:'))
            self.ui.item_data.setItem(7, 0, QTableWidgetItem('Расположение:'))
            self.ui.item_data.setItem(8, 0, QTableWidgetItem('Логин:'))
            self.ui.item_data.setItem(9, 0, QTableWidgetItem('ДК:'))
            self.ui.item_data.setItem(10, 0, QTableWidgetItem('АРМ:'))
            self.ui.item_data.setItem(11, 0, QTableWidgetItem('Работает:'))

            qt_size = self.getQTableWidgetSize(self.ui.item_data)
            self.ui.item_data.setMaximumHeight(qt_size.height())
            self.ui.item_data.setMinimumSize(qt_size)

            self.checkBox_status = QtWidgets.QCheckBox()
            self.ui.item_data.setCellWidget(11, 1, self.checkBox_status)
            self.checkBox_status.setEnabled(False)

            for rowPosition in range(numrows):
                self.ui.item_data.item(rowPosition, 0).setBackground(QBrush(Qt.lightGray))  # серый фон
                self.ui.item_data.item(rowPosition, 0).setTextAlignment(
                    Qt.AlignVCenter | Qt.AlignRight)  # Выравнивание по правому краю
                self.ui.item_data.item(rowPosition, 0).setFlags(
                    Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # запрет редактирования

            table = QTableWidgetItem()
            table.setTextAlignment(3)

            self.ui.item_data.setEditTriggers(QAbstractItemView.AllEditTriggers)
            self.ui.item_data.setFocusPolicy(Qt.NoFocus)
            self.ui.item_data.setSelectionMode(QAbstractItemView.NoSelection)

        def create_tW_user():
            numrows = 0
            numcols = 2

            self.ui.tW_users.setColumnCount(numcols)
            self.ui.tW_users.setRowCount(numrows)

            self.ui.tW_users.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
            self.ui.tW_users.verticalHeader().setVisible(False)

            self.ui.tW_users.setHorizontalHeaderItem(0, QTableWidgetItem('employeeId'))
            self.ui.tW_users.setHorizontalHeaderItem(1, QTableWidgetItem('Пользователи'))
            self.ui.tW_users.setColumnHidden(0, True)

            header = self.ui.tW_users.horizontalHeader()
            header.setSectionResizeMode(1, QHeaderView.Stretch)

            self.ui.tW_users.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
            self.ui.tW_users.itemSelectionChanged.connect(self.changed_current_cell_user)

        create_item_data()
        create_tW_user()

    def print_tW_user(self, id_user=None):
        def load_users():

            checked_branch = config['User']['checked_branch']
            checked_branch = list(checked_branch)

            checked_department = config['User']['checked_department']
            checked_department = list(checked_department)

            checked_szi = list(map(int, config['User']['checked_szi']))
            if Helper_all.convert_bool(config['User']['checkBox_szi']) == True:
                checked_szi.append(0)

            checked_system = list(map(int, config['User']['checked_system']))
            if Helper_all.convert_bool(config['User']['checkBox_system']) == True:
                checked_system.append(0)

            serch_text = '%' + self.ui.lineEdit_searchUser.text() + '%'
            if serch_text == '':
                serch_text = '%'

            status_work = Helper_all.get_status(Helper_all.convert_bool(config['User']['checkB_statusOn']),
                                                Helper_all.convert_bool(config['User']['checkB_statusOff']))

            # else:
            user = self.s.query(User.employeeId, User.fio).select_from(User). \
                join(User_System, isouter=True). \
                join(SziFileInst, isouter=True). \
                join(SziAccounting, isouter=True). \
                filter(or_(
                coalesce(SziAccounting.sziType_id, 0).in_((checked_szi))),
                coalesce(SziAccounting.status, True) == True). \
                filter(coalesce(User_System.id_inf_system, 0).in_((checked_system))). \
                filter(User.branch_id.in_((checked_branch))). \
                filter(User.departmet_id.in_((checked_department))). \
                filter(User.statusWork.like(status_work)). \
                filter(or_(
                User.employeeId.like(serch_text),
                User.fio.like(serch_text),
                User.post.like(serch_text),
                User.phone.like(serch_text),
                User.eMail.like(serch_text),
                User.address.like(serch_text),
                User.login.like(serch_text),
                User.dk.like(serch_text),
                User.armName.like(serch_text))). \
                group_by(User.employeeId). \
                order_by(User.fio)

            return user

        self.ui.tW_users.setRowCount(0)

        users = load_users()

        self.ui.statusbar.showMessage('Количество: ' + str(users.count()))

        for i in users:
            rowPosition = self.ui.tW_users.rowCount()
            self.ui.tW_users.insertRow(rowPosition)

            self.ui.tW_users.setItem(rowPosition, 0, QTableWidgetItem(str(i[0])))
            self.ui.tW_users.setItem(rowPosition, 1, QTableWidgetItem(i[1]))

        self.select_row_intable((id_user))

    def select_row_intable(self, employeeId):
        '''Функция выделяющая строку в таблице, ели employeeId=None первую строку,
        если есть выделяет указанную'''
        if employeeId == None:
            if self.ui.tW_users.rowCount() > 0:
                self.ui.tW_users.setRangeSelected(QTableWidgetSelectionRange(0, 1, 0, 1), True)
                self.print_fill_user(self.ui.tW_users.item(0, 0).text())
                self.ui.scrollArea.setVisible(True)
            else:
                self.ui.scrollArea.setVisible(False)
        else:
            for i in range(self.ui.tW_users.rowCount()):
                if int(self.ui.tW_users.item(i, 0).text()) == int(employeeId):
                    self.ui.tW_users.selectRow(i)

        # else:

    def getQTableWidgetSize(self, table):
        w = table.verticalHeader().width() - 15  # +4 seems to be needed
        for i in range(table.columnCount()):
            w += table.columnWidth(i)  # seems to include gridline (on my machine)
        h = table.horizontalHeader().height()  # +4 seems to be needed
        for i in range(table.rowCount()):
            h += table.rowHeight(i)
        return QtCore.QSize(w, h)
