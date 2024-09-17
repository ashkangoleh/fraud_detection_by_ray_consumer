from kafka import KafkaConsumer
import json
from app.core.ray_processing import process_transaction

def start_consumer():
    consumer = KafkaConsumer(
        'transactions',
        bootstrap_servers=['kafka1:9092','kafka2:9093'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='fraud_detection_group'
    )

    for message in consumer:
        transaction = message.value
        process_transaction.remote(transaction)
