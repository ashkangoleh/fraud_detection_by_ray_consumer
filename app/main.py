import logging
import os
from app.core.ray_processing import TransactionConsumer
from fastapi import FastAPI
from app.api.endpoints import router
import ray
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logging.info("Initializing Ray...")
        ray_head_host = os.getenv("RAY_HEAD_HOST", "ray-head")
        ray_address = f'ray://{ray_head_host}:10001'

        logging.info(f"Connecting to Ray cluster at {ray_address}...")

        ray.init(address=ray_address,log_to_driver=True)
        
        if ray.is_initialized():
            logging.info("Ray initialized successfully. Starting consumer...")
        else:
            logging.error("Failed to initialize Ray.")

        consumer = TransactionConsumer.remote()
        consumer.consume_transactions.remote()

        yield

    except Exception as e:
        logging.error(f"Ray initialization failed: {e}")
        raise

    finally:
        # Log Ray shutdown
        logging.info("Shutting down Ray...")
        ray.shutdown()

app = FastAPI(
    title="Fraud Detection API"
    ,
    lifespan=lifespan)

app.include_router(router)


