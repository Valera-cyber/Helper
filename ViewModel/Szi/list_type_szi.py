from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem

from Model.database import session
from Model.mainList import MainList
from Model.model import SziType
from Model.TwInfo import TwInfo
from View.main_container.newContainer import Ui_MainWindow
from ViewModel.Szi.new_type_szi import NewTypeSzi
from config_helper import config
from stylesheet import style


class ListTypeSzi(QtWidgets.QMainWindow):
    dataSignal = pyqtSignal(str)
    def __init__(self):
        super(ListTypeSzi, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.s = session()
        self.setStyleSheet(style)

        width = QtWidgets.qApp.desktop().availableGeometry(self).width()  # Устанавливаем размер долей рабочих панелей
        self.ui.splitter.setSizes([width * 1 / 3, width * 2 / 3])

        self.path_helper = config['Setting_helper']['path_helper']

        self.setWindowTitle("Тип СЗИ")
        self.setWindowIcon(QIcon(self.path_helper + '/Icons/szi.png'))

        self.create_menu_button()
        self.ui.btn_sort.setVisible(False)
        self.ui.btn_export.setVisible(False)

        self.new_mainList()

        self.new_tw_info()


        self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                    QtWidgets.QSizePolicy.Expanding)  # Подпружиниваем по вертикали
        self.ui.verticalLayout_info.addItem(self.verticalSpacer)

        self.ui.btn_edit.setEnabled(False)

    def update_typeSzi(self, selrctedRow_id):
        '''Сигнал clicked_button (ОК or Cancel)с окна szi_new возвращает id нового СЗИ, обновлет если не 0 список СЗИ'''
        if selrctedRow_id != 0:
            self.mainList.update_mainList(self.load_typeszi(), int(selrctedRow_id))

    def new_tw_info(self):
        column0 = {0: 'Наименование СЗИ:', 1: 'Тип СЗИ:', 2:'Комплектность:', 3: 'Сертификат ФСТЭК/ФСБ:', 4: 'Проект:'}
        self.tW_info=TwInfo(column0,40)
        self.ui.verticalLayout_info.insertWidget(0,self.tW_info)

    def item_selection_changed_mainList(self, current_id):
        if self.mainList.item(self.mainList.currentRow(), 0) is not None:
            current_id = self.mainList.item(self.mainList.currentRow(), 0).text()

            sziType=self.s.query(SziType).filter(SziType.id==current_id).one()


            column1 = {0: sziType.name, 1: sziType.type, 2 : sziType.completeness, 3: sziType.sert, 4: sziType.project}
            self.tW_info.update_tw_info(column1)

            self.ui.btn_edit.setEnabled(True)
        else:
            self.ui.btn_edit.setEnabled(False)

    def load_typeszi(self):
        szi_type=self.s.query(SziType.id, SziType.name).order_by(SziType.name)
        self.ui.statusBar.showMessage(' Количество: ' + str(szi_type.count()))
        return szi_type

    def new_mainList(self):
        self.mainList = MainList(self.load_typeszi(), False)
        self.mainList.dataSignal.connect(self.item_selection_changed_mainList)
        self.ui.verticalLayout_list.insertWidget(0, self.mainList)

    def create_menu_button(self):
        '''Создаем МенюБар и кноки в меню'''
        self.ui.action_exit.triggered.connect(self.close)
        self.ui.action_add.triggered.connect(self.clicked_btn_new)
        self.ui.action_edit.triggered.connect(self.clicked_btn_edit)
        self.ui.action_sort.triggered.connect(self.clicked_btn_sort)
        self.ui.action_export.triggered.connect(self.clicked_btn_export)

        self.ui.btn_new.clicked.connect(self.clicked_btn_new)
        self.ui.btn_edit.clicked.connect(self.clicked_btn_edit)
        self.ui.btn_sort.clicked.connect(self.clicked_btn_sort)
        self.ui.btn_export.clicked.connect(self.clicked_btn_export)

        self.ui.btn_new.setIcon(QIcon(self.path_helper + '/Icons/add.png'))
        self.ui.btn_edit.setIcon(QIcon(self.path_helper + '/Icons/edit.png'))
        self.ui.btn_export.setIcon(QIcon(self.path_helper + '/Icons/export.png'))
        self.ui.btn_sort.setIcon(QIcon(self.path_helper + '/Icons/sorts.png'))

    def clicked_btn_new(self):
        self.new_type_szi=NewTypeSzi(0)
        self.new_type_szi.dataSignal.connect(self.update_typeSzi)
        self.new_type_szi.exec_()

    def clicked_btn_edit(self):
        current_id=self.mainList.get_id()
        self.new_type_szi = NewTypeSzi(current_id)
        self.new_type_szi.dataSignal.connect(self.update_typeSzi)
        self.new_type_szi.exec_()

    def clicked_btn_sort(self):
        ...

    def clicked_btn_export(self):
        ...