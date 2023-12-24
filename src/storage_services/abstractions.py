import os
import sys
from abc import ABC, abstractmethod
from typing import Generic, List

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from app_types import DM  # noqa


class AbstractStorageService(ABC, Generic[DM]):
    @abstractmethod
    async def bulk_store_data(self, data_lst: List[DM]) -> None:
        pass
