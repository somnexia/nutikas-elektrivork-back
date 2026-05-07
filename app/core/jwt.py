from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config.config import settings
from app.schemas.auth_schema import RefreshTokenPayloadSchema, TokenPayloadSchema


def create_access_token(payload: dict, expires_minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    to_encode = payload.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> TokenPayloadSchema:
    try:
        data = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    return TokenPayloadSchema(**data)


def create_refresh_token(payload: dict, expires_days: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=expires_days or settings.refresh_token_expire_days
    )
    to_encode = payload.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.refresh_token_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_refresh_token(token: str) -> RefreshTokenPayloadSchema:
    try:
        data = jwt.decode(
            token, settings.refresh_token_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as exc:
        raise ValueError("Invalid refresh token") from exc

    return RefreshTokenPayloadSchema(**data)
