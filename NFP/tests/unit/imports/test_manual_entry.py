import json
from datetime import date
from decimal import Decimal
from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.imports.manual_entry import ManualEntryParser

def test_manual_entry_parser():
    data = [
        {
            "activity_type_code": "BUY",
            "activity_date": "2023-01-01",
            "settlement_date": "2023-01-03",
            "description": "Buy 10 Reliance",
            "account_identifier": "ACC01",
            "asset_identifier": "RELIANCE",
            "quantity_value": "10",
            "quantity_unit": "UNITS",
            "price_per_unit_amount": "2500",
            "price_per_unit_currency": "INR",
            "total_amount_amount": "25000",
            "total_amount_currency": "INR",
            "charges": {
                "brokerage": "20",
                "stt": "25"
            },
            "is_reversal": False,
            "status": "CONFIRMED"
        }
    ]
    parser = ManualEntryParser()
    records = parser.parse(json.dumps(data))
    
    assert len(records) == 1
    rec = records[0]
    assert rec.activity_type_code == "BUY"
    assert rec.activity_date == date(2023, 1, 1)
    assert rec.settlement_date == date(2023, 1, 3)
    assert rec.quantity == Quantity(Decimal("10"), "UNITS")
    assert rec.price_per_unit == Money(Decimal("2500"), "INR")
    assert rec.total_amount == Money(Decimal("25000"), "INR")
    assert rec.typed_charges is not None
    assert rec.typed_charges.brokerage == Money(Decimal("20"), "INR")
