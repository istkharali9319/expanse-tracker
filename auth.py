import os
from typing import Optional
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from passlib.context import CryptContext
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import models

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-production")
SESSION_COOKIE_NAME = "session"
SESSION_MAX_AGE = 60 * 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeTimedSerializer(SECRET_KEY)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_session_cookie(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})


def decode_session_cookie(cookie: str) -> Optional[dict]:
    try:
        data = serializer.loads(cookie, max_age=SESSION_MAX_AGE)
        return data
    except (BadSignature, SignatureExpired):
        return None


def get_current_user(request: Request, db: Session) -> Optional[models.User]:
    cookie = request.cookies.get(SESSION_COOKIE_NAME)
    if not cookie:
        return None
    data = decode_session_cookie(cookie)
    if not data:
        return None
    user_id = data.get("user_id")
    if not user_id:
        return None
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user


def require_auth(request: Request, db: Session) -> models.User:
    user = get_current_user(request, db)
    if not user:
        from fastapi.responses import RedirectResponse
        raise HTTPException(status_code=307, detail="Not authenticated")
    return user


def create_default_admin(db: Session):
    existing = db.query(models.User).filter(models.User.username == "admin").first()
    if not existing:
        admin = models.User(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin
    return existing
