from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import text
from fastapi import WebSocket, WebSocketDisconnect, Depends
from app.services.notification import connect_user, disconnect_user
from app.websockets.manager import manager
from app.database import SessionLocal
from app.redis_client import get_redis_client
from app.routers.auth import router as auth_router
from app.routers.event import router as event_router
from app.routers.show import router as show_router
from app.routers.screen import router as screen_router
from app.routers.venue import router as venue_router
from app.routers.seat import router as seat_router
from app.routers.booking import router as booking_router
from app.routers.payment import router as payment_router
from app.routers.notifications import router as notifications_router
from app.routers.reviews import router as reviews_router
app = FastAPI(
    title="Event & Movie Ticket Booking API",
    description="API for booking event and movie tickets",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
)


app.include_router(auth_router)
app.include_router(event_router)
app.include_router(show_router)
app.include_router(screen_router)
app.include_router(venue_router)
app.include_router(seat_router)
app.include_router(booking_router)
app.include_router(payment_router)
app.include_router(notifications_router)
app.include_router(reviews_router)


@app.get("/")
def home():
    return {
        "message": "Event & Movie Ticket Booking API is running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/health/services")
def services_health():
    results = {}

    
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            results["mysql"] = "connected"
        finally:
            db.close()
    except Exception:
        results["mysql"] = "disconnected"

    
    try:
        get_redis_client().ping()
        results["redis"] = "connected"
    except Exception:
        results["redis"] = "disconnected"

    if any(
        service_status != "connected"
        for service_status in results.values()
    ):
        raise HTTPException(
            status_code=503,
            detail=results,
        )

    return {
        "status": "healthy",
        "services": results,
    }
@app.websocket("/ws/notifications/{user_id}")
async def notification_websocket(
    websocket: WebSocket,
    user_id: int,
):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)

@app.post("/ws/test-notification/{user_id}")
async def test_notification(user_id: int):
    await manager.broadcast(
        user_id,
        {
            "type": "test",
            "message": "WebSocket notification received successfully!"
        }
    )
    return {"message": "Test notification sent"}