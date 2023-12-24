import json
import os
import sys

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from mappers.abstractions import AbstractDomainEntityMapper  # noqa
from mappers.realisations import WeatherDatabaseMapper  # noqa
from models.domains import WeatherDomain  # noqa
from models.entities import WeatherORMModel  # noqa
from repositories.abstractions import (  # noqa
    AbstractDatabaseRepository,
    AbstractFileRepository,
    IUnitOfWork,
)


class WeatherDatabaseRepository(AbstractDatabaseRepository[WeatherDomain]):
    model = WeatherORMModel

    def __init__(self, session: AsyncSession, mapper: AbstractDomainEntityMapper):
        self.session = session
        self.mapper = mapper

    async def add_all(self, data_list: list[WeatherDomain]) -> None:
        entity_list = [self.mapper.to_entity(domain_obj=data) for data in data_list]
        entity_dicts_list = [entity.__dict__ for entity in entity_list]

        stmt = insert(self.model).values(entity_dicts_list)
        await self.session.execute(stmt)

    async def find_all(self, **filter_by: dict) -> list[WeatherDomain]:
        query = select(self.model).select_from(self.model).filter_by(**filter_by)
        result_orm = await self.session.execute(query)

        entity_list = result_orm.scalars().all()
        return [self.mapper.to_domain(enity_obj=entity) for entity in entity_list]


class TextfileRepository(AbstractFileRepository[WeatherDomain]):
    def __init__(self, filepath: str, mapper: AbstractDomainEntityMapper):
        self.filepath = filepath
        self.mapper = mapper
        self.__check_filepath_exists(filepath=filepath)

    async def add_all(self, data_list: list[WeatherDomain]) -> None:
        entity_list = [self.mapper.to_entity(domain_obj=data) for data in data_list]
        entity_str = "\n\n".join(entity_list)

        with open(self.filepath, mode="w", encoding="utf-8") as file:
            file.write(entity_str)

    async def find_all(self, **filter_by: dict) -> list[WeatherDomain]:
        with open(self.filepath, mode="r", encoding="utf-8") as file:
            entity_str = file.read()

        entity_list = entity_str.split("\n\n")
        return [self.mapper.to_domain(enity_obj=entity) for entity in entity_list]


class JsonRepository(AbstractFileRepository[WeatherDomain]):
    def __init__(self, filepath: str, mapper: AbstractDomainEntityMapper):
        self.filepath = filepath
        self.mapper = mapper
        self.__check_filepath_exists(filepath=filepath)

    async def add_all(self, data_list: list[WeatherDomain]) -> None:
        entity_list = [self.mapper.to_entity(domain_obj=data) for data in data_list]
        json.dump(entity_list, self.filepath)

    async def find_all(self, **filter_by: dict) -> list[WeatherDomain]:
        entity_list = json.load(self.filepath)
        return [self.mapper.to_domain(enity_obj=entity) for entity in entity_list]


class WeatherUnitOfWork(IUnitOfWork):
    async def __aenter__(self):
        self.session = self.async_session_factory()
        weather_mapper = WeatherDatabaseMapper()

        self.weather_database_repository = WeatherDatabaseRepository(
            self.session, weather_mapper
        )

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
