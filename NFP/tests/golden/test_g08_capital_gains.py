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
from nfp.infrastructure.database.connection import get_connection
from nfp.infrastructure.database.migrations import run_migrations
from nfp.infrastructure.database.sqlite.event_repo import SQLiteFinancialEventRepository
from nfp.services.tax_service import TaxService
from nfp.tax.indian_provider import IndianTaxRuleProvider
from nfp.exchange.provider import ExchangeRateProvider

class RealClock(Clock):
    def now(self) -> datetime:
        return datetime.now()
    def today(self) -> date:
        return date.today()

class MockExchangeRateProvider(ExchangeRateProvider):
    def get_rate(self, base_currency: str, target_currency: str, date: date):
        return Decimal("1.0")

class MockAssetRepo:
    def __init__(self, assets):
        self.assets = {a.id: a for a in assets}
    def get(self, id):
        return self.assets.get(id)

def test_g08_capital_gains():
    # 1. Setup DB
    conn = get_connection(":memory:")
    run_migrations(conn)

    event_repo = SQLiteFinancialEventRepository(conn)
    tax_provider = IndianTaxRuleProvider("reference-data/tax_rules/india_tax_rules.yaml")
    exchange_provider = MockExchangeRateProvider()

    # 2. Setup Data
    asset_id_pre2023 = uuid.uuid4()
    asset_id_post2023 = uuid.uuid4()
    account_id = uuid.uuid4()
    ledger_id = uuid.uuid4()
    
    asset_pre = Asset(
        id=asset_id_pre2023, asset_type_code="MF_DEBT", symbol="PRE", isin=None, name="PRE",
        currency_code="INR", exchange=None, institution_id=None, typed_metadata=None,
        is_active=True, created_at=datetime.now(), updated_at=datetime.now()
    )
    asset_post = Asset(
        id=asset_id_post2023, asset_type_code="MF_DEBT", symbol="POST", isin=None, name="POST",
        currency_code="INR", exchange=None, institution_id=None, typed_metadata=None,
        is_active=True, created_at=datetime.now(), updated_at=datetime.now()
    )
    asset_repo = MockAssetRepo([asset_pre, asset_post])

    service = TaxService(None, exchange_provider, tax_provider, event_repo, asset_repo)

    # Pre 2023 Debt MF Buy
    buy_event_1 = FinancialEvent(
        id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=1, schema_version=1,
        event_type_code="ASSET_INCREASE", business_activity_id=uuid.uuid4(),
        account_id=account_id, asset_id=asset_id_pre2023, event_date=date(2022, 1, 1),
        amount=Money(Decimal("10000"), "INR"), direction="DEBIT",
        quantity=Quantity(Decimal("100"), "UNITS"), description="Buy", created_at=datetime.now()
    )
    
    # Post 2023 Debt MF Buy
    buy_event_2 = FinancialEvent(
        id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=2, schema_version=1,
        event_type_code="ASSET_INCREASE", business_activity_id=uuid.uuid4(),
        account_id=account_id, asset_id=asset_id_post2023, event_date=date(2023, 5, 1),
        amount=Money(Decimal("10000"), "INR"), direction="DEBIT",
        quantity=Quantity(Decimal("100"), "UNITS"), description="Buy", created_at=datetime.now()
    )
    
    # Sell Pre 2023 in 2025 (Long term: 3 years. Actually 2022 to 2025 is > 3 years (36 months))
    sell_event_1 = FinancialEvent(
        id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=3, schema_version=1,
        event_type_code="ASSET_DECREASE", business_activity_id=uuid.uuid4(),
        account_id=account_id, asset_id=asset_id_pre2023, event_date=date(2025, 2, 1),
        amount=Money(Decimal("15000"), "INR"), direction="CREDIT",
        quantity=Quantity(Decimal("100"), "UNITS"), description="Sell", created_at=datetime.now()
    )
    
    # Sell Post 2023 in 2025 (Any duration post 2023 is short term effectively because of 999999 months limit)
    sell_event_2 = FinancialEvent(
        id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=4, schema_version=1,
        event_type_code="ASSET_DECREASE", business_activity_id=uuid.uuid4(),
        account_id=account_id, asset_id=asset_id_post2023, event_date=date(2025, 2, 1),
        amount=Money(Decimal("15000"), "INR"), direction="CREDIT",
        quantity=Quantity(Decimal("100"), "UNITS"), description="Sell", created_at=datetime.now()
    )

    for ev in [buy_event_1, buy_event_2, sell_event_1, sell_event_2]:
        event_repo.add(ev)

    report = service.generate_capital_gains_report(date(2025, 1, 1), date(2025, 12, 31))
    
    assert len(report) == 2
    
    # Pre 2023 logic
    r_pre = next(r for r in report if r.asset_id == asset_id_pre2023)
    assert r_pre.term == "LONG"
    assert r_pre.tax_rate == 0.10
    
    # Post 2023 logic
    r_post = next(r for r in report if r.asset_id == asset_id_post2023)
    assert r_post.term == "SHORT"
    assert r_post.tax_rate == 0.30
