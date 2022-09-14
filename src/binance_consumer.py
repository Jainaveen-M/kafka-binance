import datetime
import logging
import threading
import time
import uuid
from xmlrpc.client import DateTime
from DataController.kafka import KafkaConsumer, KafkaHelper,TopicPartition
import json
from DataController.binance import createBinanceTradeOrder, getBinanceTradeOrder, getVerifiedOrders,updateBinanceTradeOrder, updateVerifiedOrders
from DataModel.binance import BinanceTradeAction, BinanceTradeOrderStatus, TradeOrderVerifiedStatus
from colorama import Fore

from binance import Binance

                 

def processOrderConsumer(partitionID=None):
    print(f"Process Order Consumer Started for partitionID - {partitionID}")
    while True:
        consumer = KafkaConsumer(
            bootstrap_servers='localhost:29092',
            auto_offset_reset='latest',
            group_id = "binance-orders-group",
            enable_auto_commit= False
        )
        consumer.assign([TopicPartition("binance-orders", partitionID)])
        for message in consumer:
            print(Fore.RED+f"type - {type(message.value)} data -> {message.value}"+Fore.RESET)
            message = json.loads(message.value)
            binanceOrder = None,
            orderID = None
            try:
                if message['eventName'] == "CREATE_ORDER":
                    print(f"Message from consumer -> {message}")
                    createBinanceTradeOrder(
                        ctid = message['clientid'],
                        clientorderid = str(message["orderid"]),
                        price = message['price'], 
                        qty = message['amount'], 
                        status = BinanceTradeOrderStatus.NEW, 
                        ordertype = message['ordertype'],
                        trantype =  message['trantype'],
                        coinpair = message['coinpair'], 
                        exchgid = 1,
                        action = BinanceTradeAction.CREATE,
                        updatedtime = datetime.datetime.now()
                    )
                    consumer.commit()
                    binanceOrder = binance.create_order(
                        newClientOrderId = str(message['orderid']),
                        symbol = message['coinpair'],
                        side = "BUY" if message['trantype'] == 0 else "SELL",
                        type = "LIMIT",
                        timeInForce = "GTC",
                        quantity = message['amount'],
                        price = message['price']
                    )
                    binanceOrder['eventType'] = 'httpEvent'
                    binanceOrder['eventName'] = binanceOrder['status']
                    orderID = binanceOrder['orderId']
                    partitionId = int(message["orderid"]) % partitionCount
                    KafkaHelper.producer.send('binance-events',binanceOrder,partition = partitionId,key = b"httpEvent")
                    print(Fore.GREEN+f"Consumer_process_order - eventName : CREATE_ORDER - data -> {binanceOrder}"+Fore.RESET)
                
                if message['eventName'] == "PLACE_ORDER":
                    consumer.commit()
                    binanceOrder = binance.create_order(
                        newClientOrderId = str(message['orderid']),
                        symbol = message['coinpair'],
                        side = "BUY" if message['trantype'] == 0 else "SELL",
                        type = "LIMIT",
                        timeInForce = "GTC",
                        quantity = message['amount'],
                        price = message['price']
                    )
                    binanceOrder['eventType'] = 'httpEvent'
                    binanceOrder['eventName'] = binanceOrder['status']
                    orderID = binanceOrder['orderId']
                    partitionId = int(message["orderid"]) % partitionCount
                    KafkaHelper.producer.send('binance-events',binanceOrder,partition = partitionId,key = b"httpEvent")
                    print(Fore.GREEN+f"Consumer_process_order - eventName : PLACE_ORDER - data -> {binanceOrder}"+Fore.RESET)
                    
                    
                if message['eventName'] == "CANCEL_ORDER":
                    consumer.commit()
                    print(f"Message from consumer -> {message}")
                    binanceOrder = binance.cancel_order(
                        orderId =  message['orderId'],
                        symbol = message['coinpair'],
                        origClientOrderId = message['clientorderid']
                    )
                    binanceOrder['eventType'] = 'httpEvent'
                    binanceOrder['eventName'] = binanceOrder['status']
                    orderID = binanceOrder['orderId']
                    partitionId = int(message["orderid"]) % partitionCount
                    KafkaHelper.producer.send('binance-events',binanceOrder,partition = partitionId,key = b"httpEvent")
                    print(Fore.GREEN+f"Consumer_process_order - eventName : CANCEL_ORDER - data -> {binanceOrder}"+Fore.RESET)
                
                if message['eventName'] == "REJECT_ORDER":
                    consumer.commit()
                    print(f"Message from consumer -> {message}")
                    updateBinanceTradeOrder(
                            clientorderid = message['orderid'],
                            status= BinanceTradeOrderStatus.INTERNAL_REJECT
                        )   
                    print(Fore.GREEN+f"Consumer_process_order - eventName : REJECT_ORDER - data -> { message['orderid']}"+Fore.RESET)
                
            except Exception as e:
                print(f"Unable to process order {orderID} due to {str(e)}")
                
            
def processEventConsumer(partitionID=None):
    print(f"Process Event Consumer Started for partitionID - {partitionID}")
    while True:
        consumer = KafkaConsumer(
            bootstrap_servers='localhost:29092',
            auto_offset_reset='latest',
            group_id = "binance-events-group",
            enable_auto_commit= False
        )
        consumer.assign([TopicPartition("binance-events", partitionID)])
        orderID = None
        for message in consumer:
            consumer.commit()
            print(f"type - {type(message.value)} data -> {message.value}")
            message = json.loads(message.value)
            print(Fore.YELLOW+f"Order data -> {message}")
            errorMsg = None
            try:
                if message['eventType'] == "httpEvent":
                    orderID = message['clientOrderId']
                    if message['status'] == "NEW": 
                        print(Fore.YELLOW+"============================================ NEW ==================================================")
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        #update only if the exchange order id is not updated 
                        updateBinanceTradeOrder(
                            clientorderid = message['clientOrderId'],
                            exchgorderid = message['orderId'],
                            status= BinanceTradeOrderStatus.ORDER_PLACED
                        ) 
                    if message['status'] == 'PARTIALLY_FILLED':
                        print(Fore.YELLOW+"============================================ PARTIALLY_FILLED =================================================="+Fore.RESET)
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        trandata = {
                            "executions": message['fills']
                        }
                        updateBinanceTradeOrder(
                            clientorderid = message['clientOrderId'],
                            trandata= json.dumps(trandata),
                            exchgorderid = message['orderId'],
                            status= BinanceTradeOrderStatus.PARTIALLY_FILLED
                        ) 
                    if message['status'] == 'FILLED':
                        print(Fore.YELLOW+"============================================ FILLED =================================================="+Fore.RESET)
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        trandata = {
                            "executions": message['fills']
                        }
                        updateBinanceTradeOrder(
                            clientorderid = message['clientOrderId'],
                            trandata= json.dumps(trandata),
                            exchgorderid = message['orderId'],
                            status= BinanceTradeOrderStatus.FULLY_FILLED,
                            action = BinanceTradeAction.TO_CLOSE
                        ) 
                    if message['status'] == 'PENDING_CANCEL':
                        print(Fore.YELLOW+"============================================ PENDING_CANCEL =================================================="+Fore.RESET)
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        # updateBinanceTradeOrder(
                        #     clientorderid = message['origClientOrderId'],
                        #     status= BinanceTradeOrderStatus.PENDING_CANCEL
                        # ) 
                    if message['status'] == "CANCELED":
                        print(Fore.YELLOW+"============================================ CANCELED =================================================="+Fore.RESET)
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        order = getBinanceTradeOrder(clientorderid=message['origClientOrderId'])
                        status = None
                        orderID = message['origClientOrderId']
                        if order['status'] == BinanceTradeOrderStatus.ORDER_PLACED:
                            status = BinanceTradeOrderStatus.ORDER_PLACED_AND_CANCELLED
                        elif order['status'] == BinanceTradeOrderStatus.PARTIALLY_FILLED:
                            status = BinanceTradeOrderStatus.PARTIALLY_FILLED_AND_CANCELLED
                        else:
                            errorMsg = "Unable to cancel the order due to invalid status"
                            raise Exception(errorMsg)
                        updateBinanceTradeOrder(
                            clientorderid = message['origClientOrderId'],
                            status = status,
                            action = BinanceTradeAction.TO_CLOSE
                        )                         
                    if message['status'] == "REJECTED":
                        print(Fore.YELLOW+"============================================ REJECTED =================================================="+Fore.RESET)
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        updateBinanceTradeOrder(
                            clientorderid = message['clientOrderId'],
                            status= BinanceTradeOrderStatus.REJECTED
                        )             
                    if message['status'] == 'EXPIRED':
                        print(Fore.YELLOW+"============================================ EXPIRED =================================================="+Fore.RESET)
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        status = None
                        if order['status'] == BinanceTradeOrderStatus.ORDER_PLACED:
                            status = BinanceTradeOrderStatus.ORDER_PLACED_AND_EXPIRED
                        elif order['status'] == BinanceTradeOrderStatus.PARTIALLY_FILLED:
                            status = BinanceTradeOrderStatus.PARTIALLY_FILLED_AND_EXPIRED
                        else:
                            errorMsg = "Unable to cancel the order due to invalid status"
                            raise Exception(errorMsg)
                        updateBinanceTradeOrder(
                            clientorderid = message['clientOrderId'],
                            status= status,
                            action = BinanceTradeAction.TO_CLOSE
                        ) 
                if  message['eventType'] == "wsocketEvent":
                    orderID = message['c']
                    if message['X'] == "NEW":
                        print(Fore.YELLOW+"============================================ NEW =================================================="+Fore.RESET)
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        #update only if the exchange order id is not updated 
                        updateBinanceTradeOrder(
                            clientorderid = message['c'],
                            exchgorderid = message['i'],
                            status= BinanceTradeOrderStatus.ORDER_PLACED
                        ) 
                    if message['X'] == 'PARTIALLY_FILLED':
                        print(Fore.YELLOW+"============================================ PARTIALLY_FILLED =================================================="+Fore.RESET)
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        trandata = None
                        new_trandata = {
                                    "price":message['L'],
                                    "qty":message['l'],
                                    "commission":message['n'],
                                    "commissionAsset":message['N'],
                                    "tradeId":message['t']
                                }
                        order = getBinanceTradeOrder(clientorderid=message['c'])
                        if order['trandata'] is not None:
                            trandata = json.loads(order['trandata'])
                            if new_trandata not in trandata['executions']:
                                trandata['executions'].append(new_trandata)
                           
                        else:
                            trandata = {
                                "executions": [
                                    new_trandata
                                ]
                            }
                        print(f"Trandata -> {trandata}")
                        updateBinanceTradeOrder(
                            clientorderid = message['c'],
                            trandata= json.dumps(trandata),
                            exchgorderid = message['i'],
                            status= BinanceTradeOrderStatus.PARTIALLY_FILLED
                        ) 
                    if message['X'] == 'FILLED':
                        print(Fore.YELLOW+"============================================ FILLED =================================================="+Fore.RESET)
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        new_trandata = {
                                    "price":message['L'],
                                    "qty":message['l'],
                                    "commission":message['n'],
                                    "commissionAsset":message['N'],
                                    "tradeId":message['t']
                                }
                        order = getBinanceTradeOrder(clientorderid=message['c'])
                        if order['trandata'] is not None:
                            trandata = json.loads(order['trandata'])
                            if new_trandata not in trandata['executions']:
                                trandata['executions'].append(new_trandata)
                        else:
                            trandata = {
                                "executions": [
                                    new_trandata
                                ]
                            }
                        print(f"Trandata -> {trandata}")
                        updateBinanceTradeOrder(
                            clientorderid = message['c'],
                            trandata= json.dumps(trandata),
                            exchgorderid = message['i'],
                            status= BinanceTradeOrderStatus.FULLY_FILLED,
                            action = BinanceTradeAction.TO_CLOSE
                        ) 
                    if message['X'] == 'PENDING_CANCEL':
                        print(Fore.YELLOW+"============================================ PENDING_CANCEL =================================================="+Fore.RESET)
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        # updateBinanceTradeOrder(
                        #     clientorderid = message['C'],
                        #     exchgorderid = message['i'],
                        #     status= BinanceTradeOrderStatus.PENDING_CANCEL
                        # ) 
                    if message['X'] == "CANCELED":
                        print(Fore.YELLOW+"============================================ CANCELED =================================================="+Fore.RESET)
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        order = getBinanceTradeOrder(clientorderid=message['C'])
                        status = None
                        orderID = message['C']
                        if order['status'] == BinanceTradeOrderStatus.ORDER_PLACED:
                            status = BinanceTradeOrderStatus.ORDER_PLACED_AND_CANCELLED
                        elif order['status'] == BinanceTradeOrderStatus.PARTIALLY_FILLED:
                            status = BinanceTradeOrderStatus.PARTIALLY_FILLED_AND_CANCELLED
                        else:
                            errorMsg = "Unable to cancel the order due to invalid status"
                            raise Exception(errorMsg)
                        updateBinanceTradeOrder(
                            clientorderid = message['C'],
                            status = status,
                            action = BinanceTradeAction.TO_CLOSE
                        )    
                    if message['X'] == "REJECTED":
                        print(Fore.YELLOW+"============================================ REJECTED =================================================="+Fore.RESET)
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        updateBinanceTradeOrder(
                            clientorderid = message['c'],
                            status= BinanceTradeOrderStatus.REJECTED
                        )
                    if message['X'] == 'EXPIRED':
                        print(Fore.YELLOW+"============================================ EXPIRED =================================================="+Fore.RESET)
                        print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - eventName : {message['eventName']} - data -> {message}"+Fore.RESET)
                        status = None
                        if order['status'] == BinanceTradeOrderStatus.ORDER_PLACED:
                            status = BinanceTradeOrderStatus.ORDER_PLACED_AND_EXPIRED
                        elif order['status'] == BinanceTradeOrderStatus.PARTIALLY_FILLED:
                            status = BinanceTradeOrderStatus.PARTIALLY_FILLED_AND_EXPIRED
                        else:
                            errorMsg = "Unable to cancel the order due to invalid status"
                            raise Exception(errorMsg)
                        updateBinanceTradeOrder(
                            clientorderid = message['c'],
                            status=status,
                            action = BinanceTradeAction.TO_CLOSE
                        )
                
            except Exception as e:
                msg = errorMsg if errorMsg else str(e)
                print(f"Unable to process event for order {orderID} due to {msg}")
                
# def init_thread(func):
#     t = threading.Thread(target=func)
#     t.start()
    
def init_thread(func, args=None):
    if args is None:
        args = ()
    t = threading.Thread(target=func, args=args)
    t.start()

binance = None
partitionCount = None
id = uuid.uuid1()




if __name__ == "__main__":
    binance = Binance()
    partitionCount = KafkaHelper.getPartitionCount()
    
    # order queue
    init_thread(func=processOrderConsumer,args=(0,))
    init_thread(func=processOrderConsumer,args=(1,))
    init_thread(func=processOrderConsumer,args=(2,))
    
    #event queue
    init_thread(func=processEventConsumer,args=(0,))
    init_thread(func=processEventConsumer,args=(1,))
    init_thread(func=processEventConsumer,args=(2,))