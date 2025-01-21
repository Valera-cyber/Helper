import os
import pathlib
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from sqlalchemy import func
import re
from Model.database import session
from Model.model import Office_equipment, Skr, SziEquipment


class Helper_all():
    def info_equipment_act_szi(list_equipmentId: list,id_SziAccounting:int) -> str:
        '''Получаем информацию о компьютерах
        Принимает id_equipment возвращает строку
        -ANT-ATC-1, СКР+ 89*6454281 от 25.03.2016, расположен Здание канцелярии каб. № 7'''
        s = session()
        info_equipment = ''
        for i in list_equipmentId:
            temp = s.query(func.max(Office_equipment.id), Office_equipment.name_equipment,
                                Office_equipment.location, Skr.numberSkr, Skr.startDate, SziEquipment.sziAccounting_id). \
                select_from(Office_equipment). \
                join(Skr). \
                join(SziEquipment).\
                filter(SziEquipment.sziAccounting_id==id_SziAccounting).\
                filter(Office_equipment.id == i).one()

            if temp[1] == None:  # None тогда когда в журнале СКР отсутствует пломба для данного арм
                temp1 = s.query(Office_equipment.name_equipment, Office_equipment.location). \
                    filter(Office_equipment.id == i).one()
                name_equipment = temp1[0]
                location = temp1[1]
                numberSkr = ''
                dateSkr = ''
            else:
                name_equipment = temp[1]
                location = temp[2]
                numberSkr = temp[3]
                dateSkr = (temp[4].strftime('%d.%m.%Y'))

            if location == None:
                location = ''

            info_equipment += name_equipment + ', ' + 'СКР+ ' + numberSkr + ' от ' + dateSkr + ', расположен ' + location + '; ' + '\n'

        return info_equipment

    def get_date_full(date_act: str) -> str:
        '''Получаем дату dd.mmm.yyyy возвращаем в виде 01 января 2024 года'''

        dd = (date_act.split('.'))[0]
        mm = (date_act.split('.'))[1]
        yyyy = (date_act.split('.'))[2]

        if mm == '01':
            mm = ' Января '
        elif mm == '02':
            mm = ' Февраля '
        elif mm == '03':
            mm = ' Марта '
        elif mm == '04':
            mm = ' Апреля '
        elif mm == '05':
            mm = ' Мая '
        elif mm == '06':
            mm = ' Июня '
        elif mm == '07':
            mm = ' Июля '
        elif mm == '08':
            mm = ' Августа '
        elif mm == '09':
            mm = ' Сентября '
        elif mm == '10':
            mm = ' Октября '
        elif mm == '11':
            mm = ' Ноября '
        elif mm == '12':
            mm = ' Декабря '

        return dd + mm + yyyy + ' года'

    def get_path_form(form: str) -> pathlib:
        '''Принимаем название формы возвращаем путь данной формы'''
        if getattr(sys, 'frozen', False):
            path = os.path.dirname(sys.executable)
            path = path + r'\Form_print' + '\\' + form
        elif __file__:
            path = os.path.dirname(__file__)
            path = pathlib.Path(path).parents[1]
            path = str(path) + r'\Form_print' + '\\' + form
        return path

    # def print_act_uninst(id_equipment, id_SziFileUninst, id_SziAccounting):
    #     s = session()
    #
    #     info_equipment = Helper_all.info_equipment_act_szi(id_equipment, id_SziAccounting)
    #
    #     sziFileUninst = s.query(SziFileUninst).filter(SziFileUninst.id == id_SziFileUninst).one()
    #     date_unist = sziFileUninst.date.strftime('%d.%m.%Y')
    #     date_unist_full = Helper_all.get_date_full(date_unist)
    #
    #     sziAccounting = s.query(SziAccounting, SziType). \
    #         join(SziType). \
    #         filter(SziAccounting.id == id_SziAccounting).one()
    #     nameSzi = sziAccounting[1].name
    #     sn = sziAccounting[0].sn
    #
    #     dictionary = {'DateFull': date_unist_full,
    #                   'Date': date_unist,
    #                   'Number': str(id_SziFileUninst),
    #                   'Equipment': info_equipment,
    #                   'id_SziAccounting': id_SziAccounting,
    #                   'NameSzi': nameSzi,
    #                   'SN': sn}
    #
    #     name_file = 'Акт деинсталяции- ' + str(id_SziFileUninst)
    #
    #     replace_text(Helper_all.get_path_form('Uninst_SZI.docx'), dictionary, name_file)

    def convertToBinaryData(path_file:pathlib)->bin:
        '''Конвертирует файл в двоичный код'''

        with open(path_file, 'rb') as file:
            blobData = file.read()
        return blobData

    def convert_bool(setting_bool:str)->bool:
        rezult=False
        if setting_bool == 'True' or setting_bool == True:
            rezult = True
        return rezult

    def get_status(status_on:bool,status_off:bool)->str:
        '''Для определения сотояние чекбокса (работает - нет)-(работает - работает)-(нет-работатет)-(нет-нет)'''
        rezult='%'
        if status_on == False and status_off == False:
            rezult = '% % %'
        if status_on == True and status_off == False:
            rezult = 1
        if status_on == True and status_off == True:
            rezult = '%'
        if status_on == False and status_off == True:
            rezult = 0
        return rezult

    def display_fio(user_fio, display):
        '''rezult-ФИО, rezult-И.О. Ф, rezult-Ф И.О.'''
        rezult=user_fio

        if display=='Ф И.О.:':
            rezult=re.sub(r'\b(\w+)\b\s+\b(\w)\w*\b\s+\b(\w)\w*\b', r'\1 \2.\3.', user_fio)

        elif display=='И.О. Ф:':
            rezult=re.sub(r'\b(\w+)\b\s+\b(\w)\w*\b\s+\b(\w)\w*\b', r'\2.\3. \1', user_fio)

        return rezult














