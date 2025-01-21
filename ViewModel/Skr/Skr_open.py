from PyQt5 import QtWidgets
from PyQt5.Qt import *

from Model.database import session
from Model.model import Skr, Office_equipment
from View.Skr.Skr_open import Ui_Form

from functools import partial



class Skr_open(QtWidgets.QDialog):
    def __init__(self, skr_id):
        QDialog.__init__(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.s = session()
        self.skr_id = skr_id

        skr = self.s.query(Skr, Office_equipment.name_equipment).join(Office_equipment).filter(Skr.id == skr_id).one()
        self.ui.lineEdit.setText(skr[1])

        self.ui.btn_save.clicked.connect(partial(self.clicked_btn_save, True))
        self.ui.btn_cancel.clicked.connect(partial(self.clicked_btn_save, False))

        self.result = False

    def clicked_btn_save(self, value=False):
        self.close()

        if value:
            self.result = True
            skr = self.s.query(Skr).filter(Skr.id == int(self.skr_id)).one()
            skr.note = self.ui.comboBox.currentText()

            self.s.add(skr)
            self.s.commit()

        return self.result
