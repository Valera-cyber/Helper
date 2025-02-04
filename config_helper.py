import os.path
from configobj import ConfigObj

config_file_name = 'helper_config'
path_helper = (os.path.abspath(os.getcwd()))
path_config_file_name = path_helper + '/' + config_file_name

config = ConfigObj(path_config_file_name, encoding='utf8')

if os.path.exists(path_config_file_name) == False:

    config['Setting_helper'] = {'path_db': ''}

    config['Helper_export'] = {'path_export': path_helper+'/Export_files'}

    config['User'] = {
        'checkBox_all_Branch': 'False',
        'checkBox_all_Department': 'False',
        'checkBox_all_System':'False',
        'checkBox_all_Szi':'False',

        'checked_item_Branch': '',
        'checked_item_Department':'',
        'checked_item_System':'',
        'checked_item_Szi':'',

        'checkB_statusOn':'True',
        'checkB_statusOff':'True',

        'current_indexPage':'0',

        'defolt_branch':'',
        'defolt_department':''
        }

    config['Usb'] = {
        'checkBox_all_Branch':'False',
        'checkBox_all_Department':'False',

        'checked_item_Branch': '',
        'checked_item_Department':'',

        'checkB_statusOn':'True',
        'checkB_statusOff':'True',

        'current_indexPage':'0',

        'defolt_branch':'',
        'defolt_department':''
        }

    config['Equipment'] = {
        'checkBox_all_Branch':'False',
        'checkBox_all_Department':'False',
        'checkBox_all_ServiceDepartment': 'False',

        'checked_item_Branch': '',
        'checked_item_Department':'',
        'checked_item_ServiceDepartment': '',

        'checkB_statusOn':'True',
        'checkB_statusOff':'True',

        'current_indexPage':'0',

        'defolt_branch':'',
        'defolt_department':''
        }

    config['Skr'] = {
        'checkBox_all_Branch':'False',
        'checkBox_all_Department':'False',
        'checkBox_all_ServiceDepartment': 'False',

        'checked_item_Branch': '',
        'checked_item_Department':'',
        'checked_item_ServiceDepartment': '',

        'checkB_statusOn':'True',
        'checkB_statusOff':'True',

        'current_indexPage':'0',

        'defolt_branch':'',
        'defolt_department':''
        }

    config['Szi'] = {
        'checkBox_all_Branch': 'False',
        'checkBox_all_Department': 'False',
        'checkBox_all_Szi':'False',
        'checkBox_all_User': 'False',
        'checkBox_all_Equipment': 'False',
        'checkBox_all_ServiceDepartment': 'False',

        'checked_item_Branch': '',
        'checked_item_Department': '',
        'checked_item_Szi':'',
        'checked_item_User': '',
        'checked_item_Equipment': '',
        'checked_item_ServiceDepartment': '',

        'checkB_statusOn': 'True',
        'checkB_statusOff': 'True',

        'current_indexPage': '0',

        'defolt_branch': '',
        'defolt_department': ''
    }

    config.write()
