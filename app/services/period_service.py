from datetime import datetime, timedelta
import logging
from zoneinfo import ZoneInfo

from app.core.period_alghoritms import CollectData, PeriodAlghoritms
from app.repositories.period_repository import PeriodRepository
from app.schemas.period_schema import PeriodWindowSchema


class PeriodService:
    def __init__(self, period_repository: PeriodRepository):
        self._period_repository = period_repository
        self._logger = logging.getLogger(self.__class__.__name__)

    async def get_periods(self, user_id: str) -> list[PeriodWindowSchema]:
        start, end, day = self._get_day_window()
        cached = await self._period_repository.get_by_user_day(user_id, day)
        if cached is not None:
            if cached.periods:
                self._logger.info("Periods cache hit for %s: count=%s", day, len(cached.periods))
                return cached.periods
            self._logger.info("Periods cache empty for %s, refetching", day)

        prices = await CollectData.fetch_prices(start, end)
        self._logger.info(
            "Fetched prices for %s: count=%s", day, 0 if prices is None else len(prices)
        )
        if not prices:
            self._logger.warning("No prices returned for %s", day)
        if prices:
            self._logger.debug("First price item: %s", prices[0])
            self._logger.debug("Last price item: %s", prices[-1])

        period_algorithms = PeriodAlghoritms(prices or [])

        periods_raw = period_algorithms.get_cheap_periods()
        if not periods_raw:
            periods_raw = period_algorithms.get_green_prices()
        if not periods_raw:
            periods_raw = period_algorithms.get_yellow_prices()

        if not periods_raw:
            periods_raw = self._build_full_day_window(prices or [])

        await self._period_repository.upsert_periods(user_id, day, periods_raw)
        if not periods_raw:
            self._logger.warning("No periods calculated for %s", day)
            return []

        self._logger.info("Periods calculated for %s: count=%s", day, len(periods_raw))
        return [PeriodWindowSchema.model_validate(item) for item in periods_raw]

    @staticmethod
    def _get_day_window() -> tuple[str, str, str]:
        now = datetime.now(tz=ZoneInfo("Europe/Tallinn")).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start = now.isoformat()
        end = (now + timedelta(days=1)).isoformat()
        day = now.date().isoformat()
        return start, end, day

    @staticmethod
    def _build_full_day_window(
        prices: list[dict[str, int | float]]
    ) -> list[dict[str, int | float | list[dict[str, int | float]]]]:
        if not prices:
            return []

        first = prices[0].get("timestamp")
        last = prices[-1].get("timestamp")
        if first is None or last is None:
            return []

        return [
            {
                "start": first,
                "end": last,
                "prices": [
                    {"price": item.get("price"), "timestamp": item.get("timestamp")}
                    for item in prices
                    if item.get("price") is not None and item.get("timestamp") is not None
                ],
            }
        ]