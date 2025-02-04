import subprocess
import sys
import openpyxl
from sqlalchemy import or_
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QBrush
from PyQt5.QtWidgets import  QApplication, QHeaderView, QTableWidgetItem, \
    QAbstractItemView, QMessageBox
from sqlalchemy.sql.functions import coalesce
from Model.database import session
from Model.model import Office_equipment, Branch, Department, Office_type_equipment,  Skr, User, ServiceDepartment
from View.main_container.container import Ui_MainWindow
from ViewModel.Helper_all import Helper_all
from ViewModel.Skr.Skr_open import Skr_open
from ViewModel.Skr.skr_new import Skr_new
from ViewModel.Skr.skr_sortView import Skr_sortView
from ViewModel.main_load import Main_load
from config_helper import config
from stylesheet import style


class Skr_main(QtWidgets.QMainWindow):
    def __init__(self, path_helper):
        super(Skr_main, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.s = session()

        self.path_helper = path_helper
        self.setStyleSheet(style)

        self.ui.btn_edit.setText('Вскрыть')


        width = QtWidgets.qApp.desktop().availableGeometry(self).width()  # Устанавливаем размер долей рабочих панелей
        self.ui.splitter.setSizes([width * 1 / 3, width * 2 / 3])

        self.setWindowTitle("СКР +")
        self.setWindowIcon(QIcon(self.path_helper + '/Icons/skr.png'))

        self.create_menu_button()

        self.create_btn_info()
        self.ui.verticalLayout_2.addWidget(self.btn_info)

        self.create_tW_info()
        self.ui.verticalLayout_2.addWidget(self.tW_info)

        Main_load.create_tW_list(self.ui)
        self.ui.tW_list.itemSelectionChanged.connect(self.changed_current_cell_user)
        Main_load.print_list(self.ui, self.load_skr())
        Main_load.select_row_intable(self.ui)

        self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                    QtWidgets.QSizePolicy.Expanding)  # Подпружиниваем по вертикали
        self.ui.verticalLayout_2.addItem(self.verticalSpacer)

    def load_skr(self):

        def convert_str_bool(str):
            if str == 'True' or str == True:
                return True
            else:
                return False

        status_equipment = Helper_all.get_status(Helper_all.convert_bool(config['Skr']['checkB_statusOn']),
                                                 Helper_all.convert_bool(config['Skr']['checkB_statusOff']))

        if status_equipment == '% % %':
            status_equipment = '%'

        serch_text = '%' + self.ui.lineEdit_searchUser.text() + '%'
        if serch_text == '':
            serch_text = '%'

        checked_branch = config['Skr']['checked_item_Branch']
        checked_branch = list(checked_branch)
        checked_department = config['Skr']['checked_item_Department']
        checked_department = list(checked_department)
        checked_item_ServiceDepartment = config['Skr']['checked_item_ServiceDepartment']
        checked_item_ServiceDepartment = list(checked_item_ServiceDepartment)

        skr = self.s.query(Skr.id, Office_equipment.name_equipment). \
            select_from(Skr). \
            join(Office_equipment). \
            join(Branch). \
            join(Department). \
            join(ServiceDepartment). \
            join(Office_type_equipment). \
            filter(Office_equipment.branch_id.in_((checked_branch))). \
            filter(Office_equipment.department_id.in_((checked_department))). \
            filter(Office_equipment.serviceDepartment_id.in_((checked_item_ServiceDepartment))).\
            filter(or_(coalesce(Skr.note, 1).like(status_equipment))). \
            filter(or_(
            Office_equipment.name_equipment.like(serch_text),
            Office_equipment.inv_number.like(serch_text),
            Office_equipment.model_equipment.like(serch_text),
            Office_equipment.manufacturer.like(serch_text),
            Office_equipment.sn_equipment.like(serch_text),
            Office_equipment.notes.like(serch_text),
            Skr.numberSkr.like(serch_text))). \
            order_by(Office_equipment.name_equipment)

        return skr

    def print_fill_skr(self, equipment_id):
        '''Запрос в SQL и заполняем tW_info'''
        if equipment_id != None:
            skr = self.s.query(Skr, Office_equipment.name_equipment, Branch.name, Department.name,
                               Office_type_equipment.name). \
                select_from(Skr). \
                join(Office_equipment). \
                join(Branch). \
                join(Department). \
                join(Office_type_equipment). \
                filter(Skr.id == equipment_id).one()

            self.tW_info.setItem(0, 1, QTableWidgetItem(skr[2]))
            self.tW_info.setItem(1, 1, QTableWidgetItem(skr[3]))
            self.tW_info.setItem(2, 1, QTableWidgetItem(skr[1]))
            self.tW_info.setItem(3, 1, QTableWidgetItem(skr[4]))
            self.tW_info.setItem(4, 1, QTableWidgetItem(skr[0].numberSkr))
            self.tW_info.setItem(6, 1, QTableWidgetItem(str(skr[0].startDate.strftime('%d.%m.%Y'))))
            self.tW_info.setItem(7, 1, QTableWidgetItem(skr[0].note))

            fio = self.s.query(Skr.user_id, User.fio).select_from(Skr).join(User).filter(Skr.id == equipment_id).one()
            self.tW_info.setItem(5, 1, QTableWidgetItem(fio[1]))

    def clicked_btn_info(self):
        if Main_load.get_id(self.ui) == None:
            return

        if self.btn_info.isChecked():
            self.btn_info.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
            self.tW_info.setVisible(True)
            self.print_fill_skr(Main_load.get_id(self.ui))
        else:
            self.btn_info.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))
            self.tW_info.setVisible(False)

    def create_btn_info(self):
        '''Создаем кноку свернуть развернуть инфо'''
        self.btn_info = QtWidgets.QPushButton()
        self.btn_info.clicked.connect(self.clicked_btn_info)
        self.btn_info.setText('Информация о СКР+')
        self.btn_info.setCheckable(True)
        self.btn_info.setChecked(True)
        self.btn_info.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
        self.btn_info.setIconSize(QtCore.QSize(30, 30))

    def create_tW_info(self):
        '''Создаем табицу инфо tW_info'''
        self.tW_info = QtWidgets.QTableWidget()
        self.tW_info.setShowGrid(False)
        self.tW_info.setWordWrap(True)
        self.tW_info.setCornerButtonEnabled(True)

        numrows = 8
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
        self.tW_info.setItem(2, 0, QTableWidgetItem('Устройство СКР:'))
        self.tW_info.setItem(3, 0, QTableWidgetItem('Тип устройства:'))
        self.tW_info.setItem(4, 0, QTableWidgetItem('Номер СКР:'))
        self.tW_info.setItem(5, 0, QTableWidgetItem('ФИО ответственного:'))
        self.tW_info.setItem(6, 0, QTableWidgetItem('Дата опломбирования:'))
        self.tW_info.setItem(7, 0, QTableWidgetItem('Причина вскрытия:'))

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

    def chek_empty(self):
        if self.ui.tW_list.rowCount() > 0:
            return True
        else:
            return False

    def changed_current_cell_user(self):
        '''Действие при смене ячейки в списке'''
        if self.chek_empty():
            self.print_fill_skr(Main_load.get_id(self.ui))

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

    def clicked_btn_new(self):
        self.skr_new = Skr_new(None)
        self.skr_new.exec_()

        Main_load.print_list(self.ui, self.load_skr())
        Main_load.select_row_intable(self.ui, self.skr_new.new_skr_id)

    def clicked_btn_edit(self):
        current_id = Main_load.get_id(self.ui)

        skr_open = Skr_open(current_id)
        skr_open.exec_()
        res = skr_open.clicked_btn_save()
        if res:
            Main_load.print_list(self.ui, self.load_skr())
            Main_load.select_row_intable(self.ui)

    def clicked_btn_sort(self):
        sortView = Skr_sortView()
        sortView.exec_()

        Main_load.print_list(self.ui, self.load_skr())
        Main_load.select_row_intable(self.ui)

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
            list_export_skr = []
            for i in list_Id:
                skr = self.s.query(Branch.name, Department.name, Office_equipment.name_equipment,
                                   Office_type_equipment.name, Skr.numberSkr, Skr.startDate, Skr.note). \
                    select_from(Skr). \
                    join(Office_equipment). \
                    join(Branch). \
                    join(Department). \
                    join(Office_type_equipment). \
                    filter(Skr.id == i).one()

                fio = self.s.query(Skr.user_id, User.fio).select_from(Skr).join(User).filter(Skr.id == i).one()
                new_skr = (*skr, fio[1])
                list_export_skr.append(new_skr)

            wb = openpyxl.Workbook()
            sheet = wb.sheetnames
            lis = wb.active
            # Создание строки с заголовками
            lis.append(('Филиал', 'Служба', 'Имя устройства', 'Тип устройства', 'Номер СКР+', 'Дата установки',
                        'Причина вскрытия', 'Ответственный за установку'))
            for equipment in list_export_skr:
                lis.append(list(equipment))

            path_exportEquipment = Main_load.get_helperExport('Skr')

            wb.save(filename=path_exportEquipment + '/Skr.xlsx')
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, path_exportEquipment + '/Skr.xlsx'])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(style)
    w = Skr_main()
    w.show()
    sys.exit(app.exec_())
