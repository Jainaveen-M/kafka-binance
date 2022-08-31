from ast import For
from sqlalchemy.orm import declarative_base
from sqlalchemy import BOOLEAN, Column, Integer, String, ForeignKey,DateTime,Enum
from datetime import datetime



Base = declarative_base()
    
class BINANCETRADEORDERS(Base):
    __tablename__ = 'binancetradeorders'
    id = Column(Integer(),unique=True,primary_key=True,autoincrement=True)
    clientid = Column(String())
    price = Column(String())
    qty = Column(String())
    status = Column(Integer())
    ordertype = Column(Integer())
    trantype = Column(Integer())
    coinpair = Column(String())
    exchgid = Column(Integer())
    exchgorderid = Column(String())
    trandata = Column(String())
    crypto_order_id = Column(String())

    def as_dict(self):
        return {
            "id":self.id,
            "clientid": self.clientid,
            "price": self.price, 
            "qty": self.qty, 
            "status": self.status, 
            "ordertype": self.ordertype, 
            "trantype" : self.trantype, 
            "coinpair" : self.coinpair, 
            "exchgid" : self.exchgid, 
            "exchgorderid" : self.exchgorderid, 
            "trandata" : self.trandata,
            "crypto_order_id": self.crypto_order_id
        }
    
    
class CRYPTOORDER(Base):
    __tablename__ = 'cryptoorder'
    id = Column(Integer(),unique=True,primary_key=True,autoincrement=True)
    price = Column(String())
    qty = Column(String())
    status = Column(Integer())
    ordertype = Column(Integer())
    trantype = Column(Integer())
    coinpair = Column(String())
    exchgid = Column(Integer())
    
    def as_dict(self):
        return {
            "id" : self.id,
            "price" : self.price,
            "qty" : self.qty,
            "status" : self.status,
            "ordertype" : self.ordertype,
            "trantype" :self.trantype,
            "coinpair" : self.coinpair,
            "exchgid" : self.exchgid,
        }
        


class CryptoOrderStatus():
    NEW = 1
    PROCESSED = 2
    
    


class BinanceTradeOrderStatus():
    ORDER_PLACED = 1
    PARTIALLY_FILLED = 2
    FULLY_FILLED = 5
    CANCELLED_BY_CT = 10
    
    
    
    
    
    