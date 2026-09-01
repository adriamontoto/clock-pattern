"""
Test MockSleeper sleeper.
"""

from object_mother_pattern import FloatMother
from pytest import mark, raises as assert_raises

from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.sleepers.testing import MockSleeper


@mark.unit_testing
def test_mock_sleeper_happy_path() -> None:
    """
    Test MockSleeper sleeper happy path.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)

    sleeper.sleep(seconds=1)

    assert sleeper.sleep_calls == (1,)
    assert monotonic_clock.current_seconds() == 1.0
    sleeper.assert_sleep_method_was_called_once_with(seconds=1)


@mark.unit_testing
def test_mock_sleeper_records_sleep_calls_in_order() -> None:
    """
    Test MockSleeper records sleep calls in order and advances its monotonic clock.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)

    sleeper.sleep(seconds=1)
    sleeper.sleep(seconds=2)

    assert type(sleeper.sleep_calls) is tuple
    assert sleeper.sleep_calls == (1, 2)
    assert monotonic_clock.current_seconds() == 3.0


@mark.unit_testing
def test_mock_sleeper_sleep_method_seconds_invalid_type() -> None:
    """
    Test MockSleeper sleep method raises TypeError if seconds has invalid type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'MockSleeper seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
    ):
        MockSleeper(monotonic_clock=MockMonotonicClock()).sleep(seconds=FloatMother.invalid_type())


@mark.unit_testing
def test_mock_sleeper_sleep_method_seconds_negative_random_value() -> None:
    """
    Test MockSleeper sleep method raises ValueError if seconds is random negative.
    """
    seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=rf'MockSleeper seconds <<<{seconds}>>> must be greater than or equal to zero.',
    ):
        MockSleeper(monotonic_clock=MockMonotonicClock()).sleep(seconds=seconds)


@mark.unit_testing
def test_mock_sleeper_sleep_method_seconds_negative_limit_value() -> None:
    """
    Test MockSleeper sleep method raises ValueError if seconds is negative limit.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'MockSleeper seconds <<<-1.0>>> must be greater than or equal to zero.',
    ):
        MockSleeper(monotonic_clock=MockMonotonicClock()).sleep(seconds=-1.0)


@mark.unit_testing
def test_mock_sleeper_sleep_method_seconds_zero_value() -> None:
    """
    Test MockSleeper sleep method accepts zero seconds.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)

    sleeper.sleep(seconds=0)

    assert sleeper.sleep_calls == (0,)
    assert monotonic_clock.current_seconds() == 0.0
    sleeper.assert_sleep_method_was_called_once_with(seconds=0)


@mark.unit_testing
def test_mock_sleeper_sleep_method_seconds_positive_random_value() -> None:
    """
    Test MockSleeper sleep method accepts random positive seconds.
    """
    seconds = FloatMother.positive()
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)

    sleeper.sleep(seconds=seconds)

    assert sleeper.sleep_calls == (seconds,)
    assert monotonic_clock.current_seconds() == seconds
    sleeper.assert_sleep_method_was_called_once_with(seconds=seconds)


@mark.unit_testing
def test_mock_sleeper_minimum_duration_method_sleeps_remaining_seconds() -> None:
    """
    Test MockSleeper minimum_duration method sleeps remaining seconds.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)

    with sleeper.minimum_duration(seconds=2):
        monotonic_clock.advance(seconds=0.5)

    assert sleeper.sleep_calls == (1.5,)
    assert monotonic_clock.current_seconds() == 2.0
    sleeper.assert_sleep_method_was_called_once_with(seconds=1.5)


@mark.unit_testing
def test_mock_sleeper_minimum_duration_method_does_not_sleep_if_elapsed_time_is_enough() -> None:
    """
    Test MockSleeper minimum_duration method does not sleep if elapsed time is enough.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)

    with sleeper.minimum_duration(seconds=2):
        monotonic_clock.advance(seconds=2)

    assert sleeper.sleep_calls == ()
    assert monotonic_clock.current_seconds() == 2.0
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
def test_mock_sleeper_minimum_duration_method_does_not_sleep_if_elapsed_time_is_more_than_enough() -> None:
    """
    Test MockSleeper minimum_duration method does not sleep if elapsed time is more than enough.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)

    with sleeper.minimum_duration(seconds=2):
        monotonic_clock.advance(seconds=3)

    assert sleeper.sleep_calls == ()
    assert monotonic_clock.current_seconds() == 3.0
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
def test_mock_sleeper_minimum_duration_method_seconds_invalid_type() -> None:
    """
    Test MockSleeper minimum_duration method raises TypeError if seconds has invalid type.
    """
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())

    with (
        assert_raises(
            expected_exception=TypeError,
            match=r'MockSleeper seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
        ),
        sleeper.minimum_duration(seconds=FloatMother.invalid_type()),
    ):
        pass


@mark.unit_testing
def test_mock_sleeper_minimum_duration_method_seconds_negative_random_value() -> None:
    """
    Test MockSleeper minimum_duration method raises ValueError if seconds is random negative.
    """
    seconds = FloatMother.negative()
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())

    with (
        assert_raises(
            expected_exception=ValueError,
            match=rf'MockSleeper seconds <<<{seconds}>>> must be greater than or equal to zero.',
        ),
        sleeper.minimum_duration(seconds=seconds),
    ):
        pass


@mark.unit_testing
def test_mock_sleeper_minimum_duration_method_seconds_negative_limit_value() -> None:
    """
    Test MockSleeper minimum_duration method raises ValueError if seconds is negative limit.
    """
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())

    with (
        assert_raises(
            expected_exception=ValueError,
            match=r'MockSleeper seconds <<<-1.0>>> must be greater than or equal to zero.',
        ),
        sleeper.minimum_duration(seconds=-1.0),
    ):
        pass


@mark.unit_testing
def test_mock_sleeper_minimum_duration_method_seconds_zero_value() -> None:
    """
    Test MockSleeper minimum_duration method accepts zero seconds.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)

    with sleeper.minimum_duration(seconds=0):
        pass

    assert sleeper.sleep_calls == ()
    assert monotonic_clock.current_seconds() == 0.0
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
def test_mock_sleeper_minimum_duration_method_seconds_positive_random_value() -> None:
    """
    Test MockSleeper minimum_duration method accepts random positive seconds.
    """
    seconds = FloatMother.positive()
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)

    with sleeper.minimum_duration(seconds=seconds):
        pass

    assert sleeper.sleep_calls == (seconds,)
    assert monotonic_clock.current_seconds() == seconds
    sleeper.assert_sleep_method_was_called_once_with(seconds=seconds)


@mark.unit_testing
def test_mock_sleeper_minimum_duration_method_sleeps_if_context_body_raises() -> None:
    """
    Test MockSleeper minimum_duration method sleeps remaining seconds if the context body raises.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)

    with assert_raises(expected_exception=RuntimeError, match='work failed'), sleeper.minimum_duration(seconds=2):
        monotonic_clock.advance(seconds=0.5)
        raise RuntimeError('work failed')

    assert sleeper.sleep_calls == (1.5,)
    assert monotonic_clock.current_seconds() == 2.0


@mark.unit_testing
def test_mock_sleeper_assert_sleep_method_was_not_called() -> None:
    """
    Test MockSleeper asserts sleep method was not called.
    """
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())

    assert sleeper.sleep_calls == ()
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
def test_mock_sleeper_assert_sleep_method_was_not_called_after_call() -> None:
    """
    Test MockSleeper raises AssertionError when sleep method was called.
    """
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())
    sleeper.sleep(seconds=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=r'^Expected \'mock\' to not have been called\. Called 1 times\.\nCalls: \[call\(seconds=1\)\]\.$',
    ):
        sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
def test_mock_sleeper_assert_sleep_method_was_called_once_with_different_seconds() -> None:
    """
    Test MockSleeper raises AssertionError when sleep method was called with different seconds.
    """
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())
    sleeper.sleep(seconds=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=r'^expected call not found\.\nExpected: mock\(seconds=2\)\n  Actual: mock\(seconds=1\)$',
    ):
        sleeper.assert_sleep_method_was_called_once_with(seconds=2)


@mark.unit_testing
def test_mock_sleeper_assert_sleep_method_was_called_once_with_after_multiple_calls() -> None:
    """
    Test MockSleeper raises AssertionError when sleep method was called multiple times.
    """
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())
    sleeper.sleep(seconds=1)
    sleeper.sleep(seconds=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=r'^Expected \'mock\' to be called once\. Called 2 times\.\nCalls: \[call\(seconds=1\), call\(seconds=1\)\]\.$',  # noqa: E501
    ):
        sleeper.assert_sleep_method_was_called_once_with(seconds=1)


@mark.unit_testing
def test_mock_sleeper_assert_sleep_method_seconds_invalid_type() -> None:
    """
    Test MockSleeper assert sleep method raises TypeError if seconds has invalid type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'MockSleeper seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
    ):
        MockSleeper(monotonic_clock=MockMonotonicClock()).assert_sleep_method_was_called_once_with(
            seconds=FloatMother.invalid_type(),
        )


@mark.unit_testing
def test_mock_sleeper_assert_sleep_method_seconds_negative_limit_value() -> None:
    """
    Test MockSleeper assert sleep method raises ValueError if seconds is negative limit.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'MockSleeper seconds <<<-1.0>>> must be greater than or equal to zero.',
    ):
        MockSleeper(monotonic_clock=MockMonotonicClock()).assert_sleep_method_was_called_once_with(seconds=-1.0)
