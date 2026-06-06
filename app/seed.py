from sqlalchemy import select

from app.auth_service import create_user
from app.database import Base, SessionLocal, engine
from app.models import User


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.scalars(select(User).where(User.email == "admin@example.com")).first()
        if not existing:
            create_user(db, "admin@example.com", "password123", "admin")
            print("Created admin@example.com / password123")
        else:
            print("Admin already exists")
    finally:
        db.close()


if __name__ == "__main__":
    main()
