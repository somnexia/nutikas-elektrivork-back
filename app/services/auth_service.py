import uuid

from fastapi import HTTPException, status

from app.core.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.schemas.auth_schema import RegisterResponseSchema
from app.schemas.user_schema import UserCreateSchema
from app.services.user_service import UserService


class AuthService:
	def __init__(self, user_service: UserService):
		self._user_service = user_service

	async def register_user(
		self, payload: UserCreateSchema
	) -> tuple[RegisterResponseSchema, str]:
		existing = await self._user_service.get_by_email(payload.email)
		if existing:
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="Email already registered",
			)

		user = await self._user_service.create_user(payload)
		access_token = create_access_token({"sub": user.id, "email": user.email})
		refresh_token = await self._issue_refresh_token(user.id)
		return RegisterResponseSchema(access_token=access_token, user=user), refresh_token

	async def refresh_tokens(self, refresh_token: str) -> tuple[str, str]:
		payload = decode_refresh_token(refresh_token)
		user = await self._user_service.get_user(payload.sub)
		if not user:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="User not found",
			)

		new_refresh_token = await self._issue_refresh_token(user.id)
		new_access_token = create_access_token({"sub": user.id, "email": user.email})
		return new_access_token, new_refresh_token

	async def _issue_refresh_token(self, user_id: str) -> str:
		jti = uuid.uuid4().hex
		token = create_refresh_token({"sub": user_id, "jti": jti})
		return token
