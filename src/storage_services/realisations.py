import logging
import os
import sys
from typing import List

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from exceptions import DatabaseRepositoriesManagerError  # noqa
from exceptions import FileWriteError  # noqa
from exceptions import InvalidSessionTypeError  # noqa
from exceptions import MappingError  # noqa
from exceptions import RepositoryNotFoundError  # noqa
from exceptions import RepositoryValidationError  # noqa
from models.domains import WeatherDomain  # noqa
from repositories.abstractions import AbstractFileRepository  # noqa
from storage_services.abstractions import AbstractStorageService  # noqa
from units_of_work.realisations import WeatherUnitOfWork  # noqa

logger = logging.getLogger("app.storage_services")


class DatabaseService(AbstractStorageService[WeatherDomain]):
    """DatabaseService is a storage service for WeatherDomain instances."""

    def __init__(self, uow: WeatherUnitOfWork, service_designation: str):
        self.uow = uow
        self.service_designation = service_designation

    async def bulk_store_data(self, data_lst: List[WeatherDomain]) -> None:
        try:
            logger.info(f"{self.service_designation.upper()} saving started...")
            async with self.uow:
                """
                The context operates with the Repositories Manager
                and the repositories themselves, so exceptions at these levels
                occur within the context and are handled by the context manager
                in __aexit__ method.
                """
                await self.uow.weather_database_repository.add_all(data_list=data_lst)
                await self.uow.commit()
        except RepositoryValidationError:
            logger.error(
                "Repositories do not match the allowed repositories "
                "in the Unit of Work."
            )
        except InvalidSessionTypeError:
            logger.error(
                "The Unit of Work uses a different session type than the repositories."
            )
        except RepositoryNotFoundError:
            logger.error(
                "Unit of work cannot find the repository "
                "when accessing the repositories manager."
            )
        except DatabaseRepositoriesManagerError as e:
            logger.error(
                f"An error occurred at the level of the repositories manager: {str(e)}"
            )
        except Exception:
            logger.error("An error occurred at the level of the Unit of Work.")
        else:
            logger.info(
                f"{self.service_designation.upper()} saving finished successfully!"
            )


class FileService(AbstractStorageService[WeatherDomain]):
    """FileService is a storage service for WeatherDomain instances using a
    file repository."""

    def __init__(self, repository: AbstractFileRepository, service_designation: str):
        self.repository = repository
        self.service_designation = service_designation

    async def bulk_store_data(self, data_lst: List[WeatherDomain]) -> None:
        try:
            logger.info(f"{self.service_designation.upper()} saving started...")
            await self.repository.add_all(data_list=data_lst)
        except MappingError as e:
            logger.error(f"Error mapping domain object to entity: {str(e)}")
        except FileWriteError as e:
            logger.error(f"An error occurred while writing to the file: {str(e)}")
        except Exception as e:
            logger.error(
                f"An unexpected error at the level of Repositories occurred: {str(e)}"
            )
        else:
            logger.info(
                f"{self.service_designation.upper()} saving finished successfully!"
            )
