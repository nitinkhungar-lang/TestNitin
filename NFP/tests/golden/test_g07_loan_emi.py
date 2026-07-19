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
    def get_price(self, asset_id, date_val):
        # Initial loan is 1000000. In 2024, after some EMIs, the principal drops to 800000
        if date_val.year >= 2024:
            return 800000.0
        return 1000000.0

class MockAssetRepo:
    def __init__(self, assets):
        self.assets = {a.id: a for a in assets}
    def get(self, id):
        return self.assets.get(id)

def test_g07_loan_emi():
    conn = get_connection(":memory:")
    run_migrations(conn)
    event_repo = SQLiteFinancialEventRepository(conn)

    valuation_service = ValuationService(MockValuationProvider())
    projection_engine = ProjectionEngine(event_repo=event_repo)
    tax_service = TaxService(None, None, None, event_repo, None)

    asset_id = uuid.uuid4()
    account_id = uuid.uuid4()
    ledger_id = uuid.uuid4()
    
    asset = Asset(
        id=asset_id, asset_type_code="LOAN", symbol=None, isin=None, name="Home Loan",
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

    # Loan Origination
    ev_loan = FinancialEvent(
        id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=1, schema_version=1,
        event_type_code="ASSET_INCREASE", business_activity_id=uuid.uuid4(),
        account_id=account_id, asset_id=asset_id, event_date=date(2023, 1, 1),
        amount=Money(Decimal("1000000"), "INR"), direction="CREDIT",
        quantity=Quantity(Decimal("1"), "UNITS"), description="Loan Disbursal", created_at=datetime.now()
    )
    
    # EMI 1
    ev_emi_prin = FinancialEvent(
        id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=2, schema_version=1,
        event_type_code="EMI_PRINCIPAL", business_activity_id=uuid.uuid4(),
        account_id=account_id, asset_id=asset_id, event_date=date(2023, 2, 1),
        amount=Money(Decimal("15000"), "INR"), direction="DEBIT",
        quantity=None, description="EMI Principal", created_at=datetime.now()
    )
    
    ev_emi_int = FinancialEvent(
        id=uuid.uuid4(), ledger_id=ledger_id, sequence_number=3, schema_version=1,
        event_type_code="EMI_INTEREST", business_activity_id=uuid.uuid4(),
        account_id=account_id, asset_id=asset_id, event_date=date(2023, 2, 1),
        amount=Money(Decimal("5000"), "INR"), direction="DEBIT",
        quantity=None, description="EMI Interest", created_at=datetime.now()
    )

    for ev in [ev_loan, ev_emi_prin, ev_emi_int]:
        event_repo.add(ev)

    # 1. Net worth check
    nw_2023 = report_service.generate_net_worth_report(date(2023, 6, 1))
    # It should decrease net worth by 10L
    assert nw_2023.total_net_worth_inr == -1000000.0

    nw_2024 = report_service.generate_net_worth_report(date(2024, 6, 1))
    # Mock says 8L in 2024
    assert nw_2024.total_net_worth_inr == -800000.0

    # 2. Cash flow check
    cf_report = report_service.generate_cash_flow_report(date(2023, 1, 1), date(2023, 12, 31))
    # Should contain principal and interest outflows
    assert len(cf_report.items) == 2
    assert cf_report.net_cash_flow == -20000.0 # 15k + 5k = 20k outflow
    
    prin_item = next(i for i in cf_report.items if i.description == "EMI Principal")
    int_item = next(i for i in cf_report.items if i.description == "EMI Interest")
    assert prin_item.flow_type == "OUTFLOW"
    assert int_item.flow_type == "OUTFLOW"
    assert prin_item.amount == 15000.0
    assert int_item.amount == 5000.0