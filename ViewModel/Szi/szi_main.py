import os
import pathlib
import subprocess
import sys
from datetime import datetime

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QIcon, QBrush
from PyQt5.QtWidgets import QApplication, QHeaderView, QTableWidgetItem, \
    QAbstractItemView, QMessageBox

from Model.database import session
from Model.model import Office_equipment, Branch, Department, SziAccounting, SziType, \
    SziFileInst, SziFileUninst, SziEquipment, User
from View.main_container.container import Ui_MainWindow
from ViewModel.Helper_all import Helper_all
from ViewModel.Szi.szi_new import Szi_new
from ViewModel.main_load import Main_load
from ViewModel.Szi.szi_sorView import Szi_sortView
from config_helper import config
from stylesheet import style, blue_color_tw_text, red_color_tw_text


class Szi_main(QtWidgets.QMainWindow):
    def __init__(self, path_helper):
        super(Szi_main, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.s = session()

        self.path_helper = path_helper
        self.setStyleSheet(style)

        width = QtWidgets.qApp.desktop().availableGeometry(self).width()  # Устанавливаем размер долей рабочих панелей
        self.ui.splitter.setSizes([width * 1 / 3, width * 2 / 3])

        self.setWindowTitle("Учет СЗИ")
        self.setWindowIcon(QIcon(self.path_helper + '/Icons/szi.png'))

        Main_load.create_tW_list(self.ui)
        self.ui.tW_list.itemSelectionChanged.connect(self.changed_current_cell_user)
        Main_load.print_list(self.ui, self.load_szi())

        self.create_menu_button()

        self.create_btn_info()
        self.ui.verticalLayout_2.addWidget(self.btn_info)

        self.create_tW_info()
        self.ui.verticalLayout_2.addWidget(self.tW_info)

        self.create_btn_akt()
        self.ui.verticalLayout_2.addWidget(self.btn_akt)

        self.create_tW_act()
        self.ui.verticalLayout_2.addWidget(self.tW_act)

        self.create_btn_uninstall_szi()
        self.btn_uninstall_szi.setEnabled(False)
        self.ui.horizontalLayout_4.insertWidget(4, self.btn_uninstall_szi)

        self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                    QtWidgets.QSizePolicy.Expanding)  # Подпружиниваем по вертикали
        self.ui.verticalLayout_2.addItem(self.verticalSpacer)

    def chek_uninst_szi(self, id_sziAccounting):
        sziAccounting = self.s.query(SziAccounting.fileUninstSzi_id).filter(SziAccounting.id == id_sziAccounting).one()
        if sziAccounting[0]:
            self.btn_uninstall_szi.setEnabled(False)
        else:
            self.btn_uninstall_szi.setEnabled(True)

    def clicked_btn_uninstall_szi(self):
        rezult = QMessageBox.question(self, 'Предупреждение', "Вы действительно хотите деисталировать выбранное СЗИ?",
                                      QMessageBox.Ok | QMessageBox.Cancel)
        if rezult == QMessageBox.Cancel:
            return

        def get_list_equipment_id(id_SziAccounting):
            '''Получаем список оборудования для деинсталяции'''
            list_equipmentId = []  # список оборудования для составления акта(СКР, расположение)
            for i in self.s.query(SziEquipment.equipment_id). \
                    filter(SziEquipment.sziAccounting_id == id_SziAccounting). \
                    filter(SziEquipment.status == True):
                list_equipmentId.append(i[0])

            return list_equipmentId

        def save_act_uninst(id_SziAccounting):
            '''Записываем в таблицы SziFileUninst, SziAccounting, SziEquipment id-файла деинсталяции,
            возвращаем id SziFileUninst'''

            def reserve_id_SziFileInst() -> int:
                '''Резервируем и возвращаем id в SziFileUninst '''
                sziFileUninst = SziFileUninst(fileName='', date=datetime.now().date())
                self.s.add(sziFileUninst)
                self.s.flush()
                return sziFileUninst.id

            def save_fileUninstSzi_id_SziAccounting(id: int, fileUninstSzi_id: int):
                '''Записываем в поле fileUninstSzi_id ранее зарезервированный id из SziFileUninst'''
                sziAccounting = self.s.query(SziAccounting).filter(SziAccounting.id == id).one()
                sziAccounting.fileUninstSzi_id = fileUninstSzi_id
                sziAccounting.status = False
                self.s.add(sziAccounting)

            def save_fileUninstSzi_id_SziEquipment(sziAccounting_id: int, fileUninstSzi_id: int):
                '''Записываем в поле fileUninstSzi_id ранее зарезервированный id из SziFileUninst'''
                sziEquipment = self.s.query(SziEquipment).filter(SziEquipment.sziAccounting_id == sziAccounting_id). \
                    filter(SziEquipment.status == True)
                for row in sziEquipment:
                    row.fileUninstSzi_id = fileUninstSzi_id
                    row.status = False
                    self.s.add(row)

            id_SziFileUninst = reserve_id_SziFileInst()
            save_fileUninstSzi_id_SziAccounting(id_SziAccounting, id_SziFileUninst)
            save_fileUninstSzi_id_SziEquipment(id_SziAccounting, id_SziFileUninst)

            self.s.commit()

            return id_SziFileUninst


        id_SziAccounting = Main_load.get_id(self.ui)
        get_list_equipment_id(id_SziAccounting)
        save_act_uninst(id_SziAccounting)

        self.changed_current_cell_user()

    def create_btn_uninstall_szi(self):
        self.btn_uninstall_szi = QtWidgets.QToolButton()
        self.btn_uninstall_szi.clicked.connect(self.clicked_btn_uninstall_szi)
        self.btn_uninstall_szi.setText('Удалить')
        self.btn_uninstall_szi.setIcon(QIcon(self.path_helper + '/Icons/uninstall.png'))
        self.btn_uninstall_szi.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

    def print_tW_act(self):

        id_SziAccounting = Main_load.get_id(self.ui)

        sziAccounting = self.s.query(SziAccounting, SziFileInst, SziFileUninst). \
            select_from(SziAccounting). \
            join(SziFileInst). \
            join(SziFileUninst, isouter=True). \
            filter(SziAccounting.id == id_SziAccounting).one()

        self.tW_act.setRowCount(0)

        rowPosition = self.tW_act.rowCount()
        self.tW_act.insertRow(rowPosition)

        if sziAccounting[2] is not None:
            number_act_uninst = str(sziAccounting[2].id)
            date_act_uninst = str(sziAccounting[2].date.strftime('%d.%m.%Y'))
            act_uninst = ('Акт № ' + number_act_uninst + ' от ' + date_act_uninst)

            if sziAccounting[2].file_data == None:
                collor_tex_uninst = red_color_tw_text
            else:
                collor_tex_uninst = blue_color_tw_text
        else:
            act_uninst = ''
            collor_tex_uninst = Qt.black

        number_act_inst = str(sziAccounting[1].id)
        date_act_inst = str(sziAccounting[1].date.strftime('%d.%m.%Y'))
        act_inst = ('Акт № ' + number_act_inst + ' от ' + date_act_inst)

        if sziAccounting[1].file_data == None:
            collor_tex_inst = red_color_tw_text
        else:
            collor_tex_inst = blue_color_tw_text

        self.tW_act.setItem(rowPosition, 0, QTableWidgetItem(str(sziAccounting[0].id)))
        self.tW_act.setItem(rowPosition, 1, QTableWidgetItem(act_inst))
        self.tW_act.setItem(rowPosition, 2, QTableWidgetItem(act_uninst))
        self.tW_act.item(rowPosition, 1).setForeground(QBrush(collor_tex_inst))
        self.tW_act.item(rowPosition, 2).setForeground(QBrush(collor_tex_uninst))

        row_count = 1

        height_tW = Main_load.get_height_qtable(row_count)
        self.tW_act.setMaximumHeight(height_tW)
        self.tW_act.setMinimumHeight(height_tW)

    def create_btn_akt(self):
        '''Создаем кноку свернуть развернуть инфо'''
        self.btn_akt = QtWidgets.QPushButton()
        self.btn_akt.clicked.connect(self.clicked_btn_akt)
        self.btn_akt.setText('Акты установки и удаления СЗИ')
        self.btn_akt.setCheckable(True)
        self.btn_akt.setChecked(False)
        self.btn_akt.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))
        self.btn_akt.setIconSize(QtCore.QSize(30, 30))

    def clicked_btn_akt(self):
        if Main_load.get_id(self.ui) == None:
            return

        if self.btn_akt.isChecked():
            self.btn_akt.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
            self.tW_act.setVisible(True)
            self.print_tW_act()
        else:
            self.btn_akt.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))
            self.tW_act.setVisible(False)

    def contextMenuRequested_tw_act(self, pos):
        menu = QtWidgets.QMenu()
        btn_read = menu.addAction("Открыть")
        btn_download = menu.addAction("Загрузить")

        item = self.tW_act.item(self.tW_act.currentRow(), self.tW_act.currentColumn())

        color_text = item.foreground().color().name()

        if color_text == red_color_tw_text.name():
            btn_read.setEnabled(False)

        if self.tW_act.item(self.tW_act.currentRow(), self.tW_act.currentColumn()).text() == '':
            btn_read.setEnabled(False)
            btn_download.setEnabled(False)

        btn_download.triggered.connect(self.download_act)
        btn_read.triggered.connect(self.read_act)
        menu.exec_(self.tW_act.viewport().mapToGlobal(pos))

    def read_act(self):

        def write_to_file(data, filename):
            # Преобразование двоичных данных в нужный формат
            with open(filename, 'wb') as file:
                file.write(data)

        tW_act_column = self.tW_act.currentColumn()
        id_SziAccounting = self.tW_act.item(self.tW_act.currentRow(), 0).text()
        sziAccounting = self.s.query(SziAccounting).filter(SziAccounting.id == id_SziAccounting).one()
        id_sziFileInst = sziAccounting.fileInstSzi_id
        fileUninstSzi_id = sziAccounting.fileUninstSzi_id

        if tW_act_column == 1:
            act = self.s.query(SziFileInst.file_data).filter(
                SziFileInst.id == id_sziFileInst).one()

            name_act = 'Акт установки СЗИ - ' + str(id_sziFileInst) + '.pdf'
            downloads_path = Main_load.get_helperExport('Szi')
            regForm_path = os.path.join(downloads_path + '/' + name_act)
            write_to_file(act[0], regForm_path)
            subprocess.call(["xdg-open", regForm_path])

        if tW_act_column == 2:
            act = self.s.query(SziFileUninst.file_data).filter(
                SziFileUninst.id == fileUninstSzi_id).one()
            name_act = 'Акт вывода СЗИ - ' + str(fileUninstSzi_id) + '.pdf'
            downloads_path = Main_load.get_helperExport('Szi')
            regForm_path = os.path.join(downloads_path + '/' + name_act)
            write_to_file(act[0], regForm_path)
            subprocess.call(["xdg-open", regForm_path])

    def convertToBinaryData(self, filename):
        '''convert Pdf file to binery'''

        with open(filename, 'rb') as file:
            blobData = file.read()
        return blobData

    def download_SziFileUninst(self, id_fileUninstSzi_id: int, path_file: pathlib):
        '''Сохраняем акт деинсталяции в SziFileUninst'''
        file_data = self.convertToBinaryData(path_file)
        sziFileUninst = self.s.query(SziFileUninst).filter(SziFileUninst.id == id_fileUninstSzi_id).one()
        sziFileUninst.file_data = file_data
        self.s.add(sziFileUninst)
        self.s.commit()

    def download_SziFileInst(self, id_SziFileInst: int, path_file: pathlib):
        '''Сохраняем акт инсталяции в SziFileInst'''
        file_data = self.convertToBinaryData(path_file)
        sziFileInst = self.s.query(SziFileInst).filter(SziFileInst.id == id_SziFileInst).one()
        sziFileInst.file_data = file_data
        self.s.add(sziFileInst)
        self.s.commit()

    def download_act(self):

        def check_download_file(item_tW) -> pathlib:
            '''Проверяем какого цвета текс, какое расширение файла сколько файлов,
            если все норм возвращаем путь к файлу, если нет возвращаем False'''
            color_text = item_tW.foreground().color().name()
            if color_text == blue_color_tw_text.name():
                rezult = QMessageBox.question(self, 'Предупреждение',
                                              "Заменить Акт установки/удаления СЗИ?",
                                              QMessageBox.Ok | QMessageBox.Cancel)
                if rezult == QMessageBox.Cancel:
                    return False

            path_file = QtWidgets.QFileDialog.getOpenFileName(None, 'Пожалуйста выберите Акт установки/удаления СЗИ.')

            if path_file[0] == '':
                return False

            if pathlib.Path(path_file[0]).suffix != '.pdf':
                QMessageBox.warning(self, 'Внимание', "Можно загрузить только pdf файлы!", QMessageBox.Ok)
                return False
            return path_file[0]

        item = self.tW_act.item(self.tW_act.currentRow(), self.tW_act.currentColumn())
        path_file = check_download_file(item)

        if path_file==False:
            return

        id_SziAccounting=self.tW_act.item(self.tW_act.currentRow(), 0).text()

        if self.tW_act.currentColumn() == 1:
            '''Делаем загрузку акта инсталяции'''
            sziAccounting = self.s.query(SziAccounting.fileInstSzi_id, SziAccounting.fileUninstSzi_id). \
                filter(SziAccounting.id == id_SziAccounting).one()
            id_SziFileInst = sziAccounting[0]
            self.download_SziFileInst(id_SziFileInst, path_file)

            self.changed_current_cell_user()
        else:
            '''Делаем загрузку акта деинсталяции'''
            id_fileUninstSzi_id = self.s.query(SziAccounting.fileUninstSzi_id). \
                filter(SziAccounting.id == id_SziAccounting).one()

            self.download_SziFileUninst(id_fileUninstSzi_id[0], path_file)

            self.changed_current_cell_user()

    def create_tW_act(self):
        self.tW_act = QtWidgets.QTableWidget()
        self.tW_act.setShowGrid(False)
        self.tW_act.setWordWrap(True)
        self.tW_act.setCornerButtonEnabled(True)
        self.tW_act.setVisible(False)
        self.tW_act.itemDoubleClicked.connect(self.read_act)

        self.tW_act.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tW_act.customContextMenuRequested.connect(self.contextMenuRequested_tw_act)

        numrows = 0
        numcols = 3

        self.tW_act.setColumnCount(numcols)
        self.tW_act.setRowCount(numrows)

        self.tW_act.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        self.tW_act.verticalHeader().setVisible(False)
        self.tW_act.setHorizontalHeaderItem(0, QTableWidgetItem('fileInstSzi_id'))
        self.tW_act.setHorizontalHeaderItem(1, QTableWidgetItem('Акт установки СЗИ'))
        self.tW_act.setHorizontalHeaderItem(2, QTableWidgetItem('Акт удаления СЗИ'))

        header = self.tW_act.horizontalHeader()
        header.setSectionResizeMode(0, 10)
        self.tW_act.setColumnHidden(0, True)

        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

    def create_tW_info(self):
        '''Создаем табицу инфо tW_info'''
        self.tW_info = QtWidgets.QTableWidget()
        self.tW_info.setShowGrid(False)
        self.tW_info.setWordWrap(True)
        self.tW_info.setCornerButtonEnabled(True)

        numrows = 12
        numcols = 2

        self.tW_info.setColumnCount(numcols)
        self.tW_info.setRowCount(numrows)

        header = self.tW_info.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.tW_info.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        self.tW_info.horizontalHeader().setVisible(False)
        self.tW_info.verticalHeader().setVisible(False)

        self.tW_info.setItem(0, 0, QTableWidgetItem('Тип СЗИ:'))
        self.tW_info.setItem(1, 0, QTableWidgetItem('Серийный номер:'))
        self.tW_info.setItem(2, 0, QTableWidgetItem('Инв. номер:'))
        self.tW_info.setItem(3, 0, QTableWidgetItem('Лицензия:'))
        self.tW_info.setItem(4, 0, QTableWidgetItem('Комплектность:'))
        self.tW_info.setItem(5, 0, QTableWidgetItem('Сертификаты:'))
        self.tW_info.setItem(6, 0, QTableWidgetItem('Реквизиты:'))
        self.tW_info.setItem(7, 0, QTableWidgetItem('Акт установки:'))
        self.tW_info.setItem(8, 0, QTableWidgetItem('Комплекс:'))
        self.tW_info.setItem(9, 0, QTableWidgetItem('Место установки:'))
        self.tW_info.setItem(10, 0, QTableWidgetItem('Отв-ный ФИО:'))
        self.tW_info.setItem(11, 0, QTableWidgetItem('Должность:'))

        height_tW = Main_load.get_height_qtable(numrows)
        self.tW_info.setMaximumHeight(height_tW - 22)
        self.tW_info.setMinimumHeight(height_tW - 22)

        for rowPosition in range(numrows):
            self.tW_info.item(rowPosition, 0).setBackground(QBrush(Qt.lightGray))  # серый фон
            self.tW_info.item(rowPosition, 0).setTextAlignment(
                Qt.AlignVCenter | Qt.AlignRight)  # Выравнивание по правому краю
            self.tW_info.item(rowPosition, 0).setFlags(
                Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # запрет редактирования

        self.tW_info.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.tW_info.setFocusPolicy(Qt.NoFocus)
        self.tW_info.setSelectionMode(QAbstractItemView.NoSelection)

    def clicked_btn_info(self):
        if Main_load.get_id(self.ui) == None:
            return

        if self.btn_info.isChecked():
            self.btn_info.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
            self.tW_info.setVisible(True)
            self.print_fill_szi(Main_load.get_id(self.ui))
        else:
            self.btn_info.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))
            self.tW_info.setVisible(False)

    def create_btn_info(self):
        '''Создаем кноку свернуть развернуть инфо'''
        self.btn_info = QtWidgets.QPushButton()
        self.btn_info.clicked.connect(self.clicked_btn_info)
        self.btn_info.setText('Информация о СЗИ')
        self.btn_info.setCheckable(True)
        self.btn_info.setChecked(True)
        self.btn_info.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
        self.btn_info.setIconSize(QtCore.QSize(30, 30))

    def create_menu_button(self):
        '''Создаем МенюБар и кноки в меню'''
        self.ui.action_exit.triggered.connect(self.close)
        self.ui.action_add.triggered.connect(self.clicked_btn_new)
        self.ui.action_edit.triggered.connect(self.clicked_btn_edit)
        self.ui.action_sort.triggered.connect(self.clicked_btn_sort)
        self.ui.action_export.triggered.connect(self.clicked_btn_export)

        self.ui.btn_new.clicked.connect(self.clicked_btn_new)
        self.ui.btn_edit.clicked.connect(self.clicked_btn_edit)
        self.ui.btn_sort.clicked.connect(self.clicked_btn_sort)
        self.ui.btn_export.clicked.connect(self.clicked_btn_export)

        self.ui.btn_new.setIcon(QIcon(self.path_helper + '/Icons/add.png'))
        self.ui.btn_edit.setIcon(QIcon(self.path_helper + '/Icons/edit.png'))
        self.ui.btn_export.setIcon(QIcon(self.path_helper + '/Icons/export.png'))
        self.ui.btn_sort.setIcon(QIcon(self.path_helper + '/Icons/sorts.png'))

    def load_szi(self):

        def convert_str_bool(str):
            if str == 'True' or str == True:
                return True
            else:
                return False

        checkBox_status_on = convert_str_bool(config['Szi']['checkB_statusOn'])
        checkBox_status_of = convert_str_bool(config['Szi']['checkB_statusOff'])

        checked_Equipment = config['Szi']['checked_item_Equipment']
        # checked_typeEquipment = config['Szi']['checked_typeEquipment']
        checked_brabch = config['Szi']['checked_item_Branch']
        checked_department = config['Szi']['checked_item_Department']
        checked_szi_type = config['Szi']['checked_item_Szi']
        checked_employeeId = config['Szi']['checked_item_User']

        if checkBox_status_on == False and checkBox_status_of == False:
            status = '% % %'
        if checkBox_status_on == True and checkBox_status_of == False:
            status = 1
        if checkBox_status_on == True and checkBox_status_of == True:
            status = '%'
        if checkBox_status_on == False and checkBox_status_of == True:
            status = 0

        # filter(Office_equipment.type_equipment_id.in_((checked_typeEquipment))). \
        szi = self.s.query(SziAccounting.id, SziType.name). \
            select_from(SziAccounting). \
            join(SziType). \
            join(SziEquipment). \
            join(Office_equipment). \
            join(Branch). \
            join(Department). \
            join(SziFileInst). \
            join(User, SziFileInst.user_id == User.employeeId). \
            filter(SziAccounting.sziType_id.in_((checked_szi_type))). \
            filter(SziAccounting.status.like(status)). \
            filter(SziEquipment.equipment_id.in_((checked_Equipment))). \
            filter(Branch.id.in_((checked_brabch))). \
            filter(Department.id.in_((checked_department))). \
            filter(User.employeeId.in_((checked_employeeId))). \
            order_by(SziAccounting.id). \
            group_by(SziAccounting.id)
        return szi

    def print_fill_szi(self, current_id):
        sziAccounting = self.s.query(SziAccounting, SziType, SziFileInst, User, SziFileUninst). \
            select_from(SziAccounting). \
            join(SziType). \
            join(SziFileInst). \
            join(User). \
            join(SziFileUninst, isouter=True). \
            filter(SziAccounting.id == current_id).one()

        number_act = str(sziAccounting[2].id)
        date_act = str(sziAccounting[2].date.strftime('%d.%m.%Y'))

        self.tW_info.setItem(0, 1, QTableWidgetItem(sziAccounting[1].name))
        self.tW_info.setItem(1, 1, QTableWidgetItem(sziAccounting[0].sn))
        self.tW_info.setItem(2, 1, QTableWidgetItem(sziAccounting[0].inv))
        self.tW_info.setItem(3, 1, QTableWidgetItem(sziAccounting[0].lic))
        self.tW_info.setItem(4, 1, QTableWidgetItem(sziAccounting[1].completeness))
        self.tW_info.setItem(5, 1, QTableWidgetItem(sziAccounting[1].sert))
        self.tW_info.setItem(6, 1, QTableWidgetItem(sziAccounting[0].rec))
        self.tW_info.setItem(7, 1, QTableWidgetItem('Акт № ' + number_act + ' от ' + date_act))
        self.tW_info.setItem(8, 1, QTableWidgetItem(sziAccounting[1].project))
        self.tW_info.setItem(9, 1, QTableWidgetItem(sziAccounting[2].equipments))
        self.tW_info.setItem(10, 1, QTableWidgetItem(sziAccounting[3].fio))
        self.tW_info.setItem(11, 1, QTableWidgetItem(sziAccounting[3].post))

    def changed_current_cell_user(self):
        '''Действие при смене ячейки в списке'''

        current_id = Main_load.get_id(self.ui)

        if current_id is not None:
            self.chek_uninst_szi(current_id)

            if self.btn_info.isChecked():
                self.print_fill_szi(current_id)

            if self.btn_akt.isChecked():
                self.print_tW_act()


        else:
            self.btn_uninstall_szi.setEnabled(False)

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

    def clicked_btn_new(self):
        self.szi_new = Szi_new(None, self.path_helper)
        self.szi_new.exec_()

        if self.szi_new.szi_new_id == None:
            return

        Main_load.print_list(self.ui, self.load_szi())
        Main_load.select_row_intable(self.ui, str(self.szi_new.szi_new_id))

    def clicked_btn_edit(self):
        print('clicked_btn_edit')

    def clicked_btn_sort(self):
        self.sort_view = Szi_sortView()
        self.sort_view.exec_()

        Main_load.print_list(self.ui, self.load_szi())
        Main_load.select_row_intable(self.ui)

    def clicked_btn_export(self):
        print('clicked_btn_export')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(style)
    w = Szi_main()
    w.show()
    sys.exit(app.exec_())
