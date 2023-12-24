import json
import os
import sys
from datetime import datetime

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from aiohttp import ClientSession  # noqa

from apiclients.abstractions import APIClientService  # noqa
from models.dto import JsonOpenweathermapResponseDTO  # noqa


class OpenweathermapByCityAPIClient(APIClientService[JsonOpenweathermapResponseDTO]):
    URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get(
        self, session: ClientSession, city: str, timestamp: datetime
    ) -> JsonOpenweathermapResponseDTO:
        url = f"{self.URL}?q={city}&appid={self.api_key}"
        async with session.get(url) as response:
            res = await response.text()
            res = json.loads(res)
            res["timestamp"] = timestamp
            return JsonOpenweathermapResponseDTO(**res)
