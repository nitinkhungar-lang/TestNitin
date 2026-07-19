"""Integration tests for all SQLite repositories."""
import pytest
import sqlite3
import uuid
from datetime import date, datetime
from decimal import Decimal

from nfp.infrastructure.database.connection import get_connection
from nfp.infrastructure.database.migrations import run_migrations

from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.domain import *
from nfp.domain.institution import InstitutionType
from nfp.domain.lot import LotStatus
from nfp.domain.corporate_action import CorporateActionType
from nfp.core.exchange_rate import ExchangeRate
from nfp.domain.market_price import MarketPrice

from nfp.infrastructure.database.sqlite.ledger_repo import SQLiteLedgerRepository
from nfp.infrastructure.database.sqlite.event_repo import SQLiteFinancialEventRepository
from nfp.infrastructure.database.sqlite.activity_repo import SQLiteBusinessActivityRepository
from nfp.infrastructure.database.sqlite.evidence_repo import SQLiteEvidenceRepository
from nfp.infrastructure.database.sqlite.asset_repo import SQLiteAssetRepository
from nfp.infrastructure.database.sqlite.account_repo import SQLiteFinancialAccountRepository
from nfp.infrastructure.database.sqlite.institution_repo import SQLiteInstitutionRepository
from nfp.infrastructure.database.sqlite.lot_repo import SQLiteLotRepository
from nfp.infrastructure.database.sqlite.corporate_action_repo import SQLiteCorporateActionRepository
from nfp.infrastructure.database.sqlite.exchange_rate_repo import SQLiteExchangeRateRepository
from nfp.infrastructure.database.sqlite.market_price_repo import SQLiteMarketPriceRepository

@pytest.fixture
def db():
    conn = get_connection(":memory:")
    run_migrations(conn)
    yield conn
    conn.close()

def test_ledger_repo(db):
    repo = SQLiteLedgerRepository(db)
    ent = Ledger(id=uuid.uuid4(), version=1, last_sequence_number=0, created_at=datetime.now(), updated_at=datetime.now())
    repo.add(ent)
    fetched = repo.get(ent.id)
    assert fetched.id == ent.id
    assert fetched.id == ent.id

def test_event_repo(db):
    repo = SQLiteFinancialEventRepository(db)
    ent = FinancialEvent(id=uuid.uuid4(), ledger_id=uuid.uuid4(), sequence_number=1, schema_version=1, event_type_code="TEST", business_activity_id=uuid.uuid4(), account_id=uuid.uuid4(), asset_id=None, event_date=date(2023,1,1), amount=Money(Decimal("100"), "INR"), direction="CREDIT", quantity=None, description="Test", created_at=datetime.now())
    repo.add(ent)
    fetched = repo.get(ent.id)
    assert fetched.id == ent.id

def test_activity_repo(db):
    repo = SQLiteBusinessActivityRepository(db)
    ent = BusinessActivity(id=uuid.uuid4(), activity_type_code="TEST", activity_date=date(2023,1,1), settlement_date=None, description="Test", evidence_ids=[uuid.uuid4()], account_id=uuid.uuid4(), asset_id=None, quantity=None, price_per_unit=None, total_amount=Money(Decimal("100"), "INR"), typed_charges=None, is_reversal=False, reverses_activity_id=None, status="PENDING", created_at=datetime.now(), schema_version=1)
    repo.add(ent)
    fetched = repo.get(ent.id)
    assert fetched.id == ent.id

def test_evidence_repo(db):
    repo = SQLiteEvidenceRepository(db)
    ent = Evidence(id=uuid.uuid4(), evidence_type="MANUAL_ENTRY", source_institution_id=None, document_date=date(2023,1,1), received_date=date(2023,1,1), file_reference=None, file_hash=None, file_size_bytes=None, raw_content=None, version=1, supersedes_id=None, created_at=datetime.now(), schema_version=1)
    repo.add(ent)
    fetched = repo.get(ent.id)
    assert fetched.id == ent.id

def test_asset_repo(db):
    repo = SQLiteAssetRepository(db)
    ent = Asset(id=uuid.uuid4(), asset_type_code="EQUITY", symbol="TST", isin="IN123", name="Test", currency_code="INR", exchange="NSE", institution_id=uuid.uuid4(), typed_metadata=None, is_active=True, created_at=datetime.now(), updated_at=datetime.now(), schema_version=1)
    repo.add(ent)
    fetched = repo.get(ent.id)
    assert fetched.id == ent.id

def test_account_repo(db):
    repo = SQLiteFinancialAccountRepository(db)
    ent = FinancialAccount(id=uuid.uuid4(), account_type_code="BANK_SAVINGS", institution_id=uuid.uuid4(), account_number="123", name="Test", currency_code="INR", is_active=True, opened_date=None, closed_date=None, typed_metadata=None, created_at=datetime.now(), updated_at=datetime.now(), schema_version=1)
    repo.add(ent)
    fetched = repo.get(ent.id)
    assert fetched.id == ent.id

def test_institution_repo(db):
    repo = SQLiteInstitutionRepository(db)
    ent = Institution(id=uuid.uuid4(), name="Test", institution_type=InstitutionType.BANK, country_code="IN", website=None, customer_care_email=None, customer_care_phone=None, regulatory_id=None, is_active=True, created_at=datetime.now(), updated_at=datetime.now(), schema_version=1)
    repo.add(ent)
    fetched = repo.get(ent.id)
    assert fetched.id == ent.id

def test_lot_repo(db):
    repo = SQLiteLotRepository(db)
    ent = Lot(id=uuid.uuid4(), asset_id=uuid.uuid4(), account_id=uuid.uuid4(), acquisition_date=date(2023,1,1), original_quantity=Quantity(Decimal("10"), "UNITS"), remaining_quantity=Quantity(Decimal("10"), "UNITS"), cost_per_unit=Money(Decimal("10"), "INR"), status=LotStatus.OPEN, source_activity_id=uuid.uuid4(), corporate_action_id=None, parent_lot_id=None, created_at=datetime.now(), updated_at=datetime.now(), schema_version=1)
    repo.add(ent)
    fetched = repo.get(ent.id)
    assert fetched.id == ent.id

def test_corporate_action_repo(db):
    repo = SQLiteCorporateActionRepository(db)
    ent = CorporateAction(id=uuid.uuid4(), asset_id=uuid.uuid4(), action_type=CorporateActionType.MERGER, record_date=date(2023,1,1), effective_date=date(2023,1,1), split_ratio=None, new_asset_id=None, exchange_ratio=None, description="Test", evidence_ids=[uuid.uuid4()], created_at=datetime.now(), schema_version=1)
    repo.add(ent)
    fetched = repo.get(ent.id)
    assert fetched.id == ent.id

def test_exchange_rate_repo(db):
    repo = SQLiteExchangeRateRepository(db)
    ent = ExchangeRate(from_currency="USD", to_currency="INR", rate=Decimal("83.5"), effective_date=date(2023,1,1), source="RBI")
    repo.add(ent)
    fetched = repo.get_all()
    assert len(fetched) == 1
    assert fetched[0].from_currency == "USD"
    assert fetched[0].rate == Decimal("83.5")

def test_market_price_repo(db):
    repo = SQLiteMarketPriceRepository(db)
    ent = MarketPrice(asset_id=uuid.uuid4(), date=date(2023,1,1), price=Money(Decimal("100"), "INR"), source="NSE")
    repo.add(ent)
    fetched = repo.get_all()
    assert len(fetched) == 1
    assert fetched[0].asset_id == ent.asset_id
