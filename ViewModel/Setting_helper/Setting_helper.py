# from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QAbstractItemView
# from View.Setting_helper.Setting_helper import Ui_MainWindow
# from View.Setting_helper.Setting_helper import QtWidgets
# from models.database import session
# from models.model import Department, Usb_type, Branch, Office_type_equipment
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QTableWidgetItem, QHeaderView
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from Model.database import session
from Model.model import Branch, Department
from View.Setting_helper.Setting_helper import Ui_Dialog
from config_helper import config


class Setting_helper(QtWidgets.QDialog):
    def __init__(self, parament=None):
        # super(Setting_helper, self).__init__()
        QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.s = session()

        self.old_path_db = config['Setting_helper']['path_db']
        self.ui.lineEdit_path.setText(self.old_path_db)

        self.ui.btn_path.clicked.connect(self.clicked_btn_path)
        self.ui.btn_save.clicked.connect(self.clicked_btn_save)
        self.ui.btn_cancel.clicked.connect(self.close_setting)

        self.print_table_branch()
        self.print_table_department()

        self.ui.btn_add_edit_branch.setText('Добавить')
        self.ui.table_branch.itemDoubleClicked.connect(self.doubleClicked_table_branch)
        self.ui.table_branch.currentCellChanged.connect(self.currentCellChanged_branch)
        self.ui.btn_add_edit_branch.clicked.connect(self.clicked_btn_add_edit_branch)

        self.ui.btn_add_edit.setText('Добавить')
        self.ui.table_department.itemDoubleClicked.connect(self.doubleClicked_table_department)
        self.ui.table_department.currentCellChanged.connect(self.currentCellChanged_table_department)
        self.ui.btn_add_edit.clicked.connect(self.clicked_btn_add_edit)

        self.ui.lineEdit_pathExport.setText(config['Helper_export']['path_export'])

    def print_table_branch(self):
        branch = self.s.query(Branch).order_by(Branch.name)

        numrows = branch.count()
        numcols = 2
        self.ui.table_branch.setColumnCount(numcols)
        self.ui.table_branch.setRowCount(numrows)

        self.ui.table_branch.setEditTriggers(QAbstractItemView.NoEditTriggers)  # запред редактирования
        self.ui.table_branch.setColumnHidden(0, True)  # Скрываем столбец id
        self.ui.table_branch.verticalHeader().setVisible(False)  # Убераем первую колонку
        self.ui.table_branch.setHorizontalHeaderItem(1, QTableWidgetItem('Список филиалов'))
        header = self.ui.table_branch.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        for index_row, i in enumerate(branch):
            self.ui.table_branch.setItem(index_row, 0, QTableWidgetItem(str(i.id)))
            self.ui.table_branch.setItem(index_row, 1, QTableWidgetItem(i.name))

    def clicked_btn_add_edit_branch(self):
        if self.ui.lineEdit_add_edit_branch.text() != '':
            if self.ui.btn_add_edit_branch.text() == 'Добавить':
                branch = Branch(name=self.ui.lineEdit_add_edit_branch.text())
            else:
                id_branch = self.ui.table_branch.item(self.ui.table_branch.currentRow(), 0).text()
                branch = self.s.query(Branch).filter_by(id=id_branch).one()
                branch.name = self.ui.lineEdit_add_edit_branch.text()
                self.ui.btn_add_edit_branch.setText('Добавить')
            self.s.add(branch)
            self.ui.lineEdit_add_edit_branch.clear()
            self.print_table_branch()

    def currentCellChanged_branch(self):
        self.ui.btn_add_edit_branch.setText('Добавить')
        self.ui.lineEdit_add_edit_branch.clear()

    def doubleClicked_table_branch(self):
        if self.ui.btn_add_edit_branch.text() == 'Добавить':
            self.ui.btn_add_edit_branch.setText('Изменить')
            self.ui.lineEdit_add_edit_branch.setText(
                self.ui.table_branch.item(self.ui.table_branch.currentRow(), 1).text())
        else:
            self.ui.btn_add_edit_branch.setText('Добавить')
            self.ui.table_branch.clearSelection()

    def print_table_department(self):
        departments = self.s.query(Department).order_by(Department.name)

        numrows = departments.count()
        numcols = 2
        self.ui.table_department.setColumnCount(numcols)
        self.ui.table_department.setRowCount(numrows)

        self.ui.table_department.setEditTriggers(QAbstractItemView.NoEditTriggers)  # запред редактирования
        self.ui.table_department.setColumnHidden(0, True)  # Скрываем столбец id
        self.ui.table_department.verticalHeader().setVisible(False)  # Убераем первую колонку
        self.ui.table_department.setHorizontalHeaderItem(1, QTableWidgetItem('Список служб'))
        header = self.ui.table_department.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        for index_row, i in enumerate(departments):
            self.ui.table_department.setItem(index_row, 0, QTableWidgetItem(str(i.id)))
            self.ui.table_department.setItem(index_row, 1, QTableWidgetItem(i.name))

    def clicked_btn_add_edit(self):
        if self.ui.lineEdit_department.text() != '':
            if self.ui.btn_add_edit.text() == 'Добавить':
                department = Department(name=self.ui.lineEdit_department.text())
            else:
                id_department = self.ui.table_department.item(self.ui.table_department.currentRow(), 0).text()
                department = self.s.query(Department).filter_by(id=id_department).one()
                department.name = self.ui.lineEdit_department.text()
                self.ui.btn_add_edit.setText('Добавить')
            self.s.add(department)
            self.ui.lineEdit_department.clear()
            self.print_table_department()

    def currentCellChanged_table_department(self):
        self.ui.btn_add_edit.setText('Добавить')
        self.ui.lineEdit_department.clear()

    def doubleClicked_table_department(self):
        if self.ui.btn_add_edit.text() == 'Добавить':
            self.ui.btn_add_edit.setText('Изменить')
            self.ui.lineEdit_department.setText(
                self.ui.table_department.item(self.ui.table_department.currentRow(), 1).text())
        else:
            self.ui.btn_add_edit.setText('Добавить')
            self.ui.table_department.clearSelection()

    def check_current_db(self):
        if self.ui.lineEdit_path.text() != self.old_path_db:
            quit()

    def clicked_btn_save(self):
        config['Setting_helper']['path_db'] = self.ui.lineEdit_path.text()
        config.write()
        self.s.commit()
        self.check_current_db()
        self.close()

    def close_setting(self):
        self.s.close()
        self.close()

    def clicked_btn_path(self):
        filepath = QtWidgets.QFileDialog.getOpenFileName(None, 'Пожалуйста выберите базу данных.')
        self.ui.lineEdit_path.setText(filepath[0])

        # self.s = session()

        # self.ui.btn_save.clicked.connect(self.clicked_btn_save)
        # self.ui.btn_cancel.clicked.connect(self.close_setting)
        # self.ui.btn_path.clicked.connect(self.clicked_btn_path)
        #
        # self.ui.lineEdit_path.setText(config['Setting_helper']['path_db'])
        #
        # self.print_table_department()
        # self.print_table_typeUsb()
        # self.print_table_branch()
        # self.print_table_typeEquipment()
        #
        # self.ui.btn_add_edit.setText('Добавить')
        # self.ui.table_department.itemDoubleClicked.connect(self.doubleClicked_table_department)
        # self.ui.table_department.currentCellChanged.connect(self.currentCellChanged_table_department)
        # self.ui.btn_add_edit.clicked.connect(self.clicked_btn_add_edit)
        #
        # self.ui.btn_add_edit_typeUsb.setText('Добавить')
        # self.ui.table_typeUsb.itemDoubleClicked.connect(self.doubleClicked_table_typeUsb)
        # self.ui.table_typeUsb.currentCellChanged.connect(self.currentCellChanged_typeUsb)
        # self.ui.btn_add_edit_typeUsb.clicked.connect(self.clicked_btn_add_edit_typeUsb)
        #
        # self.ui.btn_add_edit_branch.setText('Добавить')
        # self.ui.table_branch.itemDoubleClicked.connect(self.doubleClicked_table_branch)
        # self.ui.table_branch.currentCellChanged.connect(self.currentCellChanged_branch)
        # self.ui.btn_add_edit_branch.clicked.connect(self.clicked_btn_add_edit_branch)
        #
        # # typeEquipment
        #
        # self.ui.btn_add_edit_typeEquipment.setText('Добавить')
        # self.ui.table_typeEquipment.itemDoubleClicked.connect(self.doubleClicked_table_typeEquipment)
        # self.ui.table_typeEquipment.currentCellChanged.connect(self.currentCellChanged_table_typeEquipment)
        # self.ui.btn_add_edit_typeEquipment.clicked.connect(self.clicked_btn_add_edit_typeEquipment)

    # def print_table_typeEquipment(self):
    #     typeEquipment = self.s.query(Office_type_equipment).order_by(Office_type_equipment.name)
    #
    #     numrows = typeEquipment.count()
    #     numcols = 2
    #     self.ui.table_typeEquipment.setColumnCount(numcols)
    #     self.ui.table_typeEquipment.setRowCount(numrows)
    #
    #     self.ui.table_typeEquipment.setEditTriggers(QAbstractItemView.NoEditTriggers)  # запред редактирования
    #     self.ui.table_typeEquipment.setColumnHidden(0, True)  # Скрываем столбец id
    #     self.ui.table_typeEquipment.verticalHeader().setVisible(False)  # Убераем первую колонку
    #     self.ui.table_typeEquipment.setHorizontalHeaderItem(1, QTableWidgetItem('Тип оргтехники'))
    #     header = self.ui.table_typeEquipment.horizontalHeader()
    #     header.setSectionResizeMode(1, QHeaderView.Stretch)
    #
    #     for index_row, i in enumerate(typeEquipment):
    #         self.ui.table_typeEquipment.setItem(index_row, 0, QTableWidgetItem(str(i.id)))
    #         self.ui.table_typeEquipment.setItem(index_row, 1, QTableWidgetItem(i.name))
    # def clicked_btn_add_edit_typeEquipment(self):
    #     if self.ui.lineEdit_add_edit_typeEquipment.text() != '':
    #         if self.ui.btn_add_edit_typeEquipment.text() == 'Добавить':
    #             typeEquipment = Office_type_equipment(name=self.ui.lineEdit_add_edit_typeEquipment.text())
    #         else:
    #             id_typeEquipment = self.ui.table_typeEquipment.item(self.ui.table_typeEquipment.currentRow(), 0).text()
    #             typeEquipment = self.s.query(Office_type_equipment).filter_by(id=id_typeEquipment).one()
    #             typeEquipment.name = self.ui.lineEdit_add_edit_typeEquipment.text()
    #             self.ui.btn_add_edit_branch.setText('Добавить')
    #         self.s.add(typeEquipment)
    #         self.ui.lineEdit_add_edit_typeEquipment.clear()
    #         self.print_table_typeEquipment()
    #
    # def currentCellChanged_table_typeEquipment(self):
    #     self.ui.btn_add_edit_typeEquipment.setText('Добавить')
    #     self.ui.lineEdit_add_edit_typeEquipment.clear()
    #
    # def doubleClicked_table_typeEquipment(self):
    #     if self.ui.btn_add_edit_typeEquipment.text() == 'Добавить':
    #         self.ui.btn_add_edit_typeEquipment.setText('Изменить')
    #         self.ui.lineEdit_add_edit_typeEquipment.setText(
    #             self.ui.table_typeEquipment.item(self.ui.table_typeEquipment.currentRow(), 1).text())
    #     else:
    #         self.ui.btn_add_edit_typeEquipment.setText('Добавить')
    #         self.ui.table_typeEquipment.clearSelection()
    #
    #
    #
    #
    # def print_table_branch(self):
    #     branch = self.s.query(Branch).order_by(Branch.name)
    #
    #     numrows = branch.count()
    #     numcols = 2
    #     self.ui.table_branch.setColumnCount(numcols)
    #     self.ui.table_branch.setRowCount(numrows)
    #
    #     self.ui.table_branch.setEditTriggers(QAbstractItemView.NoEditTriggers)  # запред редактирования
    #     self.ui.table_branch.setColumnHidden(0, True)  # Скрываем столбец id
    #     self.ui.table_branch.verticalHeader().setVisible(False)  # Убераем первую колонку
    #     self.ui.table_branch.setHorizontalHeaderItem(1, QTableWidgetItem('Список филиалов'))
    #     header = self.ui.table_branch.horizontalHeader()
    #     header.setSectionResizeMode(1, QHeaderView.Stretch)
    #
    #     for index_row, i in enumerate(branch):
    #         self.ui.table_branch.setItem(index_row, 0, QTableWidgetItem(str(i.id)))
    #         self.ui.table_branch.setItem(index_row, 1, QTableWidgetItem(i.name))
    #
    # def clicked_btn_add_edit_branch(self):
    #     if self.ui.lineEdit_add_edit_branch.text() != '':
    #         if self.ui.btn_add_edit_branch.text() == 'Добавить':
    #             branch = Branch(name=self.ui.lineEdit_add_edit_branch.text())
    #         else:
    #             id_branch = self.ui.table_branch.item(self.ui.table_branch.currentRow(), 0).text()
    #             branch = self.s.query(Branch).filter_by(id=id_branch).one()
    #             branch.name = self.ui.lineEdit_add_edit_branch.text()
    #             self.ui.btn_add_edit_branch.setText('Добавить')
    #         self.s.add(branch)
    #         self.ui.lineEdit_add_edit_branch.clear()
    #         self.print_table_branch()
    #
    # def currentCellChanged_branch(self):
    #     self.ui.btn_add_edit_branch.setText('Добавить')
    #     self.ui.lineEdit_add_edit_branch.clear()
    #
    # def doubleClicked_table_branch(self):
    #     if self.ui.btn_add_edit_branch.text() == 'Добавить':
    #         self.ui.btn_add_edit_branch.setText('Изменить')
    #         self.ui.lineEdit_add_edit_branch.setText(
    #             self.ui.table_branch.item(self.ui.table_branch.currentRow(), 1).text())
    #     else:
    #         self.ui.btn_add_edit_branch.setText('Добавить')
    #         self.ui.table_branch.clearSelection()
    #
    # def print_table_typeUsb(self):
    #     typeUsb = self.s.query(Usb_type).order_by(Usb_type.name)
    #
    #     numrows = typeUsb.count()
    #     numcols = 2
    #     self.ui.table_typeUsb.setColumnCount(numcols)
    #     self.ui.table_typeUsb.setRowCount(numrows)
    #
    #     self.ui.table_typeUsb.setEditTriggers(QAbstractItemView.NoEditTriggers)  # запред редактирования
    #     self.ui.table_typeUsb.setColumnHidden(0, True)  # Скрываем столбец id
    #     self.ui.table_typeUsb.verticalHeader().setVisible(False)  # Убераем первую колонку
    #     self.ui.table_typeUsb.setHorizontalHeaderItem(1, QTableWidgetItem('Тип USB устройств'))
    #     header = self.ui.table_typeUsb.horizontalHeader()
    #     header.setSectionResizeMode(1, QHeaderView.Stretch)
    #
    #     for index_row, i in enumerate(typeUsb):
    #         self.ui.table_typeUsb.setItem(index_row, 0, QTableWidgetItem(str(i.id)))
    #         self.ui.table_typeUsb.setItem(index_row, 1, QTableWidgetItem(i.name))
    #
    # def clicked_btn_add_edit_typeUsb(self):
    #     if self.ui.lineEdit_add_edit_typeUsb.text() != '':
    #         if self.ui.btn_add_edit_typeUsb.text() == 'Добавить':
    #             typeUsb = Usb_type(name=self.ui.lineEdit_add_edit_typeUsb.text())
    #         else:
    #             id_typeUsb = self.ui.table_typeUsb.item(self.ui.table_typeUsb.currentRow(), 0).text()
    #             typeUsb = self.s.query(Usb_type).filter_by(id=id_typeUsb).one()
    #             typeUsb.name = self.ui.lineEdit_add_edit_typeUsb.text()
    #             self.ui.btn_add_edit_typeUsb.setText('Добавить')
    #         self.s.add(typeUsb)
    #         self.ui.lineEdit_add_edit_typeUsb.clear()
    #         self.print_table_typeUsb()
    #
    # def currentCellChanged_typeUsb(self):
    #     self.ui.btn_add_edit_typeUsb.setText('Добавить')
    #     self.ui.lineEdit_add_edit_typeUsb.clear()
    #
    # def doubleClicked_table_typeUsb(self):
    #     if self.ui.btn_add_edit_typeUsb.text() == 'Добавить':
    #         self.ui.btn_add_edit_typeUsb.setText('Изменить')
    #         self.ui.lineEdit_add_edit_typeUsb.setText(
    #             self.ui.table_typeUsb.item(self.ui.table_typeUsb.currentRow(), 1).text())
    #     else:
    #         self.ui.btn_add_edit_typeUsb.setText('Добавить')
    #         self.ui.table_typeUsb.clearSelection()
    #
    # def clicked_btn_add_edit(self):
    #     if self.ui.lineEdit_department.text() != '':
    #         if self.ui.btn_add_edit.text() == 'Добавить':
    #             department = Department(name=self.ui.lineEdit_department.text())
    #         else:
    #             id_department = self.ui.table_department.item(self.ui.table_department.currentRow(), 0).text()
    #             department = self.s.query(Department).filter_by(id=id_department).one()
    #             department.name = self.ui.lineEdit_department.text()
    #             self.ui.btn_add_edit.setText('Добавить')
    #         self.s.add(department)
    #         self.ui.lineEdit_department.clear()
    #         self.print_table_department()
    #
    # def currentCellChanged_table_department(self):
    #     self.ui.btn_add_edit.setText('Добавить')
    #     self.ui.lineEdit_department.clear()
    #
    # def doubleClicked_table_department(self):
    #     if self.ui.btn_add_edit.text() == 'Добавить':
    #         self.ui.btn_add_edit.setText('Изменить')
    #         self.ui.lineEdit_department.setText(
    #             self.ui.table_department.item(self.ui.table_department.currentRow(), 1).text())
    #     else:
    #         self.ui.btn_add_edit.setText('Добавить')
    #         self.ui.table_department.clearSelection()
    #
    # def print_table_department(self):
    #     departments = self.s.query(Department).order_by(Department.name)
    #
    #     numrows = departments.count()
    #     numcols = 2
    #     self.ui.table_department.setColumnCount(numcols)
    #     self.ui.table_department.setRowCount(numrows)
    #
    #     self.ui.table_department.setEditTriggers(QAbstractItemView.NoEditTriggers)  # запред редактирования
    #     self.ui.table_department.setColumnHidden(0, True)  # Скрываем столбец id
    #     self.ui.table_department.verticalHeader().setVisible(False)  # Убераем первую колонку
    #     self.ui.table_department.setHorizontalHeaderItem(1, QTableWidgetItem('Список служб'))
    #     header = self.ui.table_department.horizontalHeader()
    #     header.setSectionResizeMode(1, QHeaderView.Stretch)
    #
    #     for index_row, i in enumerate(departments):
    #         self.ui.table_department.setItem(index_row, 0, QTableWidgetItem(str(i.id)))
    #         self.ui.table_department.setItem(index_row, 1, QTableWidgetItem(i.name))
    #
    # def clicked_btn_path(self):
    #     filepath = QtWidgets.QFileDialog.getOpenFileName(None, 'Hey! Select a File')
    #     self.ui.lineEdit_path.setText(filepath[0])
    #
    # def clicked_btn_save(self):
    #     config['Setting_helper']['path_db'] = self.ui.lineEdit_path.text()
    #     config.write()
    #     self.s.commit()
    #     self.close()
    #
    # def close_setting(self):
    #     self.s.close()
    #     self.close()
