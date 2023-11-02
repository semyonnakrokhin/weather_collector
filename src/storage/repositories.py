import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, Type, TypeVar

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

import aiofiles  # noqa
from sqlalchemy import delete, insert, select, update  # noqa
from sqlalchemy.ext.asyncio import AsyncSession  # noqa

from mappers import AbstractRepositoryMapper, DBMapper, FileMapper, JSONMapper  # noqa
from models.models import WeatherModel  # noqa

##################################################
##############      INTEFACES      ############### # noqa
##################################################

D = TypeVar("D")


class IAddOneAsync(ABC, Generic[D]):
    @abstractmethod
    async def add_one(self, data: D) -> int:
        raise NotImplementedError


class IFindAllAsync(ABC, Generic[D]):
    @abstractmethod
    async def find_all(self) -> list[D]:
        raise NotImplementedError


class IEditOneAsync(ABC, Generic[D]):
    @abstractmethod
    async def edit_one(self, id: int, new_data: D) -> D:
        raise NotImplementedError


class IRemoveOne(ABC, Generic[D]):
    @abstractmethod
    async def remove_one(self, id: int) -> None:
        raise NotImplementedError


class AbstractDBRepository(IAddOneAsync, IFindAllAsync, IEditOneAsync, IRemoveOne):
    @abstractmethod
    async def add_one(self, data: D) -> int:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, id: int) -> list[D]:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self) -> list[D]:
        raise NotImplementedError

    @abstractmethod
    async def edit_one(self, id: int, new_data: D) -> D:
        raise NotImplementedError

    @abstractmethod
    async def remove_one(self, id: int) -> None:
        raise NotImplementedError


class AbstractFileRepository(IAddOneAsync, IFindAllAsync):
    @abstractmethod
    async def add_one(self, data: D) -> int:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self) -> list[D]:
        raise NotImplementedError


#############################################################
##############      Abstact realisations      ############### # noqa
#############################################################

E = TypeVar("E")


class SQLAlchemyRepository(AbstractDBRepository, Generic[D, E]):
    model: E = None
    mapper: Type[AbstractRepositoryMapper[D, E]]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: D) -> int:
        stmt = insert(self.model).values(**data).returning(self.model.id)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def find_all(self) -> list[D]:
        query = select(self.model)
        result = await self.session.execute(query)
        result = [
            self.mapper.to_domain(instance) for instance in result.scalars().all()
        ]
        return result

    async def find_one(self, id: int) -> D:
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return self.mapper.to_domain(result.scalar())

    async def find_filtered(self, **filter_by) -> list[D]:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.mapper.to_domain(instance) for instance in result.scalars().all()]

    async def edit_one(self, id: int, new_data: D) -> D:
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**new_data)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return self.mapper.to_domain(result.scalar())

    async def remove_one(self, id: int) -> None:
        stmt = delete(self.model).where(self.model.id == id).returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalar()


class FileRepository(AbstractFileRepository, Generic[D, E]):
    mapper: Type[AbstractRepositoryMapper[D, E]]

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.clear_file(filepath=filepath)

    @staticmethod
    def clear_file(filepath: Path) -> None:
        with open(filepath, "w"):
            pass

    async def add_one(self, data: D) -> int:
        async with aiofiles.open(self.filepath, "a", encoding="utf-8") as file:
            data_str = self.mapper.to_entity(domain_obj=data)
            await file.write(data_str)
            return 1

    async def find_all(self) -> list[D]:
        async with aiofiles.open(self.filepath, "r", encoding="utf-8") as file:
            data_str = await file.read()
            blocks = data_str.strip().split("\n\n")
            res = [self.mapper.to_domain(entity_obj=block) for block in blocks]
            return res


#############################################################
##############          Realisations          ############### # noqa
#############################################################


class HistoryRecordFileRepository(FileRepository[dict, str]):
    mapper = FileMapper


class HistoryRecordJSONRepository(FileRepository[dict, str]):
    mapper = JSONMapper


class WeatherRepository(SQLAlchemyRepository[dict, WeatherModel]):
    model = WeatherModel
    mapper = DBMapper
