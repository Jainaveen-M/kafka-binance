import datetime
import logging
import time
import uuid
from decimal import Decimal
from flask import Flask,jsonify,request
import json,threading
from DataController.kafka import KafkaHelper
from binance import Binance
from colorama import Fore
from DataController.binance import createTradeOrderVerified, getBinanceTradeOrder, getVerifiedOrders, updateBinanceTradeOrder, updateVerifiedOrders
from DataModel.binance import BinanceTradeAction, BinanceTradeOrderStatus, TradeOrderVerifiedStatus

 
app = Flask(__name__)

app_name = "Binance_demo"

@app.route("/",methods=["GET"])   
def basic():
    binance = Binance()
    result = binance.get_exchange_info()
    # initsocket()
    return jsonify({"status":"success","message":result})


@app.route("/getassets",methods=["GET"]) 
def get_assets():
    binance = Binance()
    result = binance.get_recent_trades(symbol="TRXUSDT",limit=10)
    return jsonify({"status":"success","message":result})


@app.route("/getaccount",methods=["GET"])   
def get_account():
    binance = Binance()
    result = binance.get_account(recvWindow=5000)
    return jsonify({"status":"success","message":result})


@app.route("/getallorders/<symbol>",methods=["GET"])   
def getallorders(symbol):
    binance = Binance()
    result = binance.get_all_orders(symbol=symbol)
    return jsonify({"status":"success","message":result})

@app.route("/getopenorders",methods=["GET"])    
def getOpenorders(symbol=None):
    binance = Binance()
    result = binance.get_open_orders()
    return jsonify({"status":"success","message":result})

@app.route("/gettradehistory",methods=["POST"])   
def gettradehistory():
    binance = Binance()
    request_data = request.get_json()
    result = binance.get_all_orders(symbol=request_data.get("symbol"),orderId =request_data.get("orderId"))
    return jsonify({"status":"success","message":result})


@app.route("/getmytrades",methods=["POST"])   
def getmytrades():
    binance = Binance()
    request_data = request.get_json()
    result = binance.get_my_trades(symbol=request_data['symbol'],orderId = request_data['orderId']) # we can mention the fromid to get the trade history
    return jsonify({"status":"success","message":result})

# work only in live api
@app.route("/getuserassets",methods=["GET"])   
def getuserassets():
    binance = Binance()
    result = binance.get_user_assets() # return positive assets  
    return jsonify({"status":"success","message":result})

@app.route("/createorder/market",methods=["POST"])   
def createMarketOrder():
    binance = Binance()
    request_data = request.get_json()
    result = None
    #need to pass quantity or quoteOrderQty
    if request_data.get("quantity") is not None:
        result = binance.create_order(
            symbol=request_data.get("symbol"),
            side =  request_data.get("side"),
            type = "MARKET",
            quantity =  request_data.get("quantity")
       )
    if request_data.get("quoteOrderQty") is not None:
        result = binance.create_order(
            symbol=request_data.get("symbol"),
            side =  request_data.get("side"),
            type = "MARKET",
            quoteOrderQty =  request_data.get("quoteOrderQty")
       )
    return jsonify({"status":"success","message":result})

@app.route("/createorder/limit",methods=["POST"])   
def createLimitOrder():
    request_data = request.get_json()
    binance = Binance()
    result = binance.create_order(
        symbol=request_data.get("symbol"),
        side = request_data.get("side"),
        type = "LIMIT",
        timeInForce = "GTC",
        quantity = request_data.get("qty"),
        price = request_data.get("price")
        )
    #        quoteOrderQty = 400.0,
    return jsonify({"status":"success","message":result})


@app.route("/getorderbook",methods=["POST"])   
def getorderbook():
    request_data = request.get_json()
    binance = Binance()
    result = binance.get_order_book(symbol=request_data.get("symbol"),limit=10)
    return jsonify({"status":"success","message":result})  


@app.route("/cancelorder",methods=["POST"])   
def cancelorder():
    request_data = request.get_json()
    binance = Binance()
    result = binance.cancel_order(symbol=request_data.get("symbol"),orderId = request_data.get("orderId"))
    return jsonify({"status":"success","message":result})


@app.route('/delete/allopenorders',methods=['POST'])
def deleteAllOpenOrder():
    binance = Binance()
    request_data = request.get_json()
    result = binance.cancel_all_open_orders(symbol=request_data['symbol'])
    return jsonify({"status":"success","message":result})
    
@app.route("/order/<orderId>",methods=["GET"])
def getOrderDetails(orderId):
    binanceOrder = None
    try:
        order = getBinanceTradeOrder(id=orderId)
        print(f"Order Details -> {order}")
        binanceOrder = binance.get_order(
            symbol = order['coinpair'],
            orderId = order['exchgorderid']
        )
    except Exception as e:
        return jsonify({"status":"error","message":str(e)})
    return jsonify({"status":"order cancelled successfully","message":binanceOrder})

# need to be moved
def cryptoOrderBookRefresh(*argv):
    try:
        data = json.loads(list(argv)[1])
        coinpair = list(argv)[0].header['coinpair']
        try:
            #data = binance.get_order_book(symbol=coinpair.replace("/", ""), limit=20)
            paircoin, basecoin = coinpair.split("/")
            topbids = []
            topasks = []
            for item in data['bids']:
                s = str(Decimal(item[0]) * Decimal(item[1]))
                topbids.append(
                    {"price": "{} {}".format(item[0][:item[0].find(".")], basecoin),
                     "amount": "{} {}".format(item[1][:item[1].find(".")], paircoin),
                     "total": "{} {}".format(s[:s.find(".") + 1 + 8], basecoin), "sum": "", "flash": "0"})
            for item in data['asks']:
                s = str(Decimal(item[0]) * Decimal(item[1]))
                topasks.append(
                    {"price": "{} {}".format(item[0][:item[0].find(".")], basecoin),
                     "amount": "{} {}".format(item[1][:item[1].find(".")], paircoin),
                     "total": "{} {}".format(s[:s.find(".") + 8], basecoin), "sum": "", "flash": "0"})
            '''print json.dumps(
                {"topbids": topbids, "topasks": topasks,
                 "coinpair": coinpair})'''
            # time.sleep(int(serviceMgmt.app_config['cryptopairrefresh']))
            print(f"Top Bid {topbids}")
            print(f"Top Ask {topasks}")
        except:
            print("sefdvcse")
    except Exception as e:
        print(f'watch {str(e)}')

# need to be moved        


def marketData():
    binance = Binance()
    coinpair = "TRX/USDT"
    binance.createSocketThread(path="{}@depth10@1000ms".format(coinpair.replace("/", "").lower()),
                                onmessage=cryptoOrderBookRefresh, data={"coinpair": coinpair})
    
def initsocket():
    binance = Binance()
    # marketData()
    try:
        print("Came here")
        # binance.createUserDataStreamSocket(path="btcusdt@kline_1m")
        #binance.createUserSocket(path="btcusdt@kline_1m")
        binance.createUserSocketThread(path="",onmessage=watchBinanceCyptoOrders)
        # marketData()
    except Exception as e:
        print(str(e))


# this will create a row in crypto order table with status 1(NEW)
"""
- when customer tries to place a order it will receive the order and 
produce the event to the consumer
"""
@app.route("/create/order",methods=["POST"])   
def createOrder():
    request_data = request.get_json()
    order = None
    try:
        id = str(uuid.uuid4().int)
        orderID = id[:16]
        order = createTradeOrderVerified(
            orderid = orderID,
            clientid=request_data.get("clientid"),
            price = request_data.get("price"),
            amount = request_data.get("qty"),
            coinpair = request_data.get("coinpair"),
            status = TradeOrderVerifiedStatus.VERIFIED, 
            ordertype = 1, # 1 - LIMIT order  0 - Market order, 
            trantype = 0 if request_data.get("trantype") == "BUY" else 1, # 0 - buy 1 - sell, 
            exchgid = 1,
        )
        logging.debug(f"Order create successfully order - {order}")
    except Exception as e:
        print(str(e))
        return jsonify({"status":"error","message":str(e)})
    return jsonify({"status":"order created successfully","message":order})


# this will cancel the order and send the response to kafka producer

@app.route("/cancel/order/<orderId>",methods=["POST"])
def cancelOrder(orderId):
    orderData = None
    try:
        order = getBinanceTradeOrder(id=orderId)
        print(f"Cancel Order -> {order}")
        #validate req here
        orderData = {
            "orderId": order['exchgorderid'],
            "coinpair": order['coinpair'],
            "clientorderid": order['clientorderid'],
            "eventType":"httpEvent",
            "eventName":"CANCEL_ORDER"
        }
        partitionId = int(order['clientorderid']) % partitionCount
        print(Fore.YELLOW+f"Producer cancel order -> {orderData}  partition ID -> {partitionId}"+Fore.RESET)
        KafkaHelper.producer.send('binance-orders',orderData,partition=partitionId)
    except Exception as e:
        print(str(e))
        return jsonify({"status":"error","message":str(e)})
    return jsonify({"status":"order cancelled successfully","message":orderData})

def watchBinanceCyptoOrders(*argv):
    try:
        message = json.loads(list(argv)[1])
        message = message['data']
        print(f"Message -> {str(message)}")
        if message['e']=='outboundAccountPosition':
           print(str(["watchCyptoOrders", list(argv)]))
           print(Fore.YELLOW+f"Producer websocker -> {message}"+Fore.RESET)
        elif message['e']=='executionReport':
            orderId = message['i']
            partitionId = orderId % partitionCount
            message['eventType'] = 'wsocketEvent'
            message['eventName'] = message['x']
            print(f"watchBinanceCyptoOrderstype - {type(message)}")
            KafkaHelper.producer.send('binance-events',message,partition=partitionId,key=b"wsocketEvent")
            print("event produced")
            if  message['X']=='PARTIALLY_FILLED':
                print("PARTIALLY_FILLED")
            if message['X'] == 'FILLED':
                print("FILLED")
            print(str(message))
    except Exception as e:
        print(str(e))

#Job to process the order when the order got fully executed or canceled               
"""
get the orders with action to_close
make an api call to get the transaction data
validate the transactions data
if it is correct set the action to closed
if not update the correct transaction data and set the action to closed
"""

def validateOrder():
    print(f"Process validate order started")
    while True:
        try:    
            orders = getBinanceTradeOrder(action=BinanceTradeAction.TO_CLOSE)
            print(Fore.YELLOW+f"Validate Order -> {orders}"+Fore.RESET)
            for order in orders:
                print(f"+++ Order details -> {order}")
                binanceOrderDetail = binance.get_order(symbol = order['coinpair'],origClientOrderId = order['clientorderid'])
                binanceTradeDetail = binance.get_my_trades(symbol = order['coinpair'],orderId = order['exchgorderid'])
                print(Fore.BLUE+f"{binanceTradeDetail}"+Fore.RESET);
                binance_trandata = []
                for trandata in binanceTradeDetail:
                    new_trandata = {
                                    "price":trandata['price'],
                                    "qty":trandata['qty'],
                                    "commission":trandata['commission'],
                                    "commissionAsset":trandata['commissionAsset'],
                                    "tradeId":trandata['id']
                                }
                    binance_trandata.append(new_trandata)
                
                print(Fore.BLUE+f"{binance_trandata}"+Fore.RESET)
                trandata = json.loads(order['trandata'])
                if binance_trandata == trandata['executions']:
                    print("+++++++ Both are same +++++")
                else:
                    print("++++++++ Updating the new trandata ++++++")
                    updateBinanceTradeOrder(
                        clientorderid=order['clientorderid'],
                        trandata = json.dumps({"executions":binance_trandata})
                    )
                updateBinanceTradeOrder(
                        clientorderid = order['clientorderid'],
                        action = BinanceTradeAction.CLOSED,
                    )
        except Exception as e:
            print(Fore.RED+f"{str(e)}"+Fore.RESET)
        time.sleep(5)



"""
Pick the stale order with action create
check the last updated time if its if more than 2 mins
make an api call and get the trandata
and push the response to event queue
"""
def processStaleOrders():
    print(f"Process stale order started")
    while True:
        staleOrders = getBinanceTradeOrder(action=BinanceTradeAction.CREATE)
        print(Fore.YELLOW+f"Stale Orders -> {staleOrders}"+Fore.RESET)
        for order in staleOrders:
            orderID = None
            try:
                lastupdatedTime = order['updatedtime']
                currenctTime = datetime.datetime.now()
                diff = currenctTime - lastupdatedTime
                diff_in_minutes = diff.total_seconds() / 60
                
                if diff_in_minutes > 2:
                    binanceOrderDetail = binance.get_order(symbol = order['coinpair'],origClientOrderId = order['clientorderid'])
                    binanceTradeDetail = binance.get_my_trades(symbol = order['coinpair'],orderId = order['exchgorderid'])
                    print(Fore.BLUE+f"{binanceTradeDetail}"+Fore.RESET);
                    binance_trandata = []
                    for trandata in binanceTradeDetail:
                        new_trandata = {
                                        "price":trandata['price'],
                                        "qty":trandata['qty'],
                                        "commission":trandata['commission'],
                                        "commissionAsset":trandata['commissionAsset'],
                                        "tradeId":trandata['id']
                                    }
                        binance_trandata.append(new_trandata)
                    if binanceOrderDetail['status'] in ['FILLED',"PARTIALLY_FILLED","CANCELED","EXPIRED"]:
                        binanceOrderDetail['fills'] = binance_trandata
                    binanceOrderDetail['eventType'] = 'httpEvent'
                    binanceOrderDetail['eventName'] = binanceOrderDetail['status']
                    orderID = binanceOrderDetail['orderId']
                    partitionId = int(binanceOrderDetail["orderId"]) % partitionCount
                    KafkaHelper.producer.send('binance-events',binanceOrderDetail,partition = partitionId,key = b"httpEvent")
                    print(Fore.GREEN+f"process_stale_order - eventName : get order details - data -> {binanceOrderDetail}"+Fore.RESET)
            except Exception as e:
                print(f"Unable to process the stale order - {orderID} due to {str(e)}")
                    

def init_thread(func):
    t = threading.Thread(target=func)
    t.start()

binance = None
partitionCount = None
id = uuid.uuid1()

if __name__ == "__main__":
    # initsocket()
    binance = Binance()
    partitionCount = KafkaHelper.getPartitionCount()
    binance.createUserSocketThread(path="",onmessage=watchBinanceCyptoOrders)
    # init_thread(func=validateOrder)    
    init_thread(func=processStaleOrders)    
    app.run(host="0.0.0.0", port=6091, threaded=True, debug=False)
    
    
    
# qtyExecuted = 0
#                 quoteQty = Decimal(order['qty']) * Decimal(order['price'])
#                 print(Fore.GREEN+f"Binance Order details -> {str(bianceOrderDetail)}"+Fore.RESET)
#                 if order['trandata'] is not None:
#                     trandata = json.loads(order['trandata'])
#                     print(f"Type of trandata -> {type(trandata)}  data {trandata['executions']}")
                    
#                     for transaction in trandata['executions']:
#                         qtyExecuted += Decimal(transaction['qty'])
#                         print(f"Transaction -> {transaction}")
#                     print(f"qtyExecuted  {qtyExecuted}")
#                 #check if the placed qty is same as Executed qty if yes move the status to CLOSED(10)
#                 # check if the cummulativeQuoteQty is same as qty * price 
#                 print(Fore.BLUE+f"QTY PLACED {order['qty']}    QTY EXECUTED {qtyExecuted}"+Fore.RESET)
#                 print(Fore.BLUE+f"QUOTE QTY PLACED {quoteQty}    QUOTE QTY EXECUTED {Decimal(bianceOrderDetail['cummulativeQuoteQty'])}"+Fore.RESET)"