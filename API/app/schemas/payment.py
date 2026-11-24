from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class PaymentMethod(str, Enum):
    CARD = "CARD"
    PAYPAL = "PAYPAL"
    SIMULATED = "SIMULATED"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REFUNDED = "REFUNDED"


class PaymentCreate(BaseModel):
    order_id: int = Field(gt=0)
    payment_method: PaymentMethod = PaymentMethod.SIMULATED


class PaymentUpdate(BaseModel):
    status: PaymentStatus


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    payment_method: PaymentMethod
    amount: Decimal
    status: PaymentStatus
    transaction_reference: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)