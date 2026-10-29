from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    booking_id: int = Field(..., gt=0)
    payment_method: str = Field(..., min_length=1, max_length=30)


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    transaction_reference: str | None = None
    razorpay_order_id: str | None = None
    razorpay_payment_id: str | None = None
    payment_method: str
    amount: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)