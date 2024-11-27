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
from Model.model import Office_equipment, Branch, Department, Office_type_equipment, SziAccounting, SziType, \
    SziFileInst, SziFileUninst, SziEquipment
from View.main_container.container import Ui_MainWindow
from ViewModel.Docx_replace import replace_text
from ViewModel.Equipment.equipment_new import Equipment_new
from ViewModel.Helper_all import Helper_all
from ViewModel.main_load import Main_load
from ViewModel.setting_view import Setting_view
from config_helper import config
from stylesheet import style, blue_color_tw_text


class Skr_main(QtWidgets.QMainWindow):
    def __init__(self, path_helper):
        super(Skr_main, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.s = session()

        self.path_helper = path_helper
        self.setStyleSheet(style)

        # self.ui.lineEdit_searchUser.textChanged.connect(partial(self.searchEquipment))

        width = QtWidgets.qApp.desktop().availableGeometry(self).width()  # Устанавливаем размер долей рабочих панелей
        self.ui.splitter.setSizes([width * 1 / 3, width * 2 / 3])

        self.setWindowTitle("СКР +")
        self.setWindowIcon(QIcon(self.path_helper + '/Icons/skr.png'))




if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(style)
    w = Skr_main()
    w.show()
    sys.exit(app.exec_())
