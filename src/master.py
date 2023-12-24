import asyncio
import importlib
from datetime import datetime
from typing import List

import aiohttp

from apiclients.abstractions import APIClientService
from mappers.abstractions import AbstractDTOMapper
from models.domains import WeatherDomain
from models.dto import JsonOpenweathermapResponseDTO
from storage_services.abstractions import AbstractStorageService


class MasterService:
    def __init__(
        self,
        api_client: APIClientService,
        client_storage_mapper: AbstractDTOMapper,
        storage_services: List[AbstractStorageService],
    ):
        self.api_client = api_client
        self.client_storage_mapper = client_storage_mapper
        self.storage_services = storage_services

    async def start(self) -> None:
        cities = self.get_top_cities()
        dto_list = await self.get_weather_data(cities)
        weather_list = self.convert_data(data_list=dto_list)
        await self.save_data(data_weather_list=weather_list)

    @staticmethod
    def get_top_cities() -> tuple[str]:
        module = importlib.import_module("top_cities")
        return getattr(module, "cities_tuple")

    async def get_weather_data(
        self, cities: tuple[str]
    ) -> list[JsonOpenweathermapResponseDTO]:
        timestamp = datetime.utcnow()
        async with aiohttp.ClientSession() as session_http:
            tasks = [
                self.weather_client.get(
                    session=session_http, city=city, timestamp=timestamp
                )
                for city in cities
            ]
            dto_list = await asyncio.gather(*tasks)
            return dto_list

    def convert_data(
        self, data_list: list[JsonOpenweathermapResponseDTO]
    ) -> list[WeatherDomain]:
        return [
            self.client_storage_mapper.to_target(source_obj=data) for data in data_list
        ]

    async def save_data(self, data_weather_list: list[WeatherDomain]):
        tasks = [
            storage_service.bulk_store_data(data_lst=data_weather_list)
            for storage_service in self.storage_services
        ]

        await asyncio.gather(*tasks)
