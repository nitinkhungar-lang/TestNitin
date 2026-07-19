import pytest
from nfp.valuation.manual_price_provider import ManualPriceProvider
from nfp.valuation.valuation_service import ValuationService
from decimal import Decimal

def test_valuation_service():
    provider = ManualPriceProvider()
    service = ValuationService(provider)
    val = service.valuate(None, None)
    assert val.price == Decimal('100.0')
