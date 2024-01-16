import os
import sys
from abc import ABC, abstractmethod
from typing import Generic

from sqlalchemy.ext.asyncio import AsyncSession

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from app_types import DM  # noqa
from exceptions import RepositoryValidationException  # noqa


class AbstractRepository(ABC, Generic[DM]):
    """AbstractRepository is an abstract class providing a base interface for
    repositories implementing various data storage strategies."""

    @abstractmethod
    async def add_all(self, data_list: list[DM]) -> None:
        """Abstract method for adding a list of data objects to the repository.

        Args:
            data_list (list[DM]): The list of data objects to be added
            to the repository.
        """
        pass

    @abstractmethod
    async def find_all(self, **filter_by: dict) -> list[DM]:
        """Abstract method for finding data objects in the repository based on
        specified filters.

        Args:
            **filter_by (dict): Keyword arguments representing filters
            to apply during the search.

        Returns:
            list[DM]: The list of data objects matching the specified filters.
        """
        pass


class AbstractDatabaseRepository(AbstractRepository[DM]):
    """AbstractDatabaseRepository is an abstract class that inherits from
    AbstractRepository and extends it to implement operations with a
    database."""

    @abstractmethod
    def set_session(self, session: AsyncSession) -> None:
        """Abstract method for setting the current database session.

        Args:
            session (AsyncSession): The database session to be set.
        """
        pass

    @abstractmethod
    def clear_session(self) -> None:
        """Abstract method for clearing the used database session."""
        pass

    @abstractmethod
    async def add_all(self, data_list: list[DM]) -> None:
        """Abstract method for adding a list of data objects to the database.

        Args:
            data_list (list[DM]): The list of data objects to be added to the database.
        """
        pass

    @abstractmethod
    async def find_all(self, **filter_by: dict) -> list[DM]:
        pass


class AbstractFileRepository(AbstractRepository[DM]):
    """AbstractFileRepository is an abstract class that inherits from
    AbstractRepository and extends it to implement operations with files."""

    @staticmethod
    def _check_filepath_exists(filepath: str) -> None:
        """Static method to check if the directory of the specified filepath
        exists. If not, it creates the necessary directories.

        Args:
            filepath (str): The filepath to check.
        """
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)

    @abstractmethod
    async def add_all(self, data_list: list[DM]) -> None:
        """Abstract method for adding a list of data objects to a file.

        Args:
            data_list (list[DM]): The list of data objects to be added to the file.
        """
        pass

    @abstractmethod
    async def find_all(self, **filter_by: dict) -> list[DM]:
        """Abstract method for finding data objects in a file based on
        specified filters.

        Args:
            **filter_by (dict): Keyword arguments representing filters
            to apply during the search.

        Returns:
            list[DM]: The list of data objects matching the specified filters.
        """
        pass
