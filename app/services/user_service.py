from datetime import datetime, timezone

from app.core.security import hash_password
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreateSchema, UserReadSchema, UserUpdateSchema


class UserService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def create_user(self, data: UserCreateSchema) -> UserReadSchema:
        now = datetime.now(timezone.utc)
        user_doc = {
            "email": data.email,
            "username": data.username,
            "password_hash": hash_password(data.password),
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        return await self._user_repository.create_user(user_doc)

    async def get_user(self, user_id: str) -> UserReadSchema | None:
        return await self._user_repository.get_by_id(user_id)

    async def get_by_email(self, email: str) -> UserReadSchema | None:
        return await self._user_repository.get_by_email(email)

    async def list_users(self, limit: int = 50, offset: int = 0) -> list[UserReadSchema]:
        return await self._user_repository.list_users(limit=limit, offset=offset)

    async def update_user(
        self, user_id: str, data: UserUpdateSchema
    ) -> UserReadSchema | None:
        updates = data.model_dump(exclude_unset=True)
        if "password" in updates:
            updates["password_hash"] = hash_password(updates.pop("password"))
        updates["updated_at"] = datetime.now(timezone.utc)
        return await self._user_repository.update_user(user_id, updates)

    async def delete_user(self, user_id: str) -> bool:
        return await self._user_repository.delete_user(user_id)
