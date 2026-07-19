import pytest
import sqlite3
import uuid
from datetime import date, datetime
from decimal import Decimal

from nfp.core.clock import Clock
from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.domain.business_activity import BusinessActivity
from nfp.domain.lot import Lot, LotStatus
from nfp.rules.fifo_engine import FifoEngine
from nfp.infrastructure.database.connection import get_connection
from nfp.infrastructure.database.migrations import run_migrations
from nfp.infrastructure.database.sqlite.activity_repo import SQLiteBusinessActivityRepository
from nfp.infrastructure.database.sqlite.lot_repo import SQLiteLotRepository

class RealClock(Clock):
    def now(self) -> datetime:
        return datetime.now()
    def today(self) -> date:
        return date.today()

def test_g12_mf_switch():
    # 1. Setup DB
    conn = get_connection(":memory:")
    run_migrations(conn)

    activity_repo = SQLiteBusinessActivityRepository(conn)
    lot_repo = SQLiteLotRepository(conn)
    clock = RealClock()
    fifo_engine = FifoEngine()

    # 2. Setup Base Data
    account_id = uuid.uuid4()
    source_asset_id = uuid.uuid4()
    target_asset_id = uuid.uuid4()

    # Create an initial lot of the Source MF
    initial_lot_id = uuid.uuid4()
    initial_lot = Lot(
        id=initial_lot_id,
        asset_id=source_asset_id,
        account_id=account_id,
        acquisition_date=date(2025, 1, 1),
        original_quantity=Quantity(Decimal("100"), "UNITS"),
        remaining_quantity=Quantity(Decimal("100"), "UNITS"),
        cost_per_unit=Money(Decimal("50"), "INR"),
        status=LotStatus.OPEN,
        source_activity_id=uuid.uuid4(),
        corporate_action_id=None,
        parent_lot_id=None,
        created_at=clock.now(),
        updated_at=clock.now()
    )
    lot_repo.add(initial_lot)

    # 3. Perform MF Switch
    # A switch is recorded as a SELL of the source asset and BUY of the target asset on the same date.
    switch_date = date(2025, 6, 1)
    
    # 3.1 Switch Out (SELL)
    sell_activity_id = uuid.uuid4()
    sell_activity = BusinessActivity(
        id=sell_activity_id,
        activity_type_code="SELL",
        activity_date=switch_date,
        settlement_date=switch_date,
        description="Switch Out",
        evidence_ids=[uuid.uuid4()],
        account_id=account_id,
        asset_id=source_asset_id,
        quantity=Quantity(Decimal("100"), "UNITS"),
        price_per_unit=Money(Decimal("60"), "INR"),
        total_amount=Money(Decimal("6000"), "INR"),
        typed_charges=None,
        is_reversal=False,
        reverses_activity_id=None,
        status="CONFIRMED",
        created_at=clock.now(),
        schema_version=1
    )
    activity_repo.add(sell_activity)
    
    # Consume lot
    source_lots = [l for l in lot_repo.get_all() if l.asset_id == source_asset_id and l.status != LotStatus.CONSUMED]
    fifo_engine.consume_lots(source_lots, sell_activity.quantity, clock.now())
    for lot in source_lots:
        lot_repo.add(lot)
        
    # 3.2 Switch In (BUY)
    buy_activity_id = uuid.uuid4()
    buy_activity = BusinessActivity(
        id=buy_activity_id,
        activity_type_code="BUY",
        activity_date=switch_date,
        settlement_date=switch_date,
        description="Switch In",
        evidence_ids=[uuid.uuid4()],
        account_id=account_id,
        asset_id=target_asset_id,
        quantity=Quantity(Decimal("120"), "UNITS"),
        price_per_unit=Money(Decimal("50"), "INR"), # 6000 total amount / 50 NAV = 120 units
        total_amount=Money(Decimal("6000"), "INR"),
        typed_charges=None,
        is_reversal=False,
        reverses_activity_id=None,
        status="CONFIRMED",
        created_at=clock.now(),
        schema_version=1
    )
    activity_repo.add(buy_activity)
    
    # Create new lot
    new_lot = Lot(
        id=uuid.uuid4(),
        asset_id=target_asset_id,
        account_id=account_id,
        acquisition_date=switch_date,
        original_quantity=buy_activity.quantity,
        remaining_quantity=buy_activity.quantity,
        cost_per_unit=buy_activity.price_per_unit,
        status=LotStatus.OPEN,
        source_activity_id=buy_activity_id,
        corporate_action_id=None,
        parent_lot_id=None,
        created_at=clock.now(),
        updated_at=clock.now()
    )
    lot_repo.add(new_lot)

    # 4. Assertions
    updated_source_lot = lot_repo.get(initial_lot_id)
    assert updated_source_lot.status == LotStatus.CONSUMED
    assert updated_source_lot.remaining_quantity.value == Decimal("0")
    
    target_lots = [l for l in lot_repo.get_all() if l.asset_id == target_asset_id]
    assert len(target_lots) == 1
    assert target_lots[0].status == LotStatus.OPEN
    assert target_lots[0].original_quantity.value == Decimal("120")
    assert target_lots[0].cost_per_unit.amount == Decimal("50")
