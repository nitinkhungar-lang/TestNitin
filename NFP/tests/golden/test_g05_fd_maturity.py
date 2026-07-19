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
    def now(self) -> datetime: return datetime.now()
    def today(self) -> date: return date.today()

class MockExchangeRateProvider(ExchangeRateProvider):
    def get_rate(self, base_currency: str, target_currency: str, dt: date): return Decimal("1.0")

class MockAssetRepo:
    def __init__(self, assets): self.assets = {a.id: a for a in assets}
    def get(self, id): return self.assets.get(id)

def test_g05_fd_maturity():
    # 1. Setup DB
    conn = get_connection(":memory:")
    run_migrations(conn)

    event_repo = SQLiteFinancialEventRepository(conn)
    # create dummy tax rules for FD to avoid ValueError
    # But wait, FD might not be in our yaml! Let's just mock it or assume it falls to a default or we use an existing one.
    # Actually, I will add "FIXED_DEPOSIT" to the yaml in my setup or just mock the provider.
    class MockTaxProvider:
        def get_holding_period_rule(self, asset_type: str, acquisition_date: date):
            from nfp.tax.provider import HoldingPeriodRule
            return HoldingPeriodRule(asset_types=["FIXED_DEPOSIT"], long_term_threshold_months=36)
            
    tax_provider = MockTaxProvider()
    exchange_provider = MockExchangeRateProvider()

    asset_id = uuid.uuid4()
    account_id = uuid.uuid4()
    ledger_id = uuid.uuid4()
    
    asset = Asset(
        id=asset_id, asset_type_code="FIXED_DEPOSIT", symbol=None, isin=None, name="HDFC FD",
        currency_code="INR", exchange=None, institution_id=None, typed_metadata=None,
        is_active=True, created_at=datetime.now(), updated_at=datetime.now()
    )
    asset_repo = MockAssetRepo([asset])
    
    service = TaxService(None, exchange_provider, tax_provider, event_repo, asset_repo)

    # FD Created (Buy)
    ev_buy = FinancialEvent(id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=1, schema_version=1, event_type_code="ASSET_INCREASE", business_activity_id=uuid.uuid4(), account_id=account_id, asset_id=asset_id, event_date=date(2022, 1, 1), amount=Money(Decimal("100000"), "INR"), direction="DEBIT", quantity=Quantity(Decimal("1"), "UNITS"), description="FD Invest", created_at=datetime.now())
    
    # FD Matures (Sell principal)
    ev_sell = FinancialEvent(id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=2, schema_version=1, event_type_code="ASSET_DECREASE", business_activity_id=uuid.uuid4(), account_id=account_id, asset_id=asset_id, event_date=date(2025, 1, 1), amount=Money(Decimal("100000"), "INR"), direction="CREDIT", quantity=Quantity(Decimal("1"), "UNITS"), description="FD Maturity", created_at=datetime.now())
    
    # FD Interest (Income, does not consume quantity)
    ev_interest = FinancialEvent(id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=3, schema_version=1, event_type_code="INCOME", business_activity_id=uuid.uuid4(), account_id=account_id, asset_id=asset_id, event_date=date(2025, 1, 1), amount=Money(Decimal("15000"), "INR"), direction="CREDIT", quantity=None, description="FD Interest", created_at=datetime.now())
    
    for ev in [ev_buy, ev_sell, ev_interest]:
        event_repo.add(ev)

    report = service.generate_capital_gains_report(date(2025, 1, 1), date(2025, 12, 31))
    
    # Should generate one capital gain item for the principal with gain = 0
    assert len(report) == 1
    assert report[0].gain_inr == 0.0
    assert report[0].sell_value_inr == 100000.0
    assert report[0].buy_value_inr == 100000.0
