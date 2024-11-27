import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QApplication, QDialog, QMessageBox
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from Model.database import session
from Model.model import Branch, Department, User, Usb_type, Usb, Usb_data
from View.main_container.new_item import Ui_Dialog
from ViewModel.PaddingDelegate import PaddingDelegate
from ViewModel.User import user_main
from config_helper import config

class Usb_chengUser(QtWidgets.QDialog):
    def __init__(self, usb_id, user_id):
        QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.s = session()

        self.setFixedSize(450, 200)
        self.ui.label_name.setText('Пользователь:')
        self.setWindowTitle('Сменить владельца')

        self.usb_id = usb_id
        self.user_id=user_id

        self.setStyleSheet(style)

        self.create_tw_user()
        self.create_combo()

        self.ui.btn_cancel.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.clicked_btn_save)

    def clicked_btn_save(self):
        # print(self.user_id)
        new_user_id=(self.comboBox_user.currentData())
        if self.user_id!=new_user_id:

            usb = self.s.query(Usb).filter(Usb.id==self.usb_id).one()
            usb.user_id=new_user_id
            self.s.add(usb)
            self.s.commit()
            self.close()

            if self.comboBox_user.currentData()!=None:
                usb_data = Usb_data(user_id=new_user_id,
                                    usb_id=self.usb_id)
                self.s.add(usb_data)
                self.s.commit()
                self.close()
                # print_regForm()

    def create_combo(self):
        self.comboBox_branch = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(0, 1, self.comboBox_branch)

        self.comboBox_department = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(1, 1, self.comboBox_department)

        self.comboBox_user = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(2, 1, self.comboBox_user)

        self.comboBox_user.addItem('None',None)

        for i in self.s.query(User.employeeId, User.fio).order_by(User.fio):
            self.comboBox_user.addItem(i.fio, i.employeeId)

    def create_tw_user(self):

        numrows = 3
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

        self.ui.tw_item.setItem(0, 0, QTableWidgetItem('Филиал:'))
        self.ui.tw_item.setItem(1, 0, QTableWidgetItem('Служба:'))
        self.ui.tw_item.setItem(2, 0, QTableWidgetItem('Пользователь:'))


        qt_size = self.getQTableWidgetSize(self.ui.tw_item)
        self.ui.tw_item.setMaximumHeight(qt_size.height())
        self.ui.tw_item.setMinimumSize(qt_size)

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

    def getQTableWidgetSize(self, table):
        w = table.verticalHeader().width() - 15  # +4 seems to be needed
        for i in range(table.columnCount()):
            w += table.columnWidth(i)  # seems to include gridline (on my machine)
        h = table.horizontalHeader().height() -22  # +4 seems to be needed
        for i in range(table.rowCount()):
            h += table.rowHeight(i)
        return QtCore.QSize(w, h)



style = '''
 QComboBox {
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

    w = Usb_chengUser()
    w.show()
    sys.exit(app.exec_())