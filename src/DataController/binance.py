from DataModel.binance import BINANCETRADEORDERS
from db import Session,engine


def createBinanceTradeOrder(
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
    orderId = None,
    status = None,
    db_session = None
):
    db_session = Session(bind=engine)
    query = db_session.query(BINANCETRADEORDERS)
    result = []
    try:
        if id is not None:
            query = query.filter(BINANCETRADEORDERS.id == id)
        if orderId is not None:
            query = query.filter(BINANCETRADEORDERS.exchgorderid == orderId)
        if status is not None:
            query = query.filter(BINANCETRADEORDERS.status == status)
        data = query.all()
        for order in data:
            result.append(order.as_dict())
    except Exception as e:
        print(str(e))
    return result