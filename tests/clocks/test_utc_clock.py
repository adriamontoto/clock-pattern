"""
Test UtcClock clock.
"""

from datetime import UTC, date, datetime, tzinfo

from pytest import mark

from clock_pattern.clocks import UtcClock


@mark.unit_testing
def test_utc_clock_happy_path() -> None:
    """
    Test UtcClock clock happy path.
    """
    now = UtcClock().now()

    assert isinstance(now, datetime)


@mark.unit_testing
def test_utc_clock_today_happy_path() -> None:
    """
    Test UtcClock clock today happy path.
    """
    today = UtcClock().today()

    assert isinstance(today, date)


@mark.unit_testing
def test_utc_clock_timezone_property() -> None:
    """
    Test UtcClock clock timezone property.
    """
    clock = UtcClock()

    assert isinstance(clock.timezone, tzinfo)
    assert str(clock.timezone) == str(UTC)
