import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.config import settings
from app.core.csrf import is_csrf_valid
from app.core.jwt import decode_access_token

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Simple auth middleware with JWT validation."""

    def __init__(self, app, open_paths: list[str] | None = None):
        super().__init__(app)
        self.open_paths = open_paths or ["/auth/register"]
        self.open_prefixes = ["/docs", "/openapi.json"]

        logger.info("AuthMiddleware initialized")

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in self.open_paths:
            return await call_next(request)

        if any(path == prefix or path.startswith(prefix + "/") for prefix in self.open_prefixes):
            return await call_next(request)

        response = self._validate_token(request)
        if response:
            return response

        return await call_next(request)

    @staticmethod
    def _validate_token(request: Request) -> JSONResponse | None:
        token_str = request.cookies.get(settings.access_token_cookie_name)
        used_cookie = bool(token_str)

        if not token_str:
            token_header = request.headers.get("Authorization")
            if token_header and token_header.startswith("Bearer "):
                token_str = token_header[7:]

        if not token_str:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing access token"},
            )

        try:
            token_payload = decode_access_token(token_str)
            request.state.user = token_payload
        except ValueError as exc:
            logger.debug("Token validation failed: %s", type(exc).__name__)
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
            )
        except Exception as exc:
            logger.error("Authentication middleware error: %s", type(exc).__name__)
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
            )

        if used_cookie and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            if not is_csrf_valid(request):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "CSRF validation failed"},
                )


