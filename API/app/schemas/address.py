from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class AddressCreate(BaseModel):
    recipient_name: str = Field(min_length=2, max_length=160)
    phone: str = Field(min_length=1, max_length=25)
    street: str = Field(min_length=1, max_length=220)
    city: str = Field(min_length=1, max_length=100)
    postal_code: str = Field(min_length=1, max_length=15)
    province: str = Field(min_length=1, max_length=100)
    country: str = Field(default="España", max_length=100)
    is_default: bool = False


class AddressUpdate(BaseModel):
    recipient_name: Optional[str] = Field(default=None, min_length=2, max_length=160)
    phone: Optional[str] = Field(default=None, min_length=1, max_length=25)
    street: Optional[str] = Field(default=None, min_length=1, max_length=220)
    city: Optional[str] = Field(default=None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(default=None, min_length=1, max_length=15)
    province: Optional[str] = Field(default=None, min_length=1, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    is_default: Optional[bool] = None


class AddressResponse(BaseModel):
    id: int
    user_id: int
    recipient_name: str
    phone: str
    street: str
    city: str
    postal_code: str
    province: str
    country: str
    is_default: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)