import csv
from io import StringIO
from decimal import Decimal
from datetime import date
from typing import List

from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.imports.base import ImportParser, ParsedRecord

class GenericCsvParser(ImportParser):
    """Parses a generic CSV format into ParsedRecords."""
    
    def parse(self, file_content: str) -> List[ParsedRecord]:
        records = []
        reader = csv.DictReader(StringIO(file_content))
        
        if reader.fieldnames is None:
            return []
            
        for row in reader:
            act_date = date.fromisoformat(row["activity_date"].strip())
            
            stl_date = None
            if row.get("settlement_date") and row["settlement_date"].strip():
                stl_date = date.fromisoformat(row["settlement_date"].strip())
                
            qty = None
            if row.get("quantity_value") and row["quantity_value"].strip() and row.get("quantity_unit"):
                qty = Quantity(
                    value=Decimal(row["quantity_value"].strip()),
                    unit=row["quantity_unit"].strip()
                )
                
            price = None
            if row.get("price_per_unit_amount") and row["price_per_unit_amount"].strip() and row.get("price_per_unit_currency"):
                price = Money(
                    amount=Decimal(row["price_per_unit_amount"].strip()),
                    currency_code=row["price_per_unit_currency"].strip()
                )
                
            total = Money(
                amount=Decimal(row["total_amount_amount"].strip()),
                currency_code=row["total_amount_currency"].strip()
            )
            
            record = ParsedRecord(
                activity_type_code=row["activity_type_code"].strip(),
                activity_date=act_date,
                settlement_date=stl_date,
                description=row.get("description", "").strip(),
                account_identifier=row["account_identifier"].strip(),
                asset_identifier=row.get("asset_identifier", "").strip() or None,
                quantity=qty,
                price_per_unit=price,
                total_amount=total,
                status=row.get("status", "CONFIRMED").strip() or "CONFIRMED"
            )
            records.append(record)
            
        return records
