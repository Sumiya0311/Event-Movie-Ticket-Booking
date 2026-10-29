import os
import smtplib
from email.message import EmailMessage

from fastapi import WebSocket
from sqlalchemy.orm import Session

from app.models.notification import Notification



active_connections: dict[int, list[WebSocket]] = {}


async def connect_user(user_id: int, websocket: WebSocket):
    await websocket.accept()
    active_connections.setdefault(user_id, []).append(websocket)


def disconnect_user(user_id: int, websocket: WebSocket):
    connections = active_connections.get(user_id, [])
    if websocket in connections:
        connections.remove(websocket)

    if not connections:
        active_connections.pop(user_id, None)


async def send_realtime_notification(user_id: int, payload: dict):
    connections = active_connections.get(user_id, [])

    for websocket in connections.copy():
        try:
            await websocket.send_json(payload)
        except Exception:
            disconnect_user(user_id, websocket)


def save_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        is_read=False,
        status="Sent",
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def send_email(to_email: str, subject: str, body: str):
    host = os.getenv("MAILTRAP_HOST", "sandbox.smtp.mailtrap.io")
    port = int(os.getenv("MAILTRAP_PORT", "2525"))
    username = os.getenv("MAILTRAP_USERNAME")
    password = os.getenv("MAILTRAP_PASSWORD")
    sender = os.getenv("MAILTRAP_SENDER_EMAIL", "notifications@example.com")

    if not username or not password:
        raise RuntimeError("Mailtrap SMTP credentials are not configured")

    email = EmailMessage()
    email["Subject"] = subject
    email["From"] = sender
    email["To"] = to_email
    email.set_content(body)

    with smtplib.SMTP(host, port, timeout=15) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(email)