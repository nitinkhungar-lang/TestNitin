"""NFP domain module — entities, aggregates, and domain objects."""
from nfp.domain.asset import Asset
from nfp.domain.business_activity import BusinessActivity
from nfp.domain.corporate_action import CorporateAction, CorporateActionType
from nfp.domain.evidence import Evidence
from nfp.domain.financial_account import FinancialAccount
from nfp.domain.financial_event import FinancialEvent
from nfp.domain.institution import Institution, InstitutionType
from nfp.domain.ledger import Ledger
from nfp.domain.lot import Lot, LotConsumptionResult, LotStatus
from nfp.domain.ownership import Ownership
from nfp.domain.person import Person
from nfp.domain.reference_data import (
    AccountType,
    ActivityType,
    AssetType,
    Country,
    Currency,
    EventType,
)

__all__ = [
    "Asset",
    "BusinessActivity",
    "CorporateAction",
    "CorporateActionType",
    "Evidence",
    "FinancialAccount",
    "FinancialEvent",
    "Institution",
    "InstitutionType",
    "Ledger",
    "Lot",
    "LotConsumptionResult",
    "LotStatus",
    "Ownership",
    "Person",
    # Reference data
    "AccountType",
    "ActivityType",
    "AssetType",
    "Country",
    "Currency",
    "EventType",
]

from nfp.domain.market_price import MarketPrice
