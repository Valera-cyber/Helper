from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from Model.database import session
from Model.model import SziType, Branch, Department, Inf_System, ServiceDepartment, Usb_type, User
from View.main_container.set_view import Ui_Form
from Model.newTab_sortView import NewTab_sortView
from ViewModel.Helper_all import Helper_all
from config_helper import config
from PyQt5 import QtWidgets, QtCore

class UsbSortForm(QtWidgets.QDialog):
    dataSignal = pyqtSignal(int)

    def __init__(self):
        dataSignal = pyqtSignal(int)

        QDialog.__init__(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.s = session()

        self.path_helper = config['Setting_helper']['path_helper']
        self.setWindowIcon(QIcon(self.path_helper + '/Icons/usb.png'))

        self.ui.label_name.setText('Сортировка и фильтр.')
        self.ui.label_nameStatus.setText('Статус USB устройства:')
        self.ui.checkB_statusOn.setText('Исправно')
        self.ui.checkB_statusOff.setText('Не исправно')

        self.insertTab_branch(0)
        self.insertTab_department(1)
        self.insertTab_user(2)
        self.insertTab_service_department(3)
        self.insertTab_type(4)

        self.ui.btn_save.clicked.connect(self.clicked_btn_save)
        self.ui.btn_cancel.clicked.connect(self.clicked_btn_cancel)

        self.load_status()

        self.color_page()

        current_indexPage = config['Usb']['current_indexPage']
        self.ui.tabWidget.setCurrentIndex(int(current_indexPage))

    def color_page(self):
        count_page = self.ui.tabWidget.count()
        for i in range(count_page):
            page = self.ui.tabWidget.widget(i)  # олучить доступ к виджету (странице) для каждой вкладки по индексу
            if page.checkBox_all.isChecked():
                self.ui.tabWidget.tabBar().setTabTextColor(i, QColor("gray"))
            else:
                self.ui.tabWidget.tabBar().setTabTextColor(i, QColor("black"))

    def closeEvent(self, event):
        self.s.close()

    def clicked_btn_cancel(self):
        self.s.close()
        self.close()

    def load_status(self):
        self.ui.checkB_statusOn.setChecked(Helper_all.convert_bool(config['Usb']['checkB_statusOn']))
        self.ui.checkB_statusOff.setChecked(Helper_all.convert_bool(config['Usb']['checkB_statusOff']))

    def get_Checked_id_tW(self, name_tW):
        '''Получаем список отмеченных id на подаваемой таблицы'''
        list_check_id = []
        for i in range(name_tW.rowCount()):
            if name_tW.item(i, 1).checkState() == Qt.CheckState.Checked:
                id = name_tW.item(i, 0).text()
                list_check_id.append(id)
        return list_check_id

    def clicked_btn_save(self):
        config['Usb']['checkBox_all_Branch'] = self.tab_branch.checkBox_all.isChecked()
        config['Usb']['checked_item_Branch'] = self.get_Checked_id_tW(self.tab_branch.tW_item)

        config['Usb']['checkBox_all_Department'] = self.tab_department.checkBox_all.isChecked()
        config['Usb']['checked_item_Department'] = self.get_Checked_id_tW(self.tab_department.tW_item)

        config['Usb']['checkBox_all_ServiceDepartment'] = self.tab_service_department.checkBox_all.isChecked()
        config['Usb']['checked_item_ServiceDepartment'] = self.get_Checked_id_tW(self.tab_service_department.tW_item)

        config['Usb']['checkBox_all_UsbType'] = self.tab_usb_type.checkBox_all.isChecked()
        config['Usb']['checked_item_UsbType'] = self.get_Checked_id_tW(self.tab_usb_type.tW_item)

        config['Usb']['checkBox_all_User'] = self.tab_user.checkBox_all.isChecked()
        config['Usb']['checked_item_User'] = self.get_Checked_id_tW(self.tab_user.tW_item)

        config['Usb']['checkB_statusOn'] = self.ui.checkB_statusOn.isChecked()
        config['Usb']['checkB_statusOff'] = self.ui.checkB_statusOff.isChecked()

        config['Usb']['current_indexPage'] = self.ui.tabWidget.currentIndex()

        self.dataSignal.emit(0)
        config.write()
        self.close()

    def insertTab_branch(self, index_page):
        branchs = self.s.query(Branch.id, Branch.name).order_by(Branch.name).filter(Branch.name != '')

        helper_module = {'Usb': 'Branch'}
        self.tab_branch = NewTab_sortView('Все филиалы', self.ui, helper_module, branchs)
        self.ui.tabWidget.insertTab(index_page, self.tab_branch, 'Филиал')

    def insertTab_department(self, index_page):
        department = self.s.query(Department.id, Department.name).order_by(Department.name).filter(
            Department.name != '')

        helper_module = {'Usb': 'Department'}
        self.tab_department = NewTab_sortView('Все службы', self.ui, helper_module, department)
        self.ui.tabWidget.insertTab(index_page, self.tab_department, 'Служба')

    def insertTab_service_department(self, index_page):
        service_department = self.s.query(ServiceDepartment.id, ServiceDepartment.name).order_by(ServiceDepartment.name).filter(ServiceDepartment.name != '')

        helper_module = {'Usb': 'ServiceDepartment'}
        self.tab_service_department = NewTab_sortView('Все зоны обслуживания', self.ui, helper_module, service_department)
        self.ui.tabWidget.insertTab(index_page, self.tab_service_department, 'Зоны обслуживания')

    def insertTab_type(self, index_page):
        usb_type = self.s.query(Usb_type.id, Usb_type.name).order_by(Usb_type.name).filter(Usb_type.name != '')

        helper_module = {'Usb': 'UsbType'}
        self.tab_usb_type = NewTab_sortView('Все тип', self.ui, helper_module, usb_type)
        self.ui.tabWidget.insertTab(index_page, self.tab_usb_type, 'Тип USB')

    def insertTab_user(self, index_page):
        users = self.s.query(User.employeeId, User.fio).order_by(User.fio).filter(User.fio != '')

        helper_module = {'Usb': 'User'}
        self.tab_user = NewTab_sortView('Все пользователи', self.ui, helper_module, users)
        self.ui.tabWidget.insertTab(index_page, self.tab_user, 'Пользователь')

        self.tab_user.tW_item.insertRow(0)  ## Добавляем в начале строку с None
        self.tab_user.tW_item.setItem(0, 0, QTableWidgetItem('0'))
        chkBoxItem = QTableWidgetItem(0)
        chkBoxItem.setText('Свободные')
        chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        chkBoxItem.setCheckState(QtCore.Qt.Checked)
        self.tab_user.tW_item.setItem(0, 1, chkBoxItem)
        self.tab_user.tW_item.setRowHeight(0, 8)
