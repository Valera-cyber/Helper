import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QApplication, QDialog, QMessageBox
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from Model.database import session
from Model.model import Branch, Department, User, Usb_type, Usb
from View.main_container.new_item import Ui_Dialog
from ViewModel.PaddingDelegate import PaddingDelegate
from ViewModel.User import user_main
from config_helper import config

class Usb_new(QtWidgets.QDialog):
    def __init__(self, usb_id):
        QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.s = session()

        self.usb_id = usb_id

        self.setStyleSheet(style)

        self.create_item_data()

        self.ui.btn_save.clicked.connect(self.clicked_btn_save)
        self.ui.btn_cancel.clicked.connect(self.close)

        self.setFixedSize(450, 345)

        self.get_last_id()

        if usb_id == None:
            self.ui.label_name.setText('USB устройство:')
            self.setWindowTitle('Добавить USB устройство')
            self.checkBox_status.setChecked(True)
            self.ui.tw_item.setItem(0, 1, QTableWidgetItem(str(self.get_last_id())))
        else:
            self.ui.label_name.setText('USB устройство::')
            self.setWindowTitle('Редактировать USB устройство')

            usb=self.s.query(Usb, Usb_type.name).join(Usb_type).filter(Usb.id==usb_id).one()

            index_cB_type = self.comboBox_type.findText(usb[1])

            self.ui.tw_item.setItem(0, 1, QTableWidgetItem(str(usb[0].id)))
            self.comboBox_type.setCurrentIndex(index_cB_type)
            self.ui.tw_item.setItem(2, 1, QTableWidgetItem(usb[0].name))
            self.ui.tw_item.setItem(3, 1, QTableWidgetItem(usb[0].vid))
            self.ui.tw_item.setItem(4, 1, QTableWidgetItem(usb[0].pid))
            self.ui.tw_item.setItem(5, 1, QTableWidgetItem(usb[0].sn))
            self.ui.tw_item.setItem(6, 1, QTableWidgetItem(usb[0].usbStor))
            self.checkBox_status.setChecked(usb[0].status)

            self.ui.tw_item.item(0, 1).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # запрет редактирования

    def clicked_btn_save(self):
        usb_type_id = self.comboBox_type.currentData()
        name = '' if self.ui.tw_item.item(2, 1) is None else self.ui.tw_item.item(2, 1).text()
        vid = '' if self.ui.tw_item.item(3, 1) is None else self.ui.tw_item.item(3, 1).text()
        pid = '' if self.ui.tw_item.item(4, 1) is None else self.ui.tw_item.item(4, 1).text()
        sn = '' if self.ui.tw_item.item(5, 1) is None else self.ui.tw_item.item(5, 1).text()
        usbStor = '' if self.ui.tw_item.item(6, 1) is None else self.ui.tw_item.item(6, 1).text()
        status = self.checkBox_status.isChecked()

        if self.usb_id is None:
            usb = Usb(name=name,
                      vid=vid,
                      pid=pid,
                      sn=sn,
                      usbStor=usbStor,
                      usb_type_id=usb_type_id,
                      status=status)
            self.s.add(usb)

        else:
            usb=self.s.query(Usb).filter(Usb.id==self.usb_id).one()
            usb.usb_type_id = self.comboBox_type.currentData()
            usb.name=name
            usb.vid=vid
            usb.pid=pid
            usb.sn=sn
            usb.usbStor=usbStor
            usb.status=self.checkBox_status.isChecked()

        self.s.commit()
        self.usb_id = usb.id
        self.close()

    def get_last_id(self):
        last_id=self.s.query(Usb.id).order_by(Usb.id.desc()).first()
        if last_id==None:
            return 1
        else:
            return last_id[0]+1

    def create_typeUsb(self):
        self.comboBox_type = QtWidgets.QComboBox()
        self.ui.tw_item.setCellWidget(1, 1, self.comboBox_type)

        for i in self.s.query(Usb_type):
            self.comboBox_type.addItem(i.name, i.id)

    def create_item_data(self):

        numrows = 8
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

        self.ui.tw_item.setItem(0, 0, QTableWidgetItem('Учетный №:'))
        self.ui.tw_item.setItem(1, 0, QTableWidgetItem('Тип USB:'))
        self.ui.tw_item.setItem(2, 0, QTableWidgetItem('Описание:'))
        self.ui.tw_item.setItem(3, 0, QTableWidgetItem('VID:'))
        self.ui.tw_item.setItem(4, 0, QTableWidgetItem('PID:'))
        self.ui.tw_item.setItem(5, 0, QTableWidgetItem('SN:'))
        self.ui.tw_item.setItem(6, 0, QTableWidgetItem('UsbStor:'))
        self.ui.tw_item.setItem(7, 0, QTableWidgetItem('Исправно:'))

        self.checkBox_status = QtWidgets.QCheckBox()
        self.ui.tw_item.setCellWidget(7, 1, self.checkBox_status)

        self.create_typeUsb()

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

        self.ui.tw_item.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.ui.tw_item.setFocusPolicy(Qt.NoFocus)
        self.ui.tw_item.setSelectionMode(QAbstractItemView.NoSelection)

    def changed_current_cell_user(self):

        user_id = self.get_employeeId()
        if user_id is not None:
            if self.btn_info_toggled == False:
                self.print_fill_user(user_id)
        else:
            self.ui.tW_info.setItem(0, 1, QTableWidgetItem(''))
            self.ui.tW_info.setItem(1, 1, QTableWidgetItem(''))
            self.ui.tW_info.setItem(2, 1, QTableWidgetItem(''))
            self.ui.tW_info.setItem(3, 1, QTableWidgetItem(''))
            self.ui.tW_info.setItem(4, 1, QTableWidgetItem(''))
            self.ui.tW_info.setItem(5, 1, QTableWidgetItem(''))
            self.ui.tW_info.setItem(6, 1, QTableWidgetItem(''))
            self.ui.tW_info.setItem(7, 1, QTableWidgetItem(''))
            self.ui.tW_info.setItem(8, 1, QTableWidgetItem(''))
            self.ui.tW_info.setItem(9, 1, QTableWidgetItem(''))
            self.ui.tW_info.setItem(10, 1, QTableWidgetItem(''))
            self.ui.tW_info.setItem(11, 1, QTableWidgetItem(''))

    def getQTableWidgetSize(self, table):
        w = table.verticalHeader().width() - 15  # +4 seems to be needed
        for i in range(table.columnCount()):
            w += table.columnWidth(i)  # seems to include gridline (on my machine)
        h = table.horizontalHeader().height() - 22  # +4 seems to be needed
        for i in range(table.rowCount()):
            h += table.rowHeight(i)
        return QtCore.QSize(w, h)


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

    w = Usb_new()
    w.show()
    sys.exit(app.exec_())
