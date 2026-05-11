from fastapi import APIRouter, Depends, Request, Response

from app.dependencies import get_auth_service
from app.schemas.auth_schema import AccessTokenResponseSchema, RegisterResponseSchema
from app.schemas.user_schema import UserCreateSchema
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponseSchema, status_code=201)
async def register(
    payload: UserCreateSchema,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponseSchema:
    return await auth_service.sign_up(payload, response)


@router.post("/refresh", response_model=AccessTokenResponseSchema)
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> AccessTokenResponseSchema:
    return await auth_service.refresh_session(request, response)
