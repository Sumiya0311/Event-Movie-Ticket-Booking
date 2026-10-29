from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ShowCreate(BaseModel):
    event_id: int = Field(..., gt=0)
    screen_name: str = Field(..., min_length=1, max_length=100)
    show_date: datetime
    start_time: datetime
    end_time: datetime


class ShowResponse(BaseModel):
    id: int
    event_id: int
    screen_name: str
    show_date: datetime
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)