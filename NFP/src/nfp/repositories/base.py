"""Base repository interfaces."""
import abc
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')
ID = TypeVar('ID')

class Repository(Generic[T, ID], abc.ABC):
    """Base repository interface."""
    @abc.abstractmethod
    def add(self, entity: T) -> None:
        pass

    @abc.abstractmethod
    def get(self, id: ID) -> Optional[T]:
        pass
        
    @abc.abstractmethod
    def get_all(self) -> List[T]:
        pass
