from ast import For
from sqlalchemy.orm import declarative_base
from sqlalchemy import BOOLEAN, Column, Integer, String, ForeignKey,DateTime,Enum
from datetime import datetime



Base = declarative_base()
    
class BINANCETRADEORDERS(Base):
    __tablename__ = 'binancetradeorders'
    id = Column(Integer(),unique=True,primary_key=True,autoincrement=True)
    ctid = Column(Integer())
    clientorderid = Column(String())
    price = Column(String())
    qty = Column(String())
    status = Column(Integer())
    ordertype = Column(Integer())
    trantype = Column(Integer())
    coinpair = Column(String())
    exchgid = Column(Integer())
    exchgorderid = Column(String())
    trandata = Column(String())
    action = Column(Integer())
    updatedtime = Column(DateTime())

    def as_dict(self):
        return {
            "id":self.id,
            "ctid":self.ctid,
            "clientorderid": self.clientorderid,
            "price": self.price, 
            "qty": self.qty, 
            "status": self.status, 
            "ordertype": self.ordertype, 
            "trantype" : self.trantype, 
            "coinpair" : self.coinpair, 
            "exchgid" : self.exchgid, 
            "exchgorderid" : self.exchgorderid, 
            "trandata" : self.trandata,
            "action" : self.action,
            "updatedtime":str(self.updatedtime)
        }
    
class BinanceTradeOrderStatus():
    NEW = 0
    ORDER_PLACED = 1
    PARTIALLY_FILLED = 2
    FULLY_FILLED = 3
    PARTIALLY_FILLED_AND_CANCELLED = 4
    PARTIALLY_FILLED_AND_EXPIRED = 5
    ORDER_PLACED_AND_CANCELLED = 6
    ORDER_PLACED_AND_EXPIRED = 7
    REJECTED = 8

class BinanceTradeAction():
    CREATE = 1
    CANCEL = 2
    ADMIN_CANCEL = 3
    TO_CLOSE = 4
    CLOSED = 5
    
    
    

    
    
    



class TRADEORDERVERIFIED(Base):
    __tablename__ = 'tradeordersverified'
    id = Column(Integer(),unique=True,primary_key=True,autoincrement=True)
    orderid = Column(Integer())
    clientid = Column(Integer())
    price = Column(Integer())
    amount = Column(Integer())
    coinpair = Column(String())
    status = Column(Integer())
    ordertype = Column(Integer())
    trantype = Column(Integer())
    exchgid = Column(Integer())

    def as_dict(self):
        return {
            "id":self.id,
            "orderid":self.orderid,
            "clientid":self.clientid,
            "price": str(self.price), 
            "amount": str(self.amount), 
            "coinpair": self.coinpair, 
            "status": self.status, 
            "ordertype" : self.ordertype, 
            "trantype" : self.trantype, 
            "exchgid" : self.exchgid,
        }    
      
      
class TradeOrderVerifiedStatus():
    VERIFIED = 1
    PROCESSED = 2
    REJECTED = 3