import pytest
from datetime import date
from nfp.tax.indian_provider import IndianTaxRuleProvider

def test_indian_provider():
    provider = IndianTaxRuleProvider('reference-data/tax_rules/india_tax_rules.yaml')
    rule = provider.get_holding_period_rule('MF_DEBT', date(2022, 1, 1))
    assert rule.long_term_threshold_months == 36
