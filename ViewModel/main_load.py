import os
import pathlib
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView
from config_helper import config

class Main_load():
    def check_download_file(path_file):

        if len(path_file) == 1:
            if pathlib.Path(path_file[0]).suffix == '.pdf':
                return True
        return False

    def get_helperExport(folder_name):
        '''Возвращает путь к экспортируемой папки, принимает название папки'''
        path_export = config['Helper_export']['path_export']
        path_folder_name = path_export + '/'+folder_name
        if not os.path.isdir(path_folder_name):
            os.mkdir(path_folder_name)
        return path_folder_name

    def select_row_intable(ui, id=None):
        '''Функция выделяющая строку в таблице, ели employeeId=None первую строку,
        если есть выделяет указанную'''
        if id == None or id =='None' :
            if ui.tW_list.rowCount() > 0:
                ui.tW_list.selectRow(0)
            else:
                # ui.scrollArea.setVisible(False)
                ...
        else:
            for i in range(ui.tW_list.rowCount()):
                if int(ui.tW_list.item(i, 0).text()) == int(id):
                    ui.tW_list.selectRow(i)

    def get_height_qtable(row_count):
        '''Задаем высоту таблицы от колличества строк+высота заголовка'''
        height_row = 30
        height_heder = 24
        return ((row_count * height_row) + height_heder)

    def create_tW_list(ui):
        numrows = 0
        numcols = 2

        ui.tW_list.setColumnCount(numcols)
        ui.tW_list.setRowCount(numrows)

        ui.tW_list.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
        ui.tW_list.verticalHeader().setVisible(False)

        ui.tW_list.setHorizontalHeaderItem(0, QTableWidgetItem('employeeId'))
        ui.tW_list.setHorizontalHeaderItem(1, QTableWidgetItem('Пользователи'))
        ui.tW_list.setColumnHidden(0, True)
        ui.tW_list.horizontalHeader().hide()



        header = ui.tW_list.horizontalHeader()
        # header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

    def print_list(ui, sql):
        '''Заполняем таблицу из SQL запроса'''
        ui.statusBar.showMessage(' Количество: ' + str(sql.count()))

        ui.tW_list.setRowCount(0)

        for i in sql:
            rowPosition = ui.tW_list.rowCount()
            ui.tW_list.insertRow(rowPosition)

            ui.tW_list.setItem(rowPosition, 0, QTableWidgetItem(str(i[0])))
            ui.tW_list.setItem(rowPosition, 1, QTableWidgetItem(i[1]))

    def get_id(ui):
        '''Получаем id выделенной ячейки'''
        if ui.tW_list.item(ui.tW_list.currentRow(), 0) is None:
            return None
        else:
            return ui.tW_list.item(ui.tW_list.currentRow(), 0).text()

    def new_item(s):
        print(s)

    def load_item(self):
        ...
