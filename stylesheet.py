from PyQt5.QtGui import QColor

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

blue_color_tw_text=QColor("#0e5d96")
red_color_tw_text=QColor('#ff0000')