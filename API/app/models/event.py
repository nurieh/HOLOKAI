
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    DateTime,
    Integer,
    Numeric,
    Enum,
    ForeignKey,
    TIMESTAMP,
    text
)

from app.database.connection import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    title = Column(String(180), nullable=False)
    description = Column(Text, nullable=True)

    event_type = Column(
        Enum("TOURNAMENT", "RELEASE", "CASUAL", "WORKSHOP", "SPECIAL"),
        nullable=False,
        default="TOURNAMENT"
    )

    game_name = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    location = Column(String(220), nullable=False)

    event_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

    max_participants = Column(Integer, nullable=False)
    entry_fee = Column(Numeric(10, 2), nullable=False, default=0.00)

    prize_description = Column(Text, nullable=True)

    status = Column(
        Enum("DRAFT", "PUBLISHED", "FULL", "CANCELLED", "COMPLETED"),
        nullable=False,
        default="DRAFT"
    )

    created_by = Column(
        BigInteger,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP")
    )
