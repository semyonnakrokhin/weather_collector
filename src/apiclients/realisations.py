import json
import logging
import os
import sys
from datetime import datetime

import aiohttp

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from apiclients.abstractions import APIClientService  # noqa
from exceptions import ApiClientError  # noqa
from exceptions import WeatherDataError  # noqa
from exceptions import WeatherFetchingError  # noqa
from exceptions import WeatherParsingError  # noqa
from models.dto import JsonOpenweathermapResponseDTO  # noqa

logger = logging.getLogger("app.api_clients")


class OpenweathermapByCityAPIClient(APIClientService[JsonOpenweathermapResponseDTO]):
    """
    OpenweathermapByCityAPIClient is a concrete client implementation
    for retrieving weather data from the OpenWeatherMap API based on the city name.
    """

    URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get(
        self, session: aiohttp.ClientSession, city: str, timestamp: datetime
    ) -> JsonOpenweathermapResponseDTO:
        """
        Fetches weather data for a specified city from the OpenWeatherMap API.

        This method sends an asynchronous GET request to the OpenWeatherMap API
        with the provided city name and API key, retrieves the response,
        and processes it into a JsonOpenweathermapResponseDTO.
        """
        try:
            url = f"{self.URL}?q={city}&appid={self.api_key}"
            async with session.get(url) as response:
                res = await response.text()
                res = json.loads(res)
                res["timestamp"] = timestamp

            return JsonOpenweathermapResponseDTO(**res)
        except aiohttp.ClientError as e:
            error_message = f"An error occurred while fetching weather data: {e}"
            logger.error(error_message)
            raise WeatherFetchingError(error_message)
        except json.JSONDecodeError as e:
            error_message = f"An error occurred while parsing weather data: {e}"
            logger.error(error_message)
            raise WeatherParsingError(error_message)
        except (TypeError, KeyError, ValueError) as e:
            error_message = f"An error occurred while processing weather data: {e}"
            logger.error(error_message)
            raise WeatherDataError(error_message)
        except Exception as e:
            error_message = (
                f"An unexpected error occurred in {self.__class__.__name__}: {e}"
            )
            logger.error(error_message)
            raise ApiClientError(error_message)
