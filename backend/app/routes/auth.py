from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, get_db
from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import (
    DUMMY_HASH,
    SESSION_COOKIE,
    create_session_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise ConflictError("Email already registered")
    user = User(
        name=data.name.strip(), email=email, password_hash=hash_password(data.password)
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Email already registered") from None
    db.refresh(user)
    return user


@router.post("/login", response_model=UserRead)
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        verify_password(DUMMY_HASH, data.password)
        raise UnauthorizedError("Invalid email or password")
    if not verify_password(user.password_hash, data.password):
        raise UnauthorizedError("Invalid email or password")
    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(str(user.id)),
        max_age=settings.session_max_age_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    return user


@router.post("/logout", status_code=204)
def logout(_: User = Depends(get_current_user)) -> Response:
    response = Response(status_code=204)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user
