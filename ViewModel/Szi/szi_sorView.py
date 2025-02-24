from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtWidgets
from Model.database import session
from Model.model import SziType, Branch, Department, User, Office_equipment, ServiceDepartment
from View.main_container.set_view import Ui_Form
from Model.newTab_sortView import NewTab_sortView
from ViewModel.Helper_all import Helper_all
from config_helper import config


class Szi_sortView(QtWidgets.QDialog):
    dataSignal = pyqtSignal(int)
    def __init__(self):
        QDialog.__init__(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.s = session()

        self.ui.label_name.setText('Сортировка и фильтр.')
        self.ui.label_nameStatus.setText('Статус СЗИ:')
        self.ui.checkB_statusOn.setText('Актуален')
        self.ui.checkB_statusOff.setText('Удален')

        self.insertTab_sziType(2)
        self.insertTab_branch(0)
        self.insertTab_department(1)
        self.insertTab_user(3)
        self.insertTab_equipment(4)
        self.insertTab_serviceDepartment(5)

        self.ui.btn_save.clicked.connect(self.clicked_btn_saveSzi)
        self.ui.btn_cancel.clicked.connect(self.clicked_btn_cancel)

        self.load_status()

        self.color_page()

        current_indexPage = config['Szi']['current_indexPage']
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
        self.dataSignal.emit(0)

    def load_status(self):
        self.ui.checkB_statusOn.setChecked(Helper_all.convert_bool(config['Szi']['checkB_statusOn']))
        self.ui.checkB_statusOff.setChecked(Helper_all.convert_bool(config['Szi']['checkB_statusOff']))

    def get_Checked_id_tW(self, name_tW):
        '''Получаем список отмеченных id на подаваемой таблицы'''
        list_check_id = []
        for i in range(name_tW.rowCount()):
            if name_tW.item(i, 1).checkState() == Qt.CheckState.Checked:
                id = name_tW.item(i, 0).text()
                list_check_id.append(id)
        return list_check_id

    def clicked_btn_saveSzi(self):
        config['Szi']['checkBox_all_Szi'] = self.tab_sziType.checkBox_all.isChecked()
        config['Szi']['checked_item_Szi'] = self.get_Checked_id_tW(self.tab_sziType.tW_item)

        config['Szi']['checkBox_all_Branch'] = self.tab_branch.checkBox_all.isChecked()
        config['Szi']['checked_item_Branch'] = self.get_Checked_id_tW(self.tab_branch.tW_item)

        config['Szi']['checkBox_all_Department'] = self.tab_department.checkBox_all.isChecked()
        config['Szi']['checked_item_Department'] = self.get_Checked_id_tW(self.tab_department.tW_item)

        config['Szi']['checkBox_all_User'] = self.tab_user.checkBox_all.isChecked()
        config['Szi']['checked_item_User'] = self.get_Checked_id_tW(self.tab_user.tW_item)

        config['Szi']['checkBox_all_Equipment'] = self.tab_equipment.checkBox_all.isChecked()
        config['Szi']['checked_item_Equipment'] = self.get_Checked_id_tW(self.tab_equipment.tW_item)

        config['Szi']['checkBox_all_ServiceDepartment'] = self.tab_serviceDepartment.checkBox_all.isChecked()
        config['Szi']['checked_item_ServiceDepartment'] = self.get_Checked_id_tW(self.tab_serviceDepartment.tW_item)

        config['Szi']['checkB_statusOn'] = self.ui.checkB_statusOn.isChecked()
        config['Szi']['checkB_statusOff'] = self.ui.checkB_statusOff.isChecked()

        config['Szi']['current_indexPage']= self.ui.tabWidget.currentIndex()


        config.write()
        self.close()
        self.dataSignal.emit(1)

    def insertTab_department(self,index_page):
        department = self.s.query(Department.id, Department.name).order_by(Department.name).filter(Department.name != '')

        helper_module = {'Szi': 'Department'}
        self.tab_department = NewTab_sortView('Все службы', self.ui, helper_module, department)
        self.ui.tabWidget.insertTab(index_page, self.tab_department, 'Служба')

    def insertTab_sziType(self,index_page):
        szi_types = self.s.query(SziType.id, SziType.name).order_by(SziType.name).filter(SziType.name != '')

        helper_module = {'Szi': 'Szi'}
        self.tab_sziType = NewTab_sortView('Все СЗИ', self.ui, helper_module, szi_types)
        self.ui.tabWidget.insertTab(index_page, self.tab_sziType, 'СЗИ')

    def insertTab_branch(self, index_page):
        branchs = self.s.query(Branch.id, Branch.name).order_by(Branch.name).filter(Branch.name != '')

        helper_module = {'Szi': 'Branch'}
        self.tab_branch = NewTab_sortView('Все филиалы', self.ui, helper_module, branchs)
        self.ui.tabWidget.insertTab(index_page, self.tab_branch, 'Филиал')
        
    def insertTab_user(self, index_page):
        users = self.s.query(User.employeeId, User.fio).order_by(User.fio).filter(User.fio != '')

        helper_module = {'Szi': 'User'}
        self.tab_user = NewTab_sortView('Все пользователи', self.ui, helper_module, users)
        self.ui.tabWidget.insertTab(index_page, self.tab_user, 'Пользователь')

    def insertTab_equipment(self, index_page):
        equipments = self.s.query(Office_equipment.id, Office_equipment.name_equipment).order_by(Office_equipment.name_equipment).filter(Office_equipment.name_equipment != '')

        helper_module = {'Szi': 'Equipment'}
        self.tab_equipment = NewTab_sortView('Вся оргтехника', self.ui, helper_module, equipments)
        self.ui.tabWidget.insertTab(index_page, self.tab_equipment, 'Оргтехника')

    def insertTab_serviceDepartment(self, index_page):
        serviceDepartment = self.s.query(ServiceDepartment.id, ServiceDepartment.name).order_by(ServiceDepartment.name).filter(ServiceDepartment.name != '')

        helper_module = {'Szi': 'ServiceDepartment'}
        self.tab_serviceDepartment = NewTab_sortView('Все зоны', self.ui, helper_module, serviceDepartment)
        self.ui.tabWidget.insertTab(index_page, self.tab_serviceDepartment, 'Зона обслуживания')
