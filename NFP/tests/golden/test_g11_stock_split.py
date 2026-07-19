import pytest
import sqlite3
import uuid
from datetime import date, datetime
from decimal import Decimal

from nfp.core.clock import Clock
from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.core.metadata import SplitRatio
from nfp.domain.corporate_action import CorporateAction, CorporateActionType
from nfp.domain.lot import Lot, LotStatus
from nfp.events.event_bus import DomainEventBus
from nfp.infrastructure.database.connection import get_connection
from nfp.infrastructure.database.migrations import run_migrations
from nfp.infrastructure.database.sqlite.corporate_action_repo import SQLiteCorporateActionRepository
from nfp.infrastructure.database.sqlite.lot_repo import SQLiteLotRepository
from nfp.services.corporate_action_service import CorporateActionService

class RealClock(Clock):
    def now(self) -> datetime:
        return datetime.now()
    def today(self) -> date:
        return date.today()

def test_g11_stock_split():
    # 1. Setup DB and Services
    conn = get_connection(":memory:")
    run_migrations(conn)

    ca_repo = SQLiteCorporateActionRepository(conn)
    lot_repo = SQLiteLotRepository(conn)
    event_bus = DomainEventBus()
    clock = RealClock()

    service = CorporateActionService(ca_repo, lot_repo, event_bus, clock, conn)

    # 2. Setup Data (Asset, Account, Lots)
    asset_id = uuid.uuid4()
    account_id = uuid.uuid4()

    # Create an initial lot of 100 shares at $50 each
    initial_lot_id = uuid.uuid4()
    initial_lot = Lot(
        id=initial_lot_id,
        asset_id=asset_id,
        account_id=account_id,
        acquisition_date=date(2025, 1, 1),
        original_quantity=Quantity(Decimal("100"), "UNITS"),
        remaining_quantity=Quantity(Decimal("100"), "UNITS"),
        cost_per_unit=Money(Decimal("50"), "USD"),
        status=LotStatus.OPEN,
        source_activity_id=uuid.uuid4(),
        corporate_action_id=None,
        parent_lot_id=None,
        created_at=clock.now(),
        updated_at=clock.now()
    )
    lot_repo.add(initial_lot)

    # Create a corporate action (2:1 Stock Split)
    ca_id = uuid.uuid4()
    ca = CorporateAction(
        id=ca_id,
        asset_id=asset_id,
        action_type=CorporateActionType.SPLIT,
        record_date=date(2025, 6, 1),
        effective_date=date(2025, 6, 2),
        split_ratio=SplitRatio(
            old_face_value=Decimal("10"), 
            new_face_value=Decimal("5"), 
            numerator=2, 
            denominator=1
        ),
        new_asset_id=None,
        exchange_ratio=None,
        description="2:1 Stock Split",
        evidence_ids=[],
        created_at=clock.now()
    )
    ca_repo.add(ca)

    # 3. Execute Service
    events_received = []
    event_bus.subscribe(
        event_type=type(None), # Wait, DomainEventBus only subscribes by exact type.
        handler=lambda e: events_received.append(e)
    )
    # Actually subscribe properly:
    from nfp.events.domain_events import CorporateActionProcessed
    event_bus.subscribe(CorporateActionProcessed, lambda e: events_received.append(e))

    service.apply_action(ca_id)

    # 4. Verify Results
    updated_lot = lot_repo.get(initial_lot_id)
    assert updated_lot is not None
    assert updated_lot.status == LotStatus.ADJUSTED
    assert updated_lot.original_quantity.value == Decimal("200")
    assert updated_lot.remaining_quantity.value == Decimal("200")
    assert updated_lot.cost_per_unit.amount == Decimal("25")
    
    assert len(events_received) == 1
    event = events_received[0]
    assert event.corporate_action_id == ca_id
    assert event.action_type == "SPLIT"
    assert event.lots_adjusted == 1
