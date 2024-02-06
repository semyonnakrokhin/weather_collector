import logging
import os
import sys
from typing import List, Tuple, Type

from sqlalchemy.ext.asyncio import AsyncSession

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from exceptions import InvalidSessionTypeError  # noqa
from exceptions import RepositoryNotFoundError  # noqa
from repositories.abstractions import AbstractDatabaseRepository  # noqa

logger = logging.getLogger("app.repository_manager")


class DatabaseRepositoriesManager:
    """DatabaseRepositoriesManager manages a collection of
    AbstractDatabaseRepository instances.

    This class is designed for connecting an unlimited number of
    initialized database repositories (AbstractDatabaseRepository) and
    batch managing these repositories through the public API of this
    class. This includes setting the current session, clearing the used
    session, and obtaining the required repository instance.
    """

    def __init__(self, repository_instances: List[AbstractDatabaseRepository]):
        self._repositories = {
            repo.__class__.__name__: repo for repo in repository_instances
        }

    def get_all_repositories(self) -> Tuple[AbstractDatabaseRepository]:
        """Returns all registered AbstractDatabaseRepository instances."""
        return tuple(self._repositories.values())

    def get_repository(
        self, repository_class: Type[AbstractDatabaseRepository]
    ) -> AbstractDatabaseRepository:
        """Returns a specific AbstractDatabaseRepository instance based on its
        class type."""
        repo_name_str = repository_class.__name__
        if repo_name_str not in self._repositories:
            error_message = f"Repository {repo_name_str} not found."
            logger.error(error_message)
            raise RepositoryNotFoundError(error_message)

        return self._repositories[repo_name_str]

    def set_session_for_all(self, session: AsyncSession) -> None:
        """Sets the database session for all registered repositories."""
        if not isinstance(session, AsyncSession):
            error_message = "Session must be of type AsyncSession"
            logger.error(error_message)
            raise InvalidSessionTypeError(error_message)

        for repo in self._repositories.values():
            repo.set_session(session)

    def clear_session_for_all(self) -> None:
        """Clears the database session for all registered repositories."""
        for repo in self._repositories.values():
            repo.clear_session()
