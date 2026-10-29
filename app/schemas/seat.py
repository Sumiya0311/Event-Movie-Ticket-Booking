from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SeatCreate(BaseModel):
    screen_id: int = Field(..., gt=0)
    seat_number: str = Field(..., min_length=1, max_length=20)
    seat_type: str = Field(default="Regular", max_length=30)
    row_label: str = Field(..., min_length=1, max_length=10)


class SeatResponse(BaseModel):
    id: int
    screen_id: int
    seat_number: str
    seat_type: str
    row_label: str
    seat_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)