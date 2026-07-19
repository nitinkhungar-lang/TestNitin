import pytest
import sqlite3
import uuid
from datetime import date, datetime
from decimal import Decimal

from nfp.core.clock import Clock
from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.domain.asset import Asset
from nfp.domain.financial_event import FinancialEvent
from nfp.domain.business_activity import BusinessActivity
from nfp.infrastructure.database.connection import get_connection
from nfp.infrastructure.database.migrations import run_migrations
from nfp.infrastructure.database.sqlite.event_repo import SQLiteFinancialEventRepository
from nfp.services.tax_service import TaxService
from nfp.tax.indian_provider import IndianTaxRuleProvider
from nfp.exchange.provider import ExchangeRateProvider

class RealClock(Clock):
    def now(self) -> datetime: return datetime.now()
    def today(self) -> date: return date.today()

class MockExchangeRateProvider(ExchangeRateProvider):
    def get_rate(self, base_currency: str, target_currency: str, dt: date): return Decimal("1.0")

class MockAssetRepo:
    def __init__(self, assets): self.assets = {a.id: a for a in assets}
    def get(self, id): return self.assets.get(id)
    
class MockActivityRepo:
    def __init__(self, activities): self.activities = {a.id: a for a in activities}
    def get(self, id): return self.activities.get(id)

def test_g09_reversal_correction():
    # 1. Setup DB
    conn = get_connection(":memory:")
    run_migrations(conn)

    event_repo = SQLiteFinancialEventRepository(conn)
    tax_provider = IndianTaxRuleProvider("reference-data/tax_rules/india_tax_rules.yaml")
    exchange_provider = MockExchangeRateProvider()

    asset_id = uuid.uuid4()
    account_id = uuid.uuid4()
    ledger_id = uuid.uuid4()
    
    asset = Asset(
        id=asset_id, asset_type_code="EQUITY_IN", symbol="RELIANCE", isin=None, name="Reliance",
        currency_code="INR", exchange="NSE", institution_id=None, typed_metadata=None,
        is_active=True, created_at=datetime.now(), updated_at=datetime.now()
    )
    asset_repo = MockAssetRepo([asset])

    act1_id = uuid.uuid4()
    act2_id = uuid.uuid4()
    act2_rev_id = uuid.uuid4()
    
    act1 = BusinessActivity(id=act1_id, activity_type_code="BUY", activity_date=date(2022, 1, 1), settlement_date=None, description="", evidence_ids=[uuid.uuid4()], account_id=account_id, asset_id=asset_id, quantity=Quantity(Decimal("100"), "UNITS"), price_per_unit=Money(Decimal("100"), "INR"), total_amount=Money(Decimal("10000"), "INR"), typed_charges=None, is_reversal=False, reverses_activity_id=None, status="CONFIRMED", created_at=datetime.now())
    act2 = BusinessActivity(id=act2_id, activity_type_code="SELL", activity_date=date(2023, 1, 1), settlement_date=None, description="", evidence_ids=[uuid.uuid4()], account_id=account_id, asset_id=asset_id, quantity=Quantity(Decimal("100"), "UNITS"), price_per_unit=Money(Decimal("150"), "INR"), total_amount=Money(Decimal("15000"), "INR"), typed_charges=None, is_reversal=False, reverses_activity_id=None, status="REVERSED", created_at=datetime.now())
    act2_rev = BusinessActivity(id=act2_rev_id, activity_type_code="SELL", activity_date=date(2023, 1, 2), settlement_date=None, description="Reversal", evidence_ids=[uuid.uuid4()], account_id=account_id, asset_id=asset_id, quantity=Quantity(Decimal("100"), "UNITS"), price_per_unit=Money(Decimal("150"), "INR"), total_amount=Money(Decimal("15000"), "INR"), typed_charges=None, is_reversal=True, reverses_activity_id=act2_id, status="CONFIRMED", created_at=datetime.now())
    
    activity_repo = MockActivityRepo([act1, act2, act2_rev])
    
    service = TaxService(None, exchange_provider, tax_provider, event_repo, asset_repo)
    # inject activity repo to service/engine!
    service.projection_engine.activity_repo = activity_repo

    # Events for ACT1 (BUY)
    ev_buy = FinancialEvent(id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=1, schema_version=1, event_type_code="ASSET_INCREASE", business_activity_id=act1_id, account_id=account_id, asset_id=asset_id, event_date=date(2022, 1, 1), amount=Money(Decimal("10000"), "INR"), direction="DEBIT", quantity=Quantity(Decimal("100"), "UNITS"), description="", created_at=datetime.now())
    
    # Events for ACT2 (SELL - later reversed)
    ev_sell = FinancialEvent(id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=2, schema_version=1, event_type_code="ASSET_DECREASE", business_activity_id=act2_id, account_id=account_id, asset_id=asset_id, event_date=date(2023, 1, 1), amount=Money(Decimal("15000"), "INR"), direction="CREDIT", quantity=Quantity(Decimal("100"), "UNITS"), description="", created_at=datetime.now())
    
    # Events for ACT2_REV (Reversal of ACT2)
    ev_sell_rev = FinancialEvent(id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=3, schema_version=1, event_type_code="ASSET_INCREASE", business_activity_id=act2_rev_id, account_id=account_id, asset_id=asset_id, event_date=date(2023, 1, 2), amount=Money(Decimal("15000"), "INR"), direction="DEBIT", quantity=Quantity(Decimal("100"), "UNITS"), description="", created_at=datetime.now())
    
    for ev in [ev_buy, ev_sell, ev_sell_rev]:
        event_repo.add(ev)

    report = service.generate_capital_gains_report(date(2023, 1, 1), date(2023, 12, 31))
    
    # Because ACT2 is reversed and ACT2_REV is a reversal, neither should generate capital gains!
    # Or they cancel each other out? Wait, if we use activity_repo to filter, there should be NO gains!
    assert len(report) == 0
