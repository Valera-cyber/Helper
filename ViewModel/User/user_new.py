import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QApplication, QDialog, QMessageBox
from PyQt5 import QtWidgets
from PyQt5 import QtCore

from Model.database import session
from Model.model import Branch, Department, User
from View.main_container.new_item import Ui_Dialog
from ViewModel.PaddingDelegate import PaddingDelegate

from ViewModel.User import user_main


class User_new(QtWidgets.QDialog):
    def __init__(self, current_employeeId=None):
        QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.s = session()

        self.user_main=user_main
        self.current_employeeId = current_employeeId

        self.setStyleSheet(style)

        self.create_item_data()

        self.load_branc_department()

        self.ui.btn_cancel.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.clicked_btn_save)

        self.setFixedSize(450, 460)

        if current_employeeId == None:
            self.ui.label_name.setText('Пользователь:')
            self.setWindowTitle('Создать пользователя')
            self.checkBox_status.setChecked(True)
        else:
            self.ui.label_name.setText('Пользователь:')
            self.setWindowTitle('Редактировать пользователя')

            user = self.s.query(User, Department.name, Branch.name).join(Department).join(Branch).filter(
                User.employeeId == current_employeeId).one()

            index_cB_departmen = self.comboBox_department.findText(user[1])
            index_cB_branch = self.comboBox_branch.findText(user[2])

            self.comboBox_branch.setCurrentIndex(index_cB_branch)
            self.comboBox_department.setCurrentIndex(index_cB_departmen)
            self.ui.tw_item.setItem(2, 1, QTableWidgetItem(str(user[0].employeeId)))
            self.ui.tw_item.setItem(3, 1, QTableWidgetItem(user[0].fio))
            self.ui.tw_item.setItem(4, 1, QTableWidgetItem(user[0].post))
            self.ui.tw_item.setItem(5, 1, QTableWidgetItem(user[0].phone))
            self.ui.tw_item.setItem(6, 1, QTableWidgetItem(user[0].eMail))
            self.ui.tw_item.setItem(7, 1, QTableWidgetItem(user[0].address))
            self.ui.tw_item.setItem(8, 1, QTableWidgetItem(user[0].login))
            self.ui.tw_item.setItem(9, 1, QTableWidgetItem(user[0].dk))
            self.ui.tw_item.setItem(10, 1, QTableWidgetItem(user[0].armName))
            self.checkBox_status.setChecked(user[0].statusWork)
            self.ui.tw_item.item(2, 1).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # запрет редактирования

    def load_branc_department(self):
        branches = self.s.query(Branch)
        for i in branches:
            self.comboBox_branch.addItem(i.name, i.id)

        departments = self.s.query(Department)
        for i in departments:
            self.comboBox_department.addItem(i.name, i.id)

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
        self.ui.tw_item.setItem(1, 0, QTableWidgetItem('Служба:'))
        self.ui.tw_item.setItem(2, 0, QTableWidgetItem('Табельный №:'))
        self.ui.tw_item.setItem(3, 0, QTableWidgetItem('ФИО:'))
        self.ui.tw_item.setItem(4, 0, QTableWidgetItem('Должность:'))
        self.ui.tw_item.setItem(5, 0, QTableWidgetItem('Телефон:'))
        self.ui.tw_item.setItem(6, 0, QTableWidgetItem('Почта:'))
        self.ui.tw_item.setItem(7, 0, QTableWidgetItem('Расположение:'))
        self.ui.tw_item.setItem(8, 0, QTableWidgetItem('Логин:'))
        self.ui.tw_item.setItem(9, 0, QTableWidgetItem('ДК:'))
        self.ui.tw_item.setItem(10, 0, QTableWidgetItem('АРМ:'))
        self.ui.tw_item.setItem(11, 0, QTableWidgetItem('Работает:'))

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

        self.comboBox_branch = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(0, 1, self.comboBox_branch)

        self.comboBox_department = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(1, 1, self.comboBox_department)

        self.checkBox_status = QtWidgets.QCheckBox()
        self.ui.tw_item.setCellWidget(11, 1, self.checkBox_status)

        self.ui.tw_item.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.ui.tw_item.setFocusPolicy(Qt.NoFocus)
        self.ui.tw_item.setSelectionMode(QAbstractItemView.NoSelection)

    def getQTableWidgetSize(self, table):
        w = table.verticalHeader().width() - 15  # +4 seems to be needed
        for i in range(table.columnCount()):
            w += table.columnWidth(i)  # seems to include gridline (on my machine)
        h = table.horizontalHeader().height() - 22  # +4 seems to be needed
        for i in range(table.rowCount()):
            h += table.rowHeight(i)
        return QtCore.QSize(w, h)

    def clicked_btn_save(self):
        employeeId = '' if self.ui.tw_item.item(2, 1) is None else self.ui.tw_item.item(2, 1).text()
        fio = '' if self.ui.tw_item.item(3, 1) is None else self.ui.tw_item.item(3, 1).text()
        post = '' if self.ui.tw_item.item(4, 1) is None else self.ui.tw_item.item(4, 1).text()
        phone = '' if self.ui.tw_item.item(5, 1) is None else self.ui.tw_item.item(5, 1).text()
        eMail = '' if self.ui.tw_item.item(6, 1) is None else self.ui.tw_item.item(6, 1).text()
        address = '' if self.ui.tw_item.item(7, 1) is None else self.ui.tw_item.item(7, 1).text()
        login = '' if self.ui.tw_item.item(8, 1) is None else self.ui.tw_item.item(8, 1).text()
        dk = '' if self.ui.tw_item.item(9, 1) is None else self.ui.tw_item.item(9, 1).text()
        armName = '' if self.ui.tw_item.item(10, 1) is None else self.ui.tw_item.item(10, 1).text()

        if (fio != '' and employeeId != '' and
                self.comboBox_branch.currentIndex() != -1 and self.comboBox_department.currentIndex() != -1):

            if self.current_employeeId == None:

                try:
                    if self.s.query(User.employeeId).filter_by(
                            employeeId=int(employeeId)).first() is not None:
                        QMessageBox.information(self, 'Уведомление',
                                                "Пользователь c таким табельным номером уже существует!",
                                                QMessageBox.Ok)
                    else:
                        user_new = User(employeeId=self.ui.tw_item.item(2, 1).text(),
                                        fio=fio,
                                        branch_id=self.comboBox_branch.currentData(),
                                        departmet_id=self.comboBox_department.currentData(),
                                        post=post,
                                        phone=phone,
                                        eMail=eMail,
                                        address=address,
                                        login=login,
                                        dk=dk,
                                        armName=armName,
                                        statusWork=self.checkBox_status.isChecked())
                        self.s.add(user_new)
                        self.s.commit()
                        self.employeeId = user_new.employeeId
                        self.close()

                except Exception as e:
                    QMessageBox.warning(self, 'Ошибка', str(e), QMessageBox.Ok)
            else:
                edit_user = self.s.query(User).filter_by(employeeId=int(employeeId)).one()
                edit_user.fio = fio
                edit_user.branch_id = self.comboBox_branch.currentData()
                edit_user.departmet_id = self.comboBox_department.currentData()
                edit_user.post = post
                edit_user.phone = phone
                edit_user.eMail = eMail
                edit_user.address = address
                edit_user.login = login
                edit_user.dk = dk
                edit_user.armName = armName
                edit_user.statusWork = self.checkBox_status.isChecked()

                self.s.add(edit_user)
                self.s.commit()
                self.close()




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

    w = User_new()
    w.show()
    sys.exit(app.exec_())
