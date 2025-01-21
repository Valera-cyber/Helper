import os
import pathlib
import re
import subprocess
import sys

import openpyxl
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QBrush, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
from PyQt5 import QtWidgets, QtCore
from functools import partial

from sqlalchemy import or_

from Model.database import session
from Model.model import User, Department, Branch, Usb, Usb_type, Usb_data
from View.main_container.container import Ui_MainWindow
from ViewModel.Docx_replace import replace_text
from ViewModel.Helper_all import Helper_all
from ViewModel.Usb.usb_chengUser import Usb_chengUser
from ViewModel.Usb.usb_new import Usb_new
from ViewModel.main_load import Main_load
from ViewModel.setting_view import Setting_view
from config_helper import config
from stylesheet import style


class Usb_main(QtWidgets.QMainWindow):
    def __init__(self, path_helper):
        super(Usb_main, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.s = session()

        self.path_helper = path_helper
        self.setStyleSheet(style)

        width = QtWidgets.qApp.desktop().availableGeometry(self).width()  # Устанавливаем размер долей рабочих панелей
        self.ui.splitter.setSizes([width * 1 / 3, width * 2 / 3])

        self.setWindowTitle("Мобильные устройства")
        self.setWindowIcon(QIcon(self.path_helper + '/Icons/usb.png'))

        self.create_btn_info()
        self.ui.verticalLayout_2.addWidget(self.btn_info)

        self.create_tW_info()
        self.ui.verticalLayout_2.addWidget(self.tW_info)

        self.create_btn_regForm()
        self.ui.verticalLayout_2.addWidget(self.btn_regForm)

        self.create_tW_regForm()
        self.ui.verticalLayout_2.addWidget(self.tW_regForm)

        self.create_btn_cheng()
        self.ui.horizontalLayout_4.insertWidget(4, self.btn_cheng)

        self.create_btn_print()
        self.btn_print.setEnabled(False)
        self.ui.horizontalLayout_4.insertWidget(5, self.btn_print)

        self.create_btn_download()
        self.btn_download.setEnabled(False)
        self.ui.horizontalLayout_4.insertWidget(6, self.btn_download)

        self.ui.lineEdit_searchUser.textChanged.connect(partial(self.searchUser))

        Main_load.create_tW_list(self.ui)
        self.ui.tW_list.itemSelectionChanged.connect(self.changed_current_cell_usb)
        # self.ui.tW_list.itemDoubleClicked.connect(self.clicked_btn_edit)
        Main_load.print_list(self.ui, self.load_usb())

        Main_load.select_row_intable(self.ui)

        self.create_menu_button()

        self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                    QtWidgets.QSizePolicy.Expanding)  # Подпружиниваем по вертикали
        self.ui.verticalLayout_2.addItem(self.verticalSpacer)

    def searchUser(self):
        Main_load.print_list(self.ui, self.load_usb())
        Main_load.select_row_intable(self.ui)

    def create_btn_print(self):
        '''Создаем кноку свернуть развернуть инфо'''
        self.btn_print = QtWidgets.QToolButton()
        self.btn_print.clicked.connect(self.print_regForm)
        self.btn_print.setText('Печать')
        self.btn_print.setIcon(QIcon(self.path_helper + '/Icons/print.png'))
        self.btn_print.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

    def create_btn_download(self):
        self.btn_download = QtWidgets.QToolButton()
        self.btn_download.clicked.connect(self.clicked_btn_dowload)
        self.btn_download.setText('Загрузить')
        self.btn_download.setIcon(QIcon(self.path_helper + '/Icons/download.png'))
        self.btn_download.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

    def changed_current_cell_tW_regForm(self):
        if self.tW_regForm.currentColumn() == 1:
            self.btn_download.setEnabled(True)
        else:
            self.btn_download.setEnabled(False)

    def print_regForm(self):
        '''Печать регистрационной формы'''
        id_usb = Main_load.get_id(self.ui)

        usb = self.s.query(Usb, Usb_type.name).join(Usb_type).filter(Usb.id == id_usb).one()

        user_id = usb[0].user_id

        if user_id == None:
            QMessageBox.warning(self, 'Предупреждение',
                                "USB устройство не имеет владельца.",
                                QMessageBox.Ok)
            return

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

        path_exportUsb = Main_load.get_helperExport('USB')

        forma = self.path_helper + '/' + 'Form_print' + '/' + 'Reg_form.docx'

        replace_text(forma, dictionary, path_exportUsb + '/' + Main_load.get_id(self.ui) + '-' + FIO)

    def create_btn_cheng(self):
        '''Создаем кноку свернуть развернуть инфо'''
        self.btn_cheng = QtWidgets.QToolButton()
        self.btn_cheng.clicked.connect(self.clicked_btn_cheng)
        self.btn_cheng.setText('Передать')
        self.btn_cheng.setIcon(QIcon(self.path_helper + '/Icons/cheng.png'))
        self.btn_cheng.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

    def clicked_btn_cheng(self):
        id_usb = Main_load.get_id(self.ui)
        self.btn_chenge = Usb_chengUser(id_usb, self.user_id)
        self.btn_chenge.exec_()

        Main_load.print_list(self.ui, self.load_usb())
        Main_load.select_row_intable(self.ui, str(id_usb))

    def changed_current_cell_usb(self):
        '''Действие при смене ячейки в списке'''
        if Main_load.get_id(self.ui) == None:
            self.btn_print.setEnabled(False)
        else:
            self.btn_print.setEnabled(True)

        usb_id = Main_load.get_id(self.ui)
        self.print_tW(usb_id)

    def print_fill_usb(self, id_item):
        fill_item = self.s.query(Usb, Usb_type.name).select_from(Usb). \
            join(Usb_type).filter(Usb.id == id_item).one()

        self.tW_info.setItem(3, 1, QTableWidgetItem(str(fill_item[0].id)))
        self.tW_info.setItem(4, 1, QTableWidgetItem(fill_item[1]))
        self.tW_info.setItem(5, 1, QTableWidgetItem(fill_item[0].name))
        self.tW_info.setItem(6, 1, QTableWidgetItem(fill_item[0].vid))
        self.tW_info.setItem(7, 1, QTableWidgetItem(fill_item[0].pid))
        self.tW_info.setItem(8, 1, QTableWidgetItem(fill_item[0].sn))
        self.tW_info.setItem(9, 1, QTableWidgetItem(fill_item[0].usbStor))
        self.checkBox_status.setChecked(fill_item[0].status)

        self.user_id = fill_item[0].user_id
        if self.user_id != None:
            user = (self.s.query(User.fio, Branch.name, Department.name).
                    join(Branch).join(Department)).filter(User.employeeId == self.user_id).one()

            self.tW_info.setItem(0, 1, QTableWidgetItem(user[1]))
            self.tW_info.setItem(1, 1, QTableWidgetItem(user[2]))
            self.tW_info.setItem(2, 1, QTableWidgetItem(user[0]))
        else:
            self.tW_info.setItem(0, 1, QTableWidgetItem(''))
            self.tW_info.setItem(1, 1, QTableWidgetItem(''))
            self.tW_info.setItem(2, 1, QTableWidgetItem(''))

        # self.load_regForm(id_item)

    def print_tW_regForm(self, id_item):
        '''Загружаем все регистрационные формы, выбранного USB устройства'''
        if self.btn_regForm.isChecked():
            self.tW_regForm.setRowCount(0)

            reg_forms = self.s.query(Usb_data.id, Usb_data.file_name, User.fio).join(User).filter(
                Usb_data.usb_id == id_item)

            for i in reg_forms:
                rowPosition = self.tW_regForm.rowCount()
                self.tW_regForm.insertRow(rowPosition)

                self.tW_regForm.setItem(rowPosition, 0, QTableWidgetItem(str(i[0])))
                self.tW_regForm.setItem(rowPosition, 1, QTableWidgetItem(i[1]))
                self.tW_regForm.setItem(rowPosition, 2, QTableWidgetItem(i[2]))

            row_count = reg_forms.count()

            height_tW = Main_load.get_height_qtable(row_count)
            self.tW_regForm.setMaximumHeight(height_tW)
            self.tW_regForm.setMinimumHeight(height_tW)

    def print_tW(self, id):
        usb_id = Main_load.get_id(self.ui)
        if id is not None:
            if self.btn_info.isChecked():
                self.print_fill_usb(usb_id)

            if self.btn_regForm.isChecked():
                self.print_tW_regForm(usb_id)

        else:
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

            self.tW_regForm.setRowCount(0)

    def create_menu_button(self):
        '''Создаем МенюБар и кноки в меню'''
        self.ui.action_exit.triggered.connect(self.close)
        self.ui.action_add.triggered.connect(self.clicked_btn_new)
        self.ui.action_edit.triggered.connect(self.clicked_btn_edit)
        self.ui.action_sort.triggered.connect(self.clicked_btn_sort)
        self.ui.action_export.triggered.connect(self.clicked_btn_export)

        self.ui.btn_new.clicked.connect(self.clicked_btn_new)
        self.ui.btn_edit.clicked.connect(self.clicked_btn_edit)
        self.ui.btn_edit.setEnabled(False)
        self.ui.btn_sort.clicked.connect(self.clicked_btn_sort)
        self.ui.btn_export.clicked.connect(self.clicked_btn_export)

        self.ui.btn_new.setIcon(QIcon(self.path_helper + '/Icons/add.png'))
        self.ui.btn_edit.setIcon(QIcon(self.path_helper + '/Icons/edit.png'))
        self.ui.btn_export.setIcon(QIcon(self.path_helper + '/Icons/export.png'))
        self.ui.btn_sort.setIcon(QIcon(self.path_helper + '/Icons/sorts.png'))

    def clicked_btn_new(self):
        self.new_usb = Usb_new(None)
        self.new_usb.exec_()

        Main_load.print_list(self.ui, self.load_usb())
        Main_load.select_row_intable(self.ui, str(self.new_usb.usb_id))

    def clicked_btn_edit(self):
        print('clicked_btn_edit')

    def clicked_btn_sort(self):
        self.settingViewUser = Setting_view('usb')
        self.settingViewUser.exec_()

        Main_load.print_list(self.ui, self.load_usb())
        Main_load.select_row_intable(self.ui)

    def clicked_btn_export(self):
        '''Экспорт пользователей в эксель'''
        result = QMessageBox.warning(self, 'Предупреждение',
                                     "Вы действительно хотите выгрузить Мобильные устройства в XLSX?",
                                     QMessageBox.Ok, QMessageBox.Cancel)
        if result == 1024:
            count_row = self.ui.tW_list.rowCount()
            list_usbId = []
            for i in range(count_row):
                list_usbId.append(self.ui.tW_list.item(i, 0).text())
            list_export_usb = []
            for i in list_usbId:
                list_export_usb.append(
                    self.s.query(Usb.id, Usb.name, Usb.vid, Usb.pid, Usb.sn, Usb.usbStor, Usb_type.name, Usb.status).
                    select_from(Usb).join(Usb_type).
                    filter(Usb.id == i).one())

            wb = openpyxl.Workbook()
            sheet = wb.sheetnames
            lis = wb.active
            # Создание строки с заголовками
            lis.append(
                (
                    'Учетный номер', 'Описание USB', 'VID', 'PID', 'Серийный номер', 'usbStor', 'Тип устройства',
                    'Статус'))
            for i in list_export_usb:
                lis.append(list(i))

            path_exportUsb = Main_load.get_helperExport('USB')

            wb.save(filename=path_exportUsb + '/USB.xlsx')
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, path_exportUsb + '/USB.xlsx'])

    def load_usb(self):
        checked_branch = config['Usb']['checked_branch']
        checked_branch=list(checked_branch)
        checked_department = config['Usb']['checked_department']
        checked_department = list(checked_department)

        serch_text = '%' + self.ui.lineEdit_searchUser.text() + '%'
        if serch_text == '':
            serch_text = '%'

        status_usb = Helper_all.get_status(Helper_all.convert_bool(config['Usb']['checkB_statusOn']),
                                           Helper_all.convert_bool(config['Usb']['checkB_statusOff']))

        usb = self.s.query(Usb.id, Usb.name).select_from(Usb). \
            join(User, isouter=True). \
            filter(User.branch_id.in_((checked_branch))). \
            filter(User.departmet_id.in_((checked_department))). \
            filter(User.statusWork.like(status_usb)). \
            filter(or_(
            Usb.id.like(serch_text),
            Usb.sn.like(serch_text),
            User.fio.like(serch_text))). \
            order_by(Usb.id)
        return usb

    def doubleClicked_tW_regForm(self):
        '''Save and open regForm'''

        def write_to_file(data, filename):
            # Преобразование двоичных данных в нужный формат
            with open(filename, 'wb') as file:
                file.write(data)

        regForm_id = (self.tW_regForm.item(self.tW_regForm.currentRow(), 0).text())

        reg_form = self.s.query(Usb_data.file_name, Usb_data.file_data).filter(Usb_data.id == regForm_id).one()
        if reg_form[0] == None:
            QMessageBox.warning(self, 'Предупреждение',
                                "Регистрационная форма отсутствует.",
                                QMessageBox.Ok)
            return
        downloads_path = Main_load.get_helperExport('USB')
        regForm_path = os.path.join(downloads_path + '/' + reg_form[0])

        write_to_file(reg_form[1], regForm_path)

        subprocess.call(["xdg-open", regForm_path])

    def create_tW_regForm(self):
        '''Создаем табицу инфо tW_info'''
        self.tW_regForm = QtWidgets.QTableWidget()
        self.tW_regForm.setShowGrid(False)
        self.tW_regForm.setWordWrap(True)
        self.tW_regForm.setCornerButtonEnabled(True)
        self.tW_regForm.setVisible(False)
        self.tW_regForm.itemSelectionChanged.connect(self.changed_current_cell_tW_regForm)
        self.tW_regForm.itemDoubleClicked.connect(self.doubleClicked_tW_regForm)
        self.tW_regForm.viewport().installEventFilter(self)
        self.tW_regForm.setAcceptDrops(True)

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

    def clicked_btn_dowload(self):
        if self.tW_regForm.item(self.tW_regForm.currentRow(), 1).text() != '':
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

        id_usb = Main_load.get_id(self.ui)
        Main_load.print_list(self.ui, self.load_usb())
        Main_load.select_row_intable(self.ui, id_usb)

    def eventFilter(self, source, event):
        if (source is self.tW_regForm.viewport() and
            (event.type() == QEvent.DragEnter or
             event.type() == QEvent.DragMove or
             event.type() == QEvent.Drop) and
            event.mimeData().hasUrls()) and self.tW_regForm.currentRow() != -1:
            if event.type() == QEvent.Drop:

                if self.tW_regForm.item(self.tW_regForm.currentRow(), 1).text() != '':
                    rezult = QMessageBox.question(self, 'Предупреждение', "Заменить регистрационную форму",
                                                  QMessageBox.Ok | QMessageBox.Cancel)
                    if rezult == QMessageBox.Cancel:
                        return

                regForm = []
                for url in event.mimeData().urls():
                    if url.isLocalFile():
                        regForm.append(url.path())

                if Main_load.check_download_file(regForm):
                    self.download_regForm(regForm[0], self.tW_regForm.item(self.tW_regForm.currentRow(), 0).text())
                else:
                    QMessageBox.warning(self, 'Внимание', "Можно загрузить только один pdf файл!", QMessageBox.Ok)

            event.accept()
            return True
        return super().eventFilter(source, event)

    def create_tW_info(self):
        '''Создаем табицу инфо tW_info'''
        self.tW_info = QtWidgets.QTableWidget()
        self.tW_info.setShowGrid(False)
        self.tW_info.setWordWrap(True)
        self.tW_info.setCornerButtonEnabled(True)

        numrows = 10
        numcols = 2

        self.tW_info.setColumnCount(numcols)
        self.tW_info.setRowCount(numrows)

        header = self.tW_info.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.tW_info.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        self.tW_info.horizontalHeader().setVisible(False)
        self.tW_info.verticalHeader().setVisible(False)

        self.tW_info.setItem(0, 0, QTableWidgetItem('Филиал:'))
        self.tW_info.setItem(1, 0, QTableWidgetItem('Служба:'))
        self.tW_info.setItem(2, 0, QTableWidgetItem('ФИО:'))
        self.tW_info.setItem(3, 0, QTableWidgetItem('Учеиный №:'))
        self.tW_info.setItem(4, 0, QTableWidgetItem('Тип устройства:'))
        self.tW_info.setItem(5, 0, QTableWidgetItem('Описание:'))
        self.tW_info.setItem(6, 0, QTableWidgetItem('VID:'))
        self.tW_info.setItem(7, 0, QTableWidgetItem('PID:'))
        self.tW_info.setItem(8, 0, QTableWidgetItem('SN:'))
        self.tW_info.setItem(9, 0, QTableWidgetItem('UsbStor:'))

        height_tW = Main_load.get_height_qtable(numrows)
        self.tW_info.setMaximumHeight(height_tW - 22)
        self.tW_info.setMinimumHeight(height_tW - 22)

        self.checkBox_status = QtWidgets.QCheckBox()
        self.tW_info.setCellWidget(11, 1, self.checkBox_status)
        self.checkBox_status.setEnabled(False)

        for rowPosition in range(numrows):
            self.tW_info.item(rowPosition, 0).setBackground(QBrush(Qt.lightGray))  # серый фон
            self.tW_info.item(rowPosition, 0).setTextAlignment(
                Qt.AlignVCenter | Qt.AlignRight)  # Выравнивание по правому краю
            self.tW_info.item(rowPosition, 0).setFlags(
                Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # запрет редактирования

        table = QTableWidgetItem()
        table.setTextAlignment(3)

        self.tW_info.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.tW_info.setFocusPolicy(Qt.NoFocus)
        self.tW_info.setSelectionMode(QAbstractItemView.NoSelection)

    def create_btn_regForm(self):
        '''Создаем кноку свернуть развернуть инфо'''
        self.btn_regForm = QtWidgets.QPushButton()
        self.btn_regForm.clicked.connect(self.clicked_btn_regForm)
        self.btn_regForm.setText('Регистрационные формы')
        self.btn_regForm.setCheckable(True)
        self.btn_regForm.setChecked(False)
        self.btn_regForm.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))
        self.btn_regForm.setIconSize(QtCore.QSize(30, 30))

    def create_btn_info(self):
        '''Создаем кноку свернуть развернуть инфо'''
        self.btn_info = QtWidgets.QPushButton()
        self.btn_info.clicked.connect(self.clicked_btn_info)
        self.btn_info.setText('Данные мобильного устройства')
        self.btn_info.setCheckable(True)
        self.btn_info.setChecked(True)
        self.btn_info.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
        self.btn_info.setIconSize(QtCore.QSize(30, 30))

    def clicked_btn_regForm(self):
        if Main_load.get_id(self.ui) == None:
            return

        if self.btn_regForm.isChecked():
            self.btn_regForm.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
            self.tW_regForm.setVisible(True)
            self.print_tW_regForm(Main_load.get_id(self.ui))
        else:
            self.btn_regForm.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))
            self.tW_regForm.setVisible(False)
            self.btn_download.setEnabled(False)

    def clicked_btn_info(self):
        # print('clicked_btn_info')
        if Main_load.get_id(self.ui) == None:
            return

        if self.btn_info.isChecked():
            self.btn_info.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
            self.tW_info.setVisible(True)
            self.print_fill_usb(Main_load.get_id(self.ui))
        else:
            self.btn_info.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))
            self.tW_info.setVisible(False)
