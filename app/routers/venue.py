from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.venue import Venue
from app.schemas.venue import VenueCreate, VenueResponse
from app.auth.security import get_current_user

router = APIRouter(prefix="/venues", tags=["Venues"])


@router.post(
    "/",
    response_model=VenueResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_venue(
    venue_data: VenueCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    venue = Venue(
        name=venue_data.name,
        address=venue_data.address,
        city=venue_data.city,
        state=venue_data.state,
        capacity=venue_data.capacity,
        status="Active",
    )

    db.add(venue)
    db.commit()
    db.refresh(venue)
    return venue


@router.get("/", response_model=list[VenueResponse])
def get_venues(db: Session = Depends(get_db)):
    return db.query(Venue).order_by(Venue.id.desc()).all()


@router.get("/{venue_id}", response_model=VenueResponse)
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.id == venue_id).first()

    if venue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )

    return venue