import secrets

from fastapi import Request

from app.config.config import settings


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def is_csrf_valid(request: Request) -> bool:
    header_token = request.headers.get(settings.csrf_header_name)
    cookie_token = request.cookies.get(settings.csrf_cookie_name)
    if not header_token or not cookie_token:
        return False
    return secrets.compare_digest(header_token, cookie_token)
