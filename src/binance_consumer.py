import threading
import uuid
from DataController.kafka import KafkaConsumer, KafkaHelper,TopicPartition
import json
from DataController.binance import createBinanceTradeOrder, getBinanceTradeOrder,updateBinanceTradeOrder
from DataModel.binance import BinanceTradeOrderStatus
from colorama import Fore

from binance import Binance

def processOrderConsumer(partitionID=None):
    print(f"Process Order Consumer Started for partitionID - {partitionID}")
    while True:
        consumer = KafkaConsumer(
            "binance-orders",
            bootstrap_servers='localhost:29092',
            auto_offset_reset='latest',
            group_id = "binance-orders-group",
            auto_commit_interval_ms=1000
        )
        # consumer.assign([TopicPartition("binance-orders", partitionID)])
        for message in consumer:
            print(f"type - {type(message.value)} data -> {message.value}")
            message = json.loads(message.value)
            if message['action'] == "CREATE_ORDER":
                createBinanceTradeOrder(
                    id = message["id"],
                    price = message['price'], 
                    qty = message['qty'], 
                    status = BinanceTradeOrderStatus.NEW, 
                    ordertype = message['ordertype'],
                    trantype =  message['trantype'],
                    coinpair = message['coinpair'], 
                    exchgid = 1
                )
                binanceOrder = binance.create_order(
                    symbol = message['coinpair'],
                    side = "BUY" if message['trantype'] == 0 else "SELL",
                    type = "LIMIT",
                    timeInForce = "GTC",
                    quantity = message['qty'],
                    price = message['price']
                )
                updateBinanceTradeOrder(
                    id = message["id"],
                    clientorderid = binanceOrder['clientOrderId'],
                    exchgorderid = binanceOrder['orderId'],
                    status = BinanceTradeOrderStatus.ORDER_PLACED
            
                )
                binanceOrder['id'] = message["id"]
                binanceOrder['eventType'] = 'httpEvent'
                binanceOrder['action'] = binanceOrder['status']
                orderID = binanceOrder['orderId']
                partitionId = orderID % partitionCount
                KafkaHelper.producer.send('binance-events',binanceOrder,partition = partitionId,key = b"httpEvent")
                print(Fore.GREEN+f"Consumer_process_order - action : CREATE_ORDER - data -> {binanceOrder}"+Fore.RESET)
                
            
def processEventConsumer(partitionID=None):
    print(f"Process Event Consumer Started for partitionID - {partitionID}")
    while True:
        consumer = KafkaConsumer(
            "binance-events",
            bootstrap_servers='localhost:29092',
            auto_offset_reset='latest',
            group_id = "binance-events-group",
            auto_commit_interval_ms=1000    
        )
        # consumer.assign([TopicPartition("binance-events", partitionID)])
        for message in consumer:
            print(f"type - {type(message.value)} data -> {message.value}")
            message = json.loads(message.value)
            print(Fore.GREEN+f"Order data -> {message}")
            if message['eventType'] == "httpEvent":
                if message['action'] == "NEW": 
                    print(Fore.YELLOW+"============================================ NEW ==================================================")
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
                # updateBinanceTradeOrder(
                #     id = message['id'],
                #     clientorderid=message['clientOrderId'],
                #     exchgorderid = message['orderId'],
                #     status= BinanceTradeOrderStatus.ORDER_PLACED
                # ) 
                 
                if message['status'] == 'PARTIALLY_FILLED':
                    print(Fore.YELLOW+"============================================ PARTIALLY_FILLED =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
                if message['status'] == 'FILLED':
                    print(Fore.YELLOW+"============================================ FILLED =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
                if message['status'] == 'PENDING_CANCEL':
                    print(Fore.YELLOW+"============================================ PENDING_CANCEL =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
                if message['status'] == "CANCELED":
                    print(Fore.YELLOW+"============================================ CANCELED =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)    
                if message['status'] == "REJECTED":
                    print(Fore.YELLOW+"============================================ REJECTED =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
                if message['status'] == "TRADE":
                    print(Fore.YELLOW+"============================================ TRADE =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
                if message['status'] == 'EXPIRED':
                    print(Fore.YELLOW+"============================================ EXPIRED =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
            if  message['eventType'] == "wsocketEvent":
                if message['X'] == "NEW":
                    print(Fore.YELLOW+"============================================ NEW =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
                    # updateBinanceTradeOrder(
                    #     clientorderid=message['c'],
                    #     exchgorderid = message['i'],
                    #     status= BinanceTradeOrderStatus.FULLY_FILLED,
                    #     isClientIdAvailable = True,
                    # )
                if message['X'] == 'PARTIALLY_FILLED':
                    print(Fore.YELLOW+"============================================ PARTIALLY_FILLED =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
                if message['X'] == 'FILLED':
                    print(Fore.YELLOW+"============================================ FILLED =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
                if message['X'] == 'PENDING_CANCEL':
                    print(Fore.YELLOW+"============================================ PENDING_CANCEL =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
                if message['X'] == "CANCELED":
                    print(Fore.YELLOW+"============================================ CANCELED =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)    
                if message['X'] == "REJECTED":
                    print(Fore.YELLOW+"============================================ REJECTED =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
                if message['X'] == "TRADE":
                    print(Fore.YELLOW+"============================================ TRADE =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
                if message['X'] == 'EXPIRED':
                    print(Fore.YELLOW+"============================================ EXPIRED =================================================="+Fore.RESET)
                    print(Fore.GREEN+f"Consumer_process_event eventType - {message['eventType']} - action : {message['action']} - data -> {message}"+Fore.RESET)
                     
        
def init_thread(func):
    t = threading.Thread(target=func)
    t.start()

binance = None
partitionCount = None
id = uuid.uuid1()

if __name__ == "__main__":
    binance = Binance()
    partitionCount = KafkaHelper.getPartitionCount()
    init_thread(func=processOrderConsumer)
    # init_thread(func=processOrderConsumer)
    # init_thread(func=processOrderConsumer)
    init_thread(func=processEventConsumer)
    # init_thread(func=processEventConsumer)
    # init_thread(func=processEventConsumer)