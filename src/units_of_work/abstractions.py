import os
import sys
from abc import abstractmethod, ABC
from contextlib import AbstractContextManager
from typing import List, Type, Optional, NoReturn

from sqlalchemy.ext.asyncio import AsyncSession

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from repositories.abstractions import AbstractDatabaseRepository  # noqa
from repositories.manager import DatabaseRepositoriesManager  # noqa
from exceptions import RepositoryValidationException  # noqa


class IUnitOfWork(ABC):
    """IUnitOfWork is an abstract base class defining the interface for a unit of work."""

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
    """
    BaseUnitOfWork is a base implementation of the IUnitOfWork interface.

    Attributes:
        allowed_repository_classes (List[Type[AbstractDatabaseRepository]]): The list of allowed repository classes.
    """

    allowed_repository_classes: List[Type[AbstractDatabaseRepository]]

    def __init__(self,
                 database_repositories_manager: DatabaseRepositoriesManager,
                 async_session_factory: AbstractContextManager[AsyncSession]):
        """
        Initializes the BaseUnitOfWork instance with a database repositories manager and async session factory.

        Parameters:
            database_repositories_manager (DatabaseRepositoriesManager): The manager for database repositories.
            async_session_factory (AbstractContextManager[AsyncSession]): The async session factory.
        """
        self._database_repositories_manager = database_repositories_manager
        self.validate_allowed_repositories()
        self._async_session_factory = async_session_factory

        self._session: Optional[AsyncSession] = None

    def validate_allowed_repositories(self) -> Optional[NoReturn]:
        """
        Validates the allowed repository classes against the actual repository classes.
        If actual repository instances don't correspond allowed_repository_classes
        then RepositoryValidationException raises.
        """

        rp1 = set(type(repo) for repo in self._database_repositories_manager.get_all_repositories())
        rp2 = set(self.allowed_repository_classes)
        if rp1 != rp2:
            raise RepositoryValidationException(
                "Mismatch between allowed_repository_classes and actual repository classes."
            )

    async def __aenter__(self):
        """
        Async context manager entry method.

        Creates a session for working within a single transaction.
        Sets the created session for all repository instances within the database_repositories_manager.
        """
        self._session = self._async_session_factory()
        self._database_repositories_manager.set_session_for_all(session=self._session)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit method.

        Rolls back the transaction, clears the session for all repository instances within the database_repositories_manager,
        and closes the session upon exit.
        """
        await self.rollback()
        self._database_repositories_manager.clear_session_for_all()
        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    def get_repository(self, repository_class: Type[AbstractDatabaseRepository]) -> AbstractDatabaseRepository:
        """Returns the repository instance for the specified repository class.

        Parameters:
            repository_class (Type[AbstractDatabaseRepository]): The repository class.

        Returns:
            The repository instance."""
        return self._database_repositories_manager.get_repository(repository_class=repository_class)
