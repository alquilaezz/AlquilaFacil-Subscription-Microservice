from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ---------- Plan ----------

class PlanOut(BaseModel):
    id: int
    name: str
    service: str
    price: float

    class Config:
        orm_mode = True

# ---------- Subscription ----------

class SubscriptionCreate(BaseModel):
    plan_id: int
    voucher_image_url: Optional[str] = None
    subscription_status_id: Optional[int] = None  # si no mandan, usamos "PENDING"

class SubscriptionUpdate(BaseModel):
    plan_id: Optional[int] = None
    voucher_image_url: Optional[str] = None
    subscription_status_id: Optional[int] = None

class SubscriptionOut(BaseModel):
    id: int
    user_id: int
    plan_id: int
    subscription_status_id: int
    voucher_image_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ---------- Invoice ----------

class InvoiceCreate(BaseModel):
    amount: float
    subscription_id: int
    date: Optional[datetime] = None  # si viene None, usamos utcnow en el modelo

class InvoiceOut(BaseModel):
    id: int
    amount: float
    date: datetime
    subscription_id: int

    class Config:
        orm_mode = True
