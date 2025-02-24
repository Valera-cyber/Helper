import pathlib
import re
from PyQt5.QtGui import QBrush, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
from PyQt5 import QtWidgets, QtCore
from sqlalchemy.sql.functions import coalesce
from Model.BtnMenu import BtnMenu
from Model.BtnWrap import BtnWrap
from Model.ExportExls import ExportXlsx
from Model.MainForm import MainForm
from Model.OpenPdfFile import OpenPdfFile
from Model.PrintDocForm import PrintDocForm
from Model.TwInfo import TwInfo
from Model.model import User, Department, Branch, Usb, Usb_type, Usb_data, ServiceDepartment
from ViewModel.Helper_all import Helper_all
from ViewModel.Usb.UsbChengUserForm import UsbChangUserForm
from ViewModel.Usb.UsbNewForm import UsbNewForm
from ViewModel.Usb.UsbSortForm import UsbSortForm
from ViewModel.main_load import Main_load
from config_helper import config
from stylesheet import blue_color_tw_text


class UsbMainForm(MainForm):
    def __init__(self):
        super(UsbMainForm, self).__init__()

        self.tw_mainList.setColumnHidden(0, False)

        self.path_helper = config['Setting_helper']['path_helper']
        self.setWindowTitle('Мобильные USB устройства')
        self.setWindowIcon(QIcon(self.path_helper + '/Icons/usb.png'))

        self.btn_new.clicked.connect(self.clicked_btn_new)
        self.btn_new.setToolTip('Добавить USB устройство')

        self.btn_edit.clicked.connect(self.clicked_btn_edit)
        self.btn_edit.setToolTip('Изменить данные USB устройства')

        self.btn_sort.clicked.connect(self.clicked_btn_sort)
        self.btn_sort.setToolTip('Отфильтровать список по критериям')

        self.btn_export.clicked.connect(self.clicked_btn_export)
        self.btn_export.setToolTip('Экспортировать текущий список USB устройств в XLSX')

        self.create_btn_wrap_info(0)
        self.create_tw_info(1)

        self.create_btn_wrap_reg_form(2)
        self.create_tW_regForm(3)

        self.ui.verticalLayout_info.addStretch()

        self.create_btn_cheng_user()
        self.create_btn_print_reg()

        self.update_tw_mainList(self.load_usb())

    def download_regForm(self, path_file, usb_id):
        '''Save regForm to dataBase'''

        def convertToBinaryData(filename):
            '''convert Pdf file to binery'''

            with open(filename, 'rb') as file:
                blobData = file.read()
            return blobData

        sql_update_query = self.s.query(Usb_data).filter(Usb_data.id == usb_id).one()

        file_name = pathlib.Path(path_file).name
        file_data = convertToBinaryData(path_file)

        sql_update_query.file_name = file_name
        sql_update_query.file_data = file_data
        self.s.add(sql_update_query)
        self.s.commit()

        self.update_tw_info(self.get_id(self.tw_mainList.currentRow()))

    def contextMenuRequested_tW_regForm(self, pos):

        def click_download_form(current_id):

            if self.tW_regForm.item(self.tW_regForm.currentRow(),1).text() != '':
                rezult = QMessageBox.question(self, 'Предупреждение', "Заменить регистрационную форму",
                                              QMessageBox.Ok | QMessageBox.Cancel)
                if rezult == QMessageBox.Cancel:
                    return

            path_file = QtWidgets.QFileDialog.getOpenFileName(None, 'Пожалуйста выберите регистрационную форму.')

            if path_file[0] == '':
                return

            if pathlib.Path(path_file[0]).suffix != '.pdf':
                QMessageBox.warning(self, 'Внимание', "Можно загрузить только pdf файлы!", QMessageBox.Ok)
                return

            self.download_regForm(path_file[0], self.tW_regForm.item(self.tW_regForm.currentRow(), 0).text())

        def click_open_form(current_id):
            reg_form = self.s.query(Usb_data.file_name, Usb_data.file_data).filter(Usb_data.id == current_id).one()

            open_pdf_file = OpenPdfFile('USB')
            file_name = reg_form[0]
            file_blob = reg_form[1]
            open_pdf_file.save_file(file_blob, file_name)

        def click_del_form(current_id):
            rezult = QMessageBox.question(self, 'Предупреждение', "Удалить текущию регистрационную форму?",
                                          QMessageBox.Ok | QMessageBox.Cancel)
            if rezult == QMessageBox.Cancel:
                return
            usb_data = self.s.query(Usb_data).filter(Usb_data.id == int(current_id)).one()
            self.s.delete(usb_data)
            self.s.commit()

            self.update_tw_info(self.get_id(self.tw_mainList.currentRow()))

        if self.tW_regForm.currentColumn() == 1:

            menu = QtWidgets.QMenu()
            btn_open = menu.addAction("Открыть")
            btn_download = menu.addAction("Загрузить")
            btn_del = menu.addAction("Удалить")

            if self.tW_regForm.item(self.tW_regForm.currentRow(), 1).text() == '':
                btn_open.setEnabled(False)

            current_id = (self.tW_regForm.item(self.tW_regForm.currentRow(), 0).text())
            btn_download.triggered.connect(lambda: click_download_form(current_id))
            btn_open.triggered.connect(lambda: click_open_form(current_id))
            btn_del.triggered.connect(lambda: click_del_form(current_id))
            menu.exec_(self.tW_regForm.viewport().mapToGlobal(pos))

    def create_tW_regForm(self, index):
        '''Создаем табицу инфо tW_info'''
        self.tW_regForm = QtWidgets.QTableWidget()
        self.tW_regForm.setShowGrid(False)
        self.tW_regForm.setWordWrap(True)
        self.tW_regForm.setCornerButtonEnabled(True)
        self.tW_regForm.setVisible(False)
        self.tW_regForm.viewport().installEventFilter(self)
        self.tW_regForm.setAcceptDrops(True)

        self.tW_regForm.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tW_regForm.customContextMenuRequested.connect(self.contextMenuRequested_tW_regForm)

        numrows = 0
        numcols = 3  # len(reg_forms[0])

        self.tW_regForm.setColumnCount(numcols)
        self.tW_regForm.setRowCount(numrows)

        self.tW_regForm.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        self.tW_regForm.verticalHeader().setVisible(False)

        self.tW_regForm.setHorizontalHeaderItem(0, QTableWidgetItem('id'))
        self.tW_regForm.setHorizontalHeaderItem(1, QTableWidgetItem('Регистрационная форма'))
        self.tW_regForm.setHorizontalHeaderItem(2, QTableWidgetItem('Владелец'))

        header = self.tW_regForm.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.tW_regForm.setColumnHidden(0, True)

        self.ui.verticalLayout_info.insertWidget(index, self.tW_regForm)

    def create_btn_wrap_reg_form(self, index):

        def clicked_btn_wrap_reg_form():
            if self.btn_wrap_reg_form.isChecked():
                self.tW_regForm.setVisible(True)
                self.update_tw_info(self.get_id(self.tw_mainList.currentRow()))
            else:
                self.tW_regForm.setVisible(False)

        self.btn_wrap_reg_form = BtnWrap('Регистрационные формы', False)
        self.ui.verticalLayout_info.insertWidget(index, self.btn_wrap_reg_form)
        self.btn_wrap_reg_form.clicked.connect(clicked_btn_wrap_reg_form)

    def clicked_btn_print_reg_form(self):

        def get_info_print_form(usb_id):
            usb = self.s.query(Usb, Usb_type.name).join(Usb_type).filter(Usb.id == usb_id).one()
            user_id = usb[0].user_id

            user = self.s.query(User, Department.name, Branch.name).join(Branch).join(Department).filter(
                User.employeeId == user_id).one()
            fio = user[0].fio
            title = user[0].post
            phone = user[0].phone
            address = user[0].address
            user_data = fio + ', ' + title + ',' + phone + ',' + address + '.'
            FIO = re.sub(r'\b(\w+)\b\s+\b(\w)\w*\b\s+\b(\w)\w*\b', r'\1 \2.\3.', user[0].fio)
            dictionary = {'Department': user[1],
                          'User': user_data,
                          'Description': usb[1],
                          'Name_USB': usb[0].name,
                          'Size_USB': 'none',
                          'VID': usb[0].vid,
                          'PID': usb[0].pid,
                          'SerNom_USB': usb[0].sn,
                          'FIO': FIO}

            return dictionary

        usb_id = int(self.get_id(self.tw_mainList.currentRow()))
        dictionary = get_info_print_form(usb_id)

        print_reg_for = PrintDocForm('USB')
        print_reg_for.replace_text('Reg_form.docx', dictionary, 'Регистрационная форма уч № ' + str(usb_id))

    def create_btn_print_reg(self):
        self.btn_print_reg_form = BtnMenu('Печать')
        self.ui.horizontalLayout_btn.insertWidget(5, self.btn_print_reg_form)
        self.btn_print_reg_form.setIcon(QIcon(self.path_helper + '/Icons/print.png'))
        self.btn_print_reg_form.setToolTip('Печать регистрационной формы')
        self.btn_print_reg_form.clicked.connect(self.clicked_btn_print_reg_form)

    def clicked_btn_chang_user(self):
        id_usb = self.get_id(self.tw_mainList.currentRow())
        self.user = UsbChangUserForm(id_usb)
        self.user.show()
        self.user.dataSignal.connect(self.dataSignal_update_tw_mainList)

    def create_btn_cheng_user(self):
        self.btn_chang_user = BtnMenu('Сменить')
        self.ui.horizontalLayout_btn.insertWidget(4, self.btn_chang_user)
        self.btn_chang_user.setIcon(QIcon(self.path_helper + '/Icons/cheng.png'))
        self.btn_chang_user.setToolTip('Сменить владельца USB устройства')
        self.btn_chang_user.clicked.connect(self.clicked_btn_chang_user)

    ##########################################################################################

    def update_tw_info(self, id_item):
        if self.btn_wrap_info.isChecked():
            if id_item != None:
                usb = self.s.query(Usb, Usb_type.name, Department.name, Branch.name, ServiceDepartment.name). \
                    select_from(Usb). \
                    join(Usb_type). \
                    join(Department). \
                    join(Branch). \
                    join(ServiceDepartment). \
                    filter(Usb.id == id_item).one()

                branch = usb[3]
                department = usb[2]
                service_department = usb[4]

                self.user_id = usb[0].user_id

                if self.user_id != None:
                    user = (self.s.query(User.fio).
                            join(Branch).join(Department)).filter(User.employeeId == self.user_id).one()

                    fio = user[0]
                else:
                    branch = ''
                    department = ''
                    fio = ''

                if usb[0].status:
                    status = 'Исправно'
                else:
                    status = 'Не исправно'

                column1 = {0: fio, 1: branch, 2: department, 3: service_department, 4: usb[1],
                           5: usb[0].name, 6: usb[0].vid, 7: usb[0].pid, 8: usb[0].sn, 9: usb[0].usbStor, 10: status}

                self.tW_info.update_tw_info(column1)

        if self.btn_wrap_reg_form.isChecked():
            self.tW_regForm.setRowCount(0)

            reg_forms = self.s.query(Usb_data.id, Usb_data.file_name, User.fio).join(User).filter(
                Usb_data.usb_id == id_item)

            collor_tex = blue_color_tw_text

            for i in reg_forms:
                rowPosition = self.tW_regForm.rowCount()
                self.tW_regForm.insertRow(rowPosition)

                self.tW_regForm.setItem(rowPosition, 0, QTableWidgetItem(str(i[0])))
                self.tW_regForm.setItem(rowPosition, 1, QTableWidgetItem(i[1]))
                self.tW_regForm.setItem(rowPosition, 2, QTableWidgetItem(i[2]))
                self.tW_regForm.item(rowPosition, 1).setForeground(QBrush(collor_tex))

            row_count = reg_forms.count()

            height_tW = Main_load.get_height_qtable(row_count)
            self.tW_regForm.setMaximumHeight(height_tW)
            self.tW_regForm.setMinimumHeight(height_tW)

    def create_tw_info(self, index):

        column0 = {0: 'Владелец -ФИО:', 1: 'Филиал:', 2: 'Служба:', 3: 'Принадлежность:', 4: 'Тип устройства:',
                   5: 'Описание:', 6: 'VID', 7: 'PID:', 8: 'SN:', 9: 'UsbStor:', 10: 'Статус устройства:'}

        self.tW_info = TwInfo(column0, 25)
        self.ui.verticalLayout_info.insertWidget(index, self.tW_info)

    def create_btn_wrap_info(self, index):

        def clicked_btn_wrap_info():
            if self.btn_wrap_info.isChecked():
                self.tW_info.setVisible(True)
                self.update_tw_info(self.get_id(self.tw_mainList.currentRow()))
            else:
                self.tW_info.setVisible(False)

        self.btn_wrap_info = BtnWrap('Инфомация USB устройства', True)
        self.ui.verticalLayout_info.insertWidget(index, self.btn_wrap_info)
        self.btn_wrap_info.clicked.connect(clicked_btn_wrap_info)

    def clicked_btn_sort(self):
        self.usb_sort_form = UsbSortForm()
        self.usb_sort_form.show()
        self.usb_sort_form.dataSignal.connect(lambda: self.update_tw_mainList(self.load_usb()))

    def clicked_btn_new(self):
        self.new_usb = UsbNewForm()
        self.new_usb.dataSignal.connect(self.dataSignal_update_tw_mainList)
        self.new_usb.show()

    def clicked_btn_edit(self):
        self.new_usb = UsbNewForm(self.get_id(self.tw_mainList.currentRow()))
        self.new_usb.dataSignal.connect(self.dataSignal_update_tw_mainList)
        self.new_usb.show()

    def clicked_btn_export(self):
        result = QMessageBox.question(self, 'Предупреждение',
                                      "Вы действительно хотите выгрузить USB устройства в XLSX?",
                                      QMessageBox.Ok, QMessageBox.Cancel)
        if result == 1024:

            list_export = list()

            list_export.append(['Учетный номер', 'Описание USB', 'VID', 'PID', 'Серийный номер',
                                      'usbStor', 'Тип устройства','Статус'])

            for i in range(self.tw_mainList.rowCount()):
                list_export.append(list(
                    self.s.query(Usb.id, Usb.name, Usb.vid, Usb.pid, Usb.sn, Usb.usbStor, Usb_type.name, Usb.status).
                    select_from(Usb).join(Usb_type).
                    filter(Usb.id == self.get_id(i)).one()))

            export = ExportXlsx()
            export.save_xls('USB', list_export)

    def dataSignal_update_tw_mainList(self, id):
        self.update_tw_mainList(self.load_usb(), id)

    def load_usb(self):
        checked_branch = config['Usb']['checked_item_Branch']
        checked_branch = list(checked_branch)

        checked_department = config['Usb']['checked_item_Department']
        checked_department = list(checked_department)

        checked_item_ServiceDepartment = config['Usb']['checked_item_ServiceDepartment']
        checked_item_ServiceDepartment = list(checked_item_ServiceDepartment)

        checked_item_UsbType = config['Usb']['checked_item_UsbType']
        checked_item_UsbType = list(checked_item_UsbType)

        checked_item_User = list((map(int, config['Usb']['checked_item_User'])))
        if Helper_all.convert_bool(config['Usb']['checkBox_all_User']) == True:
            checked_item_User.append(0)

        serch_text = '%' + self.ui.lineEdit_searchUser.text() + '%'
        if serch_text == '':
            serch_text = '%'

        status_usb = Helper_all.get_status(Helper_all.convert_bool(config['Usb']['checkB_statusOn']),
                                           Helper_all.convert_bool(config['Usb']['checkB_statusOff']))

        usb = self.s.query(Usb.id, Usb.name).select_from(Usb). \
            join(Branch). \
            join(Department). \
            join(ServiceDepartment). \
            join(Usb_type). \
            filter(Branch.id.in_((checked_branch))). \
            filter(Department.id.in_((checked_department))). \
            filter(ServiceDepartment.id.in_((checked_item_ServiceDepartment))). \
            filter(Usb_type.id.in_((checked_item_UsbType))). \
            filter(Usb.status.like(status_usb)). \
            filter(coalesce(Usb.user_id, 0).in_(checked_item_User)). \
            order_by(Usb.id)

        if usb.count() == 0:
            self.clear_fill()
            self.btn_chang_user.setEnabled(False)
            self.btn_print_reg_form.setEnabled(False)
            self.btn_export.setEnabled(False)
        else:
            self.btn_chang_user.setEnabled(True)
            self.btn_print_reg_form.setEnabled(True)
            self.btn_export.setEnabled(True)

        return usb

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

        self.tW_regForm.setRowCount(0)
