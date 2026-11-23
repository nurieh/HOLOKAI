
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ProductImageBase(BaseModel):
    image_url: str = Field(min_length=1, max_length=500)
    is_main: bool = False
    position: int = Field(default=0, ge=0)


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageUpdate(BaseModel):
    image_url: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500
    )
    is_main: Optional[bool] = None
    position: Optional[int] = Field(default=None, ge=0)


class ProductImageResponse(ProductImageBase):
    id: int
    product_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
