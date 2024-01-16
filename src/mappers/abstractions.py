import os
import sys
from abc import ABC, abstractmethod
from typing import Generic

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from app_types import D, E, S, T  # noqa


class AbstractDTOMapper(ABC, Generic[S, T]):
    """AbstractDTOMapper is an abstract class providing a base interface for
    mappers that transform data from Data Transfer Objects (DTO) to the domain
    model."""

    @abstractmethod
    def to_target(self, source_obj: S) -> T:
        """Abstract method for mapping data from a source DTO object to a
        target domain model object.

        Args:
            source_obj (S): The source Data Transfer Object (DTO) to be mapped.

        Returns:
            T: The target domain model object.
        """
        pass


class AbstractDomainEntityMapper(ABC, Generic[D, E]):
    """AbstractDomainEntityMapper is an abstract class providing a base
    interface for mappers that transform data between domain models and
    entities."""

    @abstractmethod
    def to_entity(self, domain_obj: D) -> E:
        """Abstract method for mapping data from a domain model object to an
        entity object.

        Args:
            domain_obj (D): The domain model object to be mapped.

        Returns:
            E: The entity object.
        """
        pass

    @abstractmethod
    def to_domain(self, entity_obj: E) -> D:
        """Abstract method for mapping data from an entity object to a domain
        model object.

        Args:
            entity_obj (E): The entity object to be mapped.

        Returns:
            D: The domain model object.
        """
        pass
