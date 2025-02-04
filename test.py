# import os
# import pathlib
# import sys
# import re
# from datetime import datetime
#
# import openpyxl
# from PyQt5.QtCore import QEvent
# from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QMessageBox
# from sqlalchemy.sql.expression import func
# from View.Szi.Szi_main import Ui_MainWindow
# from ViewModel.All.Helper_all import Helper_all
# from ViewModel.All.Docx_replace import replace_text
# from ViewModel.All.Setting import config
# from ViewModel.Szi.Szi_new import Szi_new
# from ViewModel.Szi.Szi_setting import Szi_setting
# from ViewModel.Szi.Szi_type import Szi_type
# from PyQt5 import QtWidgets
# from models.database import session
# from models.model import SziType, Office_equipment, User, \
#     Skr, SziAccounting, SziEquipment, SziFileInst, SziFileUninst, Branch, Department
# from PyQt5.QtGui import QBrush
# from PyQt5.QtCore import QEvent, Qt
# from sqlalchemy import func
#
#
# class Szi_main(QtWidgets.QMainWindow):
#     def __init__(self, parament=None):
#         super(Szi_main, self).__init__()
#         self.ui = Ui_MainWindow()
#         self.ui.setupUi(self)
#         self.s = session()
#
#         self.ui.btn_setting.clicked.connect(self.clicked_btn_setting)
#         self.ui.btn_sziType.clicked.connect(self.clicked_btn_sziType)
#         self.ui.btn_new.clicked.connect(self.clicked_btn_new)
#         self.ui.btn_ins.clicked.connect(self.clicked_btn_ins)
#         self.ui.btn_uninst.clicked.connect(self.clicked_btn_uninst)
#         self.ui.btn_exportExls.clicked.connect(self.clicked_btn_exportExls)
#
#         self.ui.table_main.itemSelectionChanged.connect(self.itemSelectionChanged_table_main)
#
#         self.print_table_szi()
#
#         self.ui.tW_act.itemDoubleClicked.connect(self.mouseDoubleClickEvent_tW_act)
#         self.ui.tW_act.viewport().installEventFilter(self)
#         self.ui.tW_act.setAcceptDrops(True)
#
#         self.create_tW_act()
#
#     def clicked_btn_exportExls(self):
#         '''Экспорт в эксель'''
#         def get_number_act_inst(id_SziFileInst):
#             sziFileInst = self.s.query(SziFileInst.id, SziFileInst.date).filter(SziFileInst.id == id_SziFileInst)
#             number_act = str(sziFileInst[0][0])
#             date_act = str(sziFileInst[0][1].strftime('%d.%m.%Y'))
#
#             return 'Акт № ' + number_act + ' от ' + date_act
#
#         def get_number_act_uninst(id_SziFileUninst):
#             sziFileUninst = self.s.query(SziFileUninst.id, SziFileUninst.date).filter(
#                 SziFileUninst.id == id_SziFileUninst)
#             number_act = str(sziFileUninst[0][0])
#             date_act = str(sziFileUninst[0][1].strftime('%d.%m.%Y'))
#
#             return ('Акт № ' + number_act + ' от ' + date_act)
#
#         def get_fio(id_SziFileInst):
#             sziFileInst=self.s.query(User.fio,User.post).\
#                 select_from(SziFileInst).\
#                 join(User).\
#                 filter(SziFileInst.id==id_SziFileInst).one()
#
#             return sziFileInst
#
#         count_row = self.ui.table_main.rowCount()
#         list_Id = []
#         for i in range(count_row):
#             list_Id.append(self.ui.table_main.item(i, 0).text())
#         list_export = []
#         for i in list_Id:
#             row = []
#             sziAccounting = self.s.query(SziAccounting.id, SziType.name, SziAccounting.sn, SziAccounting.inv,
#                                          SziAccounting.lic, SziType.type, SziType.completeness, SziType.sert,
#                                          SziAccounting.rec, SziType.completeness, SziAccounting.fileInstSzi_id,
#                                          SziAccounting.fileUninstSzi_id). \
#                 select_from(SziAccounting). \
#                 join(SziType, isouter=True). \
#                 filter(SziAccounting.id == i).one()
#
#             equipments = self.get_Eqipment_currentSzi(i)
#
#             date_inst = (get_number_act_inst(sziAccounting[10]))
#
#             fio=', '.join(get_fio(sziAccounting[10]))
#
#             if sziAccounting[11] is not None:
#                 date_uninst = (get_number_act_uninst(sziAccounting[11]))
#             else:
#                 date_uninst = ''
#
#             row.append(sziAccounting[0])
#             row.append(sziAccounting[1])
#             row.append(sziAccounting[2])
#             row.append(sziAccounting[3])
#             row.append(sziAccounting[4])
#             row.append(sziAccounting[5])
#             row.append(sziAccounting[6])
#             row.append(sziAccounting[7])
#             row.append(sziAccounting[8])
#             row.append(date_inst)
#             row.append(sziAccounting[9])
#             row.append(equipments)
#             row.append(fio)
#             row.append(date_uninst)
#             list_export.append(row)
#
#         wb = openpyxl.Workbook()
#         sheet = wb.sheetnames
#         lis = wb.active
#         # Создание строки с заголовками
#         lis.append(('№ п/п', 'Наименование СЗИ', 'Серийный номер СЗИ', 'Инвентарный номер СЗИ', 'Сведения о лецензии',
#                     'Тип СЗИ', 'Комплектность СЗИ',
#                     'Сведения о сертификате соответствия требованиям ИБ и знаке соответствия',
#                     'Реквизиты документов', 'Номер и дата акта установки (подключения) СЗИ и ввода его в эксплуатацию',
#                     'В составе комплекса / По проекту', 'Место установки (подключения) СЗИ',
#                     'Ф.И.О, должность осуществляющего эксплуатацию СЗИ',
#                     'Номер и дата акта вывода из эксплуатации и демонтажа (деинсталляции)', 'Примечание'))
#         for equipment in list_export:
#             lis.append(list(equipment))
#         wb.save(filename='Жрнал учета СЗИ.xlsx')
#         os.startfile('Жрнал учета СЗИ.xlsx')
#
#     def get_path_form(self, form: str) -> pathlib:
#         '''Принимаем название формы возвращаем путь данной формы'''
#         if getattr(sys, 'frozen', False):
#             path = os.path.dirname(sys.executable)
#             path = path + r'\Form_print' + '\\' + form
#         elif __file__:
#             path = os.path.dirname(__file__)
#             path = pathlib.Path(path).parents[1]
#             path = str(path) + r'\Form_print' + '\\' + form
#         return path
#
#     def clicked_btn_uninst(self):
#         def get_list_equipment_id():
#             '''Получаем список оборудования для деинсталяции'''
#             list_equipmentId = []  # список оборудования для составления акта(СКР, расположение)
#             for i in self.s.query(SziEquipment.equipment_id). \
#                     filter(SziEquipment.sziAccounting_id == id_SziAccounting). \
#                     filter(SziEquipment.status == True):
#                 list_equipmentId.append(i[0])
#
#             return list_equipmentId
#
#         def save_act_uninst(id_SziAccounting):
#             '''Записываем в таблицы SziFileUninst, SziAccounting, SziEquipment id-файла деинсталяции,
#             возвращаем id SziFileUninst'''
#
#             def reserve_id_SziFileInst() -> int:
#                 '''Резервируем и возвращаем id в SziFileUninst '''
#                 sziFileUninst = SziFileUninst(fileName='', date=datetime.now().date())
#                 self.s.add(sziFileUninst)
#                 self.s.flush()
#                 return sziFileUninst.id
#
#             def save_fileUninstSzi_id_SziAccounting(id: int, fileUninstSzi_id: int):
#                 '''Записываем в поле fileUninstSzi_id ранее зарезервированный id из SziFileUninst'''
#                 sziAccounting = self.s.query(SziAccounting).filter(SziAccounting.id == id).one()
#                 sziAccounting.fileUninstSzi_id = fileUninstSzi_id
#                 sziAccounting.status = False
#                 self.s.add(sziAccounting)
#
#             def save_fileUninstSzi_id_SziEquipment(sziAccounting_id: int, fileUninstSzi_id: int):
#                 '''Записываем в поле fileUninstSzi_id ранее зарезервированный id из SziFileUninst'''
#                 sziEquipment = self.s.query(SziEquipment).filter(SziEquipment.sziAccounting_id == sziAccounting_id). \
#                     filter(SziEquipment.status == True)
#                 for row in sziEquipment:
#                     row.fileUninstSzi_id = fileUninstSzi_id
#                     row.status = False
#                     self.s.add(row)
#
#             id_SziFileUninst = reserve_id_SziFileInst()
#             save_fileUninstSzi_id_SziAccounting(id_SziAccounting, id_SziFileUninst)
#             save_fileUninstSzi_id_SziEquipment(id_SziAccounting, id_SziFileUninst)
#
#             self.s.commit()
#
#             return id_SziFileUninst
#
#         def get_list_equipment_id_fileUnistal(id_SziFileUninst):
#             '''Получаем список оборудования для деинсталяции с файлом для деинсталяции'''
#             list_equipmentId = []  # список оборудования для составления акта(СКР, расположение)
#             for i in self.s.query(SziEquipment.equipment_id). \
#                     filter(SziEquipment.sziAccounting_id == id_SziAccounting). \
#                     filter(SziEquipment.status == False). \
#                     filter(SziEquipment.fileUninstSzi_id == id_SziFileUninst):
#                 list_equipmentId.append(i[0])
#
#             return list_equipmentId
#
#         if self.ui.tW_act.currentRow() >= 0:
#
#             id_SziAccounting = self.ui.table_main.item(self.ui.table_main.currentRow(), 0).text()
#             sziAccounting = self.s.query(SziAccounting).filter(SziAccounting.id == id_SziAccounting).one()
#             id_fileUninstSzi = sziAccounting.fileUninstSzi_id
#
#             if id_fileUninstSzi == None:
#
#                 if self.ui.tW_act.item(self.ui.tW_act.currentRow(), 1).text() != '':
#                     rez = QMessageBox.question(self, 'Предупреждение', "Удалить выбранный СЗИ?",
#                                                QMessageBox.Ok | QMessageBox.Cancel)
#
#                     if rez == QMessageBox.Cancel:
#                         return
#
#                     list_equipmentId = get_list_equipment_id()
#                     id_fileUninstSzi = str(save_act_uninst(id_SziAccounting))
#                     Helper_all.print_act_uninst(list_equipmentId, id_fileUninstSzi, id_SziAccounting)
#                     self.print_tW_act()
#             else:
#                 list_equipmentId = get_list_equipment_id_fileUnistal(id_fileUninstSzi)
#                 Helper_all.print_act_uninst(list_equipmentId, id_fileUninstSzi, id_SziAccounting)
#
#     def clicked_btn_ins(self):
#
#         if self.ui.tW_act.currentRow() >= 0 and self.ui.tW_act.currentColumn() == 1:
#
#             id_SziAccounting = self.ui.tW_act.item(self.ui.tW_act.currentRow(), 0).text()
#
#             list_equipmentId = list()
#             for i in self.s.query(SziEquipment.equipment_id).filter(SziEquipment.sziAccounting_id == id_SziAccounting):
#                 list_equipmentId.append(i[0])
#
#             locationEquipmentSkr = Helper_all.info_equipment_act_szi(list_equipmentId, id_SziAccounting)
#
#             act = self.ui.lE_akt.text().split()
#             number_act = act[2]
#             date_act = act[4]
#
#             def get_user_fio(user_fio):
#                 user_fio = re.sub(r'\b(\w+)\b\s+\b(\w)\w*\b\s+\b(\w)\w*\b', r'\1 \2.\3.', user_fio)
#                 return user_fio
#
#             dictionary = {'DateFull': Helper_all.get_date_full(date_act),
#                           'Date': date_act,
#                           'Number': number_act,
#                           'Equipment': locationEquipmentSkr,
#                           'NameSzi': self.ui.table_main.item(self.ui.table_main.currentRow(), 1).text(),
#                           'Id_journalInstSzi': self.ui.table_main.item(self.ui.table_main.currentRow(), 0).text(),
#                           'Lic_journalInstSzi': self.ui.lE_lic.text(),
#                           'Title': self.ui.lE_title.text(),
#                           'User': get_user_fio(self.ui.lE_user.text())}
#
#             name_file = 'Акт установки номер- ' + number_act
#
#             replace_text(self.get_path_form('Inst_SZI.docx'), dictionary, name_file)
#
#     def eventFilter(self, source, event):
#         if (source is self.ui.tW_act.viewport() and
#             (event.type() == QEvent.DragEnter or
#              event.type() == QEvent.DragMove or
#              event.type() == QEvent.Drop) and
#             event.mimeData().hasUrls()) and self.ui.tW_act.currentRow() != -1:
#             if event.type() == QEvent.Drop:
#                 act = []
#                 for url in event.mimeData().urls():
#                     if url.isLocalFile():
#                         act.append(url.path())
#
#                 if len(act) > 1:
#                     QMessageBox.warning(self, 'Внимание', "Можно загрузить только один файл!", QMessageBox.Ok)
#                 else:
#                     path_file = act[0]
#                     path_file = path_file[1:]  # Удалили первый символ
#                     self.download_file(path_file)
#             event.accept()
#             return True
#         return super().eventFilter(source, event)
#
#     def download_file(self, path_file):
#
#         def convertToBinaryData(filename):
#             '''convert Pdf file to binery'''
#
#             with open(filename, 'rb') as file:
#                 blobData = file.read()
#             return blobData
#
#         def save_inst(id_SziFileInst: int, path_file: pathlib):
#             '''Сохраняем акт инсталяции в SziFileInst'''
#
#             file_name = pathlib.Path(path_file).name
#             file_data = convertToBinaryData(path_file)
#
#             sziFileInst = self.s.query(SziFileInst).filter(SziFileInst.id == id_SziFileInst).one()
#             sziFileInst.fileName = file_name
#             sziFileInst.file_data = file_data
#             self.s.add(sziFileInst)
#             self.s.commit()
#
#         def save_uninst(id_fileUninstSzi_id: int, path_file: pathlib):
#             '''Сохраняем акт инсталяции в SziFileUninst'''
#             file_name = pathlib.Path(path_file).name
#             file_data = convertToBinaryData(path_file)
#
#             sziFileUninst = self.s.query(SziFileUninst).filter(SziFileUninst.id == id_fileUninstSzi_id).one()
#             sziFileUninst.fileName = file_name
#             sziFileUninst.file_data = file_data
#             self.s.add(sziFileUninst)
#             self.s.commit()
#
#         if pathlib.Path(path_file).suffix == '.pdf':
#
#             sziAccounting = self.s.query(SziAccounting.fileInstSzi_id, SziAccounting.fileUninstSzi_id). \
#                 filter(SziAccounting.id == self.ui.table_main.item(self.ui.table_main.currentRow(), 0).text()).one()
#             if self.ui.tW_act.currentColumn() == 1:
#                 sziFileInst = self.s.query(SziFileInst.file_data).filter(SziFileInst.id == sziAccounting[0]).one()
#                 if sziFileInst[0] is not None:
#                     rez = QMessageBox.question(self, 'Предупреждение', "Заменить Акт?",
#                                                QMessageBox.Ok | QMessageBox.Cancel)
#
#                     if rez == QMessageBox.Cancel:
#                         return
#                 id_SziFileInst = sziAccounting[0]
#                 save_inst(id_SziFileInst, path_file)
#                 self.print_tW_act()
#             elif self.ui.tW_act.currentColumn() == 2:
#                 if sziAccounting[1] == None:
#                     QMessageBox.warning(self, 'Внимание', "Необходимо распечатать акт деинсталляции!", QMessageBox.Ok)
#                 else:
#                     sziFileUninst = self.s.query(SziFileUninst.file_data).filter(
#                         SziFileUninst.id == sziAccounting[1]).one()
#                     if sziFileUninst[0] is not None:
#                         rez = QMessageBox.question(self, 'Предупреждение', "Заменить Акт?",
#                                                    QMessageBox.Ok | QMessageBox.Cancel)
#
#                         if rez == QMessageBox.Cancel:
#                             return
#                     save_uninst(sziAccounting[1], path_file)
#                     self.print_tW_act()
#         else:
#             QMessageBox.warning(self, 'Внимание', "Можно загрузить только pdf файлы!", QMessageBox.Ok)
#
#     def clear_fill(self):
#         self.ui.lE_sn.clear()
#         self.ui.lE_inv.clear()
#         self.ui.lE_lic.clear()
#         self.ui.lE_type.clear()
#         self.ui.lE_completeness.clear()
#         self.ui.lE_sert.clear()
#         self.ui.lE_rec.clear()
#         self.ui.lE_akt.clear()
#         self.ui.lE_project.clear()
#         self.ui.tE_eqipment.clear()
#         self.ui.lE_user.clear()
#         self.ui.lE_title.clear()
#
#         self.ui.tW_act.setRowCount(0)
#
#     def mouseDoubleClickEvent_tW_act(self, item: QTableWidgetItem):
#         def write_to_file(data, filename):
#             # Преобразование двоичных данных в нужный формат
#             with open(filename, 'wb') as file:
#                 file.write(data)
#
#         id_SziAccounting = self.ui.tW_act.item(self.ui.tW_act.currentRow(), 0).text()
#         sziAccounting = self.s.query(SziAccounting).filter(SziAccounting.id == id_SziAccounting).one()
#         fileInstSzi_id = sziAccounting.fileInstSzi_id
#         fileUninstSzi_id = sziAccounting.fileUninstSzi_id
#
#         if item.column() == 1 and self.ui.tW_act.item(self.ui.tW_act.currentRow(), 1).text() != '':
#             act = self.s.query(SziFileInst.fileName, SziFileInst.file_data).filter(
#                 SziFileInst.id == fileInstSzi_id).one()
#             if act[1] == None:
#                 QMessageBox.warning(self, 'Внимание', "Акт установки не загружен в систему", QMessageBox.Ok)
#                 return
#
#             downloads_path = str(pathlib.Path.home() / "Downloads")  # C:\Users\79033\Downloads
#             regForm_path = os.path.join(downloads_path + '\\' + act[0])
#             write_to_file(act[1], regForm_path)
#             os.startfile(regForm_path)
#
#         if item.column() == 2:
#             if self.ui.tW_act.item(self.ui.tW_act.currentRow(), 2).text() != '':
#                 act = self.s.query(SziFileUninst.fileName, SziFileUninst.file_data).filter(
#                     SziFileUninst.id == fileUninstSzi_id).one()
#                 if act[1] == None:
#                     QMessageBox.warning(self, 'Внимание', "Акт установки не загружен в систему", QMessageBox.Ok)
#                     return
#
#                 downloads_path = str(pathlib.Path.home() / "Downloads")  # C:\Users\79033\Downloads
#                 regForm_path = os.path.join(downloads_path + '\\' + act[0])
#                 write_to_file(act[1], regForm_path)
#                 os.startfile(regForm_path)
#
#     def print_tW_act(self):
#
#         id_SziAccounting = self.ui.table_main.item(self.ui.table_main.currentRow(), 0).text()
#
#         sziAccounting = self.s.query(SziAccounting, SziFileInst, SziFileUninst). \
#             select_from(SziAccounting). \
#             join(SziFileInst). \
#             join(SziFileUninst, isouter=True). \
#             filter(SziAccounting.id == id_SziAccounting).one()
#
#         self.ui.tW_act.setRowCount(0)
#
#         rowPosition = self.ui.tW_act.rowCount()
#         self.ui.tW_act.insertRow(rowPosition)
#
#         if sziAccounting[2] is not None:
#             number_act_uninst = str(sziAccounting[2].id)
#             date_act_uninst = str(sziAccounting[2].date.strftime('%d.%m.%Y'))
#             act_uninst = ('Акт № ' + number_act_uninst + ' от ' + date_act_uninst)
#
#             if sziAccounting[2].file_data == None:
#                 collor_tex_uninst = Qt.red
#             else:
#                 collor_tex_uninst = Qt.black
#         else:
#             act_uninst = ''
#             collor_tex_uninst = Qt.black
#
#         number_act_inst = str(sziAccounting[1].id)
#         date_act_inst = str(sziAccounting[1].date.strftime('%d.%m.%Y'))
#         act_inst = ('Акт № ' + number_act_inst + ' от ' + date_act_inst)
#
#         if sziAccounting[1].file_data == None:
#             collor_tex_inst = Qt.red
#         else:
#             collor_tex_inst = Qt.black
#
#         self.ui.tW_act.setItem(rowPosition, 0, QTableWidgetItem(str(sziAccounting[0].id)))
#         self.ui.tW_act.setItem(rowPosition, 1, QTableWidgetItem(act_inst))
#         self.ui.tW_act.setItem(rowPosition, 2, QTableWidgetItem(act_uninst))
#         self.ui.tW_act.item(rowPosition, 1).setForeground(QBrush(collor_tex_inst))
#         self.ui.tW_act.item(rowPosition, 2).setForeground(QBrush(collor_tex_uninst))
#
#     def get_Eqipment_currentSzi(self, id_SziAccounting) -> str:
#         '''Возвращаем имена объектов выбранной СЗИ'''
#
#         eqipments = list()
#         sziEquipment = self.s.query(Office_equipment.name_equipment). \
#             select_from(SziEquipment).join(Office_equipment). \
#             filter(SziEquipment.sziAccounting_id == id_SziAccounting). \
#             filter(SziEquipment.status == True)
#
#         for i in sziEquipment:
#             eqipments.append(i[0])
#
#         return ', '.join(eqipments)
#
#     def itemSelectionChanged_table_main(self):
#
#         if self.ui.table_main.item(self.ui.table_main.currentRow(), 0) is not None:
#             current_id = int(self.ui.table_main.item(self.ui.table_main.currentRow(), 0).text())
#
#             sziAccounting = self.s.query(SziAccounting, SziType, SziFileInst, User, SziFileUninst). \
#                 select_from(SziAccounting). \
#                 join(SziType). \
#                 join(SziFileInst). \
#                 join(User). \
#                 join(SziFileUninst, isouter=True). \
#                 filter(SziAccounting.id == current_id).one()
#
#             self.ui.tE_eqipment.clear()
#
#             self.ui.lE_sn.setText(sziAccounting[0].sn)
#             self.ui.lE_inv.setText(sziAccounting[0].inv)
#             self.ui.lE_lic.setText(sziAccounting[0].lic)
#             self.ui.lE_type.setText(sziAccounting[1].name)
#             self.ui.lE_completeness.setText(sziAccounting[1].completeness)
#             self.ui.lE_sert.setText(sziAccounting[1].sert)
#             self.ui.lE_rec.setText(sziAccounting[0].rec)
#             self.ui.lE_project.setText(sziAccounting[1].project)
#             # self.ui.tE_eqipment.append(sziAccounting[2].equipments)
#             self.ui.tE_eqipment.append(
#                 self.get_Eqipment_currentSzi(self.ui.table_main.item(self.ui.table_main.currentRow(), 0).text()))
#             self.ui.lE_user.setText(sziAccounting[3].fio)
#             self.ui.lE_title.setText(sziAccounting[3].post)
#             number_act = str(sziAccounting[2].id)
#             date_act = str(sziAccounting[2].date.strftime('%d.%m.%Y'))
#             self.ui.lE_akt.setText('Акт № ' + number_act + ' от ' + date_act)
#
#             self.print_tW_act()
#
#     def create_tW_act(self):
#         numrows = 0
#         numcols = 3
#
#         self.ui.tW_act.setColumnCount(numcols)
#         self.ui.tW_act.setRowCount(numrows)
#
#         self.ui.tW_act.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
#         self.ui.tW_act.verticalHeader().setVisible(False)
#         self.ui.tW_act.setHorizontalHeaderItem(0, QTableWidgetItem('fileInstSzi_id'))
#         self.ui.tW_act.setHorizontalHeaderItem(1, QTableWidgetItem('Акт установки СЗИ'))
#         self.ui.tW_act.setHorizontalHeaderItem(2, QTableWidgetItem('Акт установки СЗИ'))
#
#         header = self.ui.tW_act.horizontalHeader()
#         header.setSectionResizeMode(0, 10)
#         self.ui.tW_act.setColumnHidden(0, True)
#
#         header.setSectionResizeMode(1, QHeaderView.Stretch)
#         header.setSectionResizeMode(2, QHeaderView.Stretch)
#
#     def print_table_szi(self):
#         def load_sziAccounting():
#             def convert_str_bool(str):
#                 if str == 'True' or str == True:
#                     return True
#                 else:
#                     return False
#
#             checkBox_status_on = convert_str_bool(config['Szi_setting']['checkBox_status_on'])
#             checkBox_status_of = convert_str_bool(config['Szi_setting']['checkBox_status_of'])
#
#             checked_Equipment = config['Szi_setting']['checked_Equipment']
#             checked_typeEquipment = config['Szi_setting']['checked_typeEquipment']
#             checked_brabch = config['Szi_setting']['brabch']
#             checked_department = config['Szi_setting']['department']
#             checked_szi_type = config['Szi_setting']['szi_type']
#             checked_employeeId = config['Szi_setting']['employeeId']
#
#             if checkBox_status_on == False and checkBox_status_of == False:
#                 status = '% % %'
#             if checkBox_status_on == True and checkBox_status_of == False:
#                 status = 1
#             if checkBox_status_on == True and checkBox_status_of == True:
#                 status = '%'
#             if checkBox_status_on == False and checkBox_status_of == True:
#                 status = 0
#
#             szi = self.s.query(SziAccounting.id, SziType.name). \
#                 select_from(SziAccounting). \
#                 join(SziType). \
#                 join(SziEquipment). \
#                 join(Office_equipment). \
#                 join(Branch). \
#                 join(Department). \
#                 join(SziFileInst). \
#                 join(User, SziFileInst.user_id == User.employeeId). \
#                 filter(SziAccounting.sziType_id.in_((checked_szi_type))). \
#                 filter(SziAccounting.status.like(status)). \
#                 filter(SziEquipment.equipment_id.in_((checked_Equipment))). \
#                 filter(Office_equipment.type_equipment_id.in_((checked_typeEquipment))). \
#                 filter(Branch.id.in_((checked_brabch))). \
#                 filter(Department.id.in_((checked_department))). \
#                 filter(User.employeeId.in_((checked_employeeId))). \
#                 order_by(SziAccounting.id). \
#                 group_by(SziAccounting.id)
#             return szi
#
#         szi = load_sziAccounting()
#
#         numrows = szi.count()
#         if numrows == 0:
#             self.ui.table_main.setRowCount(0)
#             self.clear_fill()
#             return
#         numcols = 2
#
#         self.ui.statusbar.showMessage('СЗИ: ' + str(numrows))
#
#         self.ui.table_main.setColumnCount(numcols)
#         self.ui.table_main.setRowCount(numrows)
#
#         self.ui.table_main.setEditTriggers(QAbstractItemView.NoEditTriggers)  # read only
#         self.ui.table_main.verticalHeader().setVisible(False)
#         self.ui.table_main.setHorizontalHeaderItem(0, QTableWidgetItem('Уч.№'))
#         self.ui.table_main.setHorizontalHeaderItem(1, QTableWidgetItem('СЗИ'))
#         header = self.ui.table_main.horizontalHeader()
#         header.setSectionResizeMode(0, 10)
#         header.setSectionResizeMode(1, QHeaderView.Stretch)
#
#         for index_row, i in enumerate(szi):
#             self.ui.table_main.setItem(index_row, 0, QTableWidgetItem(str(i[0])))
#             self.ui.table_main.setItem(index_row, 1, QTableWidgetItem(i[1]))
#
#     def clicked_btn_new(self):
#         self.szi_new = Szi_new()
#         self.szi_new.exec_()
#         self.print_table_szi()
#
#     def clicked_btn_sziType(self):
#         self.szi_typy = Szi_type()
#         self.szi_typy.exec_()
#         self.print_table_szi()
#
#     def clicked_btn_setting(self):
#         szi_setting = Szi_setting()
#         szi_setting.exec_()
#         self.print_table_szi()