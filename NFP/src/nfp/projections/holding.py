"""Holding Projection."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class HoldingProjection:
    asset_id: UUID
    quantity: float
