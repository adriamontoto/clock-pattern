"""
Test FixedClock clock.
"""

from datetime import UTC, date, datetime, timedelta
from re import escape
from zoneinfo import ZoneInfo

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
    instant = DatetimeMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'FixedClock instant <<<{instant}>>> must be a datetime. Got <<<{type(instant).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        FixedClock(instant=instant)


@mark.unit_testing
def test_fixed_clock_today_happy_path() -> None:
    """
    Test FixedClock clock today happy path.
    """
    datetime_value = DatetimeMother.create()
    today = FixedClock(instant=datetime_value).today()

    assert isinstance(today, date)
    assert today == datetime_value.date()


@mark.unit_testing
def test_fixed_clock_set_method_happy_path() -> None:
    """
    Test FixedClock set method returns the configured datetime and its date.
    """
    clock = FixedClock(instant=DatetimeMother.create())
    instant = DatetimeMother.create()

    clock.set(instant=instant)

    assert clock.now() is instant
    assert clock.today() == instant.date()


@mark.unit_testing
def test_fixed_clock_set_method_moves_backward() -> None:
    """
    Test FixedClock set method moves backward and keeps the datetime and date consistent.
    """
    instant = DatetimeMother.create()
    clock = FixedClock(instant=instant)

    clock.set(instant=instant)

    assert clock.now() is instant
    assert clock.today() == instant.date()


@mark.unit_testing
def test_fixed_clock_set_method_instant_without_timezone() -> None:
    """
    Test FixedClock set method normalizes a naive datetime to UTC.
    """
    clock = FixedClock(instant=DatetimeMother.create())
    instant = DatetimeMother.create().replace(tzinfo=None)

    clock.set(instant=instant)

    assert clock.now() == instant.replace(tzinfo=UTC)
    assert clock.today() == instant.date()


@mark.unit_testing
def test_fixed_clock_set_method_instant_invalid_type() -> None:
    """
    Test FixedClock set method rejects an invalid type without changing the instant.
    """
    instant = DatetimeMother.create()
    clock = FixedClock(instant=instant)
    invalid_instant = DatetimeMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'FixedClock instant <<<{invalid_instant}>>> must be a datetime. Got <<<{type(invalid_instant).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        clock.set(instant=invalid_instant)

    assert clock.now() is instant


@mark.unit_testing
def test_fixed_clock_advance_method_crosses_midnight() -> None:
    """
    Test FixedClock advance method updates both the datetime and date across midnight.
    """
    instant = datetime(2025, 12, 31, 23, 59, tzinfo=UTC)
    clock = FixedClock(instant=instant)

    clock.advance(delta=timedelta(minutes=2))

    assert clock.now() == datetime(2026, 1, 1, 0, 1, tzinfo=UTC)
    assert clock.today() == date(2026, 1, 1)


@mark.unit_testing
def test_fixed_clock_advance_method_stays_fixed_between_reads() -> None:
    """
    Test FixedClock advance method leaves time fixed until another explicit adjustment.
    """
    instant = DatetimeMother.create()
    clock = FixedClock(instant=instant)

    clock.advance(delta=timedelta(hours=1))
    first_read = clock.now()
    second_read = clock.now()

    assert first_read == instant + timedelta(hours=1)
    assert second_read is first_read


@mark.unit_testing
def test_fixed_clock_advance_method_crosses_spring_daylight_saving_gap() -> None:
    """
    Test FixedClock advance method skips the spring gap while advancing by one elapsed hour.
    """
    instant = datetime(2025, 3, 30, 1, 30, tzinfo=ZoneInfo('Europe/Madrid'))
    clock = FixedClock(instant=instant)

    clock.advance(delta=timedelta(hours=1))

    assert clock.now().isoformat() == '2025-03-30T03:30:00+02:00'
    assert clock.now().fold == 0
    assert clock.now().tzinfo is instant.tzinfo
    assert clock.now().timestamp() - instant.timestamp() == 3600


@mark.unit_testing
def test_fixed_clock_advance_method_crosses_autumn_daylight_saving_fold() -> None:
    """
    Test FixedClock advance method reaches the repeated autumn hour after one elapsed hour.
    """
    instant = datetime(2025, 10, 26, 2, 30, tzinfo=ZoneInfo('Europe/Madrid'))
    clock = FixedClock(instant=instant)

    clock.advance(delta=timedelta(hours=1))

    assert clock.now().isoformat() == '2025-10-26T02:30:00+01:00'
    assert clock.now().fold == 1
    assert clock.now().tzinfo is instant.tzinfo
    assert clock.now().timestamp() - instant.timestamp() == 3600


@mark.unit_testing
def test_fixed_clock_advance_method_delta_negative_limit_value() -> None:
    """
    Test FixedClock advance method rejects a negative microsecond without mutation.
    """
    instant = DatetimeMother.create()
    clock = FixedClock(instant=instant)
    delta = timedelta(microseconds=-1)

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'FixedClock delta <<<{delta}>>> must be greater than or equal to zero.'),
    ):
        clock.advance(delta=delta)

    assert clock.now() is instant


@mark.unit_testing
def test_fixed_clock_advance_method_delta_zero_value() -> None:
    """
    Test FixedClock advance method preserves a folded instant when no time elapses.
    """
    instant = DatetimeMother.create()
    instant = instant.replace(fold=1)

    clock = FixedClock(instant=instant)

    clock.advance(delta=timedelta(0))

    assert clock.now() is instant
    assert clock.now().fold == 1


@mark.unit_testing
def test_fixed_clock_advance_method_overflow_preserves_instant() -> None:
    """
    Test FixedClock advance method rejects datetime overflow without changing the instant.
    """
    instant = datetime.max.replace(tzinfo=UTC)
    clock = FixedClock(instant=instant)

    with assert_raises(
        expected_exception=OverflowError,
        match=escape('date value out of range'),
    ):
        clock.advance(delta=timedelta(microseconds=1))

    assert clock.now() is instant
