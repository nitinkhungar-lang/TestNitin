import pytest
from nfp.rules.average_cost_engine import AverageCostEngine

def test_average_cost_engine():
    engine = AverageCostEngine()
    assert engine is not None
