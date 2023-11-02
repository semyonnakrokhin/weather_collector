import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Type

from aiohttp import ClientSession


class APIClientService(ABC):
    URL = None

    @abstractmethod
    async def get(self, *args, **kwargs) -> dict:
        raise NotImplementedError


class OpenweathermapByCityAPIClient(APIClientService):
    URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, session: ClientSession, api_key: str):
        self.session: Type[ClientSession] = session
        self.api_key = api_key

    async def get(self, city: str, timestamp: datetime) -> dict:
        url = f"{self.URL}?q={city}&appid={self.api_key}"
        async with self.session.get(url) as response:
            res = await response.text()
            res = json.loads(res)
            res["timestamp"] = timestamp
            return res
