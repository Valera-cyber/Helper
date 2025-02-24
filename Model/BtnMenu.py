from PyQt5.QtWidgets import  QToolButton
from PyQt5 import  QtCore

class BtnMenu(QToolButton):
    def __init__(self,titele:str):
        super(BtnMenu, self).__init__()
        self.setText(titele)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.setCheckable(True)
        self.setChecked(False)
        self.setIconSize(QtCore.QSize(50, 50))

        self.setStyleSheet(style)


style = '''
     QToolButton {
        border: 0px solid black;
        border-radius: 4px;
        qproperty-iconSize: 40px;
        margin: -0px;

        image-position:down;
        text-align:top;
    }
     QToolButton::hover{background-color: #fafafa;}
     QToolButton::pressed {background-color : #e3e3e3;}

     QPushButton{ 
        text-align: left;
        border: 0px solid #3873d9;
    }   
     '''
