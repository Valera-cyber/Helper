import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QPushButton, QTableWidgetSelectionRange, \
    QApplication, QTableWidget
from PyQt5 import QtWidgets
from Model.BtnMenu import BtnMenu
from Model.database import session
from View.main_container.MainForm import Ui_MainWindow
from config_helper import config


class MainForm(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainForm, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.s = session()
        self.path_helper = config['Setting_helper']['path_helper']
        self.setStyleSheet(style)

        self.create_btn_new(0)
        self.create_btn_edit(1)
        self.create_btn_sort(3)
        self.create_btn_export(4)

        self.ui.horizontalLayout_btn.addStretch()  # подпружинивает

        self.create_main_list()

        self.scrollArea = QtWidgets.QScrollArea(self.ui.splitter)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.ui.verticalLayout_info = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.ui.verticalLayout_info.setContentsMargins(0, 0, 1, 0)

        width = QtWidgets.qApp.desktop().availableGeometry(self).width()  # Устанавливаем размер долей рабочих панелей
        self.ui.splitter.setSizes([width * 1 / 3, width * 2 / 3])



    def update_tw_mainList(self, sql_data, id_selected=None):
        selected_row = True
        count_items = sql_data.count()
        self.ui.statusBar.showMessage(' Количество: ' + str(count_items))
        self.tw_mainList.setRowCount(0)
        for i in sql_data:
            rowPosition = self.tw_mainList.rowCount()
            self.tw_mainList.insertRow(rowPosition)

            self.tw_mainList.setItem(rowPosition, 0, QTableWidgetItem(str(i[0])))
            self.tw_mainList.setItem(rowPosition, 1, QTableWidgetItem(i[1]))

            if (i[0]) == id_selected:
                self.tw_mainList.selectRow(rowPosition)
                selected_row = False
            else:
                if selected_row:
                    self.tw_mainList.selectRow(0)

        if count_items <= 0:
            self.btn_edit.setEnabled(False)
        else:
            self.btn_edit.setEnabled(True)

    def get_id(self, row: int):
        if row == -1:
            return None
        else:
            return self.tw_mainList.item(row, 0).text()

    def itemSelectionChanged_tw_mainList(self):
        if self.tw_mainList.item(self.tw_mainList.currentRow(), 0) is None:
            self.update_tw_info(None)
        else:
            id_item = self.tw_mainList.item(self.tw_mainList.currentRow(), 0).text()
            self.update_tw_info(int(id_item))

    def update_tw_info(self, id_item):
        pass

    def create_main_list(self,):
        self.tw_mainList = QTableWidget()
        self.tw_mainList.setColumnCount(2)
        header = self.tw_mainList.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.tw_mainList.setColumnHidden(0, True)
        self.tw_mainList.horizontalHeader().hide()
        self.tw_mainList.verticalHeader().hide()
        self.tw_mainList.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        self.tw_mainList.setSelectionBehavior(QAbstractItemView.SelectRows)  # select all row
        self.tw_mainList.setShowGrid(False)
        self.tw_mainList.itemSelectionChanged.connect(self.itemSelectionChanged_tw_mainList)

        self.ui.verticalLayout_list.addWidget(self.tw_mainList)

    def create_btn_new(self, index: int):
        '''Создаем кноку свернуть развернуть инфо'''
        self.btn_new = BtnMenu('Добавить')
        self.btn_new.setIcon(QIcon(self.path_helper + '/Icons/add.png'))
        self.ui.horizontalLayout_btn.insertWidget(index, self.btn_new)

    def create_btn_edit(self, index: int):
        self.btn_edit = BtnMenu('Изменить')
        self.btn_edit.setIcon(QIcon(self.path_helper + '/Icons/edit.png'))
        self.ui.horizontalLayout_btn.insertWidget(index, self.btn_edit)

    def create_btn_sort(self, index: int):
        '''Создаем кноку свернуть развернуть инфо'''
        self.btn_sort = BtnMenu(' Фильтр ')
        self.btn_sort.setIcon(QIcon(self.path_helper + '/Icons/sorts.png'))
        self.ui.horizontalLayout_btn.insertWidget(index, self.btn_sort)

    def create_btn_export(self, index: int):
        '''Создаем кноку свернуть развернуть инфо'''
        self.btn_export = BtnMenu(' Экспорт ')
        self.btn_export.setIcon(QIcon(self.path_helper + '/Icons/export.png'))
        self.ui.horizontalLayout_btn.insertWidget(index, self.btn_export)


style = '''
     QScrollArea {        
        margin: 0;
        border: 0;        
        }
     QPushButton{
        text-align: left;
        border: 0;
        }
    '''

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet(style)

    w = MainForm()
    w.show()
    sys.exit(app.exec_())
