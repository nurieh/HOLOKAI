
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# ESTADOS DEL PEDIDO
# ==========================================

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


# ==========================================
# ARTÍCULOS DEL PEDIDO
# ==========================================

class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    product_name: str
    product_sku: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# CREACIÓN DE PEDIDOS
# ==========================================

class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)

    recipient_name: str = Field(min_length=2, max_length=160)
    phone: str = Field(min_length=1, max_length=25)
    street: str = Field(min_length=1, max_length=220)
    city: str = Field(min_length=1, max_length=100)
    postal_code: str = Field(min_length=1, max_length=15)
    province: str = Field(min_length=1, max_length=100)
    country: str = Field(default="España", max_length=100)


# ==========================================
# ACTUALIZACIÓN DEL ESTADO
# ==========================================

class OrderUpdate(BaseModel):
    status: OrderStatus


# ==========================================
# RESPUESTA DE PEDIDOS
# ==========================================

class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    coupon_id: Optional[int] = None

    recipient_name: str
    phone: str
    street: str
    city: str
    postal_code: str
    province: str
    country: str

    subtotal: Decimal
    discount: Decimal
    shipping_cost: Decimal
    total: Decimal

    status: OrderStatus

    items: list[OrderItemResponse]

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
