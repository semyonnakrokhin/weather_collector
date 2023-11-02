import os
import sys
from datetime import datetime

parent_directory = os.path.join(os.getcwd(), "..")  # noqa
sys.path.append(parent_directory)  # noqa

from apiclient.services import APIClientService  # noqa
from schemas import JsonOpenweathermapResponse  # noqa


async def controller_openweathermapapi(
    api_client: APIClientService, city: str, timestamp: datetime
) -> JsonOpenweathermapResponse:
    weather_data: dict = await api_client.get(city=city, timestamp=timestamp)
    return JsonOpenweathermapResponse(**weather_data)
