import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import  QIcon
from PyQt5.QtWidgets import  QApplication, QDialog, QMessageBox, QLabel
from PyQt5 import QtWidgets
from Model.TwInfo import TwInfo
from Model.database import session
from Model.model import Branch, Department, User
from View.main_container.dialog import Ui_Dialog
from config_helper import config
from stylesheet import styleNewForm


class UserNewForm(QtWidgets.QDialog):
    dataSignal = pyqtSignal(int)

    def __init__(self, current_employeeId=None):
        QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.s = session()
        self.setStyleSheet(styleNewForm)
        self.path_helper = config['Setting_helper']['path_helper']
        self.setWindowTitle('Редактор пользователя')
        self.setWindowIcon(QIcon(self.path_helper + '/Icons/user.png'))
        self.current_employeeId = current_employeeId

        self.setFixedSize(500, 430)
        self.setMaximumWidth(700)

        self.titele=QLabel('Данные пользователя:')
        self.ui.verticalLayout_2.insertWidget(0,self.titele)
        self.titele.setAlignment(Qt.AlignCenter)
        self.titele.setStyleSheet("font: bold 16px ")


        self.create_tw_info(1)

        self.load_combobox()

        self.ui.btn_save.clicked.connect(self.clicked_btn_save)
        self.ui.btn_cancel.clicked.connect(self.close)

        self.new_or_edit(current_employeeId)

    def new_or_edit(self, current_employeeId):
        if current_employeeId == None:
            self.checkBox_status.setChecked(True)

        else:

            user = self.s.query(User, Department.name, Branch.name). \
                join(Department).join(Branch). \
                filter(User.employeeId == current_employeeId). \
                one()

            # column0 = {0: 'Филиал:', 1: 'Служба:', 2: 'Табельный №:', 3: 'ФИО:', 4: 'Должность:',
            #            5: 'Телефон:', 6: 'Почта', 7: 'Расположение:', 8: 'Логин:', 9: 'ДК:', 10: 'АРМ:', 11: 'Статус:'}

            index_cB_departmen = self.comboBox_department.findText(user[1])
            index_cB_branch = self.comboBox_branch.findText(user[2])

            self.comboBox_branch.setCurrentIndex(index_cB_branch)
            self.comboBox_department.setCurrentIndex(index_cB_departmen)

            column = {2: str(user[0].employeeId), 3: user[0].fio, 4: user[0].post,
                      5: user[0].phone, 6: user[0].eMail, 7: user[0].address, 8: user[0].login, 9: user[0].dk,
                      10: user[0].armName}

            self.tW_info.update_tw_info(column)

            self.checkBox_status.setChecked(user[0].statusWork)
            self.tW_info.item(2, 1).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # запрет редактирования

    def clicked_btn_save(self):
        def check_employeeId(employeeId):
            if employeeId.isdigit():
                if self.s.query(User.employeeId).filter_by(
                        employeeId=int(employeeId)).first() is not None:
                    QMessageBox.information(self, 'Уведомление',
                                            "Пользователь c таким табельным номером уже существует!",
                                            QMessageBox.Ok)
                else:
                    return True
            else:
                QMessageBox.information(self, 'Уведомление',
                                        "Не корректен табельный номер!",
                                        QMessageBox.Ok)

        employeeId = '' if self.tW_info.item(2, 1) is None else self.tW_info.item(2, 1).text()
        fio = '' if self.tW_info.item(3, 1) is None else self.tW_info.item(3, 1).text()
        post = '' if self.tW_info.item(4, 1) is None else self.tW_info.item(4, 1).text()
        phone = '' if self.tW_info.item(5, 1) is None else self.tW_info.item(5, 1).text()
        eMail = '' if self.tW_info.item(6, 1) is None else self.tW_info.item(6, 1).text()
        address = '' if self.tW_info.item(7, 1) is None else self.tW_info.item(7, 1).text()
        login = '' if self.tW_info.item(8, 1) is None else self.tW_info.item(8, 1).text()
        dk = '' if self.tW_info.item(9, 1) is None else self.tW_info.item(9, 1).text()
        armName = '' if self.tW_info.item(10, 1) is None else self.tW_info.item(10, 1).text()

        if (fio != '' and employeeId != '' and
                self.comboBox_branch.currentIndex() != -1 and self.comboBox_department.currentIndex() != -1):

            if self.current_employeeId == None:
                '''New user'''
                if check_employeeId(employeeId):
                    user = User(employeeId=employeeId,
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
            else:
                '''Edit user'''
                user = self.s.query(User).filter_by(employeeId=int(employeeId)).one()

                user.fio = fio
                user.branch_id = self.comboBox_branch.currentData()
                user.departmet_id = self.comboBox_department.currentData()
                user.post = post
                user.phone = phone
                user.eMail = eMail
                user.address = address
                user.login = login
                user.dk = dk
                user.armName = armName
                user.statusWork = self.checkBox_status.isChecked()

            self.s.add(user)
            self.s.commit()
            self.dataSignal.emit(int(user.employeeId))
            self.close()

    def load_combobox(self):
        branches = self.s.query(Branch)
        for i in branches:
            self.comboBox_branch.addItem(i.name, i.id)
        self.comboBox_branch.setCurrentIndex(-1)

        departments = self.s.query(Department)
        for i in departments:
            self.comboBox_department.addItem(i.name, i.id)
        self.comboBox_department.setCurrentIndex(-1)

    def create_tw_info(self, index):

        column0 = {0: 'Филиал:', 1: 'Служба:', 2: 'Табельный №:', 3: 'ФИО:', 4: 'Должность:',
                   5: 'Телефон:', 6: 'Почта', 7: 'Расположение:', 8: 'Логин:', 9: 'ДК:', 10: 'АРМ:', 11: 'Статус:'}

        self.tW_info = TwInfo(column0, 28)
        self.ui.verticalLayout_2.insertWidget(index, self.tW_info)

        self.comboBox_branch = QtWidgets.QComboBox()
        self.tW_info.setCellWidget(0, 1, self.comboBox_branch)

        self.comboBox_department = QtWidgets.QComboBox()
        self.tW_info.setCellWidget(1, 1, self.comboBox_department)

        self.checkBox_status = QtWidgets.QCheckBox()
        self.tW_info.setCellWidget(11, 1, self.checkBox_status)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(styleNewForm)
    w = UserNewForm()
    w.show()
    sys.exit(app.exec_())
