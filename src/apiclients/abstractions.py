import os
import sys
from abc import ABC, abstractmethod
from typing import Generic

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from app_types import DTO  # noqa


class APIClientService(ABC, Generic[DTO]):
    """
    Abstract class for interacting with external services.

    This abstract class, `APIClientService`, serves as a base interface for clients sending requests to external services.
    It includes an abstract method `get` for retrieving data from the external service.

    Attributes:
        URL (None): Placeholder for the URL of the external service.

    Type Parameters:
        DTO: The type hint for the Data Transfer Object expected to be returned by the service.
    """

    URL = None

    @abstractmethod
    async def get(self, *args, **kwargs) -> DTO:
        """
        Abstract method for retrieving data from the external service.

        This method should be implemented in concrete subclasses to define the specific logic
        for interacting with the external service and returning the expected data type.

        Args:
            *args: Variable positional arguments.
            **kwargs: Variable keyword arguments.

        Returns:
            DTO: The Data Transfer Object representing the retrieved data.

        Raises:
            Any specific exceptions that might occur during the interaction with the external service.
        """
        pass
