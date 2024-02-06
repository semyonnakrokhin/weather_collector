import json
import logging
import os
import sys
from typing import Optional

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from exceptions import DatabaseError  # noqa
from exceptions import FileReadError  # noqa
from exceptions import FileWriteError  # noqa
from exceptions import MappingError  # noqa
from exceptions import RepositoryError  # noqa
from exceptions import SessionNotSetError  # noqa
from mappers.abstractions import AbstractDomainEntityMapper  # noqa
from mappers.realisations import WeatherDatabaseMapper  # noqa
from models.domains import WeatherDomain  # noqa
from models.entities import WeatherORMModel  # noqa
from repositories.abstractions import AbstractDatabaseRepository  # noqa
from repositories.abstractions import AbstractFileRepository  # noqa; noqa

logger = logging.getLogger("app.repositories")


class WeatherDatabaseRepository(AbstractDatabaseRepository[WeatherDomain]):
    """WeatherDatabaseRepository is a concrete implementation of
    AbstractDatabaseRepository for managing weather data in a database.

    Attributes:
        model (Type[WeatherORMModel]): The ORM model representing
        weather data in the database.
    """

    model = WeatherORMModel

    def __init__(self, mapper: AbstractDomainEntityMapper):
        self._session: Optional[AsyncSession] = None
        self._mapper = mapper

    def set_session(self, session: AsyncSession) -> None:
        if type(session) is not AsyncSession:
            error_message = (
                f"Session cannot be {type(session)}. Provide a valid AsyncSession."
            )
            logger.error(error_message)
            raise SessionNotSetError(error_message)

        self._session = session

    def clear_session(self) -> None:
        self._session = None

    async def add_all(self, data_list: list[WeatherDomain]) -> None:
        if self._session is None:
            error_message = (
                "Session not set. Call set_session() before using the repository."
            )
            logger.error(error_message)
            raise SessionNotSetError(error_message)

        try:
            entity_list = [
                self._mapper.to_entity(domain_obj=data) for data in data_list
            ]
            entity_dicts_list = [
                {
                    key: value
                    for key, value in entity.__dict__.items()
                    if key != "_sa_instance_state"
                }
                for entity in entity_list
            ]
        except MappingError as e:
            error_message = f"Error mapping domain object to entity: {str(e)}"
            logger.error(error_message)
            raise MappingError(error_message)
        except Exception as e:
            error_message = f"Error creating entity dictionary: {str(e)}"
            logger.error(error_message)
            raise RepositoryError(error_message)

        try:
            stmt = insert(self.model).values(entity_dicts_list)
            await self._session.execute(stmt)
            logger.debug("Data added successfully into the database!")
        except Exception as e:
            error_message = (
                f"An error occurred while adding data "
                f"to session and executing query: {str(e)}"
            )
            logger.error(error_message)
            raise DatabaseError(error_message)

    async def find_all(self, **filter_by: dict) -> list[WeatherDomain]:
        if self._session is None:
            raise SessionNotSetError(
                "Session not set. Call set_session() before using the repository."
            )

        try:
            query = select(self.model).select_from(self.model).filter_by(**filter_by)
            result_orm = await self._session.execute(query)
            entity_list = result_orm.scalars().all()
        except Exception as e:
            error_message = (
                f"An error occurred while executing query to find data: {str(e)}"
            )
            logger.error(error_message)
            raise DatabaseError(error_message)

        try:
            return [self._mapper.to_domain(enity_obj=entity) for entity in entity_list]
        except MappingError as e:
            error_message = f"Error mapping entity object to domain: {str(e)}"
            logger.error(error_message)
            raise MappingError(error_message)


class TextfileRepository(AbstractFileRepository[WeatherDomain]):
    def __init__(self, filepath: str, mapper: AbstractDomainEntityMapper):
        self.filepath = filepath
        self.mapper = mapper
        self._check_filepath_exists(filepath=filepath)

    async def add_all(self, data_list: list[WeatherDomain]) -> None:
        try:
            entity_list = [self.mapper.to_entity(domain_obj=data) for data in data_list]
        except (MappingError, TypeError) as e:
            error_message = f"Error mapping domain object to entity: {str(e)}"
            logger.error(error_message)
            raise MappingError(error_message)

        entity_str = "\n\n".join(entity_list)

        try:
            with open(self.filepath, mode="w", encoding="utf-8") as file:
                file.write(entity_str)
        except (FileNotFoundError, PermissionError, IOError, UnicodeEncodeError) as e:
            error_message = f"An error occurred while writing to the file: {str(e)}"
            logger.error(error_message)
            raise FileWriteError(error_message)

    async def find_all(self, **filter_by: dict) -> list[WeatherDomain]:
        try:
            with open(self.filepath, mode="r", encoding="utf-8") as file:
                entity_str = file.read()
        except (FileNotFoundError, PermissionError, IOError, UnicodeDecodeError) as e:
            error_message = f"An error occurred while reading the file: {str(e)}"
            logger.error(error_message)
            raise FileReadError(error_message)

        entity_list = entity_str.split("\n\n")
        try:
            return [self.mapper.to_domain(entity_obj=entity) for entity in entity_list]
        except (MappingError, TypeError) as e:
            error_message = f"Error mapping entity object to domain: {str(e)}"
            logger.error(error_message)
            raise MappingError(error_message)


class JsonRepository(AbstractFileRepository[WeatherDomain]):
    def __init__(self, filepath: str, mapper: AbstractDomainEntityMapper):
        self.filepath = filepath
        self.mapper = mapper
        self._check_filepath_exists(filepath=filepath)

    async def add_all(self, data_list: list[WeatherDomain]) -> None:
        entity_list = [self.mapper.to_entity(domain_obj=data) for data in data_list]

        try:
            with open(self.filepath, mode="w", encoding="utf-8") as file:
                json.dump(entity_list, file)
        except (FileNotFoundError, PermissionError, IOError) as e:
            error_message = f"An error occurred while writing to the file: {str(e)}"
            logger.error(error_message)
            raise FileWriteError(error_message)

    async def find_all(self, **filter_by: dict) -> list[WeatherDomain]:
        try:
            with open(self.filepath, mode="r", encoding="utf-8") as file:
                entity_list = json.load(file)
        except (FileNotFoundError, PermissionError, IOError, json.JSONDecodeError) as e:
            error_message = f"An error occurred while reading the file: {str(e)}"
            logger.error(error_message)
            raise FileReadError(error_message)

        return [self.mapper.to_domain(enity_obj=entity) for entity in entity_list]
