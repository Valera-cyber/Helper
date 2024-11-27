import os
import sys

from ViewModel.Equipment.equipment_main import Equipment_main
from ViewModel.Skr.skr_main import Skr_main
from ViewModel.Usb.usb_main import Usb_main
from ViewModel.User.user_main import User_main
from config_helper import config
from PyQt5 import QtWidgets

import create_database
from Model.database import DATABASE_NAME
from View.Start_menu.Start_menu import Ui_MainWindow
from ViewModel.Setting_helper.Setting_helper import Setting_helper


class Start_menu(QtWidgets.QMainWindow):
    def __init__(self):
        super(Start_menu, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.btn_user.clicked.connect(self.clicked_btn_user)
        self.ui.btn_usb.clicked.connect(self.clicked_btn_usb)
        self.ui.btn_setting.clicked.connect(self.clicked_btn_setting)
        self.ui.btn_equipment.clicked.connect(self.clicked_btn_equipment)
        self.ui.btn_skr.clicked.connect(self.clicked_btn_skr)

        self.path_helper = (os.path.abspath(os.getcwd()))

        self.read_config()

        self.export_folders()

        # self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
    def clicked_btn_skr(self):
        self.skr=Skr_main(self.path_helper)
        self.skr.show()

    def clicked_btn_user(self):
        self.user = User_main(self.path_helper)
        self.user.show()

    def clicked_btn_usb(self):
        self.usb = Usb_main(self.path_helper)
        self.usb.show()

    def clicked_btn_equipment(self):
        self.equipment = Equipment_main(self.path_helper)
        self.equipment.show()



    def read_config(self):
        path_db = config['Setting_helper']['path_db']
        if path_db == '':
            db_is_created = os.path.exists(DATABASE_NAME)
            if not db_is_created:
                create_database.create_db()
                config['Setting_helper']['path_db'] = self.path_helper + '/' + DATABASE_NAME
                config.write()
            else:
                print('Выберите базу данных, или удалите "helper_db" в корневом каталоге, для создания новой базы ')
                self.desable_button()
        else:
            self.enabled_button()

    def export_folders(self):
        path_export = config['Helper_export']['path_export']
        if path_export=='':
            if not os.path.isdir(self.path_helper+'/'+'Helper_export'):
                os.mkdir(self.path_helper+'/'+'Helper_export')
                config['Helper_export']['path_export']=self.path_helper+'/'+'Helper_export'
                config.write()

    def enabled_button(self):
        self.ui.btn_skr.setEnabled(True)
        self.ui.btn_usb.setEnabled(True)
        self.ui.btn_user.setEnabled(True)
        self.ui.btn_equipment.setEnabled(True)
        self.ui.btn_szi.setEnabled(True)

    def desable_button(self):
        self.ui.btn_skr.setEnabled(False)
        self.ui.btn_usb.setEnabled(False)
        self.ui.btn_user.setEnabled(False)
        self.ui.btn_equipment.setEnabled(False)
        self.ui.btn_szi.setEnabled(False)

    def clicked_btn_setting(self):
        setting_helper = Setting_helper(self)
        setting_helper.exec_()
        self.read_config()




app = QtWidgets.QApplication([])
main = Start_menu()
main.show()
sys.exit(app.exec_())
