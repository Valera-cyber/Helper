import sys

from PyQt5 import QtWidgets


class Start_menu(QtWidgets.QMainWindow):
    ...

app = QtWidgets.QApplication([])
main=Start_menu()
main.show()
sys.exit(app.exec_())