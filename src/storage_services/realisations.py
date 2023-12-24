import os
import sys
from typing import List

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from models.domains import WeatherDomain  # noqa
from repositories.abstractions import AbstractFileRepository, IUnitOfWork  # noqa
from storage_services.abstractions import AbstractStorageService  # noqa


class DatabaseService(AbstractStorageService[WeatherDomain]):
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def bulk_store_data(self, data_lst: List[WeatherDomain]) -> None:
        async with self.uow:
            await self.uow.weather_database_repository.add_all(data_list=data_lst)
            await self.uow.commit()


class FileService(AbstractStorageService[WeatherDomain]):
    def __init__(self, repository: AbstractFileRepository):
        self.repository = repository

    async def bulk_store_data(self, data_lst: List[WeatherDomain]) -> None:
        await self.repository.add_all(data_list=data_lst)
