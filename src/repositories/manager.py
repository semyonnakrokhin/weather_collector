import os
import sys
from typing import List, Tuple, Type

from sqlalchemy.ext.asyncio import AsyncSession

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from repositories.abstractions import AbstractDatabaseRepository  # noqa


class DatabaseRepositoriesManager:
    """
    DatabaseRepositoriesManager manages a collection of AbstractDatabaseRepository instances.

    This class is designed for connecting an unlimited number of initialized database repositories
    (AbstractDatabaseRepository) and batch managing these repositories through the public API of this class.
    This includes setting the current session, clearing the used session, and obtaining the required
    repository instance.
    """

    def __init__(self, repository_instances: List[AbstractDatabaseRepository]):
        """
        Initializes the manager with a list of AbstractDatabaseRepository instances.

        Parameters::
            repository_instances (List[AbstractDatabaseRepository]): The list of repository instances to manage.
        """
        self._repositories = {repo.__class__.__name__: repo for repo in repository_instances}

    def get_all_repositories(self) -> Tuple[AbstractDatabaseRepository]:
        """
        Returns all registered AbstractDatabaseRepository instances.

        Returns:
            Tuple[AbstractDatabaseRepository]: A tuple containing all repository instances.
        """
        return tuple(self._repositories.values())

    def get_repository(self, repository_class: Type[AbstractDatabaseRepository]) -> AbstractDatabaseRepository:
        """
        Returns a specific AbstractDatabaseRepository instance based on its class type.

        Parameters:
            repository_class (Type[AbstractDatabaseRepository]): The class type of the repository.

        Returns:
            AbstractDatabaseRepository: The requested repository instance.
        """
        repo_name_str = repository_class.__name__
        return self._repositories[repo_name_str]

    def set_session_for_all(self, session: AsyncSession) -> None:
        """
        Sets the database session for all registered repositories.

        Parameters:
            session (AsyncSession): The database session to be set for all repositories.
        """
        for repo in self._repositories.values():
            repo.set_session(session)

    def clear_session_for_all(self) -> None:
        """
        Clears the database session for all registered repositories.
        """
        for repo in self._repositories.values():
            repo.clear_session()
