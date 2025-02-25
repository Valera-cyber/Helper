from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from sqlalchemy import or_
from sqlalchemy.sql.functions import coalesce
from Model.BtnWrap import BtnWrap
from Model.ExportExls import ExportXlsx
from Model.MainForm import MainForm
from Model.TwInfo import TwInfo
from Model.model import User, User_System, SziFileInst, SziAccounting, Department, Branch
from ViewModel.Helper_all import Helper_all
from ViewModel.User.UserNewForm import UserNewForm
from ViewModel.User.UserSortForm import UserSortForm
from config_helper import config
from stylesheet import blue_color_tw_text


class InfSysMainForm(MainForm):
    def __init__(self):
        super(InfSysMainForm, self).__init__()

        self.path_helper = config['Setting_helper']['path_helper']
        self.setWindowTitle('Информационные системы')
        self.setWindowIcon(QIcon(self.path_helper + '/Icons/user.png'))

        self.btn_new.clicked.connect(self.clicked_btn_new)
        self.btn_new.setToolTip('Добавить новую систему')

        self.btn_edit.clicked.connect(self.clicked_btn_edit)
        self.btn_edit.setToolTip('Изменить текущию систему')

        self.btn_sort.clicked.connect(self.clicked_btn_sort)
        self.btn_sort.setToolTip('Отфильтровать список по критериям')

        self.btn_export.clicked.connect(self.clicked_btn_export)
        self.btn_export.setToolTip('Экспортировать текущий список систем')








    def clicked_btn_sort(self):
        ...

    def clicked_btn_new(self):
        ...

    def clicked_btn_edit(self):
        ...

    def clicked_btn_export(self):
        ...

