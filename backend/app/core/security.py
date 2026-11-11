from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from itsdangerous import BadSignature, URLSafeTimedSerializer

from app.core.config import settings

SESSION_COOKIE = "mini360_session"

_hasher = PasswordHasher()
_serializer = URLSafeTimedSerializer(settings.secret_key, salt="session")
DUMMY_HASH = _hasher.hash("dummy-password-for-timing")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def create_session_token(user_id: str) -> str:
    return _serializer.dumps({"uid": user_id})


def read_session_token(token: str) -> str | None:
    try:
        data = _serializer.loads(token, max_age=settings.session_max_age_seconds)
    except BadSignature:
        return None
    return data.get("uid")
