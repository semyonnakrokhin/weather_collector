import os
import sys
from abc import ABC, abstractmethod
from typing import Generic

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from app_types import D, E, S, T  # noqa


class AbstractDTOMapper(ABC, Generic[S, T]):
    @abstractmethod
    def to_target(self, source_obj: S) -> T:
        pass


class AbstractDomainEntityMapper(ABC, Generic[D, E]):
    @abstractmethod
    def to_entity(self, domain_obj: D) -> E:
        pass

    @abstractmethod
    def to_domain(self, entity_obj: E) -> D:
        pass
