import pytest
from datetime import date
from nfp.core.date_range import DateRange
from nfp.core.exceptions import InvalidDateRangeError

def test_date_range_valid():
    dr = DateRange(date(2024, 1, 1), date(2024, 1, 31))
    assert dr.start == date(2024, 1, 1)
    assert dr.end == date(2024, 1, 31)

def test_date_range_invalid():
    with pytest.raises(InvalidDateRangeError):
        DateRange(date(2024, 1, 31), date(2024, 1, 1))

def test_date_range_contains():
    dr = DateRange(date(2024, 1, 1), date(2024, 1, 31))
    assert dr.contains(date(2024, 1, 1)) is True
    assert dr.contains(date(2024, 1, 15)) is True
    assert dr.contains(date(2024, 1, 31)) is True
    assert dr.contains(date(2023, 12, 31)) is False
    assert dr.contains(date(2024, 2, 1)) is False

def test_date_range_overlaps():
    dr1 = DateRange(date(2024, 1, 1), date(2024, 1, 31))
    dr2 = DateRange(date(2024, 1, 15), date(2024, 2, 15))
    dr3 = DateRange(date(2024, 2, 1), date(2024, 2, 28))

    assert dr1.overlaps(dr2) is True
    assert dr2.overlaps(dr1) is True
    assert dr1.overlaps(dr3) is False

def test_date_range_days():
    dr = DateRange(date(2024, 1, 1), date(2024, 1, 31))
    assert dr.days == 30

def test_date_range_financial_year_india():
    fy = DateRange.financial_year_india(2024)
    assert fy.start == date(2024, 4, 1)
    assert fy.end == date(2025, 3, 31)
