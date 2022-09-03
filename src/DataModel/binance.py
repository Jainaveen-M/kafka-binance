from ast import For
from sqlalchemy.orm import declarative_base
from sqlalchemy import BOOLEAN, Column, Integer, String, ForeignKey,DateTime,Enum
from datetime import datetime



Base = declarative_base()
    
class BINANCETRADEORDERS(Base):
    __tablename__ = 'binancetradeorders'
    id = Column(Integer(),unique=True,primary_key=True,autoincrement=True)
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

    def as_dict(self):
        return {
            "id":self.id,
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
            "crypto_order_id": self.crypto_order_id
        }
    
class BinanceTradeOrderStatus():
    NEW = 1
    ORDER_PLACED = 2
    PARTIALLY_FILLED = 3
    FULLY_FILLED = 4
    CANCELLED_BY_CT = 5
    PENDING_CANCEL = 6
    CANCELED = 7
    REJECTED = 8 
    TRADE = 9
    EXPIRED = 10
    
    
    
    
    
    
    