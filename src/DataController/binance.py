from os import stat
import random
from unittest import result
from DataModel.binance import BINANCETRADEORDERS, CRYPTOORDER
from db import Session,engine

def createCryptoOrder(
        price=None,
        qty=None,
        status=None,
        ordertype=None,
        trantype=None,
        coinpair=None,
        exchgid=None,
    ):
    db_session = Session(bind=engine)
    cryptoOrder = CRYPTOORDER(
        price = price,
        qty = qty,
        status = status,
        ordertype = ordertype,
        trantype =trantype,
        coinpair = coinpair,
        exchgid = exchgid,
    )
    db_session.add(cryptoOrder)
    db_session.commit()
    return cryptoOrder.as_dict()
    # db_session.close()


def createBinanceTradeOrder(
        clientid = None,
        price = None, 
        qty = None, 
        status = None, 
        ordertype = None, 
        trantype = None, 
        coinpair = None, 
        exchgid = None, 
        exchgorderid = None, 
        trandata = None,
        crypto_order_id=None,
    ):
    db_session = Session(bind=engine)
    binanceOrder = BINANCETRADEORDERS(
        clientid = clientid,
        price = price, 
        qty = qty, 
        status = status, 
        ordertype = ordertype, 
        trantype = trantype, 
        coinpair = coinpair, 
        exchgid = exchgid, 
        exchgorderid = exchgorderid, 
        trandata = trandata,
        crypto_order_id = crypto_order_id,
    ) 
    db_session.add(binanceOrder);
    db_session.commit()
    # db_session.close()  

def set_crypto_order_obj(
        order = None,
        price=None,
        qty=None,
        status=None,
        ordertype=None,
        trantype=None,
        coinpair=None,
        exchgid=None,
        set_keys = None,
):
    if set_keys is None:
        set_keys = []
    arguments = locals()
    for key, value in arguments.items():
        if value is not None or key in set_keys:
            setattr(order, key, value)    

def updateCryptoOrder(
        id=None,          
        price=None,
        qty=None,
        status=None,
        ordertype=None,
        trantype=None,
        coinpair=None,
        exchgid=None,
        
):
    
    db_session = Session(bind=engine)
    order = (
        db_session.query(CRYPTOORDER).filter(CRYPTOORDER.id == id).with_for_update().one()
    )
    set_crypto_order_obj(
        order,
        price = price, 
        qty = qty, 
        status = status, 
        ordertype = ordertype, 
        trantype = trantype, 
        coinpair = coinpair, 
        exchgid = exchgid, 
    )
    db_session.flush()
    db_session.commit()
    

def set_binance_trade_order_obj(
        order = None,
        clientid = None,
        price = None, 
        qty = None, 
        status = None, 
        ordertype = None, 
        trantype = None, 
        coinpair = None, 
        exchgid = None, 
        exchgorderid = None, 
        trandata = None,
        crypto_order_id = None,
        set_keys = None,
):
    if set_keys is None:
        set_keys = []
    arguments = locals()
    for key, value in arguments.items():
        if value is not None or key in set_keys:
            setattr(order, key, value)       


def updateBinanceTradeOrder(
        id=None,
        clientid = None,
        price = None, 
        qty = None, 
        status = None, 
        ordertype = None, 
        trantype = None, 
        coinpair = None, 
        exchgid = None, 
        exchgorderid = None, 
        trandata = None,
        crypto_order_id = None,
):
    db_session = Session(bind=engine)
    order = (
        db_session.query(BINANCETRADEORDERS).filter(BINANCETRADEORDERS.exchgorderid == exchgorderid).with_for_update().one()
    )
    set_binance_trade_order_obj(
        order,
        clientid = clientid,
        price = price, 
        qty = qty, 
        status = status, 
        ordertype = ordertype, 
        trantype = trantype, 
        coinpair = coinpair, 
        exchgid = exchgid, 
        exchgorderid = exchgorderid, 
        trandata = trandata,
        crypto_order_id = crypto_order_id
    )
    db_session.flush()
    db_session.commit()
    
    

def getActiveOrders(
    id=None,
    status = None,
):
    db_session = Session(bind=engine)
    query = db_session.query(CRYPTOORDER)
    result = []
    try:
        if status is not None:
            query = query.filter(CRYPTOORDER.status == status)
        if id is not None:
            query = query.filter(CRYPTOORDER.id == id)
        for order in query.all():
            result.append(order.as_dict())
    except Exception as e:
        print(str(e))
    db_session.close()
    return result
            
def getBinanceTradeOrder(
    orderId = None,
    status = None,
    crypto_order_id = None,
    db_session = None
):
    db_session = Session(bind=engine)
    query = db_session.query(BINANCETRADEORDERS)
    result = []
    try:
        if orderId is not None:
            query = query.filter(BINANCETRADEORDERS.exchgorderid == orderId)
        if crypto_order_id is not None:
            query = query.filter(BINANCETRADEORDERS.crypto_order_id == crypto_order_id)
        if status is not None:
            query = query.filter(BINANCETRADEORDERS.status == status)
        data = query.all()
        for order in data:
            result.append(order.as_dict())
    except Exception as e:
        print(str(e))
    return result