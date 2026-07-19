import pytest
from decimal import Decimal
from nfp.core.money import Money, CurrencyRegistry, CurrencyInfo
from nfp.core.exceptions import InvalidMoneyError, CurrencyMismatchError, CurrencyNotFoundError

def test_money_valid_construction():
    m = Money(Decimal("10.50"), "USD")
    assert m.amount == Decimal("10.50")
    assert m.currency_code == "USD"

def test_money_invalid_construction_float():
    with pytest.raises(InvalidMoneyError):
        Money(10.50, "USD")  # type: ignore

def test_money_invalid_construction_empty_currency():
    with pytest.raises(InvalidMoneyError):
        Money(Decimal("10.50"), "")

def test_money_addition():
    m1 = Money(Decimal("10.50"), "USD")
    m2 = Money(Decimal("5.25"), "USD")
    result = m1 + m2
    assert result == Money(Decimal("15.75"), "USD")

def test_money_addition_currency_mismatch():
    m1 = Money(Decimal("10.50"), "USD")
    m2 = Money(Decimal("5.25"), "INR")
    with pytest.raises(CurrencyMismatchError):
        m1 + m2

def test_money_subtraction():
    m1 = Money(Decimal("10.50"), "USD")
    m2 = Money(Decimal("5.25"), "USD")
    result = m1 - m2
    assert result == Money(Decimal("5.25"), "USD")

def test_money_multiplication_decimal():
    m = Money(Decimal("10.50"), "USD")
    result = m * Decimal("2")
    assert result == Money(Decimal("21.00"), "USD")

def test_money_multiplication_invalid():
    m = Money(Decimal("10.50"), "USD")
    with pytest.raises(InvalidMoneyError):
        m * 2  # type: ignore

def test_money_division_decimal():
    m = Money(Decimal("10.50"), "USD")
    result = m / Decimal("2")
    assert result == Money(Decimal("5.25"), "USD")

def test_money_division_invalid():
    m = Money(Decimal("10.50"), "USD")
    with pytest.raises(InvalidMoneyError):
        m / 2  # type: ignore

def test_money_division_zero():
    m = Money(Decimal("10.50"), "USD")
    with pytest.raises(ZeroDivisionError):
        m / Decimal("0")

def test_money_negation():
    m = Money(Decimal("10.50"), "USD")
    result = -m
    assert result == Money(Decimal("-10.50"), "USD")

def test_money_comparisons():
    m1 = Money(Decimal("10.50"), "USD")
    m2 = Money(Decimal("5.25"), "USD")
    m3 = Money(Decimal("10.50"), "USD")

    assert m1 > m2
    assert m1 >= m2
    assert m2 < m1
    assert m2 <= m1
    assert m1 == m3
    assert m1 >= m3
    assert m1 <= m3

def test_money_comparisons_currency_mismatch():
    m1 = Money(Decimal("10.50"), "USD")
    m2 = Money(Decimal("5.25"), "INR")
    with pytest.raises(CurrencyMismatchError):
        m1 > m2

def test_money_rounding():
    registry = CurrencyRegistry.with_defaults()
    m = Money(Decimal("10.555"), "USD")
    rounded = m.round(registry)
    assert rounded == Money(Decimal("10.56"), "USD")

def test_money_rounding_jpy():
    registry = CurrencyRegistry.with_defaults()
    m = Money(Decimal("10.5"), "JPY")
    rounded = m.round(registry)
    assert rounded == Money(Decimal("11"), "JPY")

def test_money_is_positive_negative_zero():
    m_pos = Money(Decimal("10.50"), "USD")
    m_neg = Money(Decimal("-10.50"), "USD")
    m_zero = Money(Decimal("0.00"), "USD")

    assert m_pos.is_positive() is True
    assert m_pos.is_negative() is False
    assert m_pos.is_zero() is False

    assert m_neg.is_positive() is False
    assert m_neg.is_negative() is True
    assert m_neg.is_zero() is False

    assert m_zero.is_positive() is False
    assert m_zero.is_negative() is False
    assert m_zero.is_zero() is True

def test_currency_registry_get_not_found():
    registry = CurrencyRegistry()
    with pytest.raises(CurrencyNotFoundError):
        registry.get("UNK")

def test_currency_registry_defaults():
    registry = CurrencyRegistry.with_defaults()
    inr = registry.get("INR")
    usd = registry.get("USD")
    jpy = registry.get("JPY")

    assert inr.code == "INR"
    assert usd.code == "USD"
    assert jpy.code == "JPY"
