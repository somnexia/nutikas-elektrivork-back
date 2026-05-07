import json
from zoneinfo import ZoneInfo
import aiohttp
from datetime import datetime, timedelta

now = datetime.now(tz=ZoneInfo("Europe/Tallinn")).replace(hour=0, minute=0, second=0, microsecond=0)
start = now.isoformat()
end = (now + timedelta(days=1)).isoformat()


class PeriodAlghoritms:
    def __init__(self):
        self.data = CollectData.fetch_prices()

    def get_cheap_periods(self, price_limit: float = 10.0) -> list[dict[str: list[dict[str: float | int]] | int]]:
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

    def get_avg_price(self):
        total_price = 0

        for item in self.data:
            total_price += item.get("price")
        return total_price / len(self.data)

    def get_green_prices(self):
        avg_price = self.get_avg_price()
        return self.get_cheap_periods(avg_price / 4)

    def get_yellow_prices(self):
        avg_price = self.get_avg_price()
        return self.get_cheap_periods(avg_price / 2)

class CollectData:
    @staticmethod
    async def fetch_prices() -> list[dict[str, int|float]] | None:

        params = {
            "start": start,
            "end": end,
            "fields": "ee"
        }

        URL = f'https://dashboard.elering.ee/api/nps/price'


        async with aiohttp.ClientSession() as session:
            async with session.get(url=URL, params=params) as res:
                data = await res.json()
        return data.get("data").get("ee")

    async def load_to_json(self):
        data = await self.fetch_prices()
        with open("data.json", "w") as f:
            json.dump(data, f, indent=3)

    @staticmethod
    async def load_from_json(self) -> list[dict[str, int|float]]:
        with open("data.json", "r") as f:
            return json.load(f)
