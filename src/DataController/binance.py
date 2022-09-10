from unittest import result
from DataModel.binance import BINANCETRADEORDERS, TRADEORDERVERIFIED
from db import Session,engine

def createBinanceTradeOrder(
        ctid = None,
        clientorderid = None,
        price = None, 
        qty = None, 
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
        ctid = ctid,
        clientorderid = clientorderid,
        price = price, 
        qty = qty, 
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
    

def set_binance_trade_order_obj(
        order = None,
        clientorderid = None,
        price = None, 
        qty = None, 
        status = None, 
        ordertype = None, 
        trantype = None, 
        coinpair = None, 
        exchgid = None, 
        exchgorderid = None, 
        trandata = None,
        set_keys = None,
):
    if set_keys is None:
        set_keys = []
    arguments = locals()
    for key, value in arguments.items():
        if value is not None or key in set_keys:
            setattr(order, key, value)       


def updateBinanceTradeOrder(
        clientorderid = None,
        price = None, 
        qty = None, 
        status = None, 
        ordertype = None, 
        trantype = None, 
        coinpair = None, 
        exchgid = None, 
        exchgorderid = None, 
        trandata = None,
):
    db_session = Session(bind=engine)
    
    if clientorderid is not None:
        order = db_session.query(BINANCETRADEORDERS).filter(BINANCETRADEORDERS.clientorderid == clientorderid).with_for_update().one()

                
    set_binance_trade_order_obj(
        order = order,
        clientorderid = clientorderid,
        price = price, 
        qty = qty, 
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
    
    

def getBinanceTradeOrder(
    id = None,
    clientorderid = None,
    status = None,
    ctid = None,
    db_session = None
):
    db_session = Session(bind=engine)
    query = db_session.query(BINANCETRADEORDERS)
    data = []
    try:
        if id is not None:
            query = query.filter(BINANCETRADEORDERS.id == id).one()
            return query.as_dict()
        if clientorderid is not None:
            query = query.filter(BINANCETRADEORDERS.clientorderid == clientorderid).one()
            return query.as_dict()
        if status is not None:
            if isinstance(status,list):
                query = query.filter(BINANCETRADEORDERS.status.in_(status))
            else:
                query = query.filter(BINANCETRADEORDERS.status == status).one()
        if ctid is not None:
            query = query.filter(BINANCETRADEORDERS.ctid == ctid).one()
            return query.as_dict()
        for row in query:
            data.append(row.as_dict())
        print(f"Order Data from query {data}")
    except Exception as e:
        print(str(e))
    return data 



def createTradeOrderVerified(
        orderid = None,
        clientid = None,
        price = None, 
        amount = None, 
        coinpair = None, 
        status = None, 
        ordertype = None, 
        trantype = None, 
        exchgid = None,
    ):
    db_session = Session(bind=engine)
    verifiedorder = TRADEORDERVERIFIED(
        orderid = orderid,
        clientid =clientid,
        price =price, 
        amount =amount, 
        coinpair =coinpair, 
        status =status, 
        ordertype =ordertype, 
        trantype =trantype, 
        exchgid =exchgid,
    ) 
    db_session.add(verifiedorder);
    db_session.commit()
    return verifiedorder.as_dict()
    
    
    

def set_verified_order_obj(
        order = None,
        id = None,
        orderid = None,
        clientid = None,
        price = None, 
        amount = None, 
        coinpair = None, 
        status = None, 
        ordertype = None, 
        trantype = None, 
        exchgid = None,
        set_keys = None,
):
    if set_keys is None:
        set_keys = []
    arguments = locals()
    for key, value in arguments.items():
        if value is not None or key in set_keys:
            setattr(order, key, value)       


def updateVerifiedOrders(
        id = None,
        orderid = None,
        clientid = None,
        price = None, 
        amount = None, 
        coinpair = None, 
        status = None, 
        ordertype = None, 
        trantype = None, 
        exchgid = None,
):
    db_session = Session(bind=engine)
    
    if id is not None:
        order = db_session.query(TRADEORDERVERIFIED).filter(TRADEORDERVERIFIED.id == id).with_for_update().one()

                
    set_verified_order_obj(
        order = order,
        id = id,
        orderid = orderid,
        clientid = clientid,
        price = price, 
        amount = amount, 
        coinpair = coinpair, 
        status = status, 
        ordertype = ordertype, 
        trantype = trantype, 
        exchgid = exchgid,
    )
    db_session.flush()
    db_session.commit()
    
    

def getVerifiedOrders(
    id = None,
    status = None,
    orderid = None,
    clientid = None,
    db_session = None
):
    db_session = Session(bind=engine)
    query = db_session.query(TRADEORDERVERIFIED)
    data = None
    result = []
    try:
        if id is not None:
            query = query.filter(TRADEORDERVERIFIED.id == id).one()
        if status is not None:
            query = query.filter(TRADEORDERVERIFIED.status == status)
        if clientid is not None:
            query = query.filter(TRADEORDERVERIFIED.clientid == clientid).one()
        if orderid is not None:
            query = query.filter(TRADEORDERVERIFIED.orderid == orderid).one()
        data = query.all()
        for order in data:
            result.append(order.as_dict())
        print(f"Verified Order Data from query {data}")
    except Exception as e:
        print(str(e))
    return result