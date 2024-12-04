import sys
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QApplication, QDialog, QMessageBox, \
    QLabel, QDateEdit
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from Model.database import session
from Model.model import Branch, Department, User, Usb_type, Usb, Office_type_equipment, Office_equipment, Skr
from View.main_container.new_item import Ui_Dialog
from ViewModel.PaddingDelegate import PaddingDelegate
from ViewModel.Skr.Skr_open import Skr_open
from ViewModel.User import user_main
from ViewModel.main_load import Main_load
from config_helper import config
from datetime import datetime


class Skr_new(QtWidgets.QDialog):
    def __init__(self, skr_id):
        QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.s = session()

        self.new_skr_id=None

        self.equipment_id = skr_id

        self.setStyleSheet(style)

        self.ui.label_name.setText('Устройство:')
        self.setWindowTitle('Опечатать устройство')

        self.setFixedSize(550, 230)

        self.create_item_data()

        self.load_comboBox_user()
        self.load_comboBox_equipment()

        self.ui.btn_cancel.clicked.connect(self.clicked_btn_cancel)
        self.ui.btn_save.clicked.connect(self.clicked_btn_save)


    def skr_open(self):
        equipment_id = self.comboBox_equipment.currentData()
        equipment = self.s.query(Skr).filter(Skr.equipment_id == equipment_id).filter(Skr.note == None)

        result = True

        for i in equipment:
            rez = QMessageBox.question(self, 'Предупреждение',
                                       'Данный объект опечатан, снять пломбу-наклейку СКР+?',
                                       QMessageBox.Ok | QMessageBox.Cancel)
            if rez == QMessageBox.Ok:
                skr_open = Skr_open(i.id)
                skr_open.exec_()
                res = skr_open.clicked_btn_save()
                if res:
                    result = True
                else:
                    result = False
                    break
            else:
                result = False
                break

        return result

    def clicked_btn_save(self):
        number_skr=self.ui.tw_item.item(2,1).text()
        if number_skr != '':
            if self.skr_open():
                convert_date = self.date_edit.date().toPyDate()
                y, m, d = str(convert_date).split('-')
                convert_date = datetime(int(y), int(m), int(d))
                new_skr = Skr(equipment_id=self.comboBox_equipment.currentData(),
                              user_id=self.comboBox_user.currentData(),
                              numberSkr=number_skr,
                              startDate=convert_date)

                self.s.add(new_skr)
                self.s.commit()
                self.close()
                self.new_skr_id = new_skr.id
            else:
                QMessageBox.warning(self, 'Предупреждение',
                                    'Пломба-наклейка СКР+ не зарегистрирована в журнале',
                                    QMessageBox.Ok)

    def clicked_btn_cancel(self):
        self.close()

    def load_comboBox_user(self):
        user = self.s.query(User.employeeId,User.fio).order_by(User.fio)
        for i in user:
            self.comboBox_user.addItem(i[1], i[0])

    def load_comboBox_equipment(self):
        equipment = self.s.query(Office_equipment.id,Office_equipment.name_equipment).order_by(Office_equipment.name_equipment)
        for i in equipment:
            self.comboBox_equipment.addItem(i[1], i[0])

    def create_item_data(self):

        numrows = 4
        numcols = 2

        self.ui.tw_item.setColumnCount(numcols)
        self.ui.tw_item.setRowCount(numrows)

        header = self.ui.tw_item.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.tw_item.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        self.ui.tw_item.horizontalHeader().setVisible(False)
        self.ui.tw_item.verticalHeader().setVisible(False)

        self.delegate = PaddingDelegate()
        self.ui.tw_item.setItemDelegate(self.delegate)

        self.ui.tw_item.setItem(0, 0, QTableWidgetItem('Ответственный:'))
        self.ui.tw_item.setItem(1, 0, QTableWidgetItem('Устройство:'))

        self.ui.tw_item.setItem(2, 0, QTableWidgetItem('Номер СКР+:'))
        self.ui.tw_item.setItem(3, 0, QTableWidgetItem('Дата пломбирования:'))

        self.checkBox_status = QtWidgets.QCheckBox()
        self.ui.tw_item.setCellWidget(10, 1, self.checkBox_status)

        self.comboBox_user = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(0, 1, self.comboBox_user)

        self.comboBox_equipment = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(1, 1, self.comboBox_equipment)

        self.date_edit=QDateEdit()
        self.ui.tw_item.setCellWidget(3, 1, self.date_edit)
        self.date_edit.setDate(QDate.currentDate())

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

    w = Skr_new()
    w.show()
    sys.exit(app.exec_())
