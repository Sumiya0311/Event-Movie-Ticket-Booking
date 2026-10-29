from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookingCreate(BaseModel):
    show_id: int = Field(..., gt=0)
    seat_ids: list[int] = Field(..., min_length=1)


class BookingResponse(BaseModel):
    id: int
    user_id: int
    show_id: int
    booking_reference: str
    number_of_tickets: int
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)