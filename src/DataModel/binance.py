from ast import For
from sqlalchemy.orm import declarative_base
from sqlalchemy import BOOLEAN, Column, Integer, String, ForeignKey,DateTime,Enum
from datetime import datetime



Base = declarative_base()
    
class BINANCETRADEORDERS(Base):
    __tablename__ = 'binancetradeorders'
    id = Column(Integer(),unique=True,primary_key=True,autoincrement=True)
    clientid = Column(Integer())
    price = Column(String())
    amount = Column(String())
    status = Column(Integer())
    ordertype = Column(Integer())
    trantype = Column(Integer())
    coinpair = Column(String())
    exchgid = Column(Integer())
    exchgorderid = Column(String())
    trandata = Column(String())
    
    
class CRYPTOORDER(Base):
    __tablename__ = 'cryptoorder'
    id = Column(Integer(),unique=True,primary_key=True,autoincrement=True)
    price = Column(String())
    amount = Column(String())
    status = Column(Integer())
    ordertype = Column(Integer())
    trantype = Column(Integer())
    coinpair = Column(String())
    exchgid = Column(Integer())
    



class CRYPTOORDERSTATUS():
    NEW = 1
    
    
    