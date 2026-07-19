import csv
from io import StringIO
from decimal import Decimal
from datetime import datetime
from typing import List

from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.core.metadata import EquityCharges
from nfp.imports.base import ImportParser, ParsedRecord

class ZerodhaContractNoteParser(ImportParser):
    """Parses a simplified Zerodha Contract Note CSV trade export.
    
    Expected CSV columns:
    trade_date (YYYY-MM-DD), security_description, buy_sell (B/S),
    quantity, gross_rate, total_amount, account_id
    """
    
    def parse(self, file_content: str) -> List[ParsedRecord]:
        records = []
        reader = csv.DictReader(StringIO(file_content))
        
        if reader.fieldnames is None:
            return []
            
        for row in reader:
            act_date = datetime.strptime(row["trade_date"].strip(), "%Y-%m-%d").date()
            
            # Zerodha settlement is typically T+1 for equity
            # We'll omit for simplicity or just assign None
            stl_date = None
            
            buy_sell = row["buy_sell"].strip().upper()
            if buy_sell == "B":
                act_type = "BUY"
            elif buy_sell == "S":
                act_type = "SELL"
            else:
                raise ValueError(f"Unknown buy_sell indicator: {buy_sell}")
                
            qty = Quantity(
                value=Decimal(row["quantity"].strip()),
                unit="UNITS"
            )
            
            price = Money(
                amount=Decimal(row["gross_rate"].strip()),
                currency_code="INR"
            )
            
            total = Money(
                amount=Decimal(row["total_amount"].strip()),
                currency_code="INR"
            )
            
            # Simple zero charges since the generic format doesn't include them
            # For a real parser, we would extract brokerage from the end of the note
            charges = EquityCharges(
                brokerage=Money(Decimal("0"), "INR"),
                stt=Money(Decimal("0"), "INR"),
                exchange_fee=Money(Decimal("0"), "INR"),
                sebi_fee=Money(Decimal("0"), "INR"),
                gst=Money(Decimal("0"), "INR"),
                stamp_duty=Money(Decimal("0"), "INR"),
            )
            
            record = ParsedRecord(
                activity_type_code=act_type,
                activity_date=act_date,
                settlement_date=stl_date,
                description=f"Zerodha Trade {act_type} {row['security_description']}",
                account_identifier=row["account_id"].strip(),
                asset_identifier=row["security_description"].strip(),
                quantity=qty,
                price_per_unit=price,
                total_amount=total,
                typed_charges=charges
            )
            records.append(record)
            
        return records
