import os.path
from configobj import ConfigObj

config_file_name = 'config'
path_helper = (os.path.abspath(os.getcwd()))
path_config_file_name = path_helper + '/' + config_file_name

config = ConfigObj(path_config_file_name, encoding='utf8')

if os.path.exists(path_config_file_name) == False:

    config['Setting_helper'] = {'path_db': ''}

    config.write()
