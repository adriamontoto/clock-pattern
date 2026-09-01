"""
Test SystemMonotonicClock monotonic clock.
"""

from pytest import mark

from clock_pattern.monotonic_clocks import SystemMonotonicClock


@mark.unit_testing
def test_system_monotonic_clock_happy_path() -> None:
    """
    Test SystemMonotonicClock monotonic clock happy path.
    """
    current_seconds = SystemMonotonicClock().current_seconds()

    assert type(current_seconds) is float


@mark.unit_testing
def test_system_monotonic_clock_current_seconds_method_returns_monotonic_seconds() -> None:
    """
    Test SystemMonotonicClock current_seconds method returns monotonic seconds.
    """
    monotonic_clock = SystemMonotonicClock()

    first_current_seconds = monotonic_clock.current_seconds()
    second_current_seconds = monotonic_clock.current_seconds()

    assert type(first_current_seconds) is float
    assert type(second_current_seconds) is float
    assert second_current_seconds >= first_current_seconds
