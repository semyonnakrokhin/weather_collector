import os
import sys

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from schemas import Weather  # noqa
from storage.services import StorageService  # noqa


async def controller_storage(storage_service: StorageService, weather: Weather):
    report_id: int = await storage_service.add_weather(weather=weather)  # noqa
