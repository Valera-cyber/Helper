# Создаём новую рабочую книгу (файл)
import os
import subprocess
import sys

from config_helper import config

import openpyxl

class ExportXlsx():
    def save_xls(self, partition:str, data_partition:list):
        path_export = config['Helper_export']['path_export']
        path_export_partition=path_export+'/'+partition
        if not os.path.isdir(path_export_partition):
            os.mkdir(path_export_partition)


        wb = openpyxl.Workbook()
        sheet = wb.sheetnames
        lis = wb.active
        for i in data_partition:
            lis.append(i)

        wb.save(filename=path_export_partition+'/'+partition+'_list.xlsx')
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, path_export_partition+'/'+partition+'_list.xlsx'])