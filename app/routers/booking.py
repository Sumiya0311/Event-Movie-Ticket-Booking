import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.security import get_current_user
from app.models.booking import Booking
from app.models.show import Show
from app.models.event import Event
from app.models.seat import Seat
from app.models.booking_seat import BookingSeat
from app.schemas.booking import BookingCreate, BookingResponse

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 1. Check whether the show exists
    show = db.query(Show).filter(
        Show.id == booking_data.show_id
    ).first()

    if show is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Show not found",
        )

    # 2. Find the event associated with the show
    event = db.query(Event).filter(
        Event.id == show.event_id
    ).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # 3. Validate the selected seat IDs
    seat_ids = booking_data.seat_ids

    if len(seat_ids) != len(set(seat_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate seat IDs are not allowed",
        )

    seats = db.query(Seat).filter(
        Seat.id.in_(seat_ids)
    ).all()

    if len(seats) != len(seat_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more seats were not found",
        )

    # 4. Ensure seats belong to the show's screen name.
    # Your current Show model stores screen_name, not screen_id.
    # Match the screen name against the screens table.
    from app.models.screen import Screen

    screen = db.query(Screen).filter(
        Screen.name == show.screen_name
    ).first()

    if screen is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Screen for this show was not found",
        )

    if any(seat.screen_id != screen.id for seat in seats):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more seats do not belong to this show's screen",
        )

    # 5. Check seat availability
    if any(seat.seat_status != "Available" for seat in seats):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="One or more seats are not available",
        )

    # 6. Calculate the total booking amount
    total_amount = float(event.ticket_price) * len(seat_ids)

    booking = Booking(
        user_id=current_user.id,
        show_id=show.id,
        booking_reference=uuid.uuid4().hex[:12].upper(),
        number_of_tickets=len(seat_ids),
        total_amount=total_amount,
        status="Pending",
    )

    try:
        db.add(booking)
        db.flush()

        for seat in seats:
            db.add(
                BookingSeat(
                    booking_id=booking.id,
                    seat_id=seat.id,
                )
            )
            seat.seat_status = "Booked"

        db.commit()
        db.refresh(booking)
        return booking

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create booking",
        )


@router.get("/", response_model=list[BookingResponse])
def get_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.id.desc())
        .all()
    )


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id,
    ).first()

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    return booking