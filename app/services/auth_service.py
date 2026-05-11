import uuid

from fastapi import HTTPException, Request, Response, status

from app.config.config import settings
from app.core.csrf import generate_csrf_token, is_csrf_valid
from app.core.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.schemas.auth_schema import (
	AccessTokenPayloadSchema,
	AccessTokenResponseSchema,
	RegisterResponseSchema,
)
from app.schemas.user_schema import UserCreateSchema
from app.services.user_service import UserService


class AuthService:
	def __init__(self, user_service: UserService):
		self._user_service = user_service

	async def sign_up(
		self, payload: UserCreateSchema, response: Response
	) -> RegisterResponseSchema:
		result, refresh_token = await self._create_user_with_tokens(payload)
		csrf_token = generate_csrf_token()
		self._set_auth_cookies(response, result.access_token, refresh_token, csrf_token)
		return result

	async def refresh_session(
		self, request: Request, response: Response
	) -> AccessTokenResponseSchema:
		self._ensure_valid_csrf(request)
		refresh_token_value = self._get_refresh_token_from_cookie(request)
		access_token, new_refresh_token = await self._rotate_tokens(refresh_token_value)
		csrf_token = generate_csrf_token()
		self._set_auth_cookies(response, access_token, new_refresh_token, csrf_token)
		return AccessTokenResponseSchema(access_token=access_token)

	async def _create_user_with_tokens(
		self, payload: UserCreateSchema
	) -> tuple[RegisterResponseSchema, str]:
		existing = await self._user_service.get_by_email(payload.email)
		if existing:
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="Email already registered",
			)

		user = await self._user_service.create_user(payload)
		access_token = create_access_token(
			AccessTokenPayloadSchema(sub=user.id, email=user.email)
		)
		refresh_token = await self._issue_refresh_token(user.id)
		return RegisterResponseSchema(access_token=access_token, user=user), refresh_token

	async def _rotate_tokens(self, refresh_token: str) -> tuple[str, str]:
		payload = decode_refresh_token(refresh_token)
		user = await self._user_service.get_user(payload.sub)
		if not user:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="User not found",
			)

		new_refresh_token = await self._issue_refresh_token(user.id)
		new_access_token = create_access_token(
			AccessTokenPayloadSchema(sub=user.id, email=user.email)
		)
		return new_access_token, new_refresh_token

	async def _issue_refresh_token(self, user_id: str) -> str:
		jti = uuid.uuid4().hex
		token = create_refresh_token({"sub": user_id, "jti": jti})
		return token

	@staticmethod
	def _ensure_valid_csrf(request: Request) -> None:
		if not is_csrf_valid(request):
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="CSRF invalid",
			)

	@staticmethod
	def _get_refresh_token_from_cookie(request: Request) -> str:
		refresh_token_value = request.cookies.get(settings.refresh_token_cookie_name)
		if not refresh_token_value:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Missing refresh token",
			)
		return refresh_token_value

	@staticmethod
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
