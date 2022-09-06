from DataModel.binance import BINANCETRADEORDERS
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
    data = None
    try:
        if id is not None:
            query = query.filter(BINANCETRADEORDERS.id == id).one()
        if clientorderid is not None:
            query = query.filter(BINANCETRADEORDERS.clientorderid == clientorderid).one()
        if status is not None:
            query = query.filter(BINANCETRADEORDERS.status == status).one()
        if ctid is not None:
            query = query.filter(BINANCETRADEORDERS.ctid == ctid).one()
        data = query.as_dict()
        print(f"Order Data from query {data}")
    except Exception as e:
        print(str(e))
    return data
