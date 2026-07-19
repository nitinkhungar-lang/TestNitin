import pytest
from nfp.rules.integrity import LedgerIntegrityService

def test_integrity():
    service = LedgerIntegrityService()
    assert service.check_integrity() is True
