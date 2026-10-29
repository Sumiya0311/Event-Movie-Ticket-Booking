from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.screen import Screen
from app.models.venue import Venue
from app.schemas.screen import ScreenCreate, ScreenResponse
from app.auth.security import get_current_user

router = APIRouter(
    prefix="/screens",
    tags=["Screens"],
)


@router.post(
    "/",
    response_model=ScreenResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_screen(
    screen_data: ScreenCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    venue = db.query(Venue).filter(
        Venue.id == screen_data.venue_id
    ).first()

    if venue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )

    screen = Screen(
        venue_id=screen_data.venue_id,
        name=screen_data.name,
        screen_type=screen_data.screen_type,
        total_seats=screen_data.total_seats,
        status="Active",
    )

    db.add(screen)
    db.commit()
    db.refresh(screen)

    return screen


@router.get("/", response_model=list[ScreenResponse])
def get_screens(db: Session = Depends(get_db)):
    return db.query(Screen).order_by(Screen.id.desc()).all()


@router.get("/{screen_id}", response_model=ScreenResponse)
def get_screen(
    screen_id: int,
    db: Session = Depends(get_db),
):
    screen = db.query(Screen).filter(
        Screen.id == screen_id
    ).first()

    if screen is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screen not found",
        )

    return screen