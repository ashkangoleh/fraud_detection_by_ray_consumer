import numpy as np
import uuid
from datetime import datetime

def generate_transaction():
    user_id = np.random.randint(1, 10001)
    account_id = np.random.randint(1, 10001)
    transaction_type = np.random.choice(['deposit', 'withdrawal', 'buy', 'sell'])
    amount = round(np.random.exponential(scale=1000), 2)
    balance = round(np.random.uniform(1000, 100000), 2)
    created_at = datetime.now(datetime.timezone.utc).isoformat()
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
