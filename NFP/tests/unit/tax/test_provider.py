import pytest
from nfp.tax.registry import TaxRuleRegistry

def test_registry():
    registry = TaxRuleRegistry()
    assert registry is not None
