"""Evidence repository interface."""
import abc
from uuid import UUID
from typing import Optional, List
from nfp.domain import Evidence
from nfp.repositories.base import Repository

class EvidenceRepository(Repository[Evidence, UUID], abc.ABC):
    """Repository interface for Evidence."""
    
    @abc.abstractmethod
    def get_by_hash(self, file_hash: str) -> Optional[Evidence]:
        """Get evidence by its SHA-256 file hash."""
        pass
