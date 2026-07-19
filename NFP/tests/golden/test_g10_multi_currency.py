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
    def __init__(self, rates):
        self.rates = rates
    def get_rate(self, base_currency: str, target_currency: str, dt: date):
        if base_currency == target_currency: return Decimal("1.0")
        return Decimal(str(self.rates.get(dt, 1.0)))

class MockAssetRepo:
    def __init__(self, assets):
        self.assets = {a.id: a for a in assets}
    def get(self, id):
        return self.assets.get(id)

def test_g10_multi_currency():
    # 1. Setup DB
    conn = get_connection(":memory:")
    run_migrations(conn)

    event_repo = SQLiteFinancialEventRepository(conn)
    tax_provider = IndianTaxRuleProvider("reference-data/tax_rules/india_tax_rules.yaml")
    
    # Exact daily exchange rate
    rates = {
        date(2022, 1, 1): 75.0, # Buy date USD/INR
        date(2023, 1, 1): 80.0  # Sell date USD/INR
    }
    exchange_provider = MockExchangeRateProvider(rates)

    # 2. Setup Data
    asset_id = uuid.uuid4()
    account_id = uuid.uuid4()
    ledger_id = uuid.uuid4()
    
    asset = Asset(
        id=asset_id, asset_type_code="EQUITY_US", symbol="AAPL", isin=None, name="Apple",
        currency_code="USD", exchange="NASDAQ", institution_id=None, typed_metadata=None,
        is_active=True, created_at=datetime.now(), updated_at=datetime.now()
    )
    asset_repo = MockAssetRepo([asset])

    service = TaxService(None, exchange_provider, tax_provider, event_repo, asset_repo)

    # Buy 10 AAPL @ $150 = $1500 on 2022-01-01
    buy_event = FinancialEvent(
        id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=1, schema_version=1,
        event_type_code="ASSET_INCREASE", business_activity_id=uuid.uuid4(),
        account_id=account_id, asset_id=asset_id, event_date=date(2022, 1, 1),
        amount=Money(Decimal("1500"), "USD"), direction="DEBIT",
        quantity=Quantity(Decimal("10"), "UNITS"), description="Buy AAPL", created_at=datetime.now()
    )
    
    # Sell 10 AAPL @ $200 = $2000 on 2023-01-01
    sell_event = FinancialEvent(
        id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=2, schema_version=1,
        event_type_code="ASSET_DECREASE", business_activity_id=uuid.uuid4(),
        account_id=account_id, asset_id=asset_id, event_date=date(2023, 1, 1),
        amount=Money(Decimal("2000"), "USD"), direction="CREDIT",
        quantity=Quantity(Decimal("10"), "UNITS"), description="Sell AAPL", created_at=datetime.now()
    )

    for ev in [buy_event, sell_event]:
        event_repo.add(ev)

    report = service.generate_capital_gains_report(date(2023, 1, 1), date(2023, 12, 31))
    
    assert len(report) == 1
    gain = report[0]
    
    # Buy Value in INR = $1500 * 75 = 112500
    assert gain.buy_value_inr == 112500.0
    
    # Sell Value in INR = $2000 * 80 = 160000
    assert gain.sell_value_inr == 160000.0
    
    # Gain in INR = 160000 - 112500 = 47500
    assert gain.gain_inr == 47500.0
