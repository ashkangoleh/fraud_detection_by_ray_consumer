from pydantic import BaseModel
from datetime import datetime

class Transaction(BaseModel):
    transaction_id: str
    user_id: int
    account_id: int
    transaction_type: str
    amount: float
    balance: float
    created_at: str = str(datetime.now())
