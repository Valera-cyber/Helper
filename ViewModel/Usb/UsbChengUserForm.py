import sys
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QTableWidgetItem
from PyQt5 import QtWidgets
from sqlalchemy import null

from Model.WidgetSerchUser import WidgetSerchUser
from Model.database import session
from Model.model import Usb, Usb_data
from View.main_container.dialog import Ui_Dialog
from config_helper import config
from stylesheet import styleNewForm


class UsbChangUserForm(QtWidgets.QDialog):
    dataSignal = pyqtSignal(int)

    def __init__(self, id_usb):

        QDialog.__init__(self, )
        self.id_usb = int(id_usb)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.s = session()

        self.path_helper = config['Setting_helper']['path_helper']
        self.setWindowTitle('Владелец USB устройства')
        self.setWindowIcon(QIcon(self.path_helper + '/Icons/usb.png'))

        self.resize(500, 500)

        self.create_user_serch()

        self.ui.btn_cancel.clicked.connect(self.close)

        self.ui.btn_save.clicked.connect(self.clicked_btn_save)

        self.serch_user.tw_user.insertRow(0)
        self.serch_user.tw_user.setItem(0, 0, QTableWidgetItem('None'))
        self.serch_user.tw_user.setItem(0, 1, QTableWidgetItem('Свободная'))


    def add_form_usb_data(self, usb_id, user_id):
        result = QMessageBox.question(self, 'Предупреждение',
                                      "Добавить регистрационную форму в журнал учета? \n \n"
                                      "При добавлении регистрационной формы в журнал учета, "
                                      "регистрационную форму можно будет сохранить в программе. ",
                                      QMessageBox.Ok, QMessageBox.Cancel)
        if result == 1024:
            usb_data = Usb_data(user_id=user_id, usb_id=usb_id)
            self.s.add(usb_data)
            self.s.commit()

    def clicked_btn_save(self):
        if self.serch_user.tw_user.currentRow() != -1:
            user_id = self.serch_user.tw_user.item(self.serch_user.tw_user.currentRow(), 0).text()

            if user_id=='None':
                user_id=null()

            usb = self.s.query(Usb).filter(Usb.id == self.id_usb).one()
            usb.user_id = user_id

            self.s.commit()

            if self.serch_user.tw_user.item(self.serch_user.tw_user.currentRow(), 0).text()!='None':
                self.add_form_usb_data(self.id_usb, user_id)

            self.dataSignal.emit(int(usb.id))
            self.close()

    def create_user_serch(self):
        self.serch_user = WidgetSerchUser()
        self.ui.verticalLayout_2.insertWidget(0, self.serch_user)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(styleNewForm)
    w = UsbChangUserForm()
    w.show()
    sys.exit(app.exec_())
