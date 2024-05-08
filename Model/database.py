from sqlalchemy import  create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import  sessionmaker
from config_helper import config


path_db=config['Setting_helper']['path_db']

if path_db=='':
    DATABASE_NAME=r'helper_db'
else:
    DATABASE_NAME=path_db

engine=create_engine(f'sqlite:///{DATABASE_NAME}')
session=sessionmaker(bind=engine)

Base=declarative_base()

def create_db():
    Base.metadata.create_all(engine)












