from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.show import Show
from app.models.event import Event
from app.schemas.show import ShowCreate, ShowResponse
from app.auth.security import get_current_user

router = APIRouter(prefix="/shows", tags=["Shows"])


@router.post(
    "/",
    response_model=ShowResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_show(
    show_data: ShowCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    event = db.query(Event).filter(
        Event.id == show_data.event_id
    ).first()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if show_data.end_time <= show_data.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time",
        )

    show = Show(
        event_id=show_data.event_id,
        screen_name=show_data.screen_name,
        show_date=show_data.show_date,
        start_time=show_data.start_time,
        end_time=show_data.end_time,
        status="Scheduled",
    )

    db.add(show)
    db.commit()
    db.refresh(show)
    return show


@router.get("/", response_model=list[ShowResponse])
def get_shows(db: Session = Depends(get_db)):
    return db.query(Show).order_by(Show.id.desc()).all()


@router.get("/{show_id}", response_model=ShowResponse)
def get_show(show_id: int, db: Session = Depends(get_db)):
    show = db.query(Show).filter(Show.id == show_id).first()

    if show is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Show not found",
        )

    return show