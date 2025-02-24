from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from PyQt5 import QtWidgets
from Model.database import session
from Model.model import SziType
from Model.TwInfo import TwInfo
from View.main_container.qdialog import Ui_Dialog



class NewTypeSzi(QtWidgets.QDialog):
    dataSignal = pyqtSignal(int)
    def __init__(self, current_id):
        QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.s = session()

        self.setFixedSize(550, 330)

        self.current_id = current_id

        self.ui.label_name.setText('Новый тип СЗИ:')

        column0 = {0: 'Наименование СЗИ:', 1: 'Тип СЗИ:', 2:'Комплектность:', 3: 'Сертификат ФСТЭК/ФСБ:', 4: 'Проект:'}
        self.tW_info=TwInfo(column0,40)
        self.ui.verticalLayout_2.insertWidget(0,self.tW_info)

        self.sory=QtWidgets.QLabel()
        self.sory.setText('Для корректного отображения информации, данные в ячейки рекомендуется вставлять через буфер обмена.')
        self.sory.setWordWrap(True)
        self.ui.verticalLayout_2.insertWidget(2, self.sory)

        self.ui.btn_cancel.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.clicked_btn_save)

        if current_id!=0:
            self.load_current_type_szi(current_id)

    def load_current_type_szi(self,current_id):

        current_type_szi=self.s.query(SziType).filter(SziType.id==current_id).one()

        name=current_type_szi.name
        type=current_type_szi.type
        completeness=current_type_szi.completeness
        sert=current_type_szi.sert
        project=current_type_szi.project

        self.tW_info.setItem(0, 1, QTableWidgetItem(name))
        self.tW_info.setItem(1, 1, QTableWidgetItem(type))
        self.tW_info.setItem(2, 1, QTableWidgetItem(completeness))
        self.tW_info.setItem(3, 1, QTableWidgetItem(sert))
        self.tW_info.setItem(4, 1, QTableWidgetItem(project))


    def clicked_btn_save(self):

        if self.tW_info.item(0, 1) is not None:
            name = self.tW_info.item(0, 1).text()
        else:
            name = 'None'

        if self.tW_info.item(1, 1) is not None:
            type = self.tW_info.item(1, 1).text()
        else:
            type = 'None'

        if self.tW_info.item(2, 1) is not None:
            completeness = self.tW_info.item(2, 1).text()
        else:
            completeness = 'None'

        if self.tW_info.item(3, 1) is not None:
            sert = self.tW_info.item(3, 1).text()
        else:
            sert = 'None'

        if self.tW_info.item(4, 1) is not None:
            project = self.tW_info.item(4, 1).text()
        else:
            project = 'None'

        if self.current_id == 0:
            sziType = SziType(name=name, type=type, completeness=completeness, sert=sert, project=project)

            self.s.add(sziType)
            self.s.commit()
            self.dataSignal.emit(sziType.id)
            self.close()

        else:
            sziType= self.s.query(SziType).filter(SziType.id==self.current_id).one()

            sziType.name= name
            sziType.type= type
            sziType.completeness= completeness
            sziType.sert= sert
            sziType.project= project

            self.s.add(sziType)
            self.s.commit()
            self.dataSignal.emit(int(self.current_id))
            self.close()




