import sys
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QBrush, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QApplication, QDialog, QDateEdit
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from Model.database import session
from Model.model import User, Office_equipment, SziType, \
    SziFileInst, SziAccounting, SziEquipment
from View.main_container.new_item import Ui_Dialog
from ViewModel.PaddingDelegate import PaddingDelegate
from ViewModel.main_load import Main_load
from datetime import datetime


class Szi_new(QtWidgets.QDialog):
    dataSignal = pyqtSignal(int)

    def __init__(self, szi_id, path_helper):
        QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.s = session()

        self.szi_id = szi_id

        self.setStyleSheet(style)

        self.create_item_data()

        self.create_tW_equipment()
        self.ui.verticalLayout.insertWidget(2, self.tW_equipment)

        self.tW_equipment.setMinimumHeight(320)
        self.setFixedSize(550, 630)

        self.load_szi()
        self.load_user()
        self.load_equipment()

        self.numberAct = self.reserve_numberAct()

        self.ui.btn_cancel.clicked.connect(self.clicked_btn_cancel)
        self.ui.btn_save.clicked.connect(self.clicked_btn_save)

        self.ui.label_name.setText('СЗИ:')
        self.setWindowTitle('Добавить СЗИ')
        self.setWindowIcon(QIcon(path_helper + '/Icons/szi.png'))

        # self.szi_new_id = None

    def closeEvent(self, event):
        self.dataSignal.emit(0)
        self.s.close()

    def clicked_btn_cancel(self):
        self.dataSignal.emit(0)
        self.s.close()
        self.close()

    def clicked_btn_save(self):

        def get_check_equipment_tW(name_tW):
            '''Получаем список id отмеченных устройств'''
            list_check_id = []
            if name_tW.rowCount() > 0:
                for i in range(name_tW.rowCount()):
                    if name_tW.item(i, 1).checkState() == Qt.CheckState.Checked:
                        id = name_tW.item(i, 0).text()
                        list_check_id.append(id)
            return list_check_id

        def new_SziAccounting():
            '''Сохроняем в SziAccounting новое СЗИ'''

            if self.ui.tw_item.item(1, 1) is not None:
                sn = self.ui.tw_item.item(1, 1).text()
            else:
                sn = 'None'

            if self.ui.tw_item.item(2, 1) is not None:
                inv = self.ui.tw_item.item(2, 1).text()
            else:
                inv = 'None'

            if self.ui.tw_item.item(3, 1) is not None:
                lic = self.ui.tw_item.item(3, 1).text()
            else:
                lic = 'None'

            if self.ui.tw_item.item(4, 1) is not None:
                rec = self.ui.tw_item.item(4, 1).text()
            else:
                rec = 'None'

            new_sziAccounting = SziAccounting(sziType_id=self.comboBox_szi.currentData(),
                                              sn=sn,
                                              inv=inv,
                                              lic=lic,
                                              rec=rec,
                                              fileInstSzi_id=int(self.numberAct),
                                              status=True)
            self.s.add(new_sziAccounting)
            self.s.flush()
            return new_sziAccounting.id

        def new_SziEquipment(sziAccounting_id, list_checked_id_eqipment):
            '''Сохроняем в SziEquipment все отмеченное оборудование'''

            for i in list_checked_id_eqipment:
                new_sziEquipment = SziEquipment(sziAccounting_id=sziAccounting_id,
                                                equipment_id=i,
                                                status=True)
                self.s.add(new_sziEquipment)

        def new_SziFileAct():
            '''Сохроняем в SziFileAct с ранее резервироанным id данные'''

            def get_equipmens_name(list_checked_id_eqipment):
                equipmens_name = []
                for i in list_checked_id_eqipment:
                    office_equipment = self.s.query(Office_equipment.name_equipment).filter(
                        Office_equipment.id == i).one()
                    equipmens_name.append(office_equipment[0])
                return (', '.join(equipmens_name))

            convert_date = self.date_edit.date().toPyDate()
            y, m, d = str(convert_date).split('-')
            convert_date = datetime(int(y), int(m), int(d))

            new_sziFileAct = self.s.query(SziFileInst).filter(SziFileInst.id == self.numberAct).one()
            new_sziFileAct.date = convert_date
            new_sziFileAct.user_id = self.comboBox_fio.currentData()
            new_sziFileAct.equipments = get_equipmens_name(list_checked_id_eqipment)

            self.s.add(new_sziFileAct)

        list_checked_id_eqipment = get_check_equipment_tW(self.tW_equipment)  # список отмеченных id устройств

        if self.comboBox_szi.currentIndex() != -1 and \
                self.comboBox_fio.currentIndex() != -1 and \
                len(list_checked_id_eqipment) > 0:
            sziAccounting_id = new_SziAccounting()

            new_SziEquipment(sziAccounting_id, list_checked_id_eqipment)

            new_SziFileAct()

            self.s.commit()
            # self.szi_new_id = self.numberAct
            self.dataSignal.emit(sziAccounting_id)
            self.close()

    def reserve_numberAct(self):
        '''Резервируем id для файла установки СЗИ'''
        new_sziFileAct = SziFileInst(fileName='')
        self.s.add(new_sziFileAct)
        self.s.flush()
        return (str(new_sziFileAct.id))

    def load_equipment(self):

        # checked_Equipment = config['Szi_setting']['checked_Equipment']
        # filter(Office_equipment.id.in_((checked_Equipment))). \

        equipments = self.s.query(Office_equipment).order_by(Office_equipment.name_equipment)

        numrows = equipments.count()
        numcols = 2  # len(reg_forms[0])

        self.tW_equipment.setColumnCount(numcols)
        self.tW_equipment.setRowCount(numrows)
        self.tW_equipment.setColumnHidden(0, True)
        self.tW_equipment.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        self.tW_equipment.verticalHeader().setVisible(False)
        self.tW_equipment.horizontalHeader().setVisible(False)
        header = self.tW_equipment.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        for index_row, i in enumerate(equipments):
            self.tW_equipment.setItem(index_row, 0, QTableWidgetItem(str(i.id)))
            chkBoxItem = QTableWidgetItem(i.name_equipment)
            chkBoxItem.setText(i.name_equipment)
            chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            chkBoxItem.setCheckState(QtCore.Qt.Unchecked)
            self.tW_equipment.setItem(index_row, 1, chkBoxItem)
            self.tW_equipment.setRowHeight(index_row, 8)

    def load_user(self):
        # checked_department = config['Szi_setting']['department']
        # checked_branch = config['Szi_setting']['brabch']

        # filter(User.branch_id.in_((checked_branch))). \
        # filter(User.departmet_id.in_((checked_department))). \

        users = self.s.query(User.employeeId, User.fio). \
            filter(User.statusWork == True). \
            order_by(User.fio)

        for i in users:
            self.comboBox_fio.addItem(i[1], i[0])

        self.comboBox_fio.setCurrentIndex(-1)

    def load_szi(self):
        szi = self.s.query(SziType).filter(SziType.name != '').order_by(SziType.name)
        for i in szi:
            self.comboBox_szi.addItem(i.name, i.id)

        self.comboBox_szi.setCurrentIndex(-1)

    def create_tW_equipment(self):
        '''Создаем табицу инфо tW_info'''
        self.tW_equipment = QtWidgets.QTableWidget()
        self.tW_equipment.setWordWrap(True)
        self.tW_equipment.setCornerButtonEnabled(True)
        self.tW_equipment.viewport().installEventFilter(self)
        self.tW_equipment.setAcceptDrops(True)
        self.tW_equipment.setShowGrid(False)
        # self.tW_equipment.itemSelectionChanged.connect(self.changed_current_cell_tW_szi)
        # self.tW_equipment.itemDoubleClicked.connect(self.mouseDoubleClickEvent_tW_act)

        numrows = 0
        numcols = 2

        self.tW_equipment.setColumnCount(numcols)
        self.tW_equipment.setRowCount(numrows)

        self.tW_equipment.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        self.tW_equipment.verticalHeader().setVisible(False)
        self.tW_equipment.setHorizontalHeaderItem(1, QTableWidgetItem('id_equipment'))
        self.tW_equipment.setHorizontalHeaderItem(2, QTableWidgetItem('equipment'))

        header = self.tW_equipment.horizontalHeader()
        header.setSectionResizeMode(0, 10)
        self.tW_equipment.setColumnHidden(0, True)

    def create_item_data(self):

        numrows = 7
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

        self.ui.tw_item.setItem(0, 0, QTableWidgetItem('СЗИ:'))
        self.ui.tw_item.setItem(1, 0, QTableWidgetItem('Серийный номер:'))
        self.ui.tw_item.setItem(2, 0, QTableWidgetItem('Инв. Номер:'))
        self.ui.tw_item.setItem(3, 0, QTableWidgetItem('Лицензия:'))
        self.ui.tw_item.setItem(4, 0, QTableWidgetItem('Реквизиты док.'))
        self.ui.tw_item.setItem(5, 0, QTableWidgetItem('Дата установки:'))
        self.ui.tw_item.setItem(6, 0, QTableWidgetItem('ФИО отв-го.:'))

        self.comboBox_szi = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(0, 1, self.comboBox_szi)

        self.date_edit = QDateEdit()
        self.ui.tw_item.setCellWidget(5, 1, self.date_edit)
        self.date_edit.setDate(QDate.currentDate())

        self.comboBox_fio = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(6, 1, self.comboBox_fio)

        height_tW = Main_load.get_height_qtable(numrows)
        self.ui.tw_item.setMaximumHeight(height_tW - 22)
        self.ui.tw_item.setMinimumHeight(height_tW - 22)

        for rowPosition in range(numrows):
            self.ui.tw_item.item(rowPosition, 0).setBackground(QBrush(Qt.lightGray))  # серый фон
            self.ui.tw_item.item(rowPosition, 0).setTextAlignment(
                Qt.AlignVCenter | Qt.AlignRight)  # Выравнивание по правому краю
            self.ui.tw_item.item(rowPosition, 0).setFlags(
                Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # запрет редактирования

        table = QTableWidgetItem()
        table.setTextAlignment(3)

        self.ui.tw_item.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.ui.tw_item.setFocusPolicy(Qt.NoFocus)
        self.ui.tw_item.setSelectionMode(QAbstractItemView.NoSelection)


style = '''
 QComboBox {
    margin: 1px 3px 1px 4px;
    padding: 5px;  

 }

 QDateEdit{
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

    w = Szi_new()
    w.show()
    sys.exit(app.exec_())
