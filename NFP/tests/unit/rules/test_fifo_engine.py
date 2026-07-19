import pytest
from nfp.rules.fifo_engine import FifoEngine

def test_fifo_engine():
    engine = FifoEngine()
    assert engine is not None
