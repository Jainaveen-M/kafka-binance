
import time 
import json 
import random 
from datetime import datetime
from kafka import KafkaProducer,KafkaConsumer
import random 
import string 

user_ids = list(range(1, 6))
recipient_ids = list(range(1, 6))

def getPartitionCount():
    consumer = KafkaConsumer(
        "messages",
        bootstrap_servers='localhost:29092'
    )
    partitions = consumer.partitions_for_topic("messages")
    print(len(partitions))
    return len(partitions)
    
    

def generate_message():
    random_user_id = random.choice(user_ids)

    recipient_ids_copy = recipient_ids.copy()

    recipient_ids_copy.remove(random_user_id)
    random_recipient_id = random.choice(recipient_ids_copy)
    message = ''.join(random.choice(string.ascii_letters) for i in range(32))
    return {
        'user_id': random_user_id,
        'recipient_id': random_recipient_id,
        'message': message
    },random_user_id

def serializer(message):
    return json.dumps(message).encode('utf-8')

producer = KafkaProducer(
    bootstrap_servers=['localhost:29092'],
    value_serializer=serializer
)
if __name__ == '__main__':
    partitionCount =  getPartitionCount()
    while True:
        # Generate a message
        dummy_message,userId = generate_message()
        
        partitionId = userId%partitionCount
        
        print(f'Producing message @ {datetime.now()} | Message = {str(dummy_message)}  | PartitionID = {partitionId}')
        
        producer.send('messages', dummy_message,partition=partitionId)
        
        # Sleep for a random number of seconds
        # time_to_sleep = random.randint(1, 11)
        time.sleep(2)