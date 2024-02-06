import logging
import os
import sys
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import List, NoReturn, Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from exceptions import DatabaseError  # noqa
from exceptions import DatabaseRepositoriesManagerError  # noqa
from exceptions import MappingError  # noqa
from exceptions import RepositoryError  # noqa
from exceptions import RepositoryNotFoundError  # noqa
from exceptions import RepositoryValidationError  # noqa
from exceptions import SessionNotSetError  # noqa
from repositories.abstractions import AbstractDatabaseRepository  # noqa
from repositories.manager import DatabaseRepositoriesManager  # noqa

logger = logging.getLogger("app.unit_of_work")


class IUnitOfWork(ABC):
    """IUnitOfWork is an abstract base class defining the interface for a unit
    of work."""

    @abstractmethod
    async def __aenter__(self):
        """Async context manager entry method."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit method."""
        pass

    @abstractmethod
    async def commit(self):
        """Commits the changes made during the unit of work."""
        pass

    @abstractmethod
    async def rollback(self):
        """Rolls back the changes made during the unit of work."""
        pass


class BaseUnitOfWork(IUnitOfWork):
    """BaseUnitOfWork is a base implementation of the IUnitOfWork interface.

    Attributes:
        allowed_repository_classes (List[Type[AbstractDatabaseRepository]]): The list of
        allowed repository classes.
    """

    allowed_repository_classes: List[Type[AbstractDatabaseRepository]]

    def __init__(
        self,
        database_repositories_manager: DatabaseRepositoriesManager,
        async_session_factory: AbstractContextManager[AsyncSession],
    ):
        self._database_repositories_manager = database_repositories_manager
        self._async_session_factory = async_session_factory

        self._session: Optional[AsyncSession] = None

    def validate_allowed_repositories(self) -> Optional[NoReturn]:
        """Validates the allowed repository classes against the actual
        repository classes.

        If actual repository instances don't correspond
        allowed_repository_classes then RepositoryValidationException
        raises.
        """

        rp1 = set(
            type(repo)
            for repo in self._database_repositories_manager.get_all_repositories()
        )
        rp2 = set(self.allowed_repository_classes)
        if rp1 != rp2:
            error_message = "Mismatch between allowed_repository_classes "
            "and actual repository classes."
            logger.error(error_message)
            raise RepositoryValidationError(error_message)

    async def __aenter__(self):
        """Async context manager entry method."""
        self.validate_allowed_repositories()
        self._session = self._async_session_factory()
        self._database_repositories_manager.set_session_for_all(session=self._session)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit method."""

        if exc_type is not None:
            if isinstance(
                exc_val,
                (SessionNotSetError, MappingError, RepositoryError, DatabaseError),
            ):
                logger.error(
                    f"An error occurred during unit of work "
                    f"context execution: {exc_val}"
                )
            else:
                logger.error(
                    "An unexpected error occurred "
                    "during unit of work context execution"
                )

        await self.rollback()
        self._database_repositories_manager.clear_session_for_all()
        await self._session.close()

        return True

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    def get_repository(
        self, repository_class: Type[AbstractDatabaseRepository]
    ) -> AbstractDatabaseRepository:
        """Returns the repository instance for the specified repository class."""
        try:
            return self._database_repositories_manager.get_repository(
                repository_class=repository_class
            )
        except RepositoryNotFoundError as e:
            error_message = (
                f"Invalid repository class type or repository not found "
                f"in the repositories manager: {str(e)}"
            )
            logger.error(error_message)
            raise RepositoryNotFoundError(error_message)
        except Exception as e:
            error_message = (
                f"An error occurred at the level of the repositories manager: {str(e)}"
            )
            logger.error(error_message)
            raise DatabaseRepositoriesManagerError(error_message)
