import pytest
from datetime import date
from decimal import Decimal
from nfp.core.metadata import (
    FdMetadata,
    RealEstateMetadata,
    LoanMetadata,
    EquityCharges,
    MfCharges,
    SplitRatio,
)
from nfp.core.money import Money

def test_fd_metadata_valid():
    fd = FdMetadata(date(2025, 1, 1), Decimal("7.25"), "QUARTERLY", True)
    assert fd.maturity_date == date(2025, 1, 1)
    assert fd.annual_interest_rate == Decimal("7.25")
    assert fd.compounding == "QUARTERLY"
    assert fd.auto_renewal is True

def test_fd_metadata_invalid_compounding():
    with pytest.raises(ValueError):
        FdMetadata(date(2025, 1, 1), Decimal("7.25"), "INVALID", True)

def test_fd_metadata_invalid_rate():
    with pytest.raises(ValueError):
        FdMetadata(date(2025, 1, 1), Decimal("-7.25"), "QUARTERLY", True)
    with pytest.raises(ValueError):
        FdMetadata(date(2025, 1, 1), Decimal("0"), "QUARTERLY", True)

def test_real_estate_metadata_valid():
    re = RealEstateMetadata("123 Main St", "City", "State", "12345", "FLAT")
    assert re.property_type == "FLAT"

def test_real_estate_metadata_invalid_property_type():
    with pytest.raises(ValueError):
        RealEstateMetadata("123 Main St", "City", "State", "12345", "INVALID")

def test_loan_metadata_valid():
    loan = LoanMetadata(Decimal("100000"), "USD", Decimal("5.0"), 120, date(2024, 1, 1), "HOME")
    assert loan.loan_type == "HOME"

def test_loan_metadata_invalid_loan_type():
    with pytest.raises(ValueError):
        LoanMetadata(Decimal("100000"), "USD", Decimal("5.0"), 120, date(2024, 1, 1), "INVALID")

def test_loan_metadata_invalid_tenure():
    with pytest.raises(ValueError):
        LoanMetadata(Decimal("100000"), "USD", Decimal("5.0"), 0, date(2024, 1, 1), "HOME")

def test_equity_charges_total():
    charges = EquityCharges(
        brokerage=Money(Decimal("0"), "INR"),
        stt=Money(Decimal("25.00"), "INR"),
        exchange_fee=Money(Decimal("8.63"), "INR"),
        sebi_fee=Money(Decimal("0.25"), "INR"),
        gst=Money(Decimal("1.55"), "INR"),
        stamp_duty=Money(Decimal("37.50"), "INR"),
    )
    assert charges.total == Money(Decimal("72.93"), "INR")

def test_mf_charges_total():
    charges1 = MfCharges(stamp_duty=Money(Decimal("10.00"), "INR"))
    assert charges1.total == Money(Decimal("10.00"), "INR")

    charges2 = MfCharges(
        stamp_duty=Money(Decimal("10.00"), "INR"),
        exit_load=Money(Decimal("5.00"), "INR"),
        stt=Money(Decimal("2.00"), "INR"),
    )
    assert charges2.total == Money(Decimal("17.00"), "INR")

def test_split_ratio_valid():
    ratio = SplitRatio(Decimal("10"), Decimal("5"), 2, 1)
    assert ratio.quantity_multiplier == Decimal("2")
    assert ratio.price_divisor == Decimal("2")

def test_split_ratio_invalid():
    with pytest.raises(ValueError):
        SplitRatio(Decimal("10"), Decimal("5"), 0, 1)
    with pytest.raises(ValueError):
        SplitRatio(Decimal("10"), Decimal("5"), 2, 0)
