from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    location = Column(String(255), nullable=False)

    event_date = Column(DateTime(timezone=True), nullable=False)
    ticket_price = Column(Float, nullable=False, default=0.0)
    total_tickets = Column(Integer, nullable=False)
    available_tickets = Column(Integer, nullable=False)

    status = Column(String(20), default="Draft", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )