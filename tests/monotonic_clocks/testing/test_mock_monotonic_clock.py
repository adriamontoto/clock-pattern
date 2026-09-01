"""
Test MockMonotonicClock monotonic clock.
"""

from object_mother_pattern import FloatMother
from pytest import mark, raises as assert_raises

from clock_pattern.monotonic_clocks.testing import MockMonotonicClock


@mark.unit_testing
def test_mock_monotonic_clock_happy_path() -> None:
    """
    Test MockMonotonicClock monotonic clock happy path.
    """
    current_seconds_value = FloatMother.positive()
    monotonic_clock = MockMonotonicClock(current_seconds=current_seconds_value)

    assert type(monotonic_clock.current_seconds()) is float
    assert monotonic_clock.current_seconds() == current_seconds_value


@mark.unit_testing
def test_mock_monotonic_clock_default_current_seconds() -> None:
    """
    Test MockMonotonicClock monotonic clock default current seconds.
    """
    monotonic_clock = MockMonotonicClock()

    assert monotonic_clock.current_seconds() == 0.0


@mark.unit_testing
def test_mock_monotonic_clock_current_seconds_invalid_type() -> None:
    """
    Test MockMonotonicClock raises TypeError if current_seconds has invalid type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'MockMonotonicClock current_seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
    ):
        MockMonotonicClock(current_seconds=FloatMother.invalid_type())


@mark.unit_testing
def test_mock_monotonic_clock_current_seconds_negative_random_value() -> None:
    """
    Test MockMonotonicClock raises ValueError if current_seconds is random negative.
    """
    current_seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=rf'MockMonotonicClock current_seconds <<<{current_seconds}>>> must be greater than or equal to zero.',
    ):
        MockMonotonicClock(current_seconds=current_seconds)


@mark.unit_testing
def test_mock_monotonic_clock_current_seconds_negative_limit_value() -> None:
    """
    Test MockMonotonicClock raises ValueError if current_seconds is negative limit.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'MockMonotonicClock current_seconds <<<-1.0>>> must be greater than or equal to zero.',  # noqa: E501
    ):
        MockMonotonicClock(current_seconds=-1.0)


@mark.unit_testing
def test_mock_monotonic_clock_current_seconds_zero_value() -> None:
    """
    Test MockMonotonicClock accepts zero current_seconds.
    """
    monotonic_clock = MockMonotonicClock(current_seconds=0)

    assert monotonic_clock.current_seconds() == 0.0


@mark.unit_testing
def test_mock_monotonic_clock_current_seconds_positive_random_value() -> None:
    """
    Test MockMonotonicClock accepts random positive current_seconds.
    """
    current_seconds = FloatMother.positive()
    monotonic_clock = MockMonotonicClock(current_seconds=current_seconds)

    assert monotonic_clock.current_seconds() == current_seconds


@mark.unit_testing
def test_mock_monotonic_clock_advance_method_happy_path() -> None:
    """
    Test MockMonotonicClock advance method happy path.
    """
    monotonic_clock = MockMonotonicClock(current_seconds=1)

    monotonic_clock.advance(seconds=2)

    assert monotonic_clock.current_seconds() == 3.0


@mark.unit_testing
def test_mock_monotonic_clock_advance_method_zero_value() -> None:
    """
    Test MockMonotonicClock advance method accepts zero.
    """
    monotonic_clock = MockMonotonicClock(current_seconds=1)

    monotonic_clock.advance(seconds=0)

    assert monotonic_clock.current_seconds() == 1.0


@mark.unit_testing
def test_mock_monotonic_clock_advance_method_invalid_type() -> None:
    """
    Test MockMonotonicClock advance method raises TypeError if seconds has invalid type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'MockMonotonicClock seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',  # noqa: E501
    ):
        MockMonotonicClock().advance(seconds=FloatMother.invalid_type())


@mark.unit_testing
def test_mock_monotonic_clock_advance_method_negative_random_value() -> None:
    """
    Test MockMonotonicClock advance method raises ValueError if seconds is random negative.
    """
    seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=rf'MockMonotonicClock seconds <<<{seconds}>>> must be greater than or equal to zero.',  # noqa: E501
    ):
        MockMonotonicClock().advance(seconds=seconds)


@mark.unit_testing
def test_mock_monotonic_clock_advance_method_negative_limit_value() -> None:
    """
    Test MockMonotonicClock advance method raises ValueError if seconds is negative limit.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'MockMonotonicClock seconds <<<-1.0>>> must be greater than or equal to zero.',  # noqa: E501
    ):
        MockMonotonicClock().advance(seconds=-1.0)


@mark.unit_testing
def test_mock_monotonic_clock_advance_method_positive_random_value() -> None:
    """
    Test MockMonotonicClock advance method accepts random positive seconds.
    """
    seconds = FloatMother.positive()
    monotonic_clock = MockMonotonicClock()

    monotonic_clock.advance(seconds=seconds)

    assert monotonic_clock.current_seconds() == seconds


@mark.unit_testing
def test_mock_monotonic_clock_set_current_seconds_method_happy_path() -> None:
    """
    Test MockMonotonicClock set_current_seconds method happy path.
    """
    current_seconds = FloatMother.positive()
    monotonic_clock = MockMonotonicClock()

    monotonic_clock.set_current_seconds(current_seconds=current_seconds)

    assert monotonic_clock.current_seconds() == current_seconds


@mark.unit_testing
def test_mock_monotonic_clock_set_current_seconds_method_invalid_type() -> None:
    """
    Test MockMonotonicClock set_current_seconds method raises TypeError if current_seconds has invalid type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'MockMonotonicClock current_seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',  # noqa: E501
    ):
        MockMonotonicClock().set_current_seconds(current_seconds=FloatMother.invalid_type())


@mark.unit_testing
def test_mock_monotonic_clock_set_current_seconds_method_equal_value() -> None:
    """
    Test MockMonotonicClock set_current_seconds method accepts the current timestamp.
    """
    monotonic_clock = MockMonotonicClock(current_seconds=1)

    monotonic_clock.set_current_seconds(current_seconds=1)

    assert monotonic_clock.current_seconds() == 1.0


@mark.unit_testing
def test_mock_monotonic_clock_set_current_seconds_method_lower_value() -> None:
    """
    Test MockMonotonicClock set_current_seconds method rejects a lower timestamp.
    """
    monotonic_clock = MockMonotonicClock(current_seconds=2)

    with assert_raises(
        expected_exception=ValueError,
        match=r'MockMonotonicClock current_seconds <<<1.0>>> must be greater than or equal to current seconds <<<2.0>>>.',  # noqa: E501
    ):
        monotonic_clock.set_current_seconds(current_seconds=1)

    assert monotonic_clock.current_seconds() == 2.0


@mark.unit_testing
def test_mock_monotonic_clock_assert_current_seconds_method_was_called_once() -> None:
    """
    Test MockMonotonicClock asserts current_seconds method was called once.
    """
    monotonic_clock = MockMonotonicClock()

    monotonic_clock.current_seconds()

    monotonic_clock.assert_current_seconds_method_was_called_once()


@mark.unit_testing
def test_mock_monotonic_clock_assert_current_seconds_method_was_called_once_after_multiple_calls() -> None:
    """
    Test MockMonotonicClock raises AssertionError when current_seconds was called multiple times.
    """
    monotonic_clock = MockMonotonicClock()
    monotonic_clock.current_seconds()
    monotonic_clock.current_seconds()

    with assert_raises(expected_exception=AssertionError):
        monotonic_clock.assert_current_seconds_method_was_called_once()


@mark.unit_testing
def test_mock_monotonic_clock_assert_current_seconds_method_was_not_called() -> None:
    """
    Test MockMonotonicClock asserts current_seconds method was not called.
    """
    MockMonotonicClock().assert_current_seconds_method_was_not_called()


@mark.unit_testing
def test_mock_monotonic_clock_assert_current_seconds_method_was_not_called_after_call() -> None:
    """
    Test MockMonotonicClock raises AssertionError when current_seconds was called.
    """
    monotonic_clock = MockMonotonicClock()
    monotonic_clock.current_seconds()

    with assert_raises(expected_exception=AssertionError):
        monotonic_clock.assert_current_seconds_method_was_not_called()
