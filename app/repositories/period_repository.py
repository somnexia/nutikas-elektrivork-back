from datetime import datetime, timezone
from typing import Any

from app.repositories.base_repository import BaseRepository
from app.schemas.period_schema import PeriodCacheSchema


class PeriodRepository(BaseRepository):
    collection_name = "periods"

    @property
    def collection(self):
        return self.db[self.collection_name]

    async def get_by_user_day(self, user_id: str, day: str) -> PeriodCacheSchema | None:
        doc = await self.collection.find_one({"user_id": user_id, "day": day})
        if not doc:
            return None
        return PeriodCacheSchema.model_validate(self._serialize_id(doc))

    async def upsert_periods(
        self, user_id: str, day: str, periods: list[dict[str, Any]]
    ) -> PeriodCacheSchema:
        now = datetime.now(timezone.utc)
        await self.collection.update_one(
            {"user_id": user_id, "day": day},
            {
                "$set": {
                    "periods": periods,
                    "updated_at": now,
                },
                "$setOnInsert": {
                    "user_id": user_id,
                    "day": day,
                    "created_at": now,
                },
            },
            upsert=True,
        )
        doc = await self.collection.find_one({"user_id": user_id, "day": day})
        return PeriodCacheSchema.model_validate(self._serialize_id(doc))
