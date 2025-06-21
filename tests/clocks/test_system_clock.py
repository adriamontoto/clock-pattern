"""
Test SystemClock clock.
"""

from datetime import date, datetime, tzinfo

from object_mother_pattern.mothers import StringMother
from object_mother_pattern.mothers.dates import StringTimezoneMother, TimezoneMother
from pytest import mark, raises as assert_raises

from clock_pattern.clocks import SystemClock


@mark.unit_testing
def test_system_clock_happy_path() -> None:
    """
    Test SystemClock clock happy path.
    """
    now = SystemClock().now()

    assert isinstance(now, datetime)


@mark.unit_testing
def test_system_clock_random_timezone() -> None:
    """
    Test SystemClock clock random timezone.
    """
    now = SystemClock(timezone=TimezoneMother.create()).now()

    assert isinstance(now, datetime)


@mark.unit_testing
def test_system_clock_random_string_timezone() -> None:
    """
    Test SystemClock clock random string timezone.
    """
    now = SystemClock(timezone=StringTimezoneMother.create()).now()

    assert isinstance(now, datetime)


@mark.unit_testing
def test_system_clock_invalid_timezone_type() -> None:
    """
    Test SystemClock clock raises TypeError if timezone is not a string.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'SystemClock timezone <<<.*>>> must be a string. Got <<<.*>>> type.',
    ):
        SystemClock(timezone=StringTimezoneMother.invalid_type())


@mark.unit_testing
def test_system_clock_invalid_timezone_value() -> None:
    """
    Test SystemClock clock raises ValueError if timezone is not a valid timezone.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'SystemClock timezone <<<.*>>> must be a timezone.',
    ):
        SystemClock(timezone=StringMother.create())


@mark.unit_testing
def test_system_clock_invalid_timezone_empty_value() -> None:
    """
    Test SystemClock clock raises ValueError if timezone is empty.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'SystemClock timezone <<<.*>>> is an empty string. Only non-empty strings are allowed.',
    ):
        SystemClock(timezone=StringMother.empty())


@mark.unit_testing
def test_system_clock_invalid_timezone_contains_whitespace() -> None:
    """
    Test SystemClock clock raises ValueError if timezone contains whitespace.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'SystemClock timezone <<<.*>>> contains leading or trailing whitespaces. Only trimmed values are allowed.',  # noqa: E501
    ):
        SystemClock(timezone=StringMother.not_trimmed())


@mark.unit_testing
def test_system_clock_today_happy_path() -> None:
    """
    Test SystemClock clock today happy path.
    """
    today = SystemClock().today()

    assert isinstance(today, date)


@mark.unit_testing
def test_system_clock_timezone_property() -> None:
    """
    Test SystemClock clock timezone property.
    """
    timezone = TimezoneMother.create()
    clock = SystemClock(timezone=timezone)

    assert isinstance(clock.timezone, tzinfo)
    assert clock.timezone == timezone
