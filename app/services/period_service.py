from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.period_alghoritms import PeriodAlghoritms
from app.repositories.period_repository import PeriodRepository
from app.schemas.period_schema import PeriodWindowSchema


class PeriodService:
    def __init__(self, period_repository: PeriodRepository):
        self._period_repository = period_repository

    async def get_periods(self, user_id: str) -> list[PeriodWindowSchema] | None:
        day = datetime.now(tz=ZoneInfo("Europe/Tallinn")).date().isoformat()
        cached = await self._period_repository.get_by_user_day(user_id, day)
        if cached is not None:
            return cached.periods or None

        period_algorithms = PeriodAlghoritms()

        periods_raw = period_algorithms.get_cheap_periods()
        if not periods_raw:
            periods_raw = period_algorithms.get_green_prices()
        if not periods_raw:
            periods_raw = period_algorithms.get_yellow_prices()

        await self._period_repository.upsert_periods(user_id, day, periods_raw or [])
        if not periods_raw:
            return None

        return [PeriodWindowSchema.model_validate(item) for item in periods_raw]