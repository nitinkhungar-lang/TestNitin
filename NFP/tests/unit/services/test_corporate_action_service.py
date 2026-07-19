import uuid
import pytest
import sqlite3
from datetime import datetime, date
from decimal import Decimal

from nfp.core.clock import Clock
from nfp.core.quantity import Quantity
from nfp.core.money import Money
from nfp.domain.corporate_action import CorporateAction, CorporateActionType
from nfp.domain.lot import Lot, LotStatus
from nfp.events.event_bus import DomainEventBus
from nfp.services.corporate_action_service import CorporateActionService
from nfp.events.domain_events import CorporateActionProcessed
from nfp.core.metadata import SplitRatio


class MockCorporateActionRepo:
    def __init__(self):
        self.cas = {}
    
    def add(self, ca):
        self.cas[ca.id] = ca

    def get(self, id):
        return self.cas.get(id)
        
    def get_all(self):
        return list(self.cas.values())

class MockLotRepo:
    def __init__(self):
        self.lots = {}
        
    def add(self, lot):
        self.lots[lot.id] = lot
        
    def get(self, id):
        return self.lots.get(id)
        
    def get_all(self):
        return list(self.lots.values())

class MockEventBus(DomainEventBus):
    def __init__(self):
        self.events = []
    
    def publish(self, event):
        self.events.append(event)
        
    def subscribe(self, *args, **kwargs):
        pass

class MockClock(Clock):
    def __init__(self):
        self.current_time = datetime(2025, 1, 1, 12, 0, 0)
    
    def now(self) -> datetime:
        return self.current_time
        
    def today(self) -> date:
        return self.current_time.date()

class MockConnection:
    def execute(self, *args, **kwargs):
        pass
    def commit(self):
        pass
    def rollback(self):
        pass

@pytest.fixture
def service():
    ca_repo = MockCorporateActionRepo()
    lot_repo = MockLotRepo()
    event_bus = MockEventBus()
    clock = MockClock()
    conn = MockConnection()
    return CorporateActionService(ca_repo, lot_repo, event_bus, clock, conn), ca_repo, lot_repo, event_bus, clock

def test_apply_split(service):
    srv, ca_repo, lot_repo, event_bus, clock = service
    
    asset_id = uuid.uuid4()
    ca_id = uuid.uuid4()
    
    ca = CorporateAction(
        id=ca_id,
        asset_id=asset_id,
        action_type=CorporateActionType.SPLIT,
        record_date=date(2025, 1, 1),
        effective_date=date(2025, 1, 2),
        split_ratio=SplitRatio(old_face_value=Decimal("10"), new_face_value=Decimal("5"), numerator=2, denominator=1),
        new_asset_id=None,
        exchange_ratio=None,
        description="2:1 Split",
        evidence_ids=[],
        created_at=clock.now()
    )
    ca_repo.add(ca)
    
    lot = Lot(
        id=uuid.uuid4(),
        asset_id=asset_id,
        account_id=uuid.uuid4(),
        acquisition_date=date(2024, 1, 1),
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
    lot_repo.add(lot)
    
    srv.apply_action(ca_id)
    
    updated_lot = lot_repo.get(lot.id)
    assert updated_lot.original_quantity.value == Decimal("200")
    assert updated_lot.remaining_quantity.value == Decimal("200")
    assert updated_lot.cost_per_unit.amount == Decimal("25")
    assert updated_lot.status == LotStatus.ADJUSTED
    
    assert len(event_bus.events) == 1
    event = event_bus.events[0]
    assert isinstance(event, CorporateActionProcessed)
    assert event.corporate_action_id == ca_id
    assert event.lots_adjusted == 1

def test_apply_merger(service):
    srv, ca_repo, lot_repo, event_bus, clock = service
    
    asset_id = uuid.uuid4()
    new_asset_id = uuid.uuid4()
    ca_id = uuid.uuid4()
    
    ca = CorporateAction(
        id=ca_id,
        asset_id=asset_id,
        action_type=CorporateActionType.MERGER,
        record_date=date(2025, 1, 1),
        effective_date=date(2025, 1, 2),
        split_ratio=None,
        new_asset_id=new_asset_id,
        exchange_ratio="1.5",
        description="Merger",
        evidence_ids=[],
        created_at=clock.now()
    )
    ca_repo.add(ca)
    
    lot_id = uuid.uuid4()
    lot = Lot(
        id=lot_id,
        asset_id=asset_id,
        account_id=uuid.uuid4(),
        acquisition_date=date(2024, 1, 1),
        original_quantity=Quantity(Decimal("100"), "UNITS"),
        remaining_quantity=Quantity(Decimal("50"), "UNITS"),
        cost_per_unit=Money(Decimal("50"), "USD"),
        status=LotStatus.PARTIALLY_CONSUMED,
        source_activity_id=uuid.uuid4(),
        corporate_action_id=None,
        parent_lot_id=None,
        created_at=clock.now(),
        updated_at=clock.now()
    )
    lot_repo.add(lot)
    
    srv.apply_action(ca_id)
    
    old_lot = lot_repo.get(lot_id)
    assert old_lot.status == LotStatus.CONSUMED
    
    all_lots = lot_repo.get_all()
    assert len(all_lots) == 2
    
    new_lots = [l for l in all_lots if l.asset_id == new_asset_id]
    assert len(new_lots) == 1
    new_lot = new_lots[0]
    
    assert new_lot.original_quantity.value == Decimal("150")  # 100 * 1.5
    assert new_lot.remaining_quantity.value == Decimal("75")  # 50 * 1.5
    assert new_lot.cost_per_unit.amount == Decimal("50") / Decimal("1.5")
    assert new_lot.status == LotStatus.PARTIALLY_CONSUMED
    assert new_lot.parent_lot_id == lot_id
