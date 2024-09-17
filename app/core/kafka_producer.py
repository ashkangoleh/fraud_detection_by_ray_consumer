from datetime import datetime
import uuid

import pandas as pd
from confluent_kafka import Producer
import json
import time

import numpy as np

def generate_transaction():
    user_id = np.random.randint(1, 10001)
    account_id = np.random.randint(1, 10001)
    transaction_type = np.random.choice(['deposit', 'withdrawal', 'buy', 'sell'])
    amount = round(np.random.exponential(scale=1000), 2)
    balance = round(np.random.uniform(1000, 100000), 2)
    created_at = datetime.now().isoformat()
    transaction_id = str(uuid.uuid4())

    transaction = {
        'transaction_id': transaction_id,
        'user_id': user_id,
        'account_id': account_id,
        'transaction_type': transaction_type,
        'amount': amount,
        'balance': balance,
        'created_at': created_at
    }

    return transaction

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for transaction {msg.key()}: {err}")
    else:
        print(f"Transaction produced: {msg.key().decode('utf-8')}")
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)
    
def start_producer(msg):
    conf = {'bootstrap.servers': 'kafka1:9092,kafka2:9093'}
    producer = Producer(conf)

    try:
        while True:
            # transaction = generate_transaction()
            key = msg['status']
            value = json.dumps(msg, cls=DateTimeEncoder)
            producer.produce(
                topic='transactions_test',
                key=key,
                value=value,
                callback=delivery_report
            )
            producer.poll(0)
            time.sleep(1)  # Simulate transactions arriving every second
    except KeyboardInterrupt:
        pass
    finally:
        producer.flush()
