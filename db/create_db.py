from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from config import DB_NAME

BASE_DIR = os.path.dirname(__file__) + '/'
engine = create_engine(f'sqlite:///{BASE_DIR}{DB_NAME}')  # , echo=True)
session = sessionmaker(bind=engine)

Base = declarative_base()


def create_db():
    Base.metadata.create_all(engine)
