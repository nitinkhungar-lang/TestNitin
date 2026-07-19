from datetime import date
from decimal import Decimal
from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.imports.generic_csv import GenericCsvParser

def test_generic_csv_parser():
    csv_content = (
        "activity_type_code,activity_date,settlement_date,description,account_identifier,asset_identifier,"
        "quantity_value,quantity_unit,price_per_unit_amount,price_per_unit_currency,total_amount_amount,total_amount_currency,status\n"
        "SELL,2023-02-01,2023-02-03,Sell HDFC,ACC02,HDFC,5,UNITS,1500,INR,7500,INR,CONFIRMED\n"
    )
    
    parser = GenericCsvParser()
    records = parser.parse(csv_content)
    
    assert len(records) == 1
    rec = records[0]
    assert rec.activity_type_code == "SELL"
    assert rec.activity_date == date(2023, 2, 1)
    assert rec.account_identifier == "ACC02"
    assert rec.asset_identifier == "HDFC"
    assert rec.quantity == Quantity(Decimal("5"), "UNITS")
    assert rec.price_per_unit == Money(Decimal("1500"), "INR")
    assert rec.total_amount == Money(Decimal("7500"), "INR")
    assert rec.status == "CONFIRMED"
