import os
import sys
from abc import ABC, abstractmethod
from typing import Generic, List

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from app_types import DM  # noqa


class AbstractStorageService(ABC, Generic[DM]):
    """AbstractStorageService is an abstract class that serves as the base interface for data storage services."""
    @abstractmethod
    async def bulk_store_data(self, data_lst: List[DM]) -> None:
        """
        Abstract method for bulk storing data.

        Parameters:
            data_lst (List[DM]): The list of data objects to be bulk stored.

        Raises:
            Any exceptions that might occur during the data storage process.
        """
        pass
