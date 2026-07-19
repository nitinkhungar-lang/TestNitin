import os

# Create domain/market_price.py just in case
market_price_code = '''"""MarketPrice aggregate for NFP."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from nfp.core.money import Money
from uuid import UUID

@dataclass(frozen=True)
class MarketPrice:
    asset_id: UUID
    date: date
    price: Money
    source: str
'''
with open("src/nfp/domain/market_price.py", "w") as f:
    f.write(market_price_code)

# Add to domain/__init__.py
with open("src/nfp/domain/__init__.py", "a") as f:
    f.write("\nfrom nfp.domain.market_price import MarketPrice\n")
