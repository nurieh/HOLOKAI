
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# Estados permitidos para los productos
class ProductStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    OUT_OF_STOCK = "OUT_OF_STOCK"


# Campos comunes de los productos
class ProductBase(BaseModel):
    category_id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=180)
    sku: str = Field(min_length=1, max_length=80)
    description: Optional[str] = None
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    status: ProductStatus = ProductStatus.ACTIVE
    is_featured: bool = False
    is_new: bool = False


# Crear producto
class ProductCreate(ProductBase):
    pass


# Modificar producto
class ProductUpdate(BaseModel):
    category_id: Optional[int] = Field(default=None, gt=0)
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=180
    )
    sku: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=80
    )
    description: Optional[str] = None
    price: Optional[Decimal] = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2
    )
    stock: Optional[int] = Field(default=None, ge=0)
    status: Optional[ProductStatus] = None
    is_featured: Optional[bool] = None
    is_new: Optional[bool] = None


# Respuesta de la API
class ProductResponse(ProductBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
