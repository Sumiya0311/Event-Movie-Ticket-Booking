Event & Movie Ticket Booking System

Project Overview

The Event & Movie Ticket Booking System is a backend application built with FastAPI that allows users to manage bookings for events and movies. It provides APIs for booking management, payments, notifications, reviews, and ticket generation.

Technologies Used

- Backend: Python, FastAPI
- Database: MySQL
- ORM: SQLAlchemy
- Migrations: Alembic
- Caching: Redis
- Containerization: Docker and Docker Compose
- Testing: Pytest
- Payment Integration: Razorpay Test Mode
- Email Notifications: Mailtrap Sandbox
- Real-Time Communication: WebSockets
Key Features

- REST API development using FastAPI
- Database integration with MySQL and SQLAlchemy
- Database schema migrations using Alembic
- Ticket booking and booking management
- Payment verification using Razorpay test mode
- Email notification testing with Mailtrap
- Real-time notifications using WebSockets
- Review management APIs
- Automated API tests using Pytest
- Docker-based application setup

Project Structure

Event_Movie_Ticket_Booking/
├── app/
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── tests/
│   └── main.py
├── alembic/
├── tickets/
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md

Setup and Run

Prerequisites

- Python 3.9 or later
- Docker Desktop
- Git

Run with Docker Compose

1. Clone the repository.
2. Create your local ".env" file using ".env.example" as a reference.
3. Fill in the required database, security, email, and payment test configuration values.
4. Start the application:

docker compose up --build -d

5. Open the API documentation:

http://localhost:8000/docs

Run Tests

Activate your virtual environment, then run:

pytest -v

Configuration and Security

- Keep ".env" private and never commit it to GitHub.
- Use test credentials for payment and email integrations.
- Do not publish passwords, API keys, or secret keys.

Author

Sumiya Shaik

License

This project was developed for learning and training purposes.