import random
from DataModel.binance import BINANCETRADEORDERS, CRYPTOORDER
from db import Session,engine

def createCryptoOrder(
        clientid=None,
        price=None,
        amount=None,
        status=None,
        ordertype=None,
        trantype=None,
        coinpair=None,
        exchgid=None,
    ):
    db_session = Session(bind=engine)
    cryptoOrder = CRYPTOORDER(
        clientid = clientid,
        price = price,
        amount = amount,
        status = status,
        ordertype = ordertype,
        trantype =trantype,
        coinpair = coinpair,
        exchgid = exchgid,
    )
    db_session.add(cryptoOrder)
    db_session.commit()
    return cryptoOrder
    # db_session.close()


def createBinanceTradeOrder(
        clientid = None,
        price = None, 
        amount = None, 
        status = None, 
        ordertype = None, 
        trantype = None, 
        coinpair = None, 
        exchgid = None, 
        exchgorderid = None, 
        trandata = None,
    ):
    db_session = Session(bind=engine)
    binanceOrder = BINANCETRADEORDERS(
        clientid = clientid,
        price = price, 
        amount = amount, 
        status = status, 
        ordertype = ordertype, 
        trantype = trantype, 
        coinpair = coinpair, 
        exchgid = exchgid, 
        exchgorderid = exchgorderid, 
        trandata = trandata,
    ) 
    db_session.add(binanceOrder);
    db_session.commit()
    # db_session.close()  

def set_crypto_order_obj(
        order = None,
        clientid=None,
        price=None,
        amount=None,
        status=None,
        ordertype=None,
        trantype=None,
        coinpair=None,
        exchgid=None,
):
    if set_keys is None:
        set_keys = []
    arguments = locals()
    for key, value in arguments.items():
        if value is not None or key in set_keys:
            setattr(order, key, value)    

def updateCryptoOrder(
        id=None,          
        clientid=None,
        price=None,
        amount=None,
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
        clientid = clientid,
        price = price, 
        amount = amount, 
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
        amount = None, 
        status = None, 
        ordertype = None, 
        trantype = None, 
        coinpair = None, 
        exchgid = None, 
        exchgorderid = None, 
        trandata = None,
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
        amount = None, 
        status = None, 
        ordertype = None, 
        trantype = None, 
        coinpair = None, 
        exchgid = None, 
        exchgorderid = None, 
        trandata = None,
):
    db_session = Session(bind=engine)
    order = (
        db_session.query(BINANCETRADEORDERS).filter(BINANCETRADEORDERS.id == id).with_for_update().one()
    )
    set_binance_trade_order_obj(
        order,
        clientid = clientid,
        price = price, 
        amount = amount, 
        status = status, 
        ordertype = ordertype, 
        trantype = trantype, 
        coinpair = coinpair, 
        exchgid = exchgid, 
        exchgorderid = exchgorderid, 
        trandata = trandata,
    )
    db_session.flush()
    db_session.commit()