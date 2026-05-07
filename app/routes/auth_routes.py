from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.config.config import settings
from app.core.csrf import generate_csrf_token, is_csrf_valid
from app.dependencies import get_auth_service
from app.schemas.auth_schema import AccessTokenResponseSchema, RegisterResponseSchema
from app.schemas.user_schema import UserCreateSchema
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(
    response: Response, access_token: str, refresh_token: str, csrf_token: str
) -> None:
    response.set_cookie(
        settings.access_token_cookie_name,
        access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
    )
    response.set_cookie(
        settings.refresh_token_cookie_name,
        refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )
    response.set_cookie(
        settings.csrf_cookie_name,
        csrf_token,
        httponly=False,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )


@router.post("/register", response_model=RegisterResponseSchema, status_code=201)
async def register(
    payload: UserCreateSchema,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponseSchema:
    result, refresh_token = await auth_service.register_user(payload)
    csrf_token = generate_csrf_token()
    _set_auth_cookies(response, result.access_token, refresh_token, csrf_token)
    return result


@router.post("/refresh", response_model=AccessTokenResponseSchema)
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> AccessTokenResponseSchema:
    if not is_csrf_valid(request):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF invalid")

    refresh_token_value = request.cookies.get(settings.refresh_token_cookie_name)
    if not refresh_token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    access_token, new_refresh_token = await auth_service.refresh_tokens(refresh_token_value)
    csrf_token = generate_csrf_token()
    _set_auth_cookies(response, access_token, new_refresh_token, csrf_token)
    return AccessTokenResponseSchema(access_token=access_token)
