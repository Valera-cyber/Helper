from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from sqlalchemy import or_
from sqlalchemy.sql.functions import coalesce
from Model.BtnWrap import BtnWrap
from Model.ExportExls import ExportXlsx
from Model.MainForm import MainForm
from Model.TwInfo import TwInfo
from Model.model import User, User_System, SziFileInst, SziAccounting, Department, Branch
from ViewModel.Helper_all import Helper_all
from ViewModel.User.UserNewForm import UserNewForm
from ViewModel.User.UserSortForm import UserSortForm
from config_helper import config
from stylesheet import blue_color_tw_text


class UserMainForm(MainForm):
    def __init__(self):
        super(UserMainForm, self).__init__()

        self.path_helper = config['Setting_helper']['path_helper']
        self.setWindowTitle('Пользователи')
        self.setWindowIcon(QIcon(self.path_helper + '/Icons/user.png'))

        self.btn_new.clicked.connect(self.clicked_btn_new)
        self.btn_new.setToolTip('Добавить нового пользователя')

        self.btn_edit.clicked.connect(self.clicked_btn_edit)
        self.btn_edit.setToolTip('Изменить данные текущего пользователя')

        self.btn_sort.clicked.connect(self.clicked_btn_sort)
        self.btn_sort.setToolTip('Отфильтровать список по критериям')

        self.btn_export.clicked.connect(self.clicked_btn_export)
        self.btn_export.setToolTip('Экспортировать текущий список пользователей в XLSX')

        self.create_btn_wrap_info(0)
        self.create_tw_info(1)

        self.update_tw_mainList(self.load_user())

        self.ui.verticalLayout_info.addStretch()

        self.BUTTON_DISPLAY = ('ФИО:', 'И.О. Ф:', 'Ф И.О.:')
        self.fio = ''

        self.ui.lineEdit_searchUser.textChanged.connect(partial(lambda: self.update_tw_mainList(self.load_user())))

    def display_fio(self):
        '''Функция изменения отображения ФИО'''
        if self.fio != None:
            index = self.tW_info.item(3, 0).text()
            self.tW_info.setItem(3, 1, QTableWidgetItem(Helper_all.display_fio(self.fio, index)))

    #####################################################

    def update_tw_info(self, id_item):
        if self.btn_wrap_info.isChecked():
            if id_item != None:
                user = self.s.query(User, Department.name, Branch.name). \
                    join(Department).join(Branch). \
                    filter(User.employeeId == id_item). \
                    one()

                self.fio = user[0].fio

                if user[0].statusWork:
                    status = 'Работает'
                else:
                    status = 'Уволен'

                column = {0: user[2], 1: user[1], 2: str(user[0].employeeId), 3: '', 4: user[0].post,
                          5: user[0].phone, 6: user[0].eMail, 7: user[0].address, 8: user[0].login, 9: user[0].dk,
                          10: user[0].armName,
                          11: status}
                self.tW_info.update_tw_info(column)

                self.display_fio()

    def create_tw_info(self, index):

        def clicked_fio():
            '''При каждом нажатии на ФИО меняется отображение ФИО'''
            row = self.tW_info.currentRow()
            column = self.tW_info.currentColumn()

            if row == 3 and column == 0:
                text = self.tW_info.item(row, column).text()
                index = self.BUTTON_DISPLAY.index(text)
                if index >= 2:
                    index = 0
                else:
                    index += 1

                self.tW_info.setItem(3, 0, QTableWidgetItem(self.BUTTON_DISPLAY[index]))

                self.tW_info.item(row, column).setBackground(QBrush(Qt.lightGray))  # серый фон
                self.tW_info.item(row, column).setTextAlignment(
                    Qt.AlignVCenter | Qt.AlignRight)  # Выравнивание по правому краю
                self.tW_info.item(row, column).setFlags(
                    Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # запрет редактирования

                collor_tex = QColor(blue_color_tw_text)
                self.tW_info.item(3, 0).setForeground(QBrush(collor_tex))

                self.display_fio()

        column0 = {0: 'Филиал:', 1: 'Служба:', 2: 'Табельный №:', 3: 'ФИО:', 4: 'Должность:',
                   5: 'Телефон:', 6: 'Почта', 7: 'Расположение:', 8: 'Логин:', 9: 'ДК:', 10: 'АРМ:', 11: 'Статус:'}

        self.tW_info = TwInfo(column0, 25)
        self.ui.verticalLayout_info.insertWidget(index, self.tW_info)

        self.tW_info.item(3, 0).setForeground(QBrush(blue_color_tw_text))

        self.tW_info.clicked.connect(clicked_fio)

    def create_btn_wrap_info(self, index):

        def clicked_btn_wrap_info():
            if self.btn_wrap_info.isChecked():
                self.tW_info.setVisible(True)
            else:
                self.tW_info.setVisible(False)

        self.btn_wrap_info = BtnWrap('Инфомация о пользователе', True)
        self.ui.verticalLayout_info.insertWidget(index, self.btn_wrap_info)
        self.btn_wrap_info.clicked.connect(clicked_btn_wrap_info)

    def clicked_btn_sort(self):
        self.user_sort_form = UserSortForm()
        self.user_sort_form.show()
        self.user_sort_form.dataSignal.connect(lambda: self.update_tw_mainList(self.load_user()))

    def clicked_btn_new(self):
        self.new_user = UserNewForm()
        self.new_user.dataSignal.connect(self.dataSignal_update_tw_mainList)
        self.new_user.show()

    def clicked_btn_edit(self):
        self.edit_user = UserNewForm(self.get_id(self.tw_mainList.currentRow()))
        self.edit_user.dataSignal.connect(self.dataSignal_update_tw_mainList)
        self.edit_user.show()

    def clicked_btn_export(self):
        result = QMessageBox.question(self, 'Предупреждение',
                                      "Вы действительно хотите выгрузить пользователь в XLSX?",
                                      QMessageBox.Ok, QMessageBox.Cancel)
        if result == 1024:

            list_export_users = list()

            list_export_users.append(['Табельный номер', 'ФИО', 'Служба', 'Должность', 'Телефон', 'Почта',
                                      'Расположение', 'Логин', 'Договор конфиденциальности', 'Доступные АРМ'])

            for i in range(self.tw_mainList.rowCount()):
                list_export_users.append(list(
                    self.s.query(User.employeeId, User.fio, Department.name, User.post, User.phone, User.eMail,
                                 User.address, User.login, User.dk, User.armName).select_from(User).join(
                        Department).filter(
                        User.employeeId == self.get_id(i)).one()))

            export = ExportXlsx()
            export.save_xls('User', list_export_users)

    def dataSignal_update_tw_mainList(self, id):
        self.update_tw_mainList(self.load_user(), id)

    def load_user(self):
        '''Запрос в SQL список пользователей'''

        checked_branch = config['User']['checked_item_Branch']
        checked_branch = list(checked_branch)

        checked_department = config['User']['checked_item_Department']
        checked_department = list(checked_department)

        checked_szi = list(map(int, config['User']['checked_item_Szi']))
        if Helper_all.convert_bool(config['User']['checkBox_all_Szi']) == True:
            checked_szi.append(0)

        checked_system = list(map(int, config['User']['checked_item_System']))
        if Helper_all.convert_bool(config['User']['checkBox_all_System']) == True:
            checked_system.append(0)

        serch_text = '%' + self.ui.lineEdit_searchUser.text() + '%'
        if serch_text == '':
            serch_text = '%'

        status_work = Helper_all.get_status(Helper_all.convert_bool(config['User']['checkB_statusOn']),
                                            Helper_all.convert_bool(config['User']['checkB_statusOff']))

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

        if user.count() == 0:
            self.clear_fill()
        return user

    def clear_fill(self):
        self.tW_info.setItem(0, 1, QTableWidgetItem(''))
        self.tW_info.setItem(1, 1, QTableWidgetItem(''))
        self.tW_info.setItem(2, 1, QTableWidgetItem(''))
        self.tW_info.setItem(3, 1, QTableWidgetItem(''))
        self.tW_info.setItem(4, 1, QTableWidgetItem(''))
        self.tW_info.setItem(5, 1, QTableWidgetItem(''))
        self.tW_info.setItem(6, 1, QTableWidgetItem(''))
        self.tW_info.setItem(7, 1, QTableWidgetItem(''))
        self.tW_info.setItem(8, 1, QTableWidgetItem(''))
        self.tW_info.setItem(9, 1, QTableWidgetItem(''))
        self.tW_info.setItem(10, 1, QTableWidgetItem(''))
        self.tW_info.setItem(11, 1, QTableWidgetItem(''))

        self.fio = ''
