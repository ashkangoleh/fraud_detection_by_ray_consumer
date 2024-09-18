from datetime import datetime
import logging
from app.core.kafka_producer import start_producer
import ray
import json
import pandas as pd
from app.core.fraud_detection import FraudDetection

@ray.remote
class TransactionConsumer:
    def __init__(self):
        
        self.fraud_detector = FraudDetection(
            neo4j_uri="bolt://neo4j:7687",
            neo4j_user="neo4j",
            neo4j_password="password"
        )
        self.consumer = None  

    def _initialize_consumer(self):
        """ Lazily initialize the Kafka Consumer when needed. """
        if self.consumer is None:
            from confluent_kafka import Consumer  
            conf = {
                'bootstrap.servers': 'kafka1:9092,kafka2:9093',
                'group.id': 'fraud_detection_group',
                'auto.offset.reset': 'latest'
            }
            self.consumer = Consumer(conf)
            self.consumer.subscribe(['transactions'])

    def consume_transactions(self):
        """ Function to consume messages from Kafka and process them. """
        self._initialize_consumer()  

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue  
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue

                
                transaction = json.loads(msg.value())
                print(f"Received transaction: {transaction}")

                
                if transaction:
                    self.process_transaction(transaction)
        except Exception as e:
            print(f"Error while consuming transactions: {e}")
        finally:
            
            if self.consumer:
                self.consumer.close()

    def process_transaction(self, transaction):
        df = pd.DataFrame([transaction])

        anomalies = self.fraud_detector.detect_anomalies(df)
        rapid_transactions = self.fraud_detector.temporal_anomaly_detection(df)
        suspicious_users = self.fraud_detector.graph_based_analysis(df)
        
        
        if not anomalies.empty or not rapid_transactions.empty or suspicious_users:
            alert = {
                'transaction_id': transaction['transaction_id'],
                'anomalies': anomalies.to_dict(orient='records') if not anomalies.empty else [],
                'rapid_transactions': rapid_transactions.to_dict(orient='records') if not rapid_transactions.empty else [],
                'suspicious_users': suspicious_users if suspicious_users else []
            }
            
            logging.warning("Alert: " + str({
                'alert': alert,
                'created_at': datetime.now().isoformat()
            }))
                
        else:
            logging.info("No Alert: " + str({
                        'status': 'fraud not found',
                        'anomalies': anomalies.to_dict(orient='records'),
                        'rapid_transactions': rapid_transactions.to_dict(orient='records'),
                        'suspicious_users': suspicious_users,
                        'created_at': datetime.now().isoformat()
                    }))