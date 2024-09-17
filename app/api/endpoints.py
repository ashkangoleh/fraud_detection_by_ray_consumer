from fastapi import APIRouter
from app.models.transaction import Transaction
from confluent_kafka import Producer
import json

router = APIRouter()

conf = {'bootstrap.servers': 'kafka1:9092,kafka2:9093'}
producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for transaction {msg.key()}: {err}")
    else:
        print(f"Transaction produced via API: {msg.key().decode('utf-8')}")

@router.post("/detect_fraud")
async def detect_fraud(transaction: Transaction):
    key = transaction.transaction_id
    value = json.dumps(transaction.dict())
    producer.produce(
        topic='transactions',
        key=key,
        value=value,
        callback=delivery_report
    )
    producer.poll(0)
    return {"status": "Transaction received and will be processed"}
