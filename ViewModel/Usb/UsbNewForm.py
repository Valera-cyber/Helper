import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QLabel
from PyQt5 import QtWidgets
from Model.TwInfo import TwInfo
from Model.database import session
from Model.model import Branch, Department, User, Usb_type, Usb, ServiceDepartment
from View.main_container.dialog import Ui_Dialog
from config_helper import config
from stylesheet import styleNewForm


class UsbNewForm(QtWidgets.QDialog):
    dataSignal = pyqtSignal(int)

    def __init__(self, current_id=None):
        QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.s = session()
        self.setStyleSheet(styleNewForm)
        self.path_helper = config['Setting_helper']['path_helper']
        self.setWindowTitle('Редактор мобильных устройств')
        self.setWindowIcon(QIcon(self.path_helper + '/Icons/usb.png'))
        self.current_id = current_id

        self.setFixedSize(500, 380)
        self.setMaximumWidth(700)

        self.titele = QLabel('Мобильное USB устройство:')
        self.ui.verticalLayout_2.insertWidget(0, self.titele)
        self.titele.setAlignment(Qt.AlignCenter)
        self.titele.setStyleSheet("font: bold 16px ")

        self.create_tw_info(1)

        self.ui.btn_save.clicked.connect(self.clicked_btn_save)
        self.ui.btn_cancel.clicked.connect(self.close)

        self.new_or_edit(current_id)

    def new_or_edit(self, current_id):
        if current_id != None:
            usb = (self.s.query(Usb, Branch.name, Department.name, ServiceDepartment.name, Usb_type.name).select_from(Usb).
                   join(Branch).
                   join(Department).
                   join(ServiceDepartment).
                   join(Usb_type).
                   filter(Usb.id == current_id).one())

            index_combo_box_branch = self.comboBox_branch.findText(usb[1])
            index_combo_box_departmen = self.comboBox_department.findText(usb[2])
            index_combo_box_service_department= self.comboBox_servive_department.findText(usb[3])
            index_combo_box_usb_type= self.comboBox_type.findText(usb[4])

            self.comboBox_branch.setCurrentIndex(index_combo_box_branch)
            self.comboBox_department.setCurrentIndex(index_combo_box_departmen)
            self.comboBox_servive_department.setCurrentIndex(index_combo_box_service_department)
            self.comboBox_type.setCurrentIndex(index_combo_box_usb_type)

            column1 = {4: usb[0].name, 5: usb[0].vid, 6: usb[0].pid, 7: usb[0].sn, 8: usb[0].usbStor,}

            self.tW_info.update_tw_info(column1)

            self.checkBox_status.setChecked(usb[0].status)

    def clicked_btn_save(self):
        branch_id = self.comboBox_branch.currentData()
        department_id = self.comboBox_department.currentData()
        service_department_id = self.comboBox_servive_department.currentData()
        usb_type_id = self.comboBox_type.currentData()
        name = '' if self.tW_info.item(4, 1) is None else self.tW_info.item(4, 1).text()
        vid = '' if self.tW_info.item(5, 1) is None else self.tW_info.item(5, 1).text()
        pid = '' if self.tW_info.item(6, 1) is None else self.tW_info.item(6, 1).text()
        sn = '' if self.tW_info.item(7, 1) is None else self.tW_info.item(7, 1).text()
        usbStor = '' if self.tW_info.item(8, 1) is None else self.tW_info.item(8, 1).text()
        status = self.checkBox_status.isChecked()

        if (self.comboBox_type.currentIndex() != -1 and self.comboBox_branch != -1 and
                self.comboBox_department != -1 and self.comboBox_servive_department != -1):

            if self.current_id == None:
                '''New usb'''
                usb = Usb(branch_id=branch_id,
                          department_id=department_id,
                          serviceDepartment_id=service_department_id,
                          name=name,
                          vid=vid,
                          pid=pid,
                          sn=sn,
                          usbStor=usbStor,
                          usb_type_id=usb_type_id,
                          status=status)


            else:
                '''Edit usb'''
                usb = self.s.query(Usb).filter(Usb.id == self.current_id).one()
                usb.branch_id = branch_id
                usb.department_id = department_id
                usb.serviceDepartment_id = service_department_id
                usb.usb_type_id = usb_type_id
                usb.name = name
                usb.vid = vid
                usb.pid = pid
                usb.sn = sn
                usb.usbStor = usbStor
                usb.status = self.checkBox_status.isChecked()

            self.s.add(usb)
            self.s.commit()
            self.dataSignal.emit(int(usb.id))
            self.close()

    def create_tw_info(self, index):

        column0 = {0: 'Филиал:', 1: 'Служба:', 2: 'Принадлежность:', 3: 'Тип устройства:',
                   4: 'Описание:', 5: 'VID', 6: 'PID:', 7: 'SN:', 8: 'UsbStor:', 9: 'Статус устройства:'}

        self.tW_info = TwInfo(column0, 28)
        self.ui.verticalLayout_2.insertWidget(index, self.tW_info)

        self.comboBox_branch = QtWidgets.QComboBox()
        self.tW_info.setCellWidget(0, 1, self.comboBox_branch)
        for i in self.s.query(Branch):
            self.comboBox_branch.addItem(i.name, i.id)
        self.comboBox_branch.setCurrentIndex(-1)

        self.comboBox_department = QtWidgets.QComboBox()
        self.tW_info.setCellWidget(1, 1, self.comboBox_department)
        for i in self.s.query(Department):
            self.comboBox_department.addItem(i.name, i.id)
        self.comboBox_department.setCurrentIndex(-1)

        self.comboBox_servive_department = QtWidgets.QComboBox()
        self.tW_info.setCellWidget(2, 1, self.comboBox_servive_department)
        for i in self.s.query(ServiceDepartment):
            self.comboBox_servive_department.addItem(i.name, i.id)
        self.comboBox_servive_department.setCurrentIndex(-1)

        self.comboBox_type = QtWidgets.QComboBox()
        self.tW_info.setCellWidget(3, 1, self.comboBox_type)
        for i in self.s.query(Usb_type):
            self.comboBox_type.addItem(i.name, i.id)
        self.comboBox_type.setCurrentIndex(-1)

        self.checkBox_status = QtWidgets.QCheckBox()
        self.tW_info.setCellWidget(9, 1, self.checkBox_status)
        self.checkBox_status.setChecked(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(styleNewForm)
    w = UsbNewForm()
    w.show()
    sys.exit(app.exec_())
