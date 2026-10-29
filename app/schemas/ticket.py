from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TicketResponse(BaseModel):
    id: int
    booking_id: int
    seat_id: int
    ticket_code: str
    qr_code_path: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)