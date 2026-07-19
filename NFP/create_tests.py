import os

os.makedirs('tests/unit/rules', exist_ok=True)
os.makedirs('tests/unit/tax', exist_ok=True)
os.makedirs('tests/unit/exchange', exist_ok=True)
os.makedirs('tests/unit/valuation', exist_ok=True)
os.makedirs('tests/unit/projections', exist_ok=True)

# tests/unit/rules/test_validation.py
with open('tests/unit/rules/test_validation.py', 'w') as f:
    f.write('''\
import pytest
from nfp.rules.validation import ValidationRule

def test_validation():
    rule = ValidationRule()
    assert rule is not None
''')

# tests/unit/rules/test_fifo_engine.py
with open('tests/unit/rules/test_fifo_engine.py', 'w') as f:
    f.write('''\
import pytest
from nfp.rules.fifo_engine import FifoEngine

def test_fifo_engine():
    engine = FifoEngine()
    assert engine is not None
''')

# tests/unit/rules/test_average_cost_engine.py
with open('tests/unit/rules/test_average_cost_engine.py', 'w') as f:
    f.write('''\
import pytest
from nfp.rules.average_cost_engine import AverageCostEngine

def test_average_cost_engine():
    engine = AverageCostEngine()
    assert engine is not None
''')

# tests/unit/rules/test_double_entry.py
with open('tests/unit/rules/test_double_entry.py', 'w') as f:
    f.write('''\
import pytest
from nfp.rules.double_entry import DoubleEntryValidator

def test_double_entry():
    validator = DoubleEntryValidator()
    assert validator.validate([]) is True
''')

# tests/unit/rules/test_integrity.py
with open('tests/unit/rules/test_integrity.py', 'w') as f:
    f.write('''\
import pytest
from nfp.rules.integrity import LedgerIntegrityService

def test_integrity():
    service = LedgerIntegrityService()
    assert service.check_integrity() is True
''')

# tests/unit/tax/test_provider.py
with open('tests/unit/tax/test_provider.py', 'w') as f:
    f.write('''\
import pytest
from nfp.tax.registry import TaxRuleRegistry

def test_registry():
    registry = TaxRuleRegistry()
    assert registry is not None
''')

# tests/unit/tax/test_indian_provider.py
with open('tests/unit/tax/test_indian_provider.py', 'w') as f:
    f.write('''\
import pytest
from datetime import date
from nfp.tax.indian_provider import IndianTaxRuleProvider

def test_indian_provider():
    provider = IndianTaxRuleProvider('reference-data/tax_rules/india_tax_rules.yaml')
    rule = provider.get_holding_period_rule('MF_DEBT', date(2022, 1, 1))
    assert rule.long_term_threshold_months == 36
''')

# tests/unit/exchange/test_provider.py
with open('tests/unit/exchange/test_provider.py', 'w') as f:
    f.write('''\
import pytest
from nfp.exchange.manual_provider import ManualExchangeRateProvider

def test_manual_provider():
    provider = ManualExchangeRateProvider()
    assert provider.get_rate('USD', 'INR', None) == 1.0
''')

# tests/unit/valuation/test_provider.py
with open('tests/unit/valuation/test_provider.py', 'w') as f:
    f.write('''\
import pytest
from nfp.valuation.manual_price_provider import ManualPriceProvider
from nfp.valuation.valuation_service import ValuationService
from decimal import Decimal

def test_valuation_service():
    provider = ManualPriceProvider()
    service = ValuationService(provider)
    val = service.valuate(None, None)
    assert val.price == Decimal('100.0')
''')

# tests/unit/projections/test_engine.py
with open('tests/unit/projections/test_engine.py', 'w') as f:
    f.write('''\
import pytest
from nfp.projections.engine import ProjectionEngine

def test_projection_engine():
    engine = ProjectionEngine()
    assert engine.compute_holdings() == []
''')
