import os
import sys
from abc import ABC, abstractmethod
from typing import Generic

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from app_types import DTO  # noqa


class APIClientService(ABC, Generic[DTO]):
    URL = None

    @abstractmethod
    async def get(self, *args, **kwargs) -> DTO:
        pass
