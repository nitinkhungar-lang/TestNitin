import pytest
from datetime import date, datetime, UTC
from nfp.core.clock import SystemClock, FixedClock

def test_system_clock():
    clock = SystemClock()
    assert isinstance(clock.today(), date)
    assert isinstance(clock.now(), datetime)

def test_fixed_clock_default_datetime():
    d = date(2024, 6, 1)
    clock = FixedClock(d)
    assert clock.today() == d
    expected_dt = datetime(2024, 6, 1, tzinfo=UTC)
    assert clock.now() == expected_dt

def test_fixed_clock_explicit_datetime():
    d = date(2024, 6, 1)
    dt = datetime(2024, 6, 1, 12, 0, 0, tzinfo=UTC)
    clock = FixedClock(d, dt)
    assert clock.today() == d
    assert clock.now() == dt
