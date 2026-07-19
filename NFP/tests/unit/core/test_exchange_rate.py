import pytest
from datetime import date
from decimal import Decimal
from nfp.core.exchange_rate import ExchangeRate
from nfp.core.money import Money
from nfp.core.exceptions import CurrencyMismatchError

def test_exchange_rate_valid():
    rate = ExchangeRate("USD", "INR", Decimal("83.50"), date(2024, 1, 15), "RBI")
    assert rate.from_currency == "USD"
    assert rate.to_currency == "INR"
    assert rate.rate == Decimal("83.50")
    assert rate.effective_date == date(2024, 1, 15)
    assert rate.source == "RBI"

def test_exchange_rate_invalid_type():
    with pytest.raises(TypeError):
        ExchangeRate("USD", "INR", 83.50, date(2024, 1, 15), "RBI") # type: ignore

def test_exchange_rate_non_positive():
    with pytest.raises(ValueError):
        ExchangeRate("USD", "INR", Decimal("-1.0"), date(2024, 1, 15), "RBI")
    with pytest.raises(ValueError):
        ExchangeRate("USD", "INR", Decimal("0.0"), date(2024, 1, 15), "RBI")

def test_exchange_rate_convert():
    rate = ExchangeRate("USD", "INR", Decimal("83.50"), date(2024, 1, 15), "RBI")
    m = Money(Decimal("100"), "USD")
    result = rate.convert(m)
    assert result == Money(Decimal("8350.00"), "INR")

def test_exchange_rate_convert_mismatch():
    rate = ExchangeRate("USD", "INR", Decimal("83.50"), date(2024, 1, 15), "RBI")
    m = Money(Decimal("100"), "EUR")
    with pytest.raises(CurrencyMismatchError):
        rate.convert(m)

def test_exchange_rate_inverse():
    rate = ExchangeRate("USD", "INR", Decimal("80.00"), date(2024, 1, 15), "RBI")
    inverse_rate = rate.inverse()
    assert inverse_rate.from_currency == "INR"
    assert inverse_rate.to_currency == "USD"
    assert inverse_rate.rate == Decimal("0.0125")
    assert inverse_rate.effective_date == date(2024, 1, 15)
    assert inverse_rate.source == "RBI"
