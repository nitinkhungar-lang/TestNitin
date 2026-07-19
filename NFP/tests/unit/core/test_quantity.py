import pytest
from decimal import Decimal
from nfp.core.quantity import Quantity
from nfp.core.exceptions import InvalidQuantityError, UnitMismatchError

def test_quantity_valid_construction():
    q = Quantity(Decimal("10.50"), "UNITS")
    assert q.value == Decimal("10.50")
    assert q.unit == "UNITS"

def test_quantity_invalid_construction_float():
    with pytest.raises(InvalidQuantityError):
        Quantity(10.50, "UNITS")  # type: ignore

def test_quantity_invalid_unit():
    with pytest.raises(InvalidQuantityError):
        Quantity(Decimal("10.50"), "INVALID")

def test_quantity_addition():
    q1 = Quantity(Decimal("10.50"), "UNITS")
    q2 = Quantity(Decimal("5.25"), "UNITS")
    result = q1 + q2
    assert result == Quantity(Decimal("15.75"), "UNITS")

def test_quantity_addition_unit_mismatch():
    q1 = Quantity(Decimal("10.50"), "UNITS")
    q2 = Quantity(Decimal("5.25"), "GRAMS")
    with pytest.raises(UnitMismatchError):
        q1 + q2

def test_quantity_subtraction():
    q1 = Quantity(Decimal("10.50"), "UNITS")
    q2 = Quantity(Decimal("5.25"), "UNITS")
    result = q1 - q2
    assert result == Quantity(Decimal("5.25"), "UNITS")

def test_quantity_multiplication():
    q = Quantity(Decimal("10.50"), "UNITS")
    result = q * Decimal("2")
    assert result == Quantity(Decimal("21.00"), "UNITS")

def test_quantity_multiplication_invalid():
    q = Quantity(Decimal("10.50"), "UNITS")
    with pytest.raises(InvalidQuantityError):
        q * 2  # type: ignore

def test_quantity_division():
    q = Quantity(Decimal("10.50"), "UNITS")
    result = q / Decimal("2")
    assert result == Quantity(Decimal("5.25"), "UNITS")

def test_quantity_division_zero():
    q = Quantity(Decimal("10.50"), "UNITS")
    with pytest.raises(ZeroDivisionError):
        q / Decimal("0")

def test_quantity_division_invalid():
    q = Quantity(Decimal("10.50"), "UNITS")
    with pytest.raises(InvalidQuantityError):
        q / 2  # type: ignore

def test_quantity_negation():
    q = Quantity(Decimal("10.50"), "UNITS")
    result = -q
    assert result == Quantity(Decimal("-10.50"), "UNITS")

def test_quantity_is_positive_negative_zero():
    q_pos = Quantity(Decimal("10.50"), "UNITS")
    q_neg = Quantity(Decimal("-10.50"), "UNITS")
    q_zero = Quantity(Decimal("0.00"), "UNITS")

    assert q_pos.is_positive() is True
    assert q_pos.is_negative() is False
    assert q_pos.is_zero() is False

    assert q_neg.is_positive() is False
    assert q_neg.is_negative() is True
    assert q_neg.is_zero() is False

    assert q_zero.is_positive() is False
    assert q_zero.is_negative() is False
    assert q_zero.is_zero() is True

def test_quantity_comparisons():
    q1 = Quantity(Decimal("10.50"), "UNITS")
    q2 = Quantity(Decimal("5.25"), "UNITS")
    q3 = Quantity(Decimal("10.50"), "UNITS")

    assert q1 > q2
    assert q1 >= q2
    assert q2 < q1
    assert q2 <= q1
    assert q1 == q3
    assert q1 >= q3
    assert q1 <= q3

def test_quantity_comparisons_unit_mismatch():
    q1 = Quantity(Decimal("10.50"), "UNITS")
    q2 = Quantity(Decimal("5.25"), "GRAMS")
    with pytest.raises(UnitMismatchError):
        q1 > q2
