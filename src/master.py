import asyncio
import importlib
import logging
import sys
from datetime import datetime

import aiohttp

from apiclients.abstractions import APIClientService
from exceptions import (
    ApiClientError,
    CitiesRetrievalError,
    InvalidDesignationError,
    MappingError,
    WeatherDataError,
    WeatherFetchingError,
    WeatherParsingError,
)
from mappers.abstractions import AbstractDTOMapper
from models.domains import WeatherDomain
from models.dto import JsonOpenweathermapResponseDTO
from storage_services.manager import StorageServiceManager

logger = logging.getLogger("app.master")


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

        try:
            logger.info("Fetching top cities...")
            cities = self.get_top_cities()
        except CitiesRetrievalError as e:
            logger.error(f"Error retrieving top cities: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while retrieving top cities: {e}"
            )
            sys.exit(1)
        else:
            logger.info("Top cities fetched successfully!")

        try:
            logger.info("Retrieving weather data...")
            dto_list = await self.get_weather_data(cities)
        except (WeatherFetchingError, WeatherParsingError, WeatherDataError) as e:
            logger.error(f"An error occurred while retrieving weather data: {e}")
            sys.exit(1)
        except ApiClientError as e:
            logger.error(
                f"An unexpected error occurred while retrieving weather data: {e}"
            )
            sys.exit(1)
        else:
            logger.info("Weather data retrieved successfully!")

        try:
            logger.info("Converting data to domain model...")
            weather_list = self.convert_data(data_list=dto_list)
        except MappingError as e:
            logger.error(f"Error occurred while converting data to domain model: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"An unexpected error occurred while converting data: {e}")
            sys.exit(1)
        else:
            logger.info("Data converted to domain model successfully!")

        try:
            logger.info("Saving data...")
            await self.save_data(data_weather_list=weather_list)
        except InvalidDesignationError as e:
            logger.error(
                f"Invalid designation for the save service. "
                f"Check the designations and try again: {e}"
            )
            sys.exit(1)
        except Exception as e:
            logger.error(f"An unexpected error occurred while saving data: {e}")
            sys.exit(1)
        else:
            logger.info("Data saved successfully!")

    @staticmethod
    def get_top_cities() -> tuple[str]:
        """Retrieves the top cities list."""
        try:
            module = importlib.import_module("top_cities")
            return getattr(module, "cities_tuple")
        except ImportError as e:
            error_message = f"Error importing module: {e}"
            logger.error(error_message)
            raise CitiesRetrievalError(error_message)
        except AttributeError as e:
            error_message = f"Error accessing attribute 'cities_tuple': {e}"
            logger.error(error_message)
            raise CitiesRetrievalError(error_message)
        except Exception as e:
            error_message = (
                f"An unexpected error occurred while retrieving top cities {e}"
            )
            logger.error(error_message)
            raise RuntimeError(error_message)

    async def get_weather_data(
        self, cities: tuple[str]
    ) -> list[JsonOpenweathermapResponseDTO]:
        """Retrieves weather data for the specified cities."""

        timestamp = datetime.utcnow()
        async with aiohttp.ClientSession() as session_http:
            tasks = []
            for city in cities:
                task = asyncio.create_task(
                    self.weather_client.get(
                        session=session_http, city=city, timestamp=timestamp
                    )
                )
                logger.debug(f"Task created for city: {city}")
                tasks.append(task)

            logger.debug("Starting handling tasks concurrently...")
            dto_list = await asyncio.gather(*tasks)
            logger.debug("All tasks handled!")
            return dto_list

    def convert_data(
        self, data_list: list[JsonOpenweathermapResponseDTO]
    ) -> list[WeatherDomain]:
        """Converts data from DTO to the domain model."""
        return [
            self.client_storage_mapper.to_target(source_obj=data) for data in data_list
        ]

    async def save_data(self, data_weather_list: list[WeatherDomain]) -> None:
        """Saves the weather data to storage services."""

        tasks = []
        for (
            storage_service
        ) in self.storage_services_manager.get_selected_storage_services():
            task = asyncio.create_task(
                storage_service.bulk_store_data(data_lst=data_weather_list)
            )

            logger.debug(
                f"Task created for storage service: "
                f"{storage_service.service_designation}"
            )
            tasks.append(task)

        logger.debug("Starting handling tasks concurrently...")
        await asyncio.gather(*tasks)
        logger.debug("All tasks handled!")
