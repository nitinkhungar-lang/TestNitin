import json
from decimal import Decimal
from datetime import date
from typing import List, Dict, Any, Optional

from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.core.metadata import EquityCharges, MfCharges
from nfp.imports.base import ImportParser, ParsedRecord

class ManualEntryParser(ImportParser):
    """Parses a structured JSON list of entries into ParsedRecords."""
    
    def parse(self, file_content: str) -> List[ParsedRecord]:
        try:
            data = json.loads(file_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
            
        if not isinstance(data, list):
            data = [data]
            
        records = []
        for item in data:
            # Parse dates
            act_date = date.fromisoformat(item["activity_date"])
            stl_date = None
            if item.get("settlement_date"):
                stl_date = date.fromisoformat(item["settlement_date"])
                
            # Parse quantity
            qty = None
            if item.get("quantity_value") and item.get("quantity_unit"):
                qty = Quantity(
                    value=Decimal(str(item["quantity_value"])),
                    unit=item["quantity_unit"]
                )
                
            # Parse price
            price = None
            if item.get("price_per_unit_amount") and item.get("price_per_unit_currency"):
                price = Money(
                    amount=Decimal(str(item["price_per_unit_amount"])),
                    currency_code=item["price_per_unit_currency"]
                )
                
            # Parse total amount
            total = Money(
                amount=Decimal(str(item["total_amount_amount"])),
                currency_code=item["total_amount_currency"]
            )
            
            # Parse charges
            charges = None
            c_data = item.get("charges")
            if c_data:
                if "brokerage" in c_data:
                    charges = EquityCharges(
                        brokerage=Money(Decimal(str(c_data.get("brokerage", 0))), total.currency_code),
                        stt=Money(Decimal(str(c_data.get("stt", 0))), total.currency_code),
                        exchange_fee=Money(Decimal(str(c_data.get("exchange_fee", 0))), total.currency_code),
                        sebi_fee=Money(Decimal(str(c_data.get("sebi_fee", 0))), total.currency_code),
                        gst=Money(Decimal(str(c_data.get("gst", 0))), total.currency_code),
                        stamp_duty=Money(Decimal(str(c_data.get("stamp_duty", 0))), total.currency_code),
                    )
                else:
                    charges = MfCharges(
                        stamp_duty=Money(Decimal(str(c_data.get("stamp_duty", 0))), total.currency_code),
                        exit_load=Money(Decimal(str(c_data.get("exit_load", 0))), total.currency_code) if "exit_load" in c_data else None,
                        stt=Money(Decimal(str(c_data.get("stt", 0))), total.currency_code) if "stt" in c_data else None,
                    )
                    
            record = ParsedRecord(
                activity_type_code=item["activity_type_code"],
                activity_date=act_date,
                settlement_date=stl_date,
                description=item.get("description", ""),
                account_identifier=item["account_identifier"],
                asset_identifier=item.get("asset_identifier"),
                quantity=qty,
                price_per_unit=price,
                total_amount=total,
                typed_charges=charges,
                is_reversal=item.get("is_reversal", False),
                reverses_activity_id=item.get("reverses_activity_id"),
                status=item.get("status", "CONFIRMED")
            )
            records.append(record)
            
        return records
