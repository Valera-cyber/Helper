from config_helper import config

class Data_base():
    def __init__(self):
        self.puth_db=str

    def chek_db(self):
        self.puth_db = config['Setting_helper']['path_db']
        if self.puth_db=='':
            return False









