import os
import subprocess
import sys
from config_helper import config

class OpenPdfFile():
    def __init__(self, partition: str):
        '''partition - имя раздела программмы'''
        path_export = config['Helper_export']['path_export']
        self.path_export_partition = path_export + '/' + partition
        if not os.path.isdir(self.path_export_partition):
            os.mkdir(self.path_export_partition)

    def save_file(self, data_blob, file_name):
        path_save_file=self.path_export_partition+'/'+file_name

        self.write_to_file(data_blob,path_save_file)

        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, path_save_file])

    def write_to_file(sekf,data, filename):
        # Преобразование двоичных данных в нужный формат
        with open(filename, 'wb') as file:
            file.write(data)