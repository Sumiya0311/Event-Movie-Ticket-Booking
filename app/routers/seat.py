from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.seat import Seat
from app.models.screen import Screen
from app.schemas.seat import SeatCreate, SeatResponse
from app.auth.security import get_current_user

router = APIRouter(prefix="/seats", tags=["Seats"])


@router.post(
    "/",
    response_model=SeatResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_seat(
    seat_data: SeatCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    screen = db.query(Screen).filter(
        Screen.id == seat_data.screen_id
    ).first()

    if screen is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screen not found",
        )

    existing_seat = db.query(Seat).filter(
        Seat.screen_id == seat_data.screen_id,
        Seat.seat_number == seat_data.seat_number,
    ).first()

    if existing_seat:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This seat number already exists for this screen",
        )

    seat = Seat(
        screen_id=seat_data.screen_id,
        seat_number=seat_data.seat_number,
        seat_type=seat_data.seat_type,
        row_label=seat_data.row_label,
        seat_status="Available",
    )

    db.add(seat)
    db.commit()
    db.refresh(seat)
    return seat


@router.get("/", response_model=list[SeatResponse])
def get_seats(db: Session = Depends(get_db)):
    return db.query(Seat).order_by(Seat.id.asc()).all()


@router.get("/{seat_id}", response_model=SeatResponse)
def get_seat(seat_id: int, db: Session = Depends(get_db)):
    seat = db.query(Seat).filter(Seat.id == seat_id).first()

    if seat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seat not found",
        )

    return seat