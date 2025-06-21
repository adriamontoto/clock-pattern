"""
Test MockClock clock.
"""

from datetime import UTC, date, datetime

from object_mother_pattern.mothers import DateMother, DatetimeMother
from pytest import mark, raises as assert_raises

from clock_pattern.clocks.testing import MockClock


@mark.unit_testing
def test_mock_clock_happy_path() -> None:
    """
    Test MockClock clock happy path.
    """
    clock = MockClock()
    datetime_value = DatetimeMother.create()
    clock.prepare_now_method_return_value(now=datetime_value)

    now = clock.now()

    assert isinstance(now, datetime)
    assert now == datetime_value
    clock.assert_now_method_was_called_once()


@mark.unit_testing
def test_mock_clock_call_now_method_without_calling_prepare_method() -> None:
    """
    Test MockClock clock raises ValueError if now method is called without calling prepare method.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'MockClock now <<<None>>> must be not None.',
    ):
        MockClock().now()


@mark.unit_testing
def test_mock_clock_prepare_now_method_invalid_now_type() -> None:
    """
    Test MockClock clock prepare now method raises TypeError if now is not a datetime.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'MockClock now <<<.*>>> must be a datetime. Got <<<.*>>> type.',
    ):
        MockClock().prepare_now_method_return_value(now=DatetimeMother.invalid_type())


@mark.unit_testing
def test_mock_clock_prepare_now_method_without_timezone() -> None:
    """
    Test MockClock clock prepare now method without timezone sets UTC.
    """
    clock = MockClock()
    datetime_value = DatetimeMother.create().replace(tzinfo=None)
    clock.prepare_now_method_return_value(now=datetime_value)

    now = clock.now()

    assert isinstance(now, datetime)
    assert now == datetime_value.replace(tzinfo=UTC)


@mark.unit_testing
def test_mock_clock_now_method_when_assert_now_method_was_called_once_is_called() -> None:
    """
    Test MockClock clock now method was called once when assert_now_method_was_called_once is called.
    """
    clock = MockClock()
    datetime_value = DatetimeMother.create()
    clock.prepare_now_method_return_value(now=datetime_value)

    clock.now()
    clock.assert_now_method_was_called_once()


@mark.unit_testing
def test_mock_clock_now_method_when_assert_now_method_was_called_once_is_called_more_than_once() -> None:
    """
    Test MockClock raises AssertionError if now method was called more than once when assert_now_method_was_called_once
    is called.
    """
    clock = MockClock()
    datetime_value = DatetimeMother.create()
    clock.prepare_now_method_return_value(now=datetime_value)

    clock.now()
    clock.now()

    with assert_raises(
        expected_exception=AssertionError,
        match=r'Expected \'mock\' to be called once. Called 2 times.\nCalls: \[call\(\), call\(\)\].',
    ):
        clock.assert_now_method_was_called_once()


@mark.unit_testing
def test_mock_clock_now_method_when_assert_now_method_was_not_called_is_not_called() -> None:
    """
    Test MockClock clock now method was not called when assert_now_method_was_not_called is not called.
    """
    clock = MockClock()
    datetime_value = DatetimeMother.create()
    clock.prepare_now_method_return_value(now=datetime_value)

    clock.assert_now_method_was_not_called()


@mark.unit_testing
def test_mock_clock_now_method_when_assert_now_method_was_not_called_is_called_once() -> None:
    """
    Test MockClock raises AssertionError if now method was not called when assert_now_method_was_not_called is called.
    """
    clock = MockClock()
    datetime_value = DatetimeMother.create()
    clock.prepare_now_method_return_value(now=datetime_value)

    clock.now()

    with assert_raises(
        expected_exception=AssertionError,
        match=r'Expected \'mock\' to not have been called. Called 1 times.\nCalls: \[call\(\)\].',
    ):
        clock.assert_now_method_was_not_called()


@mark.unit_testing
def test_mock_clock_today_happy_path() -> None:
    """
    Test MockClock clock today happy path.
    """
    clock = MockClock()
    date_value = DateMother.create()
    clock.prepare_today_method_return_value(today=date_value)

    today = clock.today()

    assert isinstance(today, date)
    assert today == date_value

    clock.assert_today_method_was_called_once()


@mark.unit_testing
def test_mock_clock_prepare_today_method_invalid_today_type() -> None:
    """
    Test MockClock clock prepare today method raises TypeError if today is not a date.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'MockClock today <<<.*>>> must be a date. Got <<<.*>>> type.',
    ):
        MockClock().prepare_today_method_return_value(today=DateMother.invalid_type())


@mark.unit_testing
def test_mock_clock_today_method_when_assert_today_method_was_called_once_is_called() -> None:
    """
    Test MockClock clock today method was called once when assert_today_method_was_called_once is called.
    """
    clock = MockClock()
    date_value = DateMother.create()
    clock.prepare_today_method_return_value(today=date_value)

    clock.today()
    clock.assert_today_method_was_called_once()


@mark.unit_testing
def test_mock_clock_today_method_when_assert_today_method_was_called_once_is_called_more_than_once() -> None:
    """
    Test MockClock raises AssertionError if today method was called more than once when
    assert_today_method_was_called_once is called.
    """
    clock = MockClock()
    date_value = DateMother.create()
    clock.prepare_today_method_return_value(today=date_value)

    clock.today()
    clock.today()

    with assert_raises(
        expected_exception=AssertionError,
        match=r'Expected \'mock\' to be called once. Called 2 times.\nCalls: \[call\(\), call\(\)\].',
    ):
        clock.assert_today_method_was_called_once()


@mark.unit_testing
def test_mock_clock_today_method_when_assert_today_method_was_not_called_is_not_called() -> None:
    """
    Test MockClock clock today method was not called when assert_today_method_was_not_called is not called.
    """
    clock = MockClock()
    date_value = DateMother.create()
    clock.prepare_today_method_return_value(today=date_value)

    clock.assert_today_method_was_not_called()


@mark.unit_testing
def test_mock_clock_today_method_when_assert_today_method_was_not_called_is_called_once() -> None:
    """
    Test MockClock raises AssertionError if today method was not called when assert_today_method_was_not_called is
    called.
    """
    clock = MockClock()
    date_value = DateMother.create()
    clock.prepare_today_method_return_value(today=date_value)

    clock.today()

    with assert_raises(
        expected_exception=AssertionError,
        match=r'Expected \'mock\' to not have been called. Called 1 times.\nCalls: \[call\(\)\].',
    ):
        clock.assert_today_method_was_not_called()
