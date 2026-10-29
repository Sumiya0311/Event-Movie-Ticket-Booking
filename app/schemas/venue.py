from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VenueCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    address: str
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    capacity: int = Field(..., gt=0)


class VenueResponse(BaseModel):
    id: int
    name: str
    address: str
    city: str
    state: str
    capacity: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)