import sys
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5 import QtWidgets
from Model.database import session
from Model.model import Office_equipment, SziEquipment
from View.main_container.dialog import Ui_Dialog


class Change_equipment(QtWidgets.QDialog):
    def __init__(self, equipment_id, sziAccounting_id):
        QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.s = session()

        self.equipment_id = equipment_id
        self.sziAccounting_id = sziAccounting_id

        self.setWindowTitle('Перенос СЗИ на другой объект')

        self.setStyleSheet(style)

        self.label_titel = QtWidgets.QLabel()
        self.label_titel.setText('Выбирите новый объект установки СЗИ')
        self.ui.verticalLayout.insertWidget(0, self.label_titel)

        self.combobox_equipment = QtWidgets.QComboBox()
        self.ui.verticalLayout.insertWidget(1, self.combobox_equipment)

        self.label_info = QtWidgets.QLabel()
        self.label_info.setWordWrap(True)
        self.label_info.setText(
            '(Переносить СЗИ необходимо на объекты с такими же именами как и в Актах на установку СЗИ. '
            'Перенос СЗИ не меняет указанные имена в актах на установку СЗИ. '
            'Перенос СЗИ необходим если была подмена объекта установки СЗИ)')
        self.ui.verticalLayout.insertWidget(2, self.label_info)

        self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                    QtWidgets.QSizePolicy.Expanding)  # Подпружиниваем по вертикали
        self.ui.verticalLayout.addItem(self.verticalSpacer)

        self.add_equipment_to_combobox_equipment()

        self.ui.btn_cancel.clicked.connect(self.clicked_btn_cancel)
        self.ui.btn_save.clicked.connect(self.clicked_btn_save)

    def clicked_btn_save(self):
        if self.combobox_equipment.currentIndex()!=-1:
            sziEquipment = (self.s.query(SziEquipment).
                            filter(SziEquipment.equipment_id == self.equipment_id).
                            filter(SziEquipment.sziAccounting_id == self.sziAccounting_id).
                            one())

            new_equipmen_id = self.combobox_equipment.currentData()

            sziEquipment.equipment_id = new_equipmen_id
            self.s.add(sziEquipment)
            self.s.commit()
            self.close()

    def closeEvent(self, event):
        self.s.close()

    def clicked_btn_cancel(self):
        self.s.close()
        self.close()

    def add_equipment_to_combobox_equipment(self):
        equipments = self.s.query(Office_equipment.id, Office_equipment.name_equipment).order_by(
            Office_equipment.name_equipment)
        for i in equipments:
            # print(i)
            self.combobox_equipment.addItem(i[1], i[0])

            self.combobox_equipment.setCurrentIndex(-1)


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

    w = Change_equipment()
    w.show()
    sys.exit(app.exec_())
