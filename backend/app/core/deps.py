import uuid
from collections.abc import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.errors import UnauthorizedError
from app.core.security import SESSION_COOKIE, read_session_token
from app.models import User


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise UnauthorizedError()
    user_id = read_session_token(token)
    if user_id is None:
        raise UnauthorizedError("Session expired or invalid")
    user = db.get(User, uuid.UUID(user_id))
    if user is None:
        raise UnauthorizedError()
    return user
