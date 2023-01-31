from sqlalchemy import Column, Integer, String
from .create_db import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False)
    rand_num = Column(Integer, nullable=False)

    def __init__(self,
                 name: str,
                 username: str,
                 rand_num: int,
                 ):
        self.name = name
        self.username = username
        self.rand_num = rand_num
