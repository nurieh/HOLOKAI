
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    title: str = Field(..., max_length=180)
    description: Optional[str] = None

    event_type: str = "TOURNAMENT"

    game_name: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    location: str = Field(..., max_length=220)

    event_date: datetime
    end_date: Optional[datetime] = None

    max_participants: int = Field(..., gt=0)
    entry_fee: Decimal = Field(default=Decimal("0.00"), ge=0)

    prize_description: Optional[str] = None


class EventCreate(EventBase):
    created_by: int


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=180)
    description: Optional[str] = None
    event_type: Optional[str] = None
    game_name: Optional[str] = None
    image_url: Optional[str] = None
    location: Optional[str] = None
    event_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_participants: Optional[int] = Field(None, gt=0)
    entry_fee: Optional[Decimal] = Field(None, ge=0)
    prize_description: Optional[str] = None
    status: Optional[str] = None


class EventResponse(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime
