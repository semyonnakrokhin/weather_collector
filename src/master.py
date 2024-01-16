import asyncio
import importlib
from datetime import datetime

import aiohttp

from apiclients.abstractions import APIClientService
from mappers.abstractions import AbstractDTOMapper
from models.domains import WeatherDomain
from models.dto import JsonOpenweathermapResponseDTO
from storage_services.manager import StorageServiceManager


class MasterService:
    """MasterService coordinates the weather data retrieval and storage process."""

    def __init__(
        self,
        weather_client: APIClientService,
        client_storage_mapper: AbstractDTOMapper,
        storage_services_manager: StorageServiceManager,
    ):
        self.weather_client = weather_client
        self.client_storage_mapper = client_storage_mapper
        self.storage_services_manager = storage_services_manager

    async def start(self) -> None:
        """Initiates the weather data retrieval and storage process."""

        cities = self.get_top_cities()
        dto_list = await self.get_weather_data(cities)
        weather_list = self.convert_data(data_list=dto_list)
        await self.save_data(data_weather_list=weather_list)

    @staticmethod
    def get_top_cities() -> tuple[str]:
        """
        Retrieves the top cities list.

        Returns:
            tuple[str]: The tuple of top cities.
        """
        module = importlib.import_module("top_cities")
        return getattr(module, "cities_tuple")

    async def get_weather_data(
        self, cities: tuple[str]
    ) -> list[JsonOpenweathermapResponseDTO]:
        """
        Retrieves weather data for the specified cities.

        Parameters:
            cities (tuple[str]): The list of cities to retrieve weather data for.

        Returns:
            list[JsonOpenweathermapResponseDTO]: The list of weather data DTOs.
        """

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
        """
        Converts data from DTO to the domain model.

        Parameters:
            data_list (list[JsonOpenweathermapResponseDTO]): The list of weather data DTOs.

        Returns:
            list[WeatherDomain]: The list of weather domain model instances.
        """
        return [
            self.client_storage_mapper.to_target(source_obj=data) for data in data_list
        ]

    async def save_data(self, data_weather_list: list[WeatherDomain]):
        """
        Saves the weather data to storage services.

        Parameters:
            data_weather_list (list[WeatherDomain]): The list of weather domain model instances.
        """
        tasks = [
            storage_service.bulk_store_data(data_lst=data_weather_list)
            for storage_service in self.storage_services_manager.get_selected_storage_services()
        ]

        await asyncio.gather(*tasks)
