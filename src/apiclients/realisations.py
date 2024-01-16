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
    """
    OpenweathermapByCityAPIClient is a concrete client implementation for retrieving weather data
    from the OpenWeatherMap API based on the city name.
    """

    URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get(
        self, session: ClientSession, city: str, timestamp: datetime
    ) -> JsonOpenweathermapResponseDTO:
        """
        Fetches weather data for a specified city from the OpenWeatherMap API.

        This method sends an asynchronous GET request to the OpenWeatherMap API with the provided
        city name and API key, retrieves the response, and processes it into a JsonOpenweathermapResponseDTO.

        Args:
            session (ClientSession): A client session for making asynchronous HTTP requests.
            city (str): The name of the city for which weather data is requested.
            timestamp (datetime): The timestamp to associate with the retrieved weather data.

        Returns:
            JsonOpenweathermapResponseDTO: The data transfer object representing the retrieved weather data.
        """
        url = f"{self.URL}?q={city}&appid={self.api_key}"
        async with session.get(url) as response:
            res = await response.text()
            res = json.loads(res)
            res["timestamp"] = timestamp
            return JsonOpenweathermapResponseDTO(**res)
