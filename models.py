from decimal import Decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Wallet(BaseModel):
    id: int
    username: str
    balance: Optional[Decimal] = None

class Transaction(BaseModel):
    id: int
    from_id: Optional[int]
    to_id: int
    amount: Decimal
    ts: datetime
    comment: str
    type: str
