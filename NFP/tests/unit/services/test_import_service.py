import os
import tempfile
import uuid
from datetime import date
from decimal import Decimal
import pytest

from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.domain.financial_account import FinancialAccount
from nfp.domain.asset import Asset
from nfp.domain.evidence import Evidence
from nfp.infrastructure.database.sqlite.evidence_repo import SQLiteEvidenceRepository
from nfp.infrastructure.database.sqlite.activity_repo import SQLiteBusinessActivityRepository
from nfp.infrastructure.database.sqlite.account_repo import SQLiteFinancialAccountRepository
from nfp.infrastructure.database.sqlite.asset_repo import SQLiteAssetRepository
from nfp.services.import_service import ImportService
from nfp.infrastructure.database.connection import get_connection

@pytest.fixture
def sqlite_conn():
    conn = get_connection(":memory:")
    from nfp.infrastructure.database.migrations import run_migrations
    run_migrations(conn)
    yield conn
    conn.close()

@pytest.fixture
def import_service(sqlite_conn):
    ev_repo = SQLiteEvidenceRepository(sqlite_conn)
    act_repo = SQLiteBusinessActivityRepository(sqlite_conn)
    acc_repo = SQLiteFinancialAccountRepository(sqlite_conn)
    ast_repo = SQLiteAssetRepository(sqlite_conn)
    
    # Pre-populate an account and asset
    from datetime import datetime
    acc_id = uuid.uuid4()
    acc = FinancialAccount(
        id=acc_id,
        account_type_code="DEMAT",
        institution_id=uuid.uuid4(),
        account_number="ACC123",
        name="Test Account",
        currency_code="INR",
        is_active=True,
        opened_date=date.today(),
        closed_date=None,
        typed_metadata=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    acc_repo.add(acc)
    
    ast_id = uuid.uuid4()
    ast = Asset(
        id=ast_id,
        asset_type_code="EQUITY",
        symbol="TCS",
        isin="INE001",
        name="TCS Equity",
        currency_code="INR",
        exchange="NSE",
        institution_id=None,
        typed_metadata=None,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    ast_repo.add(ast)
    
    return ImportService(ev_repo, act_repo, acc_repo, ast_repo), acc_id, ast_id

def test_import_service_idempotency(import_service):
    svc, acc_id, ast_id = import_service
    
    # Create temp CSV
    csv_content = (
        "activity_type_code,activity_date,settlement_date,description,account_identifier,asset_identifier,"
        "quantity_value,quantity_unit,price_per_unit_amount,price_per_unit_currency,total_amount_amount,total_amount_currency,status\n"
        f"BUY,2023-05-01,2023-05-03,Buy TCS,{acc_id},{ast_id},10,UNITS,3000,INR,30000,INR,CONFIRMED\n"
    )
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(csv_content.encode('utf-8'))
        tmp_path = tmp.name
        
    try:
        # First import
        act_ids_1 = svc.import_file(tmp_path, "generic_csv", "BROKER_CONTRACT_NOTE")
        assert len(act_ids_1) == 1
        
        # Check activities
        acts = svc.activity_repo.get_all()
        assert len(acts) == 1
        assert acts[0].account_id == acc_id
        assert acts[0].asset_id == ast_id
        assert acts[0].total_amount == Money(Decimal("30000"), "INR")
        
        # Second import (same file)
        act_ids_2 = svc.import_file(tmp_path, "generic_csv", "BROKER_CONTRACT_NOTE")
        assert len(act_ids_2) == 0 # Idempotent!
        
        # Check activities count didn't change
        acts_again = svc.activity_repo.get_all()
        assert len(acts_again) == 1
        
    finally:
        os.remove(tmp_path)
