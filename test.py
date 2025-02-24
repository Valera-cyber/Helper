import sys
from PyQt5.Qt import *


class PaletteListModel(QAbstractListModel):
    def __init__(self, colors = [], parent = None):
        QAbstractListModel.__init__(self, parent)
        self.__colors = colors

    def rowCount(self, parent):
        return len(self.__colors)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return "Palette"
            else:
                return "Color {}".format(section)

        if role == Qt.ToolTipRole:
            if orientation == Qt.Horizontal:
                return "Horizontal Header {} Tooltip".format(section)
            else:
                return "Vertical Header {} Tooltip".format(section)

    def data(self, index, role):
        row = index.row()
        value = self.__colors[row]

        if role == Qt.EditRole:
            return self.__colors[row].name()

        # add a tooltip
        if role == Qt.ToolTipRole:
            return "Hex code: {}".format(value.name())

        if role == Qt.DecorationRole:
            pixmap = QPixmap(26,26)
            pixmap.fill(value)
            icon = QIcon(pixmap)
            return icon

        if role == Qt.DisplayRole:
            return value.name()

    def setData(self, index, value, role = Qt.EditRole):
        row = index.row()
        if role == Qt.EditRole:
            color = QColor(value)
            if color.isValid():
                self.__colors[row] = color
                self.dataChanged.emit(index, index)
                return True

        return False

    # implment flags() method
    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable


if __name__ == '__main__':
    app = QApplication(sys.argv)

    tableView = QTableView()
    red   = QColor(255,0,0)
    green = QColor(0,255,0)
    blue  = QColor(0,0,255)

    model = PaletteListModel([red, green, blue])
    tableView.setModel(model)
    tableView.show()

    sys.exit(app.exec_())