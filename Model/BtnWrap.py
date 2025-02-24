from PyQt5.QtGui import QIcon, QBrush, QFont
from PyQt5.QtWidgets import  QPushButton
from config_helper import config
from PyQt5 import  QtCore

from stylesheet import blue_color_tw_text


class BtnWrap(QPushButton):
    def __init__(self,titele:str, isChecked:bool):
        super(BtnWrap, self).__init__()
        self.path_helper = config['Setting_helper']['path_helper']
        self.setText(titele)
        self.setCheckable(True)
        self.setChecked(isChecked)

        self.clicked.connect(self.btn_clicked)

        self.setStyleSheet(style)

        if self.isChecked():
            self.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
        else:
            self.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))


    def btn_clicked(self):
        if self.isChecked():
            self.setIcon(QIcon(self.path_helper + '/Icons/unwrap.png'))
        else:
            self.setIcon(QIcon(self.path_helper + '/Icons/wrap.png'))

style = '''
     QPushButton {
        
        
        qproperty-iconSize: 30px;     
         
        text-align:left;
        
        color: #0e5d96;
        font: bold 14px;
        
        margin: 0px;       
    } 
     '''


