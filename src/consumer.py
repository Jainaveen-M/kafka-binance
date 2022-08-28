
import json
import threading 
from kafka import KafkaConsumer
from kafka.structs import TopicPartition


TOPIC = 'messages'

def init_thread(func):
    t = threading.Thread(target=func)
    t.start()
 
# def consumer1():
#     while True:
#         consumer = KafkaConsumer(
#             bootstrap_servers='localhost:29092',
#             auto_offset_reset='latest',
#             group_id = 'my-created-consumer-group',
#             auto_commit_interval_ms=1000
#         )
#         print("Before loop")
#         consumer.assign([TopicPartition(TOPIC, 1)])
#         for message in consumer:
#             print(f"consumer 1 {json.loads(message.value)}")
    

# def consumer2():
#     while True:
#         consumer = KafkaConsumer(
#             bootstrap_servers='localhost:29092',
#             auto_offset_reset='latest',
#             group_id = 'my-created-consumer-group2',
#             auto_commit_interval_ms=1000
#         )
#         print("Before loop")
#         consumer.assign([TopicPartition(TOPIC, 2)])
#         for message in consumer:
#             print(f"consumer 2 {json.loads(message.value)}")

# #subscribe to same partition            
# def consumer3():
#     while True:
#         consumer = KafkaConsumer(
#             bootstrap_servers='localhost:29092',
#             auto_offset_reset='latest',
#             group_id = 'my-created-consumer-group',
#             auto_commit_interval_ms=1000
#         )
#         print("Before loop")
#         consumer.assign([TopicPartition(TOPIC, 1)])
#         for message in consumer:
#             print(f"consumer 3 {json.loads(message.value)}")

def consumer():
    while True:
        consumer = KafkaConsumer(
            "trade",
            bootstrap_servers='localhost:29092',
            auto_offset_reset='latest',
            group_id = 'trade-group1',
            auto_commit_interval_ms=1000
        )
        # consumer.assign([TopicPartition("trade", 1)])
        for message in consumer:
            print(f"consumer {json.loads(message.value)}")

if __name__ == '__main__':
    # Kafka Consumer 
    # init_thread(func=consumer1)
    # init_thread(func=consumer2)
    # init_thread(func=consumer3)
    init_thread(func=consumer)

   
