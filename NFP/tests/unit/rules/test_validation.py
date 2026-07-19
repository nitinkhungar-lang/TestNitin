import pytest
from nfp.rules.validation import ValidationRule

def test_validation():
    rule = ValidationRule()
    assert rule is not None
