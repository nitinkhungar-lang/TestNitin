import uuid
from datetime import date, datetime
from decimal import Decimal

from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.domain.asset import Asset
from nfp.domain.financial_event import FinancialEvent
from nfp.infrastructure.database.connection import get_connection
from nfp.infrastructure.database.migrations import run_migrations
from nfp.infrastructure.database.sqlite.event_repo import SQLiteFinancialEventRepository
from nfp.projections.engine import ProjectionEngine
from nfp.services.report_service import ReportService
from nfp.services.tax_service import TaxService
from nfp.valuation.valuation_service import ValuationService

class MockValuationProvider:
    def get_price(self, asset_id, date):
        # Suppose market price appreciates
        if date.year >= 2025:
            return 15000000.0 # 1.5 Cr
        return 5000000.0 # 50 L

class MockAssetRepo:
    def __init__(self, assets):
        self.assets = {a.id: a for a in assets}
    def get(self, id):
        return self.assets.get(id)

def test_g06_builder_payments():
    # 1. Setup DB
    conn = get_connection(":memory:")
    run_migrations(conn)
    event_repo = SQLiteFinancialEventRepository(conn)

    # 2. Setup Services
    valuation_service = ValuationService(MockValuationProvider())
    projection_engine = ProjectionEngine(event_repo=event_repo)
    
    # We can mock tax service for this test
    tax_service = TaxService(None, None, None, event_repo, None)

    # Asset
    asset_id = uuid.uuid4()
    account_id = uuid.uuid4()
    ledger_id = uuid.uuid4()
    
    asset = Asset(
        id=asset_id, asset_type_code="REAL_ESTATE", symbol=None, isin=None, name="Under Construction Flat",
        currency_code="INR", exchange=None, institution_id=None, typed_metadata=None,
        is_active=True, created_at=datetime.now(), updated_at=datetime.now()
    )
    asset_repo = MockAssetRepo([asset])
    
    report_service = ReportService(
        tax_service=tax_service,
        projection_engine=projection_engine,
        valuation_service=valuation_service,
        asset_repo=asset_repo
    )

    # Builder payments
    ev_pay1 = FinancialEvent(
        id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=1, schema_version=1,
        event_type_code="ASSET_INCREASE", business_activity_id=uuid.uuid4(),
        account_id=account_id, asset_id=asset_id, event_date=date(2022, 1, 1),
        amount=Money(Decimal("1000000"), "INR"), direction="DEBIT",
        quantity=Quantity(Decimal("1"), "UNITS"), description="Booking Amount", created_at=datetime.now()
    )
    
    ev_pay1_cash = FinancialEvent(
        id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=2, schema_version=1,
        event_type_code="CASH_OUT", business_activity_id=uuid.uuid4(),
        account_id=account_id, asset_id=None, event_date=date(2022, 1, 1),
        amount=Money(Decimal("1000000"), "INR"), direction="CREDIT",
        quantity=None, description="Booking Amount Cash Flow", created_at=datetime.now()
    )

    ev_pay2 = FinancialEvent(
        id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=3, schema_version=1,
        event_type_code="ASSET_INCREASE", business_activity_id=uuid.uuid4(),
        account_id=account_id, asset_id=asset_id, event_date=date(2023, 1, 1),
        amount=Money(Decimal("2000000"), "INR"), direction="DEBIT",
        quantity=Quantity(Decimal("0"), "UNITS"), description="Milestone 1", created_at=datetime.now()
    )

    ev_pay2_cash = FinancialEvent(
        id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=4, schema_version=1,
        event_type_code="CASH_OUT", business_activity_id=uuid.uuid4(),
        account_id=account_id, asset_id=None, event_date=date(2023, 1, 1),
        amount=Money(Decimal("2000000"), "INR"), direction="CREDIT",
        quantity=None, description="Milestone 1 Cash Flow", created_at=datetime.now()
    )

    for ev in [ev_pay1, ev_pay1_cash, ev_pay2, ev_pay2_cash]:
        event_repo.add(ev)

    # Net Worth in 2024
    nw_2024 = report_service.generate_net_worth_report(date(2024, 1, 1))
    assert len(nw_2024.items) == 1
    assert nw_2024.items[0].quantity == 1.0
    assert nw_2024.total_net_worth_inr == 5000000.0 # 50 L value

    # Net Worth in 2025 (Price Appreciated)
    nw_2025 = report_service.generate_net_worth_report(date(2025, 1, 1))
    assert nw_2025.total_net_worth_inr == 15000000.0 # 1.5 Cr value

    # Check cash flows for the period
    cf_report = report_service.generate_cash_flow_report(date(2022, 1, 1), date(2023, 12, 31))
    assert len(cf_report.items) == 2
    assert cf_report.net_cash_flow == -3000000.0 # 30 L total outflow
