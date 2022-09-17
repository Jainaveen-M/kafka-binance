from kafka import KafkaProducer,KafkaConsumer,TopicPartition
import json


def serializer(message):
    return json.dumps(message).encode('utf-8')
def deserializer(message):
    return json.loads(message).decode('utf-8')

class KafkaHelper():       
    producer = KafkaProducer(
        bootstrap_servers=['localhost:29092'],
        value_serializer=serializer
    )
    def getPartitionCount():
        consumer = KafkaConsumer(
            "binance-orders",
            bootstrap_servers='localhost:29092',
        )
        partitions = consumer.partitions_for_topic("binance-orders")
        print(len(partitions))
        return len(partitions)