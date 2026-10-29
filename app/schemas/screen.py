from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ScreenCreate(BaseModel):
    venue_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    screen_type: str = Field(default="Standard", max_length=50)
    total_seats: int = Field(..., gt=0)


class ScreenResponse(BaseModel):
    id: int
    venue_id: int
    name: str
    screen_type: str
    total_seats: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)