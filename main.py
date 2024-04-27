import os
import sys


from PyQt5 import QtWidgets

from View.Start_menu.Start_menu import Ui_MainWindow
from ViewModel.Setting_helper.Setting_helper import Setting_helper
from ViewModel.data_base import Data_base


class Start_menu(QtWidgets.QMainWindow):
    def __init__(self):
        super(Start_menu, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.btn_setting.clicked.connect(self.clicked_btn_setting)

        self.path_helper = (os.path.abspath(os.getcwd()))


        self.data_base()

    def data_base(self):
        data_base = Data_base()
        if data_base.chek_db()==False:
            self.ui.btn_skr.setEnabled(False)
            self.ui.btn_usb.setEnabled(False)
            self.ui.btn_user.setEnabled(False)
            self.ui.btn_equipment.setEnabled(False)
            self.ui.btn_szi.setEnabled(False)


    def clicked_btn_setting(self):
        self.setting_helper = Setting_helper()
        self.setting_helper.show()

app = QtWidgets.QApplication([])
main = Start_menu()
main.show()
sys.exit(app.exec_())
