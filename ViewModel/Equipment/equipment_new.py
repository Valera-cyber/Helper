import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QApplication, QDialog, QMessageBox, \
    QLabel, QDateEdit
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from Model.database import session
from Model.model import Branch, Department, User, Usb_type, Usb, Office_type_equipment, Office_equipment, \
    ServiceDepartment
from View.main_container.new_item import Ui_Dialog
from ViewModel.PaddingDelegate import PaddingDelegate
# from ViewModel.User import user_main
from ViewModel.main_load import Main_load
# from config_helper import config
from datetime import datetime


class Equipment_new(QtWidgets.QDialog):
    dataSignal = pyqtSignal(int)
    def __init__(self, equipment_id):
        QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.s = session()

        self.equipment_id = equipment_id

        self.setStyleSheet(style)

        self.create_item_data()

        self.create_label_notes()
        self.ui.verticalLayout.insertWidget(2, self.label_notes)

        self.create_tE_notes()
        self.ui.verticalLayout.insertWidget(3, self.tE_notes)

        self.load_branc_department()

        self.ui.btn_save.clicked.connect(self.clicked_btn_save)
        self.ui.btn_cancel.clicked.connect(self.close)

        self.setFixedSize(550, 630)

        if equipment_id == None:
            self.ui.label_name.setText('Оргтехника:')
            self.setWindowTitle('Добавить новое устройство')
            self.checkBox_status.setChecked(True)
            # self.ui.tw_item.setItem(0, 1, QTableWidgetItem(str(self.get_last_id())))
        else:
            self.ui.label_name.setText('Оргтехника:')
            self.setWindowTitle('Редактировать устройство')

            equipment = self.s.query(Office_equipment, Department.name, Branch.name,
                                     Office_type_equipment.name, ServiceDepartment.name).select_from(Office_equipment). \
                join(Department). \
                join(Branch). \
                join(ServiceDepartment).\
                join(Office_type_equipment). \
                filter(Office_equipment.id == equipment_id).one()

            index_cB_type = self.comboBox_type.findText(equipment[3])
            self.comboBox_type.setCurrentIndex(index_cB_type)
            self.ui.tw_item.setItem(4, 1, QTableWidgetItem(equipment[0].name_equipment))
            self.ui.tw_item.setItem(5, 1, QTableWidgetItem(equipment[0].inv_number))
            self.date_edit.setDate(equipment[0].start_date)
            index_cB_branch = self.comboBox_branch.findText(equipment[2])
            self.comboBox_branch.setCurrentIndex(index_cB_branch)
            index_cB_department = self.comboBox_department.findText(equipment[1])
            self.comboBox_department.setCurrentIndex(index_cB_department)
            self.ui.tw_item.setItem(7, 1, QTableWidgetItem(equipment[0].model_equipment))
            self.ui.tw_item.setItem(8, 1, QTableWidgetItem(equipment[0].manufacturer))
            self.ui.tw_item.setItem(9, 1, QTableWidgetItem(equipment[0].sn_equipment))
            self.tE_notes.setText(equipment[0].notes)
            self.checkBox_status.setChecked(equipment[0].is_work)
            self.ui.tw_item.setItem(10, 1, QTableWidgetItem(equipment[0].location))
            index_comboBox_serviceDepartment=self.comboBox_serviceDepartment.findText(equipment[4])
            self.comboBox_serviceDepartment.setCurrentIndex(index_comboBox_serviceDepartment)



    def load_branc_department(self):
        branches = self.s.query(Branch)
        for i in branches:
            self.comboBox_branch.addItem(i.name, i.id)
        self.comboBox_branch.setCurrentIndex(-1)

        departments = self.s.query(Department)
        for i in departments:
            self.comboBox_department.addItem(i.name, i.id)
        self.comboBox_department.setCurrentIndex(-1)

        type = self.s.query(Office_type_equipment)
        for i in type:
            self.comboBox_type.addItem(i.name, i.id)
        self.comboBox_type.setCurrentIndex(-1)

        serviceDepartment=self.s.query(ServiceDepartment).order_by(ServiceDepartment.name)
        for i in serviceDepartment:
            self.comboBox_serviceDepartment.addItem(i.name, i.id)
        self.comboBox_serviceDepartment.setCurrentIndex(-1)

    def create_label_notes(self):
        self.label_notes = QLabel()
        self.label_notes.setText('Дополнительная информация:')
        self.label_notes.setAlignment(Qt.AlignCenter)

    def create_tE_notes(self):
        self.tE_notes = QtWidgets.QTextEdit()
        # self.tE_notes.setVisible(False)

    def clicked_btn_save(self):

        if (self.comboBox_serviceDepartment.currentIndex()!=-1
                and self.comboBox_branch.currentIndex()!=-1
                and self.comboBox_department.currentIndex()!=-1
                and self.comboBox_type!=-1):

            convert_date = self.date_edit.date().toPyDate()
            y, m, d = str(convert_date).split('-')
            convert_date = datetime(int(y), int(m), int(d))

            if self.equipment_id == None:
                new_arm = Office_equipment(type_equipment_id=self.comboBox_type.currentData(),
                                           name_equipment='' if self.ui.tw_item.item(4,1) is None else self.ui.tw_item.item(4, 1).text(),
                                           inv_number='' if self.ui.tw_item.item(5,1) is None else self.ui.tw_item.item(5, 1).text(),
                                           start_date=convert_date,
                                           department_id=self.comboBox_department.currentData(),
                                           model_equipment='' if self.ui.tw_item.item(7,1) is None else self.ui.tw_item.item(7, 1).text(),
                                           manufacturer='' if self.ui.tw_item.item(8,1) is None else  self.ui.tw_item.item(8, 1).text(),
                                           sn_equipment='' if self.ui.tw_item.item(9,1) is None else self.ui.tw_item.item(9, 1).text(),
                                           notes=self.tE_notes.toPlainText(),
                                           is_work=self.checkBox_status.isChecked(),
                                           branch_id=self.comboBox_branch.currentData(),
                                           location='' if self.ui.tw_item.item(10,1) is None else self.ui.tw_item.item(10, 1).text(),
                                           serviceDepartment_id=self.comboBox_serviceDepartment.currentData())

                self.s.add(new_arm)
                self.s.commit()
                self.id_new_arm = new_arm.id

            else:
                new_arm = self.s.query(Office_equipment).filter(Office_equipment.id == self.equipment_id).one()
                new_arm.type_equipment_id = self.comboBox_type.currentData()
                new_arm.name_equipment = self.ui.tw_item.item(4, 1).text()
                new_arm.inv_number = self.ui.tw_item.item(5, 1).text()
                new_arm.start_date = convert_date
                new_arm.department_id = self.comboBox_department.currentData()
                new_arm.model_equipment = self.ui.tw_item.item(7, 1).text()
                new_arm.manufacturer = self.ui.tw_item.item(8, 1).text()
                new_arm.sn_equipment = self.ui.tw_item.item(9, 1).text()
                new_arm.notes = self.tE_notes.toPlainText()
                new_arm.is_work = self.checkBox_status.isChecked()
                new_arm.branch_id = self.comboBox_branch.currentData()
                new_arm.location = self.ui.tw_item.item(10, 1).text()
                new_arm.serviceDepartment_id=self.comboBox_serviceDepartment.currentData()

                self.s.add(new_arm)
                self.s.commit()
                self.id_new_arm = self.equipment_id

            self.dataSignal.emit(int(self.id_new_arm))
            self.close()


    def create_item_data(self):

        numrows = 12
        numcols = 2

        self.ui.tw_item.setColumnCount(numcols)
        self.ui.tw_item.setRowCount(numrows)

        header = self.ui.tw_item.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.tw_item.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # self.ui.tw_item.horizontalHeader().resizeSection(0,150)

        self.ui.tw_item.horizontalHeader().setVisible(False)
        self.ui.tw_item.verticalHeader().setVisible(False)

        self.delegate = PaddingDelegate()
        self.ui.tw_item.setItemDelegate(self.delegate)

        self.ui.tw_item.setItem(0, 0, QTableWidgetItem('Филиал:'))
        self.ui.tw_item.setItem(1, 0, QTableWidgetItem('Обслуживающия служба:'))
        self.ui.tw_item.setItem(2, 0, QTableWidgetItem('Эксплуатирующия служба:'))
        self.ui.tw_item.setItem(3, 0, QTableWidgetItem('Тип устройства:'))
        self.ui.tw_item.setItem(4, 0, QTableWidgetItem('Наименование:'))
        self.ui.tw_item.setItem(5, 0, QTableWidgetItem('Инв. номер'))
        self.ui.tw_item.setItem(6, 0, QTableWidgetItem('Дата ввода:'))
        self.ui.tw_item.setItem(7, 0, QTableWidgetItem('Модель:'))
        self.ui.tw_item.setItem(8, 0, QTableWidgetItem('Производитель:'))
        self.ui.tw_item.setItem(9, 0, QTableWidgetItem('Серийный номер:'))
        self.ui.tw_item.setItem(10, 0, QTableWidgetItem('Расположение:'))
        self.ui.tw_item.setItem(11, 0, QTableWidgetItem('Эксплуатируется:'))

        self.checkBox_status = QtWidgets.QCheckBox()
        self.ui.tw_item.setCellWidget(11, 1, self.checkBox_status)

        self.comboBox_branch = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(0, 1, self.comboBox_branch)

        self.comboBox_serviceDepartment = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(1, 1, self.comboBox_serviceDepartment)

        self.comboBox_department = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(2, 1, self.comboBox_department)

        self.comboBox_type = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(3, 1, self.comboBox_type)

        self.date_edit = QDateEdit()
        self.ui.tw_item.setCellWidget(6, 1, self.date_edit)

        height_tW = Main_load.get_height_qtable(numrows)
        self.ui.tw_item.setMaximumHeight(height_tW - 22)
        self.ui.tw_item.setMinimumHeight(height_tW - 22)

        for rowPosition in range(numrows):
            self.ui.tw_item.item(rowPosition, 0).setBackground(QBrush(Qt.lightGray))  # серый фон
            self.ui.tw_item.item(rowPosition, 0).setTextAlignment(
                Qt.AlignVCenter | Qt.AlignRight)  # Выравнивание по правому краю
            self.ui.tw_item.item(rowPosition, 0).setFlags(
                Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # запрет редактирования

        table = QTableWidgetItem()
        table.setTextAlignment(3)

        self.ui.tw_item.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.ui.tw_item.setFocusPolicy(Qt.NoFocus)
        self.ui.tw_item.setSelectionMode(QAbstractItemView.NoSelection)


style = '''
 QComboBox {
    margin: 1px 3px 1px 4px;
    padding: 5px;  

 }
 
 QDateEdit{
    margin: 1px 3px 1px 4px;
    padding: 5px;  

 }
 
 QLabel {
    margin: 5px 0px 5px 0px;
 }
 
 QCheckBox{
    margin: 5px;
 }

QTableWidget.Item
 {
    padding: 5px; 
    margin: 5px 0px 5px 0px;
 } 
 '''

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet(style)

    w = Equipment_new()
    w.show()
    sys.exit(app.exec_())
