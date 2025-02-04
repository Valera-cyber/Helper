from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtWidgets
from Model.database import session
from Model.model import SziType, Branch, Department, User, Office_equipment, Inf_System
from View.main_container.set_view import Ui_Form
from Model.newTab_sortView import NewTab_sortView
from ViewModel.Helper_all import Helper_all
from config_helper import config


class User_sortView(QtWidgets.QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.s = session()

        self.ui.label_name.setText('Сортировка и фильтр.')
        self.ui.label_nameStatus.setText('Статус пользователя:')
        self.ui.checkB_statusOn.setText('Работает')
        self.ui.checkB_statusOff.setText('Уволен')

        self.insertTab_branch(0)
        self.insertTab_department(1)
        self.insertTab_system(2)
        self.insertTab_szi(3)

        self.ui.btn_save.clicked.connect(self.clicked_btn_save)
        self.ui.btn_cancel.clicked.connect(self.clicked_btn_cancel)

        self.load_status()

        self.color_page()

        current_indexPage = config['User']['current_indexPage']
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
        self.ui.checkB_statusOn.setChecked(Helper_all.convert_bool(config['User']['checkB_statusOn']))
        self.ui.checkB_statusOff.setChecked(Helper_all.convert_bool(config['User']['checkB_statusOff']))

    def get_Checked_id_tW(self, name_tW):
        '''Получаем список отмеченных id на подаваемой таблицы'''
        list_check_id = []
        for i in range(name_tW.rowCount()):
            if name_tW.item(i, 1).checkState() == Qt.CheckState.Checked:
                id = name_tW.item(i, 0).text()
                list_check_id.append(id)
        return list_check_id

    def clicked_btn_save(self):
        config['User']['checkBox_all_Branch'] = self.tab_branch.checkBox_all.isChecked()
        config['User']['checked_item_Branch'] = self.get_Checked_id_tW(self.tab_branch.tW_item)

        config['User']['checkBox_all_Department'] = self.tab_department.checkBox_all.isChecked()
        config['User']['checked_item_Department'] = self.get_Checked_id_tW(self.tab_department.tW_item)

        config['User']['checkBox_all_System'] = self.tab_system.checkBox_all.isChecked()
        config['User']['checked_item_System'] = self.get_Checked_id_tW(self.tab_system.tW_item)

        config['User']['checkBox_all_Szi'] = self.tab_szi.checkBox_all.isChecked()
        config['User']['checked_item_Szi'] = self.get_Checked_id_tW(self.tab_szi.tW_item)

        config['User']['checkB_statusOn'] = self.ui.checkB_statusOn.isChecked()
        config['User']['checkB_statusOff'] = self.ui.checkB_statusOff.isChecked()

        config['User']['current_indexPage'] = self.ui.tabWidget.currentIndex()

        config.write()
        self.close()

    def insertTab_szi(self, index_page):
        szi = self.s.query(SziType.id, SziType.name).order_by(SziType.name).filter(
            SziType.name != '')

        helper_module = {'User': 'Szi'}
        self.tab_szi = NewTab_sortView('Все СЗИ', self.ui, helper_module, szi)
        self.ui.tabWidget.insertTab(index_page, self.tab_szi, 'СЗИ')

    def insertTab_system(self, index_page):
        systems = self.s.query(Inf_System.id, Inf_System.inf_system).order_by(Inf_System.inf_system).filter(
            Inf_System.inf_system != '')

        helper_module = {'User': 'System'}
        self.tab_system = NewTab_sortView('Все системы', self.ui, helper_module, systems)
        self.ui.tabWidget.insertTab(index_page, self.tab_system, 'Инф. система')

    def insertTab_department(self, index_page):
        department = self.s.query(Department.id, Department.name).order_by(Department.name).filter(
            Department.name != '')

        helper_module = {'User': 'Department'}
        self.tab_department = NewTab_sortView('Все службы', self.ui, helper_module, department)
        self.ui.tabWidget.insertTab(index_page, self.tab_department, 'Служба')

    def insertTab_branch(self, index_page):
        branchs = self.s.query(Branch.id, Branch.name).order_by(Branch.name).filter(Branch.name != '')

        helper_module = {'User': 'Branch'}
        self.tab_branch = NewTab_sortView('Все филиалы', self.ui, helper_module, branchs)
        self.ui.tabWidget.insertTab(index_page, self.tab_branch, 'Филиал')
