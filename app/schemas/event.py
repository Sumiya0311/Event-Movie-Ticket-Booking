from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str | None = None
    category: str = Field(..., min_length=2, max_length=100)
    location: str = Field(..., min_length=2, max_length=255)
    event_date: datetime
    ticket_price: float = Field(..., ge=0)
    total_tickets: int = Field(..., gt=0)


class EventResponse(BaseModel):
    id: int
    organizer_id: int
    title: str
    description: str | None
    category: str
    location: str
    event_date: datetime
    ticket_price: float
    total_tickets: int
    available_tickets: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)