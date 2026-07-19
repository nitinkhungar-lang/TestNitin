import os
import json
import shutil
import textwrap

base_dir = r"C:\Users\khung\.gemini\antigravity\scratch\nfp"
os.makedirs(base_dir, exist_ok=True)

dirs_with_init = [
    "src/nfp", "src/nfp/core", "src/nfp/domain", "src/nfp/events", "src/nfp/rules", 
    "src/nfp/tax", "src/nfp/exchange", "src/nfp/valuation", "src/nfp/projections", 
    "src/nfp/repositories", "src/nfp/services", "src/nfp/infrastructure", 
    "src/nfp/infrastructure/database", "src/nfp/infrastructure/database/sqlite", 
    "src/nfp/infrastructure/file_storage", "src/nfp/infrastructure/crypto", 
    "src/nfp/infrastructure/tax", "src/nfp/imports", "src/nfp/reports", "src/nfp/api", 
    "src/nfp/api/routes", "src/nfp/api/schemas", "src/nfp/ai", "tests", "tests/unit", 
    "tests/unit/core", "tests/unit/domain", "tests/unit/rules", "tests/unit/tax", 
    "tests/integration", "tests/integration/repositories", "tests/golden", "tests/api"
]

empty_dirs = [
    "golden-data/G01_simple_equity_buy", "golden-data/G02_equity_sell_fifo", 
    "golden-data/G03_dividend_tds", "golden-data/G04_mf_sip", "golden-data/G05_fd_maturity", 
    "golden-data/G06_builder_payments", "golden-data/G07_loan_emi", "golden-data/G08_capital_gains", 
    "golden-data/G09_reversal_correction", "golden-data/G10_multi_currency", 
    "golden-data/G11_stock_split", "golden-data/G12_mf_switch", "docs", "adr", 
    "reference-data/tax_rules", "examples"
]

for d in dirs_with_init:
    p = os.path.join(base_dir, d.replace("/", os.sep))
    os.makedirs(p, exist_ok=True)
    open(os.path.join(p, "__init__.py"), "w", encoding="utf-8").close()

for d in empty_dirs:
    p = os.path.join(base_dir, d.replace("/", os.sep))
    os.makedirs(p, exist_ok=True)

# pyproject.toml
pyproject_toml = """[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "nfp"
version = "0.1.0"
description = "NFP — Nitin Financial Platform: Personal Financial Operating System"
readme = "README.md"
requires-python = ">=3.13"
license = { file = "LICENSE" }
authors = [{ name = "NFP" }]
classifiers = [
    "Programming Language :: Python :: 3.13",
    "License :: OSI Approved :: MIT License",
]
dependencies = [
    "cryptography>=42.0.0",
    "keyring>=25.0.0",
    "pyyaml>=6.0.0",
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.29.0",
    "pydantic>=2.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.2.0",
    "pytest-cov>=5.0.0",
    "httpx>=0.27.0",
    "mypy>=1.10.0",
    "ruff>=0.4.0",
    "black>=24.4.0",
    "types-PyYAML>=6.0.0",
    "pre-commit>=3.7.0",
]

[tool.black]
line-length = 100
target-version = ["py313"]

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]
ignore = ["E501"]

[tool.mypy]
strict = true
python_version = "3.13"
files = ["src/nfp"]
exclude = ["tests"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src/nfp --cov-report=term-missing --cov-fail-under=80"

[tool.coverage.run]
source = ["src/nfp"]
omit = ["*/tests/*"]

[tool.hatch.build.targets.wheel]
packages = ["src/nfp"]
"""
with open(os.path.join(base_dir, "pyproject.toml"), "w", encoding="utf-8") as f:
    f.write(pyproject_toml)

# Reference data
currencies = [
  {"code": "INR", "name": "Indian Rupee", "symbol": "\u20b9", "decimal_places": 2, "is_active": True},
  {"code": "USD", "name": "US Dollar", "symbol": "$", "decimal_places": 2, "is_active": True},
  {"code": "EUR", "name": "Euro", "symbol": "\u20ac", "decimal_places": 2, "is_active": True},
  {"code": "GBP", "name": "British Pound", "symbol": "\u00a3", "decimal_places": 2, "is_active": True},
  {"code": "JPY", "name": "Japanese Yen", "symbol": "\u00a5", "decimal_places": 0, "is_active": True},
  {"code": "SGD", "name": "Singapore Dollar", "symbol": "S$", "decimal_places": 2, "is_active": True},
  {"code": "AED", "name": "UAE Dirham", "symbol": "AED", "decimal_places": 2, "is_active": True},
  {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$", "decimal_places": 2, "is_active": True},
  {"code": "AUD", "name": "Australian Dollar", "symbol": "A$", "decimal_places": 2, "is_active": True},
  {"code": "CHF", "name": "Swiss Franc", "symbol": "CHF", "decimal_places": 2, "is_active": True}
]
with open(os.path.join(base_dir, "reference-data", "currencies.json"), "w", encoding="utf-8") as f:
    json.dump(currencies, f, indent=2)

countries = [
  {"code": "IN", "name": "India", "currency_code": "INR"},
  {"code": "US", "name": "United States", "currency_code": "USD"},
  {"code": "GB", "name": "United Kingdom", "currency_code": "GBP"},
  {"code": "SG", "name": "Singapore", "currency_code": "SGD"},
  {"code": "AE", "name": "United Arab Emirates", "currency_code": "AED"},
  {"code": "JP", "name": "Japan", "currency_code": "JPY"},
  {"code": "DE", "name": "Germany", "currency_code": "EUR"},
  {"code": "CA", "name": "Canada", "currency_code": "CAD"},
  {"code": "AU", "name": "Australia", "currency_code": "AUD"},
  {"code": "CH", "name": "Switzerland", "currency_code": "CHF"}
]
with open(os.path.join(base_dir, "reference-data", "countries.json"), "w", encoding="utf-8") as f:
    json.dump(countries, f, indent=2)

asset_types = [
  {"code": "EQUITY_IN", "name": "Indian Listed Equity", "country_code": "IN"},
  {"code": "EQUITY_US", "name": "US Listed Equity", "country_code": "US"},
  {"code": "EQUITY_UNLISTED", "name": "Unlisted Equity", "country_code": None},
  {"code": "MF_EQUITY", "name": "Equity Mutual Fund", "country_code": "IN"},
  {"code": "MF_DEBT", "name": "Debt Mutual Fund", "country_code": "IN"},
  {"code": "MF_HYBRID", "name": "Hybrid Mutual Fund", "country_code": "IN"},
  {"code": "MF_ELSS", "name": "ELSS Tax Saving Fund", "country_code": "IN"},
  {"code": "MF_INDEX", "name": "Index Fund", "country_code": "IN"},
  {"code": "MF_LIQUID", "name": "Liquid Fund", "country_code": "IN"},
  {"code": "ETF_IN", "name": "Indian ETF", "country_code": "IN"},
  {"code": "ETF_US", "name": "US ETF", "country_code": "US"},
  {"code": "FD", "name": "Fixed Deposit", "country_code": "IN"},
  {"code": "RD", "name": "Recurring Deposit", "country_code": "IN"},
  {"code": "PPF", "name": "Public Provident Fund", "country_code": "IN"},
  {"code": "EPF", "name": "Employee Provident Fund", "country_code": "IN"},
  {"code": "NPS", "name": "National Pension System", "country_code": "IN"},
  {"code": "BOND_LISTED", "name": "Listed Bond / Debenture", "country_code": "IN"},
  {"code": "BOND_UNLISTED", "name": "Unlisted Bond", "country_code": "IN"},
  {"code": "BOND_SGB", "name": "Sovereign Gold Bond", "country_code": "IN"},
  {"code": "GOLD_PHYSICAL", "name": "Physical Gold", "country_code": None},
  {"code": "GOLD_DIGITAL", "name": "Digital Gold", "country_code": "IN"},
  {"code": "REAL_ESTATE", "name": "Real Estate", "country_code": None},
  {"code": "CRYPTO", "name": "Cryptocurrency", "country_code": None},
  {"code": "INSURANCE_ULIP", "name": "ULIP", "country_code": "IN"},
  {"code": "INSURANCE_ENDOWMENT", "name": "Endowment Plan", "country_code": "IN"},
  {"code": "CASH", "name": "Cash / Bank Balance", "country_code": None}
]
with open(os.path.join(base_dir, "reference-data", "asset_types.json"), "w", encoding="utf-8") as f:
    json.dump(asset_types, f, indent=2)

account_types = [
  {"code": "DEMAT", "name": "Demat Account"},
  {"code": "TRADING", "name": "Trading Account"},
  {"code": "SAVINGS", "name": "Savings Bank Account"},
  {"code": "CURRENT", "name": "Current Account"},
  {"code": "LOAN", "name": "Loan Account"},
  {"code": "CREDIT_CARD", "name": "Credit Card"},
  {"code": "PPF", "name": "PPF Account"},
  {"code": "NPS", "name": "NPS Account"},
  {"code": "EPF", "name": "EPF Account"},
  {"code": "FD", "name": "Fixed Deposit Account"},
  {"code": "RD", "name": "Recurring Deposit Account"},
  {"code": "WALLET", "name": "Digital Wallet"}
]
with open(os.path.join(base_dir, "reference-data", "account_types.json"), "w", encoding="utf-8") as f:
    json.dump(account_types, f, indent=2)

event_types = [
  {"code": "CASH_DEBIT", "name": "Cash Debit", "direction": "DEBIT", "category": "CASH"},
  {"code": "CASH_CREDIT", "name": "Cash Credit", "direction": "CREDIT", "category": "CASH"},
  {"code": "ASSET_INCREASE", "name": "Asset Increase", "direction": "CREDIT", "category": "ASSET"},
  {"code": "ASSET_DECREASE", "name": "Asset Decrease", "direction": "DEBIT", "category": "ASSET"},
  {"code": "LIABILITY_INCREASE", "name": "Liability Increase", "direction": "CREDIT", "category": "LIABILITY"},
  {"code": "LIABILITY_DECREASE", "name": "Liability Decrease", "direction": "DEBIT", "category": "LIABILITY"},
  {"code": "BROKERAGE", "name": "Brokerage", "direction": "DEBIT", "category": "EXPENSE"},
  {"code": "STT", "name": "Securities Transaction Tax", "direction": "DEBIT", "category": "TAX"},
  {"code": "STAMP_DUTY", "name": "Stamp Duty", "direction": "DEBIT", "category": "TAX"},
  {"code": "GST", "name": "GST", "direction": "DEBIT", "category": "TAX"},
  {"code": "SEBI_FEE", "name": "SEBI Turnover Fee", "direction": "DEBIT", "category": "EXPENSE"},
  {"code": "EXCHANGE_FEE", "name": "Exchange Transaction Charge", "direction": "DEBIT", "category": "EXPENSE"},
  {"code": "TDS", "name": "Tax Deducted at Source", "direction": "DEBIT", "category": "TAX"},
  {"code": "DIVIDEND_INCOME", "name": "Dividend Income", "direction": "CREDIT", "category": "INCOME"},
  {"code": "INTEREST_INCOME", "name": "Interest Income", "direction": "CREDIT", "category": "INCOME"},
  {"code": "CAPITAL_GAIN_ST", "name": "Short-Term Capital Gain", "direction": "CREDIT", "category": "INCOME"},
  {"code": "CAPITAL_GAIN_LT", "name": "Long-Term Capital Gain", "direction": "CREDIT", "category": "INCOME"},
  {"code": "CAPITAL_LOSS_ST", "name": "Short-Term Capital Loss", "direction": "DEBIT", "category": "EXPENSE"},
  {"code": "CAPITAL_LOSS_LT", "name": "Long-Term Capital Loss", "direction": "DEBIT", "category": "EXPENSE"},
  {"code": "RENTAL_INCOME", "name": "Rental Income", "direction": "CREDIT", "category": "INCOME"},
  {"code": "SALARY_INCOME", "name": "Salary Income", "direction": "CREDIT", "category": "INCOME"},
  {"code": "BONUS_INCOME", "name": "Bonus Income", "direction": "CREDIT", "category": "INCOME"},
  {"code": "LOAN_PRINCIPAL", "name": "Loan Principal Payment", "direction": "DEBIT", "category": "CASH"},
  {"code": "LOAN_INTEREST", "name": "Loan Interest Payment", "direction": "DEBIT", "category": "EXPENSE"},
  {"code": "INSURANCE_PREMIUM", "name": "Insurance Premium", "direction": "DEBIT", "category": "EXPENSE"},
  {"code": "BONUS_SHARES", "name": "Bonus Shares Received", "direction": "CREDIT", "category": "ASSET"},
  {"code": "RIGHTS_SHARES", "name": "Rights Shares Received", "direction": "CREDIT", "category": "ASSET"},
  {"code": "SPLIT_ADJUSTMENT", "name": "Split/Consolidation Adjustment", "direction": "BOTH", "category": "ASSET"},
  {"code": "CURRENCY_GAIN", "name": "Forex Gain", "direction": "CREDIT", "category": "INCOME"},
  {"code": "CURRENCY_LOSS", "name": "Forex Loss", "direction": "DEBIT", "category": "EXPENSE"},
  {"code": "REVERSAL", "name": "Reversal Event", "direction": "BOTH", "category": "REVERSAL"}
]
with open(os.path.join(base_dir, "reference-data", "event_types.json"), "w", encoding="utf-8") as f:
    json.dump(event_types, f, indent=2)

activities = [
    # EQUITY
    ("EQUITY_BUY", "Equity Buy", "EQUITY"),
    ("EQUITY_SELL", "Equity Sell", "EQUITY"),
    ("EQUITY_BONUS", "Equity Bonus Issue", "EQUITY"),
    ("EQUITY_RIGHTS_ISSUE", "Equity Rights Issue", "EQUITY"),
    ("EQUITY_SPLIT", "Equity Stock Split", "EQUITY"),
    ("EQUITY_CONSOLIDATION", "Equity Consolidation", "EQUITY"),
    ("EQUITY_DIVIDEND", "Equity Dividend", "EQUITY"),
    ("EQUITY_SPINOFF", "Equity Spinoff", "EQUITY"),
    ("EQUITY_MERGER", "Equity Merger", "EQUITY"),
    ("EQUITY_DELISTING", "Equity Delisting", "EQUITY"),
    ("EQUITY_IPO_ALLOTMENT", "IPO Allotment", "EQUITY"),
    ("EQUITY_IPO_REFUND", "IPO Refund", "EQUITY"),
    
    # MF
    ("MF_BUY", "Mutual Fund Buy", "MF"),
    ("MF_SELL", "Mutual Fund Sell", "MF"),
    ("MF_SWITCH_OUT", "MF Switch Out", "MF"),
    ("MF_SWITCH_IN", "MF Switch In", "MF"),
    ("MF_DIVIDEND_PAYOUT", "MF Dividend Payout", "MF"),
    ("MF_DIVIDEND_REINVEST", "MF Dividend Reinvest", "MF"),
    ("MF_MERGER", "MF Merger", "MF"),
    ("MF_SEGREGATION", "MF Segregation", "MF"),
    ("MF_STP_OUT", "MF STP Out", "MF"),
    ("MF_STP_IN", "MF STP In", "MF"),
    ("MF_SWP", "MF SWP", "MF"),

    # FIXED_INCOME
    ("FD_OPEN", "FD Open", "FIXED_INCOME"),
    ("FD_MATURED", "FD Matured", "FIXED_INCOME"),
    ("FD_BROKEN", "FD Broken", "FIXED_INCOME"),
    ("FD_INTEREST_ACCRUED", "FD Interest Accrued", "FIXED_INCOME"),
    ("RD_INSTALMENT", "RD Instalment", "FIXED_INCOME"),
    ("RD_MATURED", "RD Matured", "FIXED_INCOME"),
    ("BOND_BUY", "Bond Buy", "FIXED_INCOME"),
    ("BOND_SELL", "Bond Sell", "FIXED_INCOME"),
    ("BOND_INTEREST", "Bond Interest", "FIXED_INCOME"),
    ("BOND_MATURITY", "Bond Maturity", "FIXED_INCOME"),
    ("PPF_CONTRIBUTION", "PPF Contribution", "FIXED_INCOME"),
    ("PPF_INTEREST", "PPF Interest", "FIXED_INCOME"),
    ("PPF_WITHDRAWAL", "PPF Withdrawal", "FIXED_INCOME"),
    ("EPF_CONTRIBUTION", "EPF Contribution", "FIXED_INCOME"),
    ("EPF_WITHDRAWAL", "EPF Withdrawal", "FIXED_INCOME"),
    ("NPS_CONTRIBUTION", "NPS Contribution", "FIXED_INCOME"),
    ("NPS_WITHDRAWAL", "NPS Withdrawal", "FIXED_INCOME"),

    # REAL_ESTATE
    ("PROPERTY_BUILDER_PAYMENT", "Property Builder Payment", "REAL_ESTATE"),
    ("PROPERTY_STAMP_DUTY", "Property Stamp Duty", "REAL_ESTATE"),
    ("PROPERTY_REGISTRATION", "Property Registration", "REAL_ESTATE"),
    ("PROPERTY_SOLD", "Property Sold", "REAL_ESTATE"),
    ("RENTAL_RECEIVED", "Rental Received", "REAL_ESTATE"),

    # LOANS
    ("LOAN_DISBURSED", "Loan Disbursed", "LOANS"),
    ("LOAN_EMI", "Loan EMI", "LOANS"),
    ("LOAN_PREPAYMENT", "Loan Prepayment", "LOANS"),
    ("LOAN_CLOSED", "Loan Closed", "LOANS"),

    # BANKING
    ("BANK_TRANSFER_OUT", "Bank Transfer Out", "BANKING"),
    ("BANK_TRANSFER_IN", "Bank Transfer In", "BANKING"),
    ("CASH_DEPOSIT", "Cash Deposit", "BANKING"),
    ("CASH_WITHDRAWAL", "Cash Withdrawal", "BANKING"),
    ("SALARY_RECEIVED", "Salary Received", "BANKING"),
    ("BONUS_RECEIVED", "Bonus Received", "BANKING"),
    ("INSURANCE_PREMIUM_PAID", "Insurance Premium Paid", "BANKING"),
    ("INSURANCE_CLAIM_RECEIVED", "Insurance Claim Received", "BANKING"),
    ("GOLD_BUY", "Gold Buy", "BANKING"),
    ("GOLD_SELL", "Gold Sell", "BANKING"),
    ("CRYPTO_BUY", "Crypto Buy", "BANKING"),
    ("CRYPTO_SELL", "Crypto Sell", "BANKING"),

    # GENERAL
    ("ACTIVITY_REVERSAL", "Activity Reversal", "GENERAL")
]

activity_types = []
for code, name, category in activities:
    activity_types.append({
        "code": code,
        "name": name,
        "category": category,
        "description": f"{name} transaction",
        "event_template_key": f"{code}_TEMPLATE",
        "is_active": True,
        "schema_version": 1
    })

with open(os.path.join(base_dir, "reference-data", "activity_types.json"), "w", encoding="utf-8") as f:
    json.dump(activity_types, f, indent=2)

tax_rules = """jurisdiction: IN
rules:
  holding_period_rules:
    - asset_types: ["EQUITY_IN", "MF_EQUITY"]
      long_term_threshold_months: 12
    - asset_types: ["MF_DEBT"]
      condition: "acquisition_date < '2023-04-01'"
      long_term_threshold_months: 36
    - asset_types: ["MF_DEBT"]
      condition: "acquisition_date >= '2023-04-01'"
      long_term_threshold_months: 999999
    - asset_types: ["REAL_ESTATE", "GOLD_PHYSICAL", "BOND_UNLISTED"]
      long_term_threshold_months: 24
    - asset_types: ["BOND_LISTED"]
      long_term_threshold_months: 12
"""
with open(os.path.join(base_dir, "reference-data", "tax_rules", "india_tax_rules.yaml"), "w", encoding="utf-8") as f:
    f.write(tax_rules)

# ADR Stubs
adrs = [
    ("001-initial-architecture.md", "Modular Monolith with Clean Architecture. No microservices without demonstrated need documented in an ADR."),
    ("002-sqlite-money-as-text.md", "All monetary Decimal values stored as TEXT strings in SQLite to prevent floating-point precision loss."),
    ("003-holdings-as-projections.md", "HoldingProjection and PortfolioProjection are computed on-the-fly from FinancialEvents. No holdings table as primary storage."),
    ("004-pan-encryption-fernet.md", "PAN stored as Fernet-encrypted BLOB. Plaintext never in DB or API response. Masked PAN only in API."),
    ("005-evidence-external-file-storage.md", "Evidence documents stored on local filesystem at NFP_EVIDENCE_ROOT. DB stores file_reference path and SHA-256 hash."),
    ("006-tax-rule-provider-abstraction.md", "All tax logic via TaxRuleProvider ABC. Rules loaded from YAML, not hardcoded."),
    ("007-exchange-rate-provider-abstraction.md", "ExchangeRateProvider ABC with pluggable implementations. Domain never calls a specific exchange rate source."),
    ("008-ledger-aggregate.md", "Ledger is an explicit aggregate that owns the FinancialEvent stream. Assigns sequence numbers. Has version counter for optimistic concurrency."),
    ("009-lot-as-domain-entity.md", "Lot is a first-class persisted domain entity (not a projection cache). Enables FIFO state to survive restarts and corporate action adjustments."),
    ("010-corporate-action-aggregate.md", "CorporateAction is a separate aggregate from BusinessActivity. Processes directly against Lots."),
    ("011-price-provider-valuation-service.md", "PriceProvider ABC separates market price from cost basis. ValuationService combines Holdings with PriceProvider to produce AssetValuation."),
    ("012-multi-jurisdiction-tax.md", "TaxRuleRegistry maps TaxJurisdiction to TaxRuleProvider. Supports IN and US initially."),
    ("013-event-schema-versioning.md", "All domain entities carry schema_version: int = 1. EventUpgrader pattern for future schema migrations."),
    ("014-clock-abstraction.md", "Clock ABC (SystemClock + FixedClock) injected everywhere datetime.now() / date.today() is needed. Direct calls forbidden in domain and services.")
]

for filename, decision in adrs:
    content = f"""# ADR {filename.split('-')[0].lstrip('0')}
Status: ACCEPTED
Date: 2026-07-19

## Context
Initial setup

## Decision
{decision}

## Consequences
TBD
"""
    with open(os.path.join(base_dir, "adr", filename), "w", encoding="utf-8") as f:
        f.write(content)

# Supporting Files
readme = """# NFP — Nitin Financial Platform

A Personal Financial Operating System built around an immutable financial ledger.

## Architecture

Modular Monolith · Clean Architecture · Immutable Ledger · Event Sourcing

## Quick Start

```bash
pip install -e ".[dev]"
pytest
```

## Documentation

See `docs/NFP_ENGINEERING_BIBLE_v1.2.md` for the full specification.

## Phase Status

- [x] Phase 1: Bootstrap
- [ ] Phase 2: Core Domain
- [ ] Phase 3: Rule Engine
- [ ] Phase 4: Persistence
- [ ] Phase 5: Imports
- [ ] Phase 6: Corporate Actions
- [ ] Phase 7: Capital Gains & Tax
- [ ] Phase 8: Reports
- [ ] Phase 9: REST API
- [ ] Phase 10: Additional Parsers
- [ ] Phase 11: AI Integration
"""
with open(os.path.join(base_dir, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme)

changelog = """# Changelog

All notable changes to NFP are documented here.

## [Unreleased]

### Added
- Phase 1: Project bootstrap — pyproject.toml, folder structure, reference data, ADRs
"""
with open(os.path.join(base_dir, "CHANGELOG.md"), "w", encoding="utf-8") as f:
    f.write(changelog)

license = """MIT License
"""
with open(os.path.join(base_dir, "LICENSE"), "w", encoding="utf-8") as f:
    f.write(license)

conftest = '\"\"\"Shared pytest fixtures for NFP tests.\"\"\"\nfrom __future__ import annotations\n'
with open(os.path.join(base_dir, "tests", "conftest.py"), "w", encoding="utf-8") as f:
    f.write(conftest)

init_py = '\"\"\"NFP — Nitin Financial Platform.\n\nA Personal Financial Operating System built on an immutable financial ledger.\n\"\"\"\n__version__ = "0.1.0"\n'
with open(os.path.join(base_dir, "src", "nfp", "__init__.py"), "w", encoding="utf-8") as f:
    f.write(init_py)

print("Setup script done.")
