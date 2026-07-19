import hashlib
import os
import uuid
from datetime import datetime, date
from typing import Dict

from nfp.domain.evidence import Evidence
from nfp.domain.business_activity import BusinessActivity
from nfp.imports.base import ImportParser
from nfp.imports.generic_csv import GenericCsvParser
from nfp.imports.manual_entry import ManualEntryParser
from nfp.imports.zerodha_parser import ZerodhaContractNoteParser
from nfp.repositories.evidence_repo import EvidenceRepository
from nfp.repositories.activity_repo import BusinessActivityRepository
from nfp.repositories.account_repo import FinancialAccountRepository
from nfp.repositories.asset_repo import AssetRepository
from nfp.core.money import Money
from nfp.core.quantity import Quantity

class ImportService:
    def __init__(self,
                 evidence_repo: EvidenceRepository,
                 activity_repo: BusinessActivityRepository,
                 account_repo: FinancialAccountRepository,
                 asset_repo: AssetRepository):
        self.evidence_repo = evidence_repo
        self.activity_repo = activity_repo
        self.account_repo = account_repo
        self.asset_repo = asset_repo
        
        self.parsers: Dict[str, ImportParser] = {
            "generic_csv": GenericCsvParser(),
            "manual_entry": ManualEntryParser(),
            "zerodha": ZerodhaContractNoteParser(),
        }

    def import_file(self, file_path: str, parser_type: str, evidence_type: str, source_institution_id: uuid.UUID = None) -> list[uuid.UUID]:
        """Imports a file, maintaining idempotency based on SHA-256 hash."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if parser_type not in self.parsers:
            raise ValueError(f"Unknown parser type: {parser_type}")
            
        # Calculate SHA-256 hash
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            content_bytes = f.read()
            hasher.update(content_bytes)
        file_hash = hasher.hexdigest()
        
        # Check idempotency
        existing_evidence = self.evidence_repo.get_by_hash(file_hash)
        if existing_evidence:
            return [] # Already imported
            
        # Create Evidence
        evidence_id = uuid.uuid4()
        now = datetime.now()
        
        evidence = Evidence(
            id=evidence_id,
            evidence_type=evidence_type,
            source_institution_id=source_institution_id,
            document_date=date.today(), # Or extract from parsed content if possible
            received_date=date.today(),
            file_reference=file_path,
            file_hash=file_hash,
            file_size_bytes=len(content_bytes),
            raw_content=None,
            version=1,
            supersedes_id=None,
            created_at=now
        )
        self.evidence_repo.add(evidence)
        
        # Parse content
        content_str = content_bytes.decode('utf-8')
        parser = self.parsers[parser_type]
        parsed_records = parser.parse(content_str)
        
        activity_ids = []
        for rec in parsed_records:
            # Resolve account
            account_id = None
            for acc in self.account_repo.get_all():
                if rec.account_identifier in (str(acc.id), acc.account_number, acc.name):
                    account_id = acc.id
                    break
            if not account_id:
                try:
                    account_id = uuid.UUID(rec.account_identifier)
                except ValueError:
                    # Auto-create account
                    account_id = uuid.uuid4()
                    from nfp.domain import FinancialAccount, AccountType
                    new_acc = FinancialAccount(
                        id=account_id,
                        account_type_code="DEMAT", # Default fallback
                        name=rec.account_identifier,
                        account_number=rec.account_identifier,
                        currency_code="INR",
                        institution_id=None,
                        opened_date=datetime.now().date(),
                        closed_date=None,
                        typed_metadata={},
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    self.account_repo.add(new_acc)
                    
            # Resolve asset
            asset_id = None
            if rec.asset_identifier:
                for ast in self.asset_repo.get_all():
                    if rec.asset_identifier in (str(ast.id), ast.symbol, ast.isin, ast.name):
                        asset_id = ast.id
                        break
                if not asset_id:
                    try:
                        asset_id = uuid.UUID(rec.asset_identifier)
                    except ValueError:
                        # Auto-create asset
                        asset_id = uuid.uuid4()
                        from nfp.domain import Asset
                        new_ast = Asset(
                            id=asset_id,
                            asset_type_code="EQUITY_UNLISTED", # Default fallback
                            name=rec.asset_identifier,
                            symbol=rec.asset_identifier[:10].upper(),
                            currency_code="INR",
                            isin=None,
                            exchange=None,
                            institution_id=None,
                            is_active=True,
                            typed_metadata={},
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        self.asset_repo.add(new_ast)
                        
            activity_id = uuid.uuid4()
            activity = BusinessActivity(
                id=activity_id,
                activity_type_code=rec.activity_type_code,
                activity_date=rec.activity_date,
                settlement_date=rec.settlement_date,
                description=rec.description,
                evidence_ids=[evidence_id],
                account_id=account_id,
                asset_id=asset_id,
                quantity=rec.quantity,
                price_per_unit=rec.price_per_unit,
                total_amount=rec.total_amount,
                typed_charges=rec.typed_charges,
                is_reversal=rec.is_reversal,
                reverses_activity_id=uuid.UUID(rec.reverses_activity_id) if rec.reverses_activity_id else None,
                status=rec.status,
                created_at=now
            )
            self.activity_repo.add(activity)
            activity_ids.append(activity_id)
            
        return activity_ids
