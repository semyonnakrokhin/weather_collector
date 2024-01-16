import os
import sys
from typing import List

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from models.domains import WeatherDomain  # noqa
from repositories.abstractions import AbstractFileRepository  # noqa
from storage_services.abstractions import AbstractStorageService  # noqa
from units_of_work.realisations import WeatherUnitOfWork  # noqa


class DatabaseService(AbstractStorageService[WeatherDomain]):
    """DatabaseService is a storage service for WeatherDomain instances."""

    def __init__(self, uow: WeatherUnitOfWork, service_designation: str):
        """Initializes the DatabaseService instance with a unit of work and
        service designation.

        Parameters:
            uow (WeatherUnitOfWork): The unit of work for coordinating
            database operations.
            service_designation (str): The designation of the storage service
            for selections.
        """
        self.uow = uow
        self.service_designation = service_designation

    async def bulk_store_data(self, data_lst: List[WeatherDomain]) -> None:
        async with self.uow:
            await self.uow.weather_database_repository.add_all(data_list=data_lst)
            await self.uow.commit()


class FileService(AbstractStorageService[WeatherDomain]):
    """FileService is a storage service for WeatherDomain instances using a
    file repository."""

    def __init__(self, repository: AbstractFileRepository, service_designation: str):
        """Initializes the FileService instance with a file repository and
        service designation.

        Parameters:
            repository (AbstractFileRepository): The file repository for
            storing WeatherDomain instances.
            service_designation (str): The designation of the storage service
            for selections.
        """
        self.repository = repository
        self.service_designation = service_designation

    async def bulk_store_data(self, data_lst: List[WeatherDomain]) -> None:
        await self.repository.add_all(data_list=data_lst)
