import os
import sys
from abc import ABC, abstractmethod
from typing import Generic

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from app_types import DM  # noqa


class AbstractRepository(ABC, Generic[DM]):
    @abstractmethod
    async def add_all(self, data_list: list[DM]) -> None:
        pass

    @abstractmethod
    async def find_all(self, **filter_by: dict) -> list[DM]:
        pass


class AbstractDatabaseRepository(AbstractRepository[DM]):
    @abstractmethod
    async def add_all(self, data_list: list[DM]) -> None:
        pass

    @abstractmethod
    async def find_all(self, **filter_by: dict) -> list[DM]:
        pass


class AbstractFileRepository(AbstractRepository[DM]):
    @staticmethod
    def __check_filepath_exists(filepath: str) -> None:
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)

    @abstractmethod
    async def add_all(self, data_list: list[DM]) -> None:
        pass

    @abstractmethod
    async def find_all(self, **filter_by: dict) -> list[DM]:
        pass


class IUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass
