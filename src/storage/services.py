import os
import sys
from abc import ABC
from datetime import datetime
from typing import Type

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from database.db import async_session_maker  # noqa
from exceptions.exceptions import DataNotFoundError  # noqa
from schemas import Weather, WeatherTypeOpenweathermap  # noqa
from storage.repositories import AbstractDBRepository  # noqa
from storage.repositories import AbstractFileRepository  # noqa; noqa


class StorageService(ABC):
    """Abstract class for services"""

    pass


class WeatherServiceDB(StorageService):
    """Service for reading and writing data to database"""

    def __init__(self, repository: Type[AbstractDBRepository]):
        self.repository = repository

    async def add_weather(self, weather: Weather) -> int:
        async with async_session_maker() as session:
            weather_dict = weather.model_dump()
            report_id = await self.repository(session).add_one(data=weather_dict)
            await session.commit()
            return report_id

    async def get_weather_in_city(self, city: str) -> Weather:
        async with async_session_maker() as session:
            weather_dict = await self.repository(session).find_filtered(city=city)

            if not weather_dict:
                raise DataNotFoundError

            return Weather(**weather_dict)

    async def update_weather(self, report_id: int, new_weather: Weather) -> Weather:
        async with async_session_maker() as session:
            new_weather_dict = new_weather.model_dump()
            updated_weather_dict = await self.repository(session).edit_one(
                id=report_id, new_data=new_weather_dict
            )
            await session.commit()
            return Weather(**updated_weather_dict)

    async def delete_weather(self, report_id: int) -> None:
        async with async_session_maker() as session:
            await self.repository(session).remove_one(id=report_id)
            await session.commit()


class FileService(StorageService):
    def __init__(self, repository: AbstractFileRepository):
        self.repository = repository

    async def add_weather(self, weather: Weather) -> int:
        weather_dict = weather.model_dump()
        num = await self.repository.add_one(data=weather_dict)
        return num


if __name__ == "__main__":
    example1 = {
        "timestamp": datetime.now(),
        "city": "Moscow",
        "temperature": 25,
        "weather_type": WeatherTypeOpenweathermap.CLOUDS,
        "sunrise": "07:30",
        "sunset": "18:00",
    }

    weather_example = Weather(**example1)
