import os
import pathlib
import subprocess
import sys
from functools import partial
import openpyxl
from sqlalchemy import or_
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon, QBrush, QColor, QFont
from datetime import datetime
from PyQt5.QtWidgets import QPushButton, QApplication, QToolButton, QAction, QHeaderView, QTableWidgetItem, \
    QAbstractItemView, QAbstractScrollArea, QMessageBox
from PyQt5.uic.properties import QtGui
from Model.database import session
from Model.mainList import MainList
from Model.model import Office_equipment, Branch, Department, Office_type_equipment, SziAccounting, SziType, \
    SziFileInst, SziFileUninst, SziEquipment, ServiceDepartment
from View.main_container.newContainer import Ui_MainWindow
from ViewModel.Docx_replace import replace_text
from ViewModel.Equipment.change_equipment import Change_equipment
from ViewModel.Equipment.equipment_new import Equipment_new
from ViewModel.Equipment.equipment_sortView import Equipment_sortView
from ViewModel.Helper_all import Helper_all
from ViewModel.main_load import Main_load
from ViewModel.setting_view import Setting_view
from config_helper import config
from stylesheet import style, blue_color_tw_text


class Equipment_main(QtWidgets.QMainWindow):
    def __init__(self, path_helper):
        super(Equipment_main, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.s = session()

        self.path_helper = path_helper
        self.setStyleSheet(style)

        self.ui.lineEdit_searchUser.textChanged.connect(partial(self.searchEquipment))

        width = QtWidgets.qApp.desktop().availableGeometry(self).width()  # Устанавливаем размер долей рабочих панелей
        self.ui.splitter.setSizes([width * 1 / 3, width * 2 / 3])

        self.setWindowTitle("Оргтехника")
        self.setWindowIcon(QIcon(self.path_helper + '/Icons/equipment.png'))

        self.create_menu_button()

        self.create_btn_info()
        self.ui.verticalLayout_info.addWidget(self.btn_info)

        self.create_tW_info()
        self.ui.verticalLayout_info.addWidget(self.tW_info)

        self.create_btn_notes()
        self.ui.verticalLayout_info.addWidget(self.btn_notes)

        self.create_tE_notes()
        self.ui.verticalLayout_info.addWidget(self.tE_notes)

        self.create_btn_szi()
        self.ui.verticalLayout_info.addWidget(self.btn_szi)

        self.create_tW_szi()
        self.ui.verticalLayout_info.addWidget(self.tW_szi)

        self.create_btn_uninstall_szi()
        self.btn_uninstall_szi.setEnabled(False)
        self.ui.horizontalLayout_4.insertWidget(4, self.btn_uninstall_szi)

        self.create_btn_print()
        self.btn_print.setEnabled(False)
        self.ui.horizontalLayout_4.insertWidget(5, self.btn_print)

        self.create_btn_download()
        self.btn_download.setEnabled(False)
        self.ui.horizontalLayout_4.insertWidget(6, self.btn_download)

        self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                    QtWidgets.QSizePolicy.Expanding)  # Подпружиниваем по вертикали
        self.ui.verticalLayout_info.addItem(self.verticalSpacer)

        self.new_mainList()

    def update_mainList(self, selrctedRow_id):
        '''Сигнал clicked_button (ОК or Cancel)с окна szi_new возвращает id нового СЗИ, обновлет если не 0 список СЗИ'''
        if selrctedRow_id != 0:
            self.mainList.update_mainList(self.load_equipment(), int(selrctedRow_id))

        self.ui.btn_new.setEnabled(True)
        self.ui.btn_edit.setEnabled(True)

    def new_mainList(self):
        self.mainList = MainList(self.load_equipment(), False)
        self.mainList.dataSignal.connect(self.item_selection_changed_mainList)
        self.ui.verticalLayout_list.insertWidget(0, self.mainList)

    def mouseDoubleClickEvent_tW_act(self, item: QTableWidgetItem):
        def write_to_file(data, filename):
            # Преобразование двоичных данных в нужный формат
            with open(filename, 'wb') as file:
                file.write(data)

        if item.column() == 4 or item.column() == 5:

            id_sziFileInst = self.tW_szi.item(self.tW_szi.currentRow(), 1).text()
            id_sziFileUnInst = self.tW_szi.item(self.tW_szi.currentRow(), 6).text()

            if item.column() == 4 and id_sziFileInst != '':
                fileInstSzi = self.s.query(SziFileInst.file_data).filter(SziFileInst.id == id_sziFileInst).one()
                if fileInstSzi[0] != None:
                    name_act = 'Акт установки СЗИ - ' + id_sziFileInst + '.pdf'
                    downloads_path = Main_load.get_helperExport('Equipment')
                    regForm_path = os.path.join(downloads_path + '/' + name_act)
                    write_to_file(fileInstSzi[0], regForm_path)
                    subprocess.call(["xdg-open", regForm_path])

            if item.column() == 5 and id_sziFileUnInst != '':
                if self.check_replace_actUninst(id_sziFileUnInst):
                    act = self.s.query(SziFileUninst.file_data). \
                        filter(SziFileUninst.id == id_sziFileUnInst).one()
                    name_act = 'Акт вывода СЗИ - ' + id_sziFileUnInst + '.pdf'
                    downloads_path = Main_load.get_helperExport('Equipment')
                    regForm_path = os.path.join(downloads_path + '/' + name_act)
                    write_to_file(act[0], regForm_path)
                    subprocess.call(["xdg-open", regForm_path])

    def eventFilter(self, source, event):
        if (source is self.tW_szi.viewport() and
            (event.type() == QEvent.DragEnter or
             event.type() == QEvent.DragMove or
             event.type() == QEvent.Drop) and
            event.mimeData().hasUrls()) and self.tW_szi.currentRow() != -1:
            if event.type() == QEvent.Drop:
                if self.chek_count_fileUnistSzi_id(self.tW_szi.item(self.tW_szi.currentRow(), 6).text()):
                    path_file = []
                    for url in event.mimeData().urls():
                        if url.isLocalFile():
                            path_file.append(url.path())

                    if Main_load.check_download_file(path_file):
                        if self.check_replace_actUninst(self.tW_szi.item(self.tW_szi.currentRow(), 6).text()):
                            rezult = QMessageBox.question(self, 'Предупреждение',
                                                          "Заменить Акт вывода из эксплуатации?",
                                                          QMessageBox.Ok | QMessageBox.Cancel)

                            if rezult == QMessageBox.Cancel:
                                event.accept()
                                return True
                                return super().eventFilter(source, event)

                        self.download_SziFileUninst(path_file[0],
                                                    self.tW_szi.item(self.tW_szi.currentRow(), 6).text())
                        QMessageBox.warning(self, 'Внимание', "Фаил загружен!",
                                            QMessageBox.Ok)
                        self.print_tW_Szi(self.mainList.get_id())
                        self.tW_szi.selectRow(False)
                    else:
                        QMessageBox.warning(self, 'Внимание', "Можно загрузить только один pdf файл!", QMessageBox.Ok)

            event.accept()
            return True
        return super().eventFilter(source, event)

    def download_SziFileUninst(self, path_file, id_SziFileUninst):
        '''Save regForm to dataBase'''

        file_name = pathlib.Path(path_file).name
        file_data = Helper_all.convertToBinaryData(path_file)

        sziFileUninst = self.s.query(SziFileUninst).filter(SziFileUninst.id == id_SziFileUninst).one()
        sziFileUninst.fileName = file_name
        sziFileUninst.file_data = file_data

        self.s.add(sziFileUninst)
        self.s.commit()

    def chek_count_fileUnistSzi_id(self, fileUninstSzi_id):
        '''Проверяем количество актов удаления в таблице SziEquipment, если один возращаем True'''
        count_fileUnistSzi_id = self.s.query(SziEquipment.fileUninstSzi_id).filter(
            SziEquipment.fileUninstSzi_id == fileUninstSzi_id)
        if count_fileUnistSzi_id.count() == 1:
            return True
        else:
            return False

    def check_replace_actUninst(self, id_SziFileUninst):
        '''Проверяем загружен ли акт деинсталяции, если загружен возвращаем True'''
        file_data = (self.s.query(SziFileUninst.file_data).
                     filter(SziFileUninst.id == id_SziFileUninst).one())
        if file_data[0] == None:
            return False
        else:
            return True

    def clicked_btn_dowload(self):
        if self.check_replace_actUninst(self.tW_szi.item(self.tW_szi.currentRow(), 6).text()):
            rezult = QMessageBox.question(self, 'Предупреждение', "Заменить Акт вывода из эксплуатации?",
                                          QMessageBox.Ok | QMessageBox.Cancel)
            if rezult == QMessageBox.Cancel:
                return

        path_file = QtWidgets.QFileDialog.getOpenFileName(None, 'Пожалуйста выберите Акт вывода из эксплуатации.')

        if path_file[0] == '':
            return

        if pathlib.Path(path_file[0]).suffix != '.pdf':
            QMessageBox.warning(self, 'Внимание', "Можно загрузить только pdf файлы!", QMessageBox.Ok)
            return

        self.download_SziFileUninst(path_file[0], self.tW_szi.item(self.tW_szi.currentRow(), 6).text())

        self.print_tW_Szi(self.mainList.get_id())
        self.tW_szi.selectRow(False)

    def create_btn_download(self):
        self.btn_download = QtWidgets.QToolButton()
        self.btn_download.clicked.connect(self.clicked_btn_dowload)
        self.btn_download.setText('Загрузить')
        self.btn_download.setIcon(QIcon(self.path_helper + '/Icons/download.png'))
        self.btn_download.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

    def clicked_btn_print(self):

        id_equipment = self.mainList.get_id()
        id_SziFileUninst = self.tW_szi.item(self.tW_szi.currentRow(), 6).text()
        id_SziAccounting = self.tW_szi.item(self.tW_szi.currentRow(), 3).text()

        lst = []
        lst.append(id_equipment)

        info_equipment = Helper_all.info_equipment_act_szi(lst, id_SziAccounting)

        sziFileUninst = self.s.query(SziFileUninst).filter(SziFileUninst.id == id_SziFileUninst).one()
        date_unist = sziFileUninst.date.strftime('%d.%m.%Y')
        date_unist_full = Helper_all.get_date_full(date_unist)

        sziAccounting = self.s.query(SziAccounting, SziType). \
            join(SziType). \
            filter(SziAccounting.id == id_SziAccounting).one()
        nameSzi = sziAccounting[1].name
        sn = sziAccounting[0].sn

        dictionary = {'DateFull': date_unist_full,
                      'Date': date_unist,
                      'Number': str(id_SziFileUninst),
                      'Equipment': info_equipment,
                      'id_SziAccounting': id_SziAccounting,
                      'NameSzi': nameSzi,
                      'SN': sn}

        path_exportEquipment = Main_load.get_helperExport('Equipment')

        forma = self.path_helper + '/' + 'Form_print' + '/' + 'Uninst_SZI.docx'

        name_file = 'Акт вывода из эксплуатации № ' + str(id_SziFileUninst)

        replace_text(forma, dictionary, path_exportEquipment + '/' + name_file)

        # name_file = 'Акт удаления- ' + str(id_SziFileUninst)
        #
        # replace_text(Helper_all.get_path_form('Uninst_SZI.docx'), dictionary, name_file)

    def create_btn_print(self):
        '''Создаем кноку свернуть развернуть инфо'''
        self.btn_print = QtWidgets.QToolButton()
        self.btn_print.clicked.connect(self.clicked_btn_print)
        self.btn_print.setText('Печать')
        self.btn_print.setIcon(QIcon(self.path_helper + '/Icons/print.png'))
        self.btn_print.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

    def uninstal_szi(self):
        def check_last_equipment():
            '''Если посталсья последний с установленным СЗИ equipment, то возвращаем False'''
            sziEquipment = self.s.query(SziEquipment). \
                filter(SziEquipment.sziAccounting_id == id_SziAccounting). \
                filter(SziEquipment.status == True)
            if sziEquipment.count() <= 1:
                return True
            else:
                return False

        def reserve_id_SziFileUninst() -> int:
            '''Резервируем и возвращаем id в SziFileUninst '''
            sziFileUninst = SziFileUninst(fileName='', date=datetime.now().date())
            self.s.add(sziFileUninst)
            self.s.flush()
            return sziFileUninst.id

        id_Equipment = self.mainList.get_id()
        id_SziAccounting = self.tW_szi.item(self.tW_szi.currentRow(), 3).text()

        if check_last_equipment():
            QMessageBox.warning(self, 'Внимание',
                                "Остался последний объект с установленным СЗИ, удалите с раздела СЗИ",
                                QMessageBox.Ok)
            return

        id_SziFileUninst = reserve_id_SziFileUninst()

        sziEquipment = self.s.query(SziEquipment). \
            filter(SziEquipment.equipment_id == id_Equipment). \
            filter(SziEquipment.sziAccounting_id == id_SziAccounting).one()
        sziEquipment.fileUninstSzi_id = id_SziFileUninst
        sziEquipment.status = False
        self.s.add(sziEquipment)

        self.s.commit()

        self.print_tW_Szi(id_Equipment)

    def clicked_btn_uninstall_szi(self):

        rezult = QMessageBox.question(self, 'Предупреждение', "Вы действительно хотите деисталировать выбранное СЗИ?",
                                      QMessageBox.Ok | QMessageBox.Cancel)
        if rezult == QMessageBox.Cancel:
            return

        self.uninstal_szi()
        #
        # path_file = QtWidgets.QFileDialog.getOpenFileName(None, 'Пожалуйста выберите регистрационную форму.')
        #
        # if path_file[0] == '':
        #     return
        #
        # if pathlib.Path(path_file[0]).suffix != '.pdf':
        #     QMessageBox.warning(self, 'Внимание', "Можно загрузить только pdf файлы!", QMessageBox.Ok)
        #     return
        #
        # self.download_regForm(path_file[0], self.tW_regForm.item(self.tW_regForm.currentRow(), 0).text())

    def create_btn_uninstall_szi(self):
        self.btn_uninstall_szi = QtWidgets.QToolButton()
        self.btn_uninstall_szi.clicked.connect(self.clicked_btn_uninstall_szi)
        self.btn_uninstall_szi.setText('Удалить')
        self.btn_uninstall_szi.setIcon(QIcon(self.path_helper + '/Icons/uninstall.png'))
        self.btn_uninstall_szi.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

    def searchEquipment(self):
        Main_load.print_list(self.ui, self.load_equipment())
        Main_load.select_row_intable(self.ui)

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

        self.ui.btn_new.setIcon(QIcon(self.path_helper + '/Icons/User/add-user-male-40.png'))
        self.ui.btn_edit.setIcon(QIcon(self.path_helper + '/Icons/User/registration-40.png'))
        self.ui.btn_export.setIcon(QIcon(self.path_helper + '/Icons/microsoft-excel-40.png'))
        self.ui.btn_sort.setIcon(QIcon(self.path_helper + '/Icons/User/search-user-40.png'))

        self.ui.btn_new.setIcon(QIcon(self.path_helper + '/Icons/add.png'))
        self.ui.btn_edit.setIcon(QIcon(self.path_helper + '/Icons/edit.png'))
        self.ui.btn_export.setIcon(QIcon(self.path_helper + '/Icons/export.png'))
        self.ui.btn_sort.setIcon(QIcon(self.path_helper + '/Icons/sorts.png'))

    def clicked_btn_info(self):
        if self.mainList.get_id() == None:
            return

        if self.btn_info.isChecked():
            self.btn_info.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
            self.tW_info.setVisible(True)
            self.print_fill_equipment(self.mainList.get_id())
        else:
            self.btn_info.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))
            self.tW_info.setVisible(False)

    def clicked_btn_new(self):
        self.equipment_new = Equipment_new(None)
        self.equipment_new.dataSignal.connect(self.update_mainList)
        self.equipment_new.exec_()

    def clicked_btn_edit(self):
        self.equipment_new = Equipment_new(self.mainList.get_id())
        self.equipment_new.dataSignal.connect(self.update_mainList)
        self.equipment_new.exec_()

    def clicked_btn_sort(self):
        self.sort_view = Equipment_sortView()
        self.sort_view.dataSignal.connect(self.update_mainList)
        self.sort_view.exec_()

    def clicked_btn_export(self):
        '''Экспорт в эксель'''
        result = QMessageBox.warning(self, 'Предупреждение',
                                     "Вы действительно хотите выгрузить в XLSX?",
                                     QMessageBox.Ok, QMessageBox.Cancel)
        if result == 1024:
            count_row = self.ui.tW_list.rowCount()
            list_Id = []
            for i in range(count_row):
                list_Id.append(self.ui.tW_list.item(i, 0).text())
            list_export_equipments = []
            for i in list_Id:
                list_export_equipments.append(
                    self.s.query(Office_equipment.branch_id, Department.name,
                                 Office_equipment.type_equipment_id, Office_equipment.name_equipment,
                                 Office_equipment.inv_number, Office_equipment.start_date,
                                 Office_equipment.model_equipment, Office_equipment.manufacturer,
                                 Office_equipment.sn_equipment, Office_equipment.notes).
                    select_from(Office_equipment).join(Department).filter(Office_equipment.id == i).one())

            wb = openpyxl.Workbook()
            sheet = wb.sheetnames
            lis = wb.active
            # Создание строки с заголовками
            lis.append(('Филиал', 'Служба', 'Тип устройства', 'Имя устройства', 'Инвентарный номер',
                        'Дата производства', 'Модель', 'Производитель',
                        'Серийный номер', 'Дополнительно'))
            for equipment in list_export_equipments:
                lis.append(list(equipment))

            path_exportEquipment = Main_load.get_helperExport('Equipment')

            wb.save(filename=path_exportEquipment + '/Equipments.xlsx')
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, path_exportEquipment + '/Equipments.xlsx'])

    def item_selection_changed_mainList(self):
        '''Действие при смене ячейки в списке'''
        equipment_id = self.mainList.get_id()
        if equipment_id is not None:
            if self.btn_info.isChecked():
                self.print_fill_equipment(equipment_id)

            if self.btn_notes.isChecked():
                self.print_tE_notes(equipment_id)

            if self.btn_szi.isCheckable():
                self.print_tW_Szi(equipment_id)

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

            self.tE_notes.setText('')

            self.tW_szi.setRowCount(0)

    def create_btn_info(self):
        '''Создаем кноку свернуть развернуть инфо'''
        self.btn_info = QtWidgets.QPushButton()
        self.btn_info.clicked.connect(self.clicked_btn_info)
        self.btn_info.setText('Информация о технике')
        self.btn_info.setCheckable(True)
        self.btn_info.setChecked(True)
        self.btn_info.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
        self.btn_info.setIconSize(QtCore.QSize(30, 30))

    def create_btn_notes(self):
        '''Создаем кноку свернуть развернуть tE_notes'''
        self.btn_notes = QtWidgets.QPushButton()
        self.btn_notes.clicked.connect(self.clicked_btn_notes)
        self.btn_notes.setText('Дополнительная информация')
        # self.btn_notes.setFont(QFont('Arial', 14))
        self.btn_notes.setCheckable(True)
        self.btn_notes.setChecked(False)
        self.btn_notes.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))
        self.btn_notes.setIconSize(QtCore.QSize(30, 30))

    def clicked_btn_notes(self):
        if self.mainList.get_id() == None:
            return

        if self.btn_notes.isChecked():
            self.btn_notes.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
            self.tE_notes.setVisible(True)
            self.print_tE_notes(self.mainList.get_id())
        else:
            self.btn_notes.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))
            self.tE_notes.setVisible(False)

    def create_tE_notes(self):
        self.tE_notes = QtWidgets.QTextEdit()
        self.tE_notes.setVisible(False)

    def create_btn_szi(self):
        '''Создаем кноку свернуть развернуть tW_szi'''
        self.btn_szi = QtWidgets.QPushButton()
        self.btn_szi.clicked.connect(self.clicked_btn_szi)
        self.btn_szi.setText('Сведения о СЗИ')
        # self.btn_notes.setFont(QFont('Arial', 14))
        self.btn_szi.setCheckable(True)
        self.btn_szi.setChecked(False)
        self.btn_szi.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))
        self.btn_szi.setIconSize(QtCore.QSize(30, 30))

    def clicked_btn_szi(self):
        if self.mainList.get_id() == None:
            return

        if self.btn_szi.isChecked():
            self.btn_szi.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
            self.tW_szi.setVisible(True)
            # self.print_tE_notes(Mself.mainList.get_id())
        else:
            self.btn_szi.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))
            self.tW_szi.setVisible(False)
            self.tW_szi.selectRow(False)

    def changed_current_cell_tW_szi(self):
        if self.tW_szi.currentColumn() == 5 and self.tW_szi.item(self.tW_szi.currentRow(), 5).text() == '':
            self.btn_uninstall_szi.setEnabled(True)
        else:
            self.btn_uninstall_szi.setEnabled(False)

        if self.tW_szi.currentColumn() == 5 and self.tW_szi.item(self.tW_szi.currentRow(), 6).text() != '':
            self.btn_print.setEnabled(True)

            if self.chek_count_fileUnistSzi_id(self.tW_szi.item(self.tW_szi.currentRow(), 6).text()):
                self.btn_download.setEnabled(True)
            else:
                self.btn_download.setEnabled(False)
                self.btn_print.setEnabled(False)
        else:
            self.btn_print.setEnabled(False)
            self.btn_download.setEnabled(False)

    def change_equipment(self):
        change_equipment = Change_equipment(self.mainList.get_id(),
                                            self.tW_szi.item(self.tW_szi.currentRow(), 3).text())
        change_equipment.exec_()

        self.print_tW_Szi(self.mainList.get_id())

    def contextMenuRequested_tW_szi(self, pos):
        if self.tW_szi.currentColumn() == 2:
            menu = QtWidgets.QMenu()
            btn_change_equipment = menu.addAction("Перенести СЗИ")

            btn_change_equipment.triggered.connect(self.change_equipment)

            menu.exec_(self.tW_szi.viewport().mapToGlobal(pos))

    def create_tW_szi(self):
        '''Создаем табицу инфо tW_info'''
        self.tW_szi = QtWidgets.QTableWidget()
        self.tW_szi.setWordWrap(True)
        self.tW_szi.setVisible(False)
        self.tW_szi.setCornerButtonEnabled(True)
        self.tW_szi.viewport().installEventFilter(self)
        self.tW_szi.setAcceptDrops(True)
        self.tW_szi.itemSelectionChanged.connect(self.changed_current_cell_tW_szi)
        self.tW_szi.itemDoubleClicked.connect(self.mouseDoubleClickEvent_tW_act)

        self.tW_szi.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tW_szi.customContextMenuRequested.connect(self.contextMenuRequested_tW_szi)

        numrows = 0
        numcols = 7

        self.tW_szi.setColumnCount(numcols)
        self.tW_szi.setRowCount(numrows)

        self.tW_szi.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        self.tW_szi.verticalHeader().setVisible(False)
        self.tW_szi.setHorizontalHeaderItem(1, QTableWidgetItem('id file inst'))
        self.tW_szi.setHorizontalHeaderItem(2, QTableWidgetItem('Наименование СЗИ'))
        self.tW_szi.setHorizontalHeaderItem(3, QTableWidgetItem('Уч. №'))
        self.tW_szi.setHorizontalHeaderItem(4, QTableWidgetItem('Акт установки'))
        self.tW_szi.setHorizontalHeaderItem(5, QTableWidgetItem('Акт удаления'))
        self.tW_szi.setHorizontalHeaderItem(6, QTableWidgetItem('id file uninst'))

        header = self.tW_szi.horizontalHeader()
        header.setSectionResizeMode(0, 10)
        self.tW_szi.setColumnHidden(0, True)
        self.tW_szi.setColumnHidden(1, True)
        self.tW_szi.setColumnHidden(6, True)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(3, 10)

    def print_tW_Szi(self, id_Office_equipment):
        self.tW_szi.setRowCount(0)

        office_equipment = self.s.query(SziAccounting.id, SziType.name, SziFileInst.id, SziFileInst.date,
                                        SziFileUninst.id, SziFileUninst.date, SziFileUninst.file_data,
                                        SziFileInst.file_data). \
            select_from(Office_equipment). \
            join(SziEquipment). \
            join(SziAccounting). \
            join(SziType). \
            join(SziFileInst). \
            join(SziFileUninst, SziEquipment.fileUninstSzi_id == SziFileUninst.id, isouter=True). \
            filter(Office_equipment.id == id_Office_equipment)

        for i in office_equipment:
            rowPosition = self.tW_szi.rowCount()
            self.tW_szi.insertRow(rowPosition)

            number_act = str(i[2])
            date_act = str(i[3].strftime('%d.%m.%Y'))
            act = ('Акт № ' + number_act + ' от ' + date_act)

            if i[4] is not None:
                number_uninst = str(i[4])
                date_uninst = str(i[5].strftime('%d.%m.%Y'))
                act_uninst = ('Акт № ' + number_uninst + ' от ' + date_uninst)
            else:
                number_uninst = ''
                act_uninst = ''

            if i[6] == None:
                collor_tex = Qt.red
            else:
                collor_tex = blue_color_tw_text

            if i[7] == None:
                collor_tex_inst = Qt.red
            else:
                collor_tex_inst = blue_color_tw_text

            self.tW_szi.setItem(rowPosition, 1, QTableWidgetItem(str(i[2])))
            self.tW_szi.setItem(rowPosition, 3, QTableWidgetItem(str(i[0])))
            self.tW_szi.setItem(rowPosition, 2, QTableWidgetItem(i[1]))
            self.tW_szi.setItem(rowPosition, 4, QTableWidgetItem(act))
            self.tW_szi.setItem(rowPosition, 5, QTableWidgetItem(act_uninst))
            self.tW_szi.setItem(rowPosition, 6, QTableWidgetItem(number_uninst))

            self.tW_szi.item(rowPosition, 5).setForeground(QBrush(collor_tex))
            self.tW_szi.item(rowPosition, 4).setForeground(QBrush(collor_tex_inst))

        row_count = office_equipment.count()

        height_tW = Main_load.get_height_qtable(row_count)
        self.tW_szi.setMaximumHeight(height_tW)
        self.tW_szi.setMinimumHeight(height_tW)

    def create_tW_info(self):
        '''Создаем табицу инфо tW_info'''
        self.tW_info = QtWidgets.QTableWidget()
        self.tW_info.setShowGrid(False)
        self.tW_info.setWordWrap(True)
        self.tW_info.setCornerButtonEnabled(True)

        numrows = 11
        numcols = 2

        self.tW_info.setColumnCount(numcols)
        self.tW_info.setRowCount(numrows)

        header = self.tW_info.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.tW_info.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        self.tW_info.horizontalHeader().setVisible(False)
        self.tW_info.verticalHeader().setVisible(False)

        self.tW_info.setItem(0, 0, QTableWidgetItem('Филиал:'))
        self.tW_info.setItem(1, 0, QTableWidgetItem('Обслуживающия служба:'))
        self.tW_info.setItem(2, 0, QTableWidgetItem('Эксплуатирующия служба:'))
        self.tW_info.setItem(3, 0, QTableWidgetItem('Тип устройства:'))
        self.tW_info.setItem(4, 0, QTableWidgetItem('Наименование:'))
        self.tW_info.setItem(5, 0, QTableWidgetItem('Инвентарный номер:'))
        self.tW_info.setItem(6, 0, QTableWidgetItem('Начало эксплуатации:'))
        self.tW_info.setItem(7, 0, QTableWidgetItem('Модель:'))
        self.tW_info.setItem(8, 0, QTableWidgetItem('Производитель:'))
        self.tW_info.setItem(9, 0, QTableWidgetItem('Серийный номер:'))
        self.tW_info.setItem(10, 0, QTableWidgetItem('Расположение:'))

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

    def print_fill_equipment(self, equipment_id):
        '''Запрос в SQL и заполняем tW_info'''
        equipment = self.s.query(Office_equipment, Department.name, Office_type_equipment.name, Branch.name, ServiceDepartment.name). \
            select_from(Office_equipment). \
            join(Department). \
            join(Office_type_equipment). \
            join(Branch). \
            join(ServiceDepartment).\
            filter(Office_equipment.id == equipment_id).one()

        self.tW_info.setItem(0, 1, QTableWidgetItem(equipment[3]))
        self.tW_info.setItem(3, 1, QTableWidgetItem(equipment[2]))
        self.tW_info.setItem(4, 1, QTableWidgetItem(equipment[0].name_equipment))
        self.tW_info.setItem(5, 1, QTableWidgetItem(equipment[0].inv_number))
        self.tW_info.setItem(6, 1, QTableWidgetItem(str((equipment[0].start_date).strftime('%d.%m.%Y'))))
        self.tW_info.setItem(2, 1, QTableWidgetItem(equipment[1]))
        self.tW_info.setItem(7, 1, QTableWidgetItem(equipment[0].model_equipment))
        self.tW_info.setItem(8, 1, QTableWidgetItem(equipment[0].manufacturer))
        self.tW_info.setItem(9, 1, QTableWidgetItem(equipment[0].sn_equipment))
        self.tW_info.setItem(10, 1, QTableWidgetItem(equipment[0].location))
        self.tW_info.setItem(1, 1, QTableWidgetItem(equipment[4]))

    def print_tE_notes(self, equipment_id):
        notes = self.s.query(Office_equipment.notes).filter(Office_equipment.id == equipment_id).one()
        self.tE_notes.setText(notes[0])

    def load_equipment(self):
        checked_branch = config['Equipment']['checked_item_Branch']
        checked_branch = list(checked_branch)
        checked_department = config['Equipment']['checked_item_Department']
        checked_department = list(checked_department)
        serviceDepartment = config['Equipment']['checked_item_ServiceDepartment']
        serviceDepartment = list(serviceDepartment)

        serch_text = '%' + self.ui.lineEdit_searchUser.text() + '%'
        if serch_text == '':
            serch_text = '%'

        status_equipment = Helper_all.get_status(Helper_all.convert_bool(config['Equipment']['checkB_statusOn']),
                                                 Helper_all.convert_bool(config['Equipment']['checkB_statusOff']))
        '''Запрос в SQL список оборудования'''

        equipments = self.s.query(Office_equipment.id, Office_equipment.name_equipment). \
            filter(Office_equipment.branch_id.in_((checked_branch))). \
            filter(Office_equipment.department_id.in_((checked_department))). \
            filter(Office_equipment.serviceDepartment_id.in_((serviceDepartment))). \
            filter(Office_equipment.is_work.like(status_equipment)). \
            filter(or_(
            Office_equipment.name_equipment.like(serch_text),
            Office_equipment.inv_number.like(serch_text),
            Office_equipment.model_equipment.like(serch_text),
            Office_equipment.manufacturer.like(serch_text),
            Office_equipment.sn_equipment.like(serch_text),
            Office_equipment.notes.like(serch_text))). \
            order_by(Office_equipment.name_equipment)
        return equipments


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(style)
    w = Equipment_main()
    w.show()
    sys.exit(app.exec_())
