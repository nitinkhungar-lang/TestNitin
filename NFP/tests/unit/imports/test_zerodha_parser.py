from datetime import date
from decimal import Decimal
from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.imports.zerodha_parser import ZerodhaContractNoteParser

def test_zerodha_parser():
    csv_content = (
        "trade_date,security_description,buy_sell,quantity,gross_rate,total_amount,account_id\n"
        "2023-03-01,INFY,B,20,1200.50,24010.00,ZERODHA01\n"
    )
    
    parser = ZerodhaContractNoteParser()
    records = parser.parse(csv_content)
    
    assert len(records) == 1
    rec = records[0]
    assert rec.activity_type_code == "BUY"
    assert rec.activity_date == date(2023, 3, 1)
    assert rec.account_identifier == "ZERODHA01"
    assert rec.asset_identifier == "INFY"
    assert rec.quantity == Quantity(Decimal("20"), "UNITS")
    assert rec.price_per_unit == Money(Decimal("1200.50"), "INR")
    assert rec.total_amount == Money(Decimal("24010.00"), "INR")
    assert rec.typed_charges is not None
    assert rec.typed_charges.brokerage == Money(Decimal("0"), "INR")
