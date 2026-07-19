import pytest
from nfp.rules.double_entry import DoubleEntryValidator

def test_double_entry():
    validator = DoubleEntryValidator()
    assert validator.validate([]) is True
