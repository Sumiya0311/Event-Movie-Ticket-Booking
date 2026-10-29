import os
import hmac
import hashlib

import razorpay
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.security import get_current_user
from app.models.payment import Payment
from app.models.booking import Booking
from app.schemas.payment import PaymentCreate, PaymentResponse


router = APIRouter(prefix="/payments", tags=["Payments"])


def get_razorpay_client():
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")

    if not key_id or not key_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Razorpay is not configured",
        )

    return razorpay.Client(auth=(key_id, key_secret))


class PaymentVerification(BaseModel):
    razorpay_order_id: str = Field(..., min_length=1)
    razorpay_payment_id: str = Field(..., min_length=1)
    razorpay_signature: str = Field(..., min_length=1)


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    booking = (
        db.query(Booking)
        .filter(
            Booking.id == payment_data.booking_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending bookings can be paid",
        )

    if booking.total_amount is None or booking.total_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking amount must be greater than zero",
        )

    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.booking_id == booking.id,
            Payment.status == "Pending",
        )
        .first()
    )

    # Reuse an existing Razorpay order instead of creating a duplicate.
    if existing_payment and existing_payment.razorpay_order_id:
        return existing_payment

    client = get_razorpay_client()

    try:
        order = client.order.create(
            data={
                "amount": int(round(booking.total_amount * 100)),
                "currency": "INR",
                "receipt": f"booking_{booking.id}",
            }
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to create Razorpay order. Please try again.",
        )

    # Recover the existing pending record if its order ID is missing.
    if existing_payment:
        payment = existing_payment
        payment.razorpay_order_id = order["id"]
        payment.razorpay_payment_id = None
        payment.transaction_reference = None
        payment.payment_method = payment_data.payment_method
        payment.amount = booking.total_amount
    else:
        payment = Payment(
            booking_id=booking.id,
            transaction_reference=None,
            razorpay_order_id=order["id"],
            razorpay_payment_id=None,
            payment_method=payment_data.payment_method,
            amount=booking.total_amount,
            status="Pending",
        )
        db.add(payment)

    try:
        db.commit()
        db.refresh(payment)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save payment record",
        )

    return payment


@router.post("/verify")
def verify_payment(
    verification: PaymentVerification,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    payment = (
        db.query(Payment)
        .join(Booking, Payment.booking_id == Booking.id)
        .filter(
            Payment.razorpay_order_id == verification.razorpay_order_id,
            Payment.status == "Pending",
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending payment not found",
        )

    secret = os.getenv("RAZORPAY_KEY_SECRET")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Razorpay is not configured",
        )

    message = (
        f"{verification.razorpay_order_id}|"
        f"{verification.razorpay_payment_id}"
    ).encode("utf-8")

    expected_signature = hmac.new(
        secret.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        expected_signature,
        verification.razorpay_signature,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Razorpay payment signature",
        )

    try:
        client = get_razorpay_client()
        razorpay_payment = client.payment.fetch(
            verification.razorpay_payment_id
        )

        if razorpay_payment.get("order_id") != verification.razorpay_order_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment does not match the Razorpay order",
            )

        if razorpay_payment.get("status") != "captured":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment has not been captured",
            )

        if int(razorpay_payment.get("amount", -1)) != int(
            round(payment.amount * 100)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment amount does not match the booking",
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to verify payment with Razorpay",
        )

    booking = (
        db.query(Booking)
        .filter(Booking.id == payment.booking_id)
        .with_for_update()
        .first()
    )

    if booking is None or booking.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking is no longer pending",
        )

    payment.razorpay_payment_id = verification.razorpay_payment_id
    payment.transaction_reference = verification.razorpay_payment_id
    payment.status = "Success"
    booking.status = "Confirmed"

    try:
        db.commit()
        db.refresh(payment)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save verified payment",
        )

    return {
        "message": "Payment verified successfully",
        "payment": PaymentResponse.model_validate(payment),
    }


@router.get("/", response_model=list[PaymentResponse])
def get_payments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        db.query(Payment)
        .join(Booking, Payment.booking_id == Booking.id)
        .filter(Booking.user_id == current_user.id)
        .order_by(Payment.id.desc())
        .all()
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    payment = (
        db.query(Payment)
        .join(Booking, Payment.booking_id == Booking.id)
        .filter(
            Payment.id == payment_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment