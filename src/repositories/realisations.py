import json
import os
import sys
from typing import Optional

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from exceptions import SessionNotSetError  # noqa
from mappers.abstractions import AbstractDomainEntityMapper  # noqa
from mappers.realisations import WeatherDatabaseMapper  # noqa
from models.domains import WeatherDomain  # noqa
from models.entities import WeatherORMModel  # noqa
from repositories.abstractions import AbstractDatabaseRepository  # noqa
from repositories.abstractions import AbstractFileRepository  # noqa; noqa


class WeatherDatabaseRepository(AbstractDatabaseRepository[WeatherDomain]):
    """WeatherDatabaseRepository is a concrete implementation of
    AbstractDatabaseRepository for managing weather data in a database.

    Attributes:
        model (Type[WeatherORMModel]): The ORM model representing
        weather data in the database.
    """

    model = WeatherORMModel

    def __init__(self, mapper: AbstractDomainEntityMapper):
        """Initializes the repository with a specified mapper for data
        transformation.

        Parameters:
            mapper (AbstractDomainEntityMapper): The mapper used for
            transforming data between domain and database entity models.
        """
        self._session: Optional[AsyncSession] = None
        self._mapper = mapper

    def set_session(self, session: AsyncSession) -> None:
        """Sets the current database session.

        Parameters:
            session (AsyncSession): The database session to be set.
        """
        if type(session) is not AsyncSession:
            raise SessionNotSetError(
                f"Session cannot be {type(session)}. Provide a valid AsyncSession."
            )
        self._session = session

    def clear_session(self) -> None:
        """Deletes the used database session."""
        self._session = None

    async def add_all(self, data_list: list[WeatherDomain]) -> None:
        """Adds a list of WeatherDomain objects to the database.

        Parameters:
            data_list (list[WeatherDomain]): The list of weather data
            to be added to the database.
        """
        if self._session is None:
            raise SessionNotSetError(
                "Session not set. Call set_session() before using the repository."
            )

        entity_list = [self._mapper.to_entity(domain_obj=data) for data in data_list]
        entity_dicts_list = [
            {
                key: value
                for key, value in entity.__dict__.items()
                if key != "_sa_instance_state"
            }
            for entity in entity_list
        ]

        stmt = insert(self.model).values(entity_dicts_list)
        await self._session.execute(stmt)

    async def find_all(self, **filter_by: dict) -> list[WeatherDomain]:
        """Finds weather data in the database based on specified filters.

        Parameters:
            **filter_by (dict): Keyword arguments representing filters
            to apply during the search.

        Returns:
            list[WeatherDomain]: The list of weather data matching
            the specified filters.
        """
        if self._session is None:
            raise SessionNotSetError(
                "Session not set. Call set_session() before using the repository."
            )

        query = select(self.model).select_from(self.model).filter_by(**filter_by)
        result_orm = await self._session.execute(query)

        entity_list = result_orm.scalars().all()
        return [self._mapper.to_domain(enity_obj=entity) for entity in entity_list]


class TextfileRepository(AbstractFileRepository[WeatherDomain]):
    def __init__(self, filepath: str, mapper: AbstractDomainEntityMapper):
        self.filepath = filepath
        self.mapper = mapper
        self._check_filepath_exists(filepath=filepath)

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
        self._check_filepath_exists(filepath=filepath)

    async def add_all(self, data_list: list[WeatherDomain]) -> None:
        entity_list = [self.mapper.to_entity(domain_obj=data) for data in data_list]

        with open(self.filepath, mode="w", encoding="utf-8") as file:
            json.dump(entity_list, file)

    async def find_all(self, **filter_by: dict) -> list[WeatherDomain]:
        with open(self.filepath, mode="r", encoding="utf-8") as file:
            entity_list = json.load(file)
        return [self.mapper.to_domain(enity_obj=entity) for entity in entity_list]
