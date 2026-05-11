import json
import logging
from typing import Any

import aiohttp


class PeriodAlghoritms:
    def __init__(self, data: list[dict[str, float | int]] | None = None):
        self.data = data or []
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Initialized with %s price items", len(self.data))

    def get_cheap_periods(self, price_limit: float = 10.0) -> list[dict[str, Any]]:
        """
        Возвращает список периодов когда энергия дешевле или равна
        заданному лимиту в формате
        {
            start: timestamp,
            end: timestamp,
            prices: list
        }
        """
        data = self.data

        cheap_periods = []
        current = None

        for item in data:
            price = item.get("price")
            ts = item.get("timestamp")

            if price is None or ts is None:
                continue

            if price <= price_limit:
                if current is None:
                    current = {"start": ts, "prices": []}

                current["prices"].append({"price": price, "timestamp": ts})
                current["end"] = ts

            else:
                if current and len(current["prices"]) > 1:
                    cheap_periods.append(current)
                current = None

        if current and len(current["prices"]) > 1:
            cheap_periods.append(current)

        return cheap_periods

    def get_avg_price(self) -> float:
        if not self.data:
            return 0.0

        total_price = 0

        count = 0

        for item in self.data:
            price = item.get("price")
            if price is None:
                continue
            total_price += float(price)
            count += 1

        return total_price / count if count else 0.0

    def get_green_prices(self):
        avg_price = self.get_avg_price()
        return self.get_cheap_periods(avg_price / 4) if avg_price else []

    def get_yellow_prices(self):
        avg_price = self.get_avg_price()
        return self.get_cheap_periods(avg_price / 2) if avg_price else []

class CollectData:
    @staticmethod
    async def fetch_prices(start: str, end: str) -> list[dict[str, int | float]] | None:
        logger = logging.getLogger("CollectData")
        params = {
            "start": start,
            "end": end,
            "fields": "ee"
        }

        url = "https://dashboard.elering.ee/api/nps/price"


        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, params=params) as res:
                logger.info("Elering response: status=%s", res.status)
                if res.status != 200:
                    body = await res.text()
                    logger.warning("Elering error body: %s", body)
                    return None

                try:
                    data = await res.json()
                except Exception:
                    body = await res.text()
                    logger.exception("Failed to decode JSON. Body: %s", body)
                    return None

        prices = data.get("data", {}).get("ee")
        logger.info(
            "Elering prices loaded: count=%s", 0 if prices is None else len(prices)
        )
        if prices:
            logger.debug("Elering first item: %s", prices[0])
            logger.debug("Elering last item: %s", prices[-1])
        return prices

    async def load_to_json(self, start: str, end: str) -> None:
        data = await self.fetch_prices(start, end)
        with open("data.json", "w") as f:
            json.dump(data, f, indent=3)

    @staticmethod
    def load_from_json() -> list[dict[str, int | float]]:
        with open("data.json", "r") as f:
            return json.load(f)
