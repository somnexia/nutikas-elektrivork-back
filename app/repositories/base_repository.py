from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class BaseRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    @property
    def db(self) -> AsyncIOMotorDatabase:
        return self._db

    @staticmethod
    def _serialize_id(document: dict[str, Any]) -> dict[str, Any]:
        if "_id" in document:
            document["id"] = str(document.pop("_id"))
        return document
