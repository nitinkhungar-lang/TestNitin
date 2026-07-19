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
