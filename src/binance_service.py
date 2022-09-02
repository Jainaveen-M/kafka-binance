import uuid
from decimal import Decimal
from flask import Flask,jsonify,request
import json,threading
from DataController.kafka import KafkaHelper
from binance import Binance
from colorama import Fore
from DataController.binance import getBinanceTradeOrder
from DataModel.binance import BinanceTradeOrderStatus
    
 
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

@app.route("/gettradehistory",methods=["GET"])   
def gettradehistory():
    binance = Binance()
    result = binance.get_all_orders(symbol="TRXUSDT")
    return jsonify({"status":"success","message":result})


@app.route("/getmytrades/<symbol>",methods=["POST"])   
def getmytrades(symbol):
    binance = Binance()
    result = binance.get_my_trades(symbol=symbol) # we can mention the fromid to get the trade history
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
        orderID = uuid.uuid4()
        order = {
            "id":str(orderID),
            "price":request_data.get("price"),
            "qty":request_data.get("qty"),
            "status": BinanceTradeOrderStatus.NEW,
            "ordertype":1, # 1 - LIMIT order  0 - Market order
            "trantype": 0 if request_data.get("trantype") == "BUY" else 1, # 0 - buy 1 - sell
            "coinpair":request_data.get("coinpair"),
            "exchgid":1,
            "event":"httpEvent",
            "action":"CREATE_ORDER"
        }
        KafkaHelper.producer.send('binance-orders',order,key = b"httpEvent")
        print(f"Order create successfully order - {order}")
    except Exception as e:
        print(str(e))
        return jsonify({"status":"error","message":str(e)})
    return jsonify({"status":"order created successfully","message":order})


# this will cancel the order and send the response to kafka producer

@app.route("/cancel/order/<orderId>",methods=["POST"])
def cancelOrder(orderId):
    binanceOrder = None
    try:
        order = getBinanceTradeOrder(crypto_order_id=orderId)
        print(f"Cancel Order -> {order}")
        binanceOrder = binance.cancel_order(
            orderId = order[0]['exchgorderid'],
            symbol = order[0]['coinpair']
        )
        orderId = binanceOrder['orderId']
        binanceOrder['eventType'] = 'httpEvent'
        binanceOrder['action'] = "CANCELED"
        partitionId = orderId % partitionCount
        print(Fore.YELLOW+f"Producer cancel order -> {binanceOrder}"+Fore.RESET)
        KafkaHelper.producer.send('binance-orders',binanceOrder,partition = partitionId,key = b"httpEvent")
    except Exception as e:
        print(str(e))
    return jsonify({"status":"order cancelled successfully","message":binanceOrder})


#This will take order from cryptoorders and place order in binance and make the order as processed
# @app.route("/process/order",methods=["GET"])
# def process_order():
#     result = []
#     try:
        # activeOrders = getActiveOrders(status=1)
        # for order in activeOrders:
        #     binanceOrder = binance.create_order(
        #         symbol=order['coinpair'],
        #         side = "BUY" if order['trantype'] == 0 else "SELL",
        #         type = "LIMIT",
        #         timeInForce = "GTC",
        #         quantity = order['qty'],
        #         price = order['price']
        #     )            
        #     createBinanceTradeOrder(
        #         clientid = binanceOrder['clientOrderId'],
        #         price = binanceOrder['price'], 
        #         qty = binanceOrder['origQty'], 
        #         status = BinanceTradeOrderStatus.FULLY_FILLED if binanceOrder['status'] == "FILLED" else BinanceTradeOrderStatus.ORDER_PLACED, 
        #         ordertype = 1 if binanceOrder['type'] == "LIMIT" else 0, 
        #         trantype = 0 if binanceOrder['side'] == "BUY" else 1, 
        #         coinpair = binanceOrder['symbol'], 
        #         exchgid = 1, 
        #         exchgorderid = binanceOrder['orderId'], 
        #         trandata = json.dumps(binanceOrder['fills']),
        #         crypto_order_id = order['id']
        #     )
        #     updateCryptoOrder(
        #         id = order['id'],
        #         status = CryptoOrderStatus.PROCESSED
        #     )
        #     orderId = binanceOrder['orderId']
        #     partitionId = orderId % partitionCount
        #     binanceOrder['eventType'] = 'httpEvent'
        #     binanceOrder['action'] = "NEW"
        #     print(Fore.YELLOW+f"Producer process order -> {binanceOrder}"+Fore.RESET)
        #     Kafka.producer.send('binance-orders',binanceOrder,partition = partitionId,key = b"httpEvent")
        #     print("event produced")
        #     if  binanceOrder['status'] == 'PARTIALLY_FILLED':
        #         print("PARTIALLY_FILLED")
        #     if binanceOrder['status'] == 'FILLED':
        #         print("FILLED")
        #     result.append(binanceOrder)
    # except Exception as e:
    #     return jsonify({"status":"error","message":str(e)})
    # return jsonify({"status":"order created successfully","message":result})


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
            message['action'] = message['x']
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
         
        
def init_thread(func,partitionID):
    t = threading.Thread(target=func,args=(partitionID))
    t.daemon = True
    t.start()

binance = None
partitionCount = None
id = uuid.uuid1()

if __name__ == "__main__":
    # initsocket()
    binance = Binance()
    partitionCount = KafkaHelper.getPartitionCount()
    binance.createUserSocketThread(path="",onmessage=watchBinanceCyptoOrders)
    app.run(host="0.0.0.0", port=6091, threaded=True, debug=False)