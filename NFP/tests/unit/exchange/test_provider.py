import pytest
from nfp.exchange.manual_provider import ManualExchangeRateProvider

def test_manual_provider():
    provider = ManualExchangeRateProvider()
    assert provider.get_rate('USD', 'INR', None) == 1.0
