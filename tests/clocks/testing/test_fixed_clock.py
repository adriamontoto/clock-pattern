"""
Test FixedClock clock.
"""

from datetime import UTC, date, datetime

from object_mother_pattern.mothers import DatetimeMother
from pytest import mark, raises as assert_raises

from clock_pattern.clocks.testing import FixedClock


@mark.unit_testing
def test_fixed_clock_happy_path() -> None:
    """
    Test FixedClock clock happy path.
    """
    datetime_value = DatetimeMother.create()
    now = FixedClock(instant=datetime_value).now()

    assert isinstance(now, datetime)
    assert now == datetime_value


@mark.unit_testing
def test_fixed_clock_instant_without_timezone() -> None:
    """
    Test FixedClock clock instant without timezone.
    """
    datetime_value = DatetimeMother.create().replace(tzinfo=None)
    now = FixedClock(instant=datetime_value).now()

    assert isinstance(now, datetime)
    assert now == datetime_value.replace(tzinfo=UTC)


@mark.unit_testing
def test_fixed_clock_invalid_instant_type() -> None:
    """
    Test FixedClock clock raises TypeError if instant is not a datetime.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'FixedClock instant <<<.*>>> must be a datetime. Got <<<.*>>> type.',
    ):
        FixedClock(instant=DatetimeMother.invalid_type())


@mark.unit_testing
def test_fixed_clock_today_happy_path() -> None:
    """
    Test FixedClock clock today happy path.
    """
    datetime_value = DatetimeMother.create()
    today = FixedClock(instant=datetime_value).today()

    assert isinstance(today, date)
    assert today == datetime_value.date()
