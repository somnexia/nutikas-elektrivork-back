from typing import Any

from bson import ObjectId

from app.repositories.base_repository import BaseRepository
from app.schemas.user_schema import UserReadSchema, UserUnsafeReadSchema


class UserRepository(BaseRepository):
	collection_name = "users"

	@property
	def collection(self):
		return self.db[self.collection_name]

	async def create_user(self, user_doc: dict[str, Any]) -> UserReadSchema:
		result = await self.collection.insert_one(user_doc)
		created = await self.collection.find_one({"_id": result.inserted_id})
		return UserReadSchema.model_validate(self._serialize_id(created))

	async def get_by_id(self, user_id: str) -> UserReadSchema | None:
		try:
			object_id = ObjectId(user_id)
		except Exception:
			return None

		user = await self.collection.find_one({"_id": object_id})
		if not user:
			return None
		return UserReadSchema.model_validate(self._serialize_id(user))

	async def get_by_email(self, email: str) -> UserUnsafeReadSchema | None:
		user = await self.collection.find_one({"email": email})
		if not user:
			return None
		return UserUnsafeReadSchema.model_validate(self._serialize_id(user))

	async def get_by_username(self, username: str) -> UserUnsafeReadSchema | None:
		user = await self.collection.find_one({"username": username})
		if not user:
			return None
		return UserUnsafeReadSchema.model_validate(self._serialize_id(user))

	async def list_users(self, limit: int = 50, offset: int = 0) -> list[UserReadSchema]:
		cursor = self.collection.find().skip(offset).limit(limit)
		users: list[UserReadSchema] = []
		async for doc in cursor:
			users.append(UserReadSchema.model_validate(self._serialize_id(doc)))
		return users

	async def update_user(
		self, user_id: str, updates: dict[str, Any]
	) -> UserReadSchema | None:
		try:
			object_id = ObjectId(user_id)
		except Exception:
			return None

		await self.collection.update_one({"_id": object_id}, {"$set": updates})
		updated = await self.collection.find_one({"_id": object_id})
		if not updated:
			return None
		return UserReadSchema.model_validate(self._serialize_id(updated))

	async def delete_user(self, user_id: str) -> bool:
		try:
			object_id = ObjectId(user_id)
		except Exception:
			return False

		result = await self.collection.delete_one({"_id": object_id})
		return result.deleted_count == 1
