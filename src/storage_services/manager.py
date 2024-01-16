import os
import sys
from typing import List, NoReturn, Optional

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from config import allowed_storage_services_designations  # noqa
from exceptions import InvalidDesignationError  # noqa
from storage_services.abstractions import AbstractStorageService  # noqa


class StorageServiceManager:
    """StorageServiceManager manages a collection of AbstractStorageService
    instances."""

    def __init__(
        self,
        all_storage_services: List[AbstractStorageService],
        selected_storage_services: List[str],
    ):
        """Initializes the manager with a list of all storage services and the
        selected storage services.

        Parameters:
            all_storage_services (List[AbstractStorageService]): The list of
            all available storage services.
            selected_storage_services (List[str]): The list of designated
            storage services to be managed.
        """
        self.validate_designations(selected_storage_services)
        self.__all_storage_services = all_storage_services
        self.__selected_storage_services = selected_storage_services

    @staticmethod
    def validate_designations(
        selected_storage_services: List[str],
    ) -> Optional[NoReturn]:
        """Validates the selected storage services against the allowed
        designations.

        Parameters:
            selected_storage_services (List[str]): The list of
            storage service designations to be validated.
        """
        for designation in selected_storage_services:
            if designation not in allowed_storage_services_designations:
                raise InvalidDesignationError(designation)

    def get_selected_storage_services(self) -> List[AbstractStorageService]:
        """Returns a list of AbstractStorageService instances corresponding to
        the selected services.

        Returns:
            List[AbstractStorageService]: The list of selected storage service
            instances.
        """
        res = []
        for storage_service in self.__all_storage_services:
            if storage_service.service_designation in self.__selected_storage_services:
                res.append(storage_service)

        return res
