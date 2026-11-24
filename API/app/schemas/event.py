
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EventType(str, Enum):
    TOURNAMENT = "TOURNAMENT"
    RELEASE = "RELEASE"
    CASUAL = "CASUAL"
    WORKSHOP = "WORKSHOP"
    SPECIAL = "SPECIAL"


class EventStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    FULL = "FULL"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class EventBase(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    description: Optional[str] = None

    event_type: EventType = EventType.TOURNAMENT

    game_name: Optional[str] = Field(default=None, max_length=100)
    image_url: Optional[str] = Field(default=None, max_length=500)
    location: str = Field(min_length=1, max_length=220)

    event_date: datetime
    end_date: Optional[datetime] = None

    max_participants: int = Field(gt=0)
    entry_fee: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=10,
        decimal_places=2
    )

    prize_description: Optional[str] = None

    @model_validator(mode="after")
    def validate_event_dates(self):
        if self.end_date is not None and self.end_date <= self.event_date:
            raise ValueError(
                "La fecha de finalización debe ser posterior a la fecha del evento"
            )
        return self


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=180)
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    game_name: Optional[str] = Field(default=None, max_length=100)
    image_url: Optional[str] = Field(default=None, max_length=500)
    location: Optional[str] = Field(default=None, min_length=1, max_length=220)
    event_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_participants: Optional[int] = Field(default=None, gt=0)
    entry_fee: Optional[Decimal] = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2
    )
    prize_description: Optional[str] = None
    status: Optional[EventStatus] = None

    @model_validator(mode="after")
    def validate_event_dates(self):
        if (
            self.event_date is not None
            and self.end_date is not None
            and self.end_date <= self.event_date
        ):
            raise ValueError(
                "La fecha de finalización debe ser posterior a la fecha del evento"
            )
        return self


class EventResponse(EventBase):
    id: int
    status: EventStatus
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
