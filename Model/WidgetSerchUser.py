from PyQt5 import QtWidgets
from sqlalchemy import or_
from Model.database import session
from Model.model import User
from PyQt5.Qt import *

class WidgetSerchUser(QtWidgets.QWidget):
    def __init__(self):
        super(WidgetSerchUser, self).__init__()
        self.s = session()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.create_tW_user()
        self.layout.insertWidget(1,self.tw_user)

        self.create_serch_line_edit()
        self.layout.insertWidget(0,self.serch_line_edit)
        self.load_user()

    def create_tW_user(self):
        self.tw_user = QTableWidget()
        self.tw_user.setColumnCount(2)
        header = self.tw_user.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.tw_user.setColumnHidden(0, True)
        self.tw_user.horizontalHeader().hide()
        self.tw_user.verticalHeader().hide()
        self.tw_user.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        self.tw_user.setSelectionBehavior(QAbstractItemView.SelectRows)  # select all row
        self.tw_user.setShowGrid(False)

    def create_serch_line_edit(self):
        self.serch_line_edit=QLineEdit()
        self.serch_line_edit.textChanged.connect(self.load_user)
        self.serch_line_edit.setClearButtonEnabled(True)
        self.serch_line_edit.setPlaceholderText('Поиск пользователя')

    def load_user(self):
        serch_text = '%' + self.serch_line_edit.text() + '%'
        if serch_text == '':
            serch_text = '%'

        user=(self.s.query(User.employeeId, User.fio).
              filter(User.statusWork==True).
              filter(or_(User.fio.like(serch_text))).
              order_by(User.fio))

        self.tw_user.setRowCount(0)

        for i in user:
            rowPosition = self.tw_user.rowCount()
            self.tw_user.insertRow(rowPosition)

            self.tw_user.setItem(rowPosition, 0, QTableWidgetItem(str(i[0])))
            self.tw_user.setItem(rowPosition, 1, QTableWidgetItem(i[1]))


