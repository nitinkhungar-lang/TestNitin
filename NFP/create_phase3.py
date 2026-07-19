import os

# --- src/nfp/rules/validation.py ---
os.makedirs('src/nfp/rules', exist_ok=True)
with open('src/nfp/rules/validation.py', 'w') as f:
    f.write('''\
"""Validation rules for FinancialEvent and BusinessActivity."""
from nfp.domain.financial_event import FinancialEvent

class ValidationRule:
    def validate(self, event: FinancialEvent) -> None:
        if event.amount.amount < 0:
            raise ValueError("Event amount cannot be negative")
''')

# --- src/nfp/rules/fifo_engine.py ---
with open('src/nfp/rules/fifo_engine.py', 'w') as f:
    f.write('''\
"""FIFO Engine to consume Lots."""
from typing import List
from datetime import datetime
from nfp.domain.lot import Lot, LotConsumptionResult
from nfp.core.quantity import Quantity
from nfp.core.exceptions import InsufficientLotQuantityError

class FifoEngine:
    def consume_lots(self, lots: List[Lot], quantity: Quantity, updated_at: datetime) -> List[LotConsumptionResult]:
        lots = sorted(lots, key=lambda l: l.acquisition_date)
        results = []
        remaining = quantity
        for lot in lots:
            if remaining.is_zero():
                break
            if lot.remaining_quantity.is_zero():
                continue
            to_consume = min(lot.remaining_quantity, remaining)
            result = lot.consume(to_consume, updated_at)
            results.append(result)
            remaining -= to_consume
        if not remaining.is_zero():
            raise InsufficientLotQuantityError(str(remaining), "not enough lots")
        return results
''')

# --- src/nfp/rules/average_cost_engine.py ---
with open('src/nfp/rules/average_cost_engine.py', 'w') as f:
    f.write('''\
"""Average Cost Engine."""
class AverageCostEngine:
    pass
''')

# --- src/nfp/rules/double_entry.py ---
with open('src/nfp/rules/double_entry.py', 'w') as f:
    f.write('''\
"""Double Entry Validator."""
from typing import List
from nfp.domain.financial_event import FinancialEvent

class DoubleEntryValidator:
    def validate(self, events: List[FinancialEvent]) -> bool:
        return True
''')

# --- src/nfp/rules/integrity.py ---
with open('src/nfp/rules/integrity.py', 'w') as f:
    f.write('''\
"""Ledger Integrity Service."""
class LedgerIntegrityService:
    def check_integrity(self) -> bool:
        return True
''')

# --- src/nfp/rules/__init__.py ---
with open('src/nfp/rules/__init__.py', 'w') as f:
    f.write('')

# --- src/nfp/tax/provider.py ---
os.makedirs('src/nfp/tax', exist_ok=True)
with open('src/nfp/tax/provider.py', 'w') as f:
    f.write('''\
"""Tax Rule Provider ABC."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class HoldingPeriodRule:
    asset_types: List[str]
    long_term_threshold_months: int
    condition: Optional[str] = None

@dataclass
class TaxRate:
    rate: float

@dataclass
class TaxJurisdiction:
    code: str

class TaxRuleProvider(ABC):
    @abstractmethod
    def get_holding_period_rule(self, asset_type: str, acquisition_date) -> HoldingPeriodRule:
        pass
''')

# --- src/nfp/tax/registry.py ---
with open('src/nfp/tax/registry.py', 'w') as f:
    f.write('''\
"""Tax Rule Registry."""
class TaxRuleRegistry:
    def __init__(self):
        self.providers = {}
        
    def register(self, jurisdiction: str, provider):
        self.providers[jurisdiction] = provider
        
    def get_provider(self, jurisdiction: str):
        return self.providers.get(jurisdiction)
''')

# --- src/nfp/tax/indian_provider.py ---
with open('src/nfp/tax/indian_provider.py', 'w') as f:
    f.write('''\
"""Indian Tax Rule Provider."""
import yaml
from datetime import date
from typing import List
from nfp.tax.provider import TaxRuleProvider, HoldingPeriodRule

class IndianTaxRuleProvider(TaxRuleProvider):
    def __init__(self, yaml_path: str):
        with open(yaml_path, 'r') as f:
            self.data = yaml.safe_load(f)
            
    def get_holding_period_rule(self, asset_type: str, acquisition_date: date) -> HoldingPeriodRule:
        rules = self.data.get('rules', {}).get('holding_period_rules', [])
        for r in rules:
            if asset_type in r.get('asset_types', []):
                cond = r.get('condition')
                if cond:
                    if "acquisition_date < '2023-04-01'" in cond and acquisition_date < date(2023, 4, 1):
                        return HoldingPeriodRule(asset_types=r['asset_types'], long_term_threshold_months=r['long_term_threshold_months'], condition=cond)
                    elif "acquisition_date >= '2023-04-01'" in cond and acquisition_date >= date(2023, 4, 1):
                        return HoldingPeriodRule(asset_types=r['asset_types'], long_term_threshold_months=r['long_term_threshold_months'], condition=cond)
                else:
                    return HoldingPeriodRule(asset_types=r['asset_types'], long_term_threshold_months=r['long_term_threshold_months'])
        raise ValueError("No rule found")
''')

# --- src/nfp/tax/__init__.py ---
with open('src/nfp/tax/__init__.py', 'w') as f:
    f.write('')

# --- src/nfp/exchange/provider.py ---
os.makedirs('src/nfp/exchange', exist_ok=True)
with open('src/nfp/exchange/provider.py', 'w') as f:
    f.write('''\
"""Exchange Rate Provider ABC."""
from abc import ABC, abstractmethod
class ExchangeRateProvider(ABC):
    @abstractmethod
    def get_rate(self, base_currency: str, target_currency: str, date):
        pass
''')

# --- src/nfp/exchange/manual_provider.py ---
with open('src/nfp/exchange/manual_provider.py', 'w') as f:
    f.write('''\
"""Manual Exchange Rate Provider."""
from nfp.exchange.provider import ExchangeRateProvider
class ManualExchangeRateProvider(ExchangeRateProvider):
    def get_rate(self, base_currency: str, target_currency: str, date):
        return 1.0
''')

# --- src/nfp/exchange/__init__.py ---
with open('src/nfp/exchange/__init__.py', 'w') as f:
    f.write('')

# --- src/nfp/valuation/price_provider.py ---
os.makedirs('src/nfp/valuation', exist_ok=True)
with open('src/nfp/valuation/price_provider.py', 'w') as f:
    f.write('''\
"""Price Provider ABC."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class AssetValuation:
    price: Decimal

class PriceProvider(ABC):
    @abstractmethod
    def get_price(self, asset_id, date) -> AssetValuation:
        pass
''')

# --- src/nfp/valuation/manual_price_provider.py ---
with open('src/nfp/valuation/manual_price_provider.py', 'w') as f:
    f.write('''\
"""Manual Price Provider."""
from decimal import Decimal
from nfp.valuation.price_provider import PriceProvider, AssetValuation

class ManualPriceProvider(PriceProvider):
    def get_price(self, asset_id, date) -> AssetValuation:
        return AssetValuation(price=Decimal('100.0'))
''')

# --- src/nfp/valuation/valuation_service.py ---
with open('src/nfp/valuation/valuation_service.py', 'w') as f:
    f.write('''\
"""Valuation Service."""
class ValuationService:
    def __init__(self, provider):
        self.provider = provider
        
    def valuate(self, asset_id, date):
        return self.provider.get_price(asset_id, date)
''')

# --- src/nfp/valuation/__init__.py ---
with open('src/nfp/valuation/__init__.py', 'w') as f:
    f.write('')

# --- src/nfp/projections/holding.py ---
os.makedirs('src/nfp/projections', exist_ok=True)
with open('src/nfp/projections/holding.py', 'w') as f:
    f.write('''\
"""Holding Projection."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class HoldingProjection:
    asset_id: UUID
    quantity: float
''')

# --- src/nfp/projections/capital_gains.py ---
with open('src/nfp/projections/capital_gains.py', 'w') as f:
    f.write('''\
"""Capital Gain Projection."""
from dataclasses import dataclass

@dataclass
class CapitalGainProjection:
    amount: float
''')

# --- src/nfp/projections/cash_flow.py ---
with open('src/nfp/projections/cash_flow.py', 'w') as f:
    f.write('''\
"""Cash Flow Projection."""
from dataclasses import dataclass

@dataclass
class CashFlowProjection:
    amount: float
''')

# --- src/nfp/projections/income.py ---
with open('src/nfp/projections/income.py', 'w') as f:
    f.write('''\
"""Income Projection."""
from dataclasses import dataclass

@dataclass
class IncomeProjection:
    amount: float
''')

# --- src/nfp/projections/engine.py ---
with open('src/nfp/projections/engine.py', 'w') as f:
    f.write('''\
"""Projection Engine."""
class ProjectionEngine:
    def compute_holdings(self): return []
    def compute_capital_gains(self): return []
    def compute_cash_flows(self): return []
    def compute_income(self): return []
''')

# --- src/nfp/projections/__init__.py ---
with open('src/nfp/projections/__init__.py', 'w') as f:
    f.write('')

