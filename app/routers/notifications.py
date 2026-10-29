from fastapi import HTTPException
from app.services.notification import send_email
from fastapi import APIRouter
from app.websockets.manager import manager

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.post("/test/{user_id}")
async def test_notification(user_id: int):
    await manager.broadcast(
        user_id,
        {
            "type": "test",
            "message": "WebSocket notification received successfully!"
        }
    )
    return {"message": "Test notification sent"}
@router.post("/test-email")
async def test_email(to_email: str):
    try:
        send_email(
            to_email=to_email,
            subject="Event & Movie Ticket Booking - Test Email",
            body="Success! Your Mailtrap email integration is working."
        )
        return {"message": "Test email sent successfully"}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Email sending failed: {str(exc)}"
        )