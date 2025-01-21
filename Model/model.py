from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BLOB, Date

from Model.database import Base


class User(Base):
    __tablename__ = 'Users'

    employeeId = Column(Integer, primary_key=True)
    fio = Column(String, nullable=False)
    branch_id = Column(String, ForeignKey('branches.id'))
    departmet_id = Column(Integer, ForeignKey('departments.id'))
    post = Column(String)
    phone = Column(String)
    eMail = Column(String)
    address = Column(String)
    login = Column(String)
    dk = Column(String)
    armName = Column(String)
    statusWork = Column(Boolean, unique=False)


class Usb(Base):
    __tablename__ = 'Usbs'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    vid = Column(String)
    pid = Column(String)
    sn = Column(String)
    usbStor = Column(String)
    usb_type_id = Column(Integer, ForeignKey('usb_types.id'))
    status = Column(Boolean, unique=False)
    user_id = Column(Integer, ForeignKey('Users.employeeId'))


class Usb_type(Base):
    __tablename__ = 'usb_types'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Usb_data(Base):
    __tablename__ = 'Usb_data'

    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    file_data = Column(BLOB)

    usb_id = Column(Integer, ForeignKey('Usbs.id'))
    user_id = Column(Integer, ForeignKey('Users.employeeId'))


class User_System(Base):
    __tablename__ = 'User_systems'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.employeeId'))
    id_inf_system = Column(Integer, ForeignKey('inf_systems.id'))
    file_name = Column(String)
    file_data = Column(BLOB)


class Inf_System(Base):
    __tablename__ = 'inf_systems'

    id = Column(Integer, primary_key=True)
    inf_system = Column(String)


class Office_equipment(Base):
    __tablename__ = 'office_equipments'

    id = Column(Integer, primary_key=True)
    branch_id = Column(String, ForeignKey('branches.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    type_equipment_id = Column(Integer, ForeignKey('office_type_equipments.id'))
    name_equipment = Column(String)
    inv_number = Column(String)
    start_date = Column(Date)
    model_equipment = Column(String)
    manufacturer = Column(String)
    sn_equipment = Column(String)
    notes = Column(String)
    is_work = Column(Boolean, unique=False)
    location = Column(String)


class Office_type_equipment(Base):
    __tablename__ = 'office_type_equipments'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Branch(Base):
    __tablename__ = 'branches'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Skr(Base):
    __tablename__ = 'skrs'

    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, ForeignKey('office_equipments.id'))
    user_id = Column(Integer, ForeignKey('Users.employeeId'))
    numberSkr = Column(String)
    startDate = Column(Date)
    note = Column(String)


class SziType(Base):
    __tablename__ = 'sziType'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    completeness = Column(String)
    sert = Column(String)
    project = Column(String)


class SziAccounting(Base):
    __tablename__ = 'sziAccounting'

    id = Column(Integer, primary_key=True)
    sziType_id = Column(Integer, ForeignKey('sziType.id'))
    sn = Column(String)
    inv = Column(String)
    lic = Column(String)
    rec = Column(String)
    fileInstSzi_id = Column(Integer, ForeignKey('sziFileInst.id'))
    fileUninstSzi_id = Column(Integer, ForeignKey('sziFileUninst.id'))
    status = Column(Boolean)


class SziEquipment(Base):
    __tablename__ = 'sziEquipment'

    id = Column(Integer, primary_key=True)
    sziAccounting_id = Column(Integer, ForeignKey('sziAccounting.id'))
    equipment_id = Column(Integer, ForeignKey('office_equipments.id'))
    fileUninstSzi_id = Column(Integer, ForeignKey('sziFileUninst.id'))
    status = Column(Boolean)


class SziFileInst(Base):
    __tablename__ = 'sziFileInst'

    id = Column(Integer, primary_key=True)
    fileName = Column(String)
    file_data = Column(BLOB)
    date = Column(Date)
    user_id = Column(Integer, ForeignKey('Users.employeeId'))
    equipments = Column(String)


class SziFileUninst(Base):
    __tablename__ = 'sziFileUninst'

    id = Column(Integer, primary_key=True)
    fileName = Column(String)
    file_data = Column(BLOB)
    date = Column(Date)
    cause = Column(String)
