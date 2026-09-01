"""
Test SystemSleeper sleeper.
"""

from unittest.mock import patch

from object_mother_pattern import FloatMother
from pytest import mark, raises as assert_raises

from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.sleepers import SystemSleeper


@mark.unit_testing
def test_system_sleeper_happy_path() -> None:
    """
    Test SystemSleeper sleeper happy path.
    """
    with patch('clock_pattern.sleepers.system_sleeper.sleep') as sleep_mock:
        SystemSleeper(monotonic_clock=MockMonotonicClock()).sleep(seconds=1)

    sleep_mock.assert_called_once_with(1)


@mark.unit_testing
def test_system_sleeper_sleep_method_seconds_invalid_type() -> None:
    """
    Test SystemSleeper sleep method raises TypeError if seconds has invalid type.
    """
    sleeper = SystemSleeper(monotonic_clock=MockMonotonicClock())

    with assert_raises(
        expected_exception=TypeError,
        match=r'SystemSleeper seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
    ):
        sleeper.sleep(seconds=FloatMother.invalid_type())


@mark.unit_testing
def test_system_sleeper_sleep_method_seconds_negative_random_value() -> None:
    """
    Test SystemSleeper sleep method raises ValueError if seconds is random negative.
    """
    seconds = FloatMother.negative()
    sleeper = SystemSleeper(monotonic_clock=MockMonotonicClock())

    with assert_raises(
        expected_exception=ValueError,
        match=rf'SystemSleeper seconds <<<{seconds}>>> must be greater than or equal to zero.',
    ):
        sleeper.sleep(seconds=seconds)


@mark.unit_testing
def test_system_sleeper_sleep_method_seconds_negative_limit_value() -> None:
    """
    Test SystemSleeper sleep method raises ValueError if seconds is negative limit.
    """
    sleeper = SystemSleeper(monotonic_clock=MockMonotonicClock())

    with assert_raises(
        expected_exception=ValueError,
        match=r'SystemSleeper seconds <<<-1.0>>> must be greater than or equal to zero.',
    ):
        sleeper.sleep(seconds=-1.0)


@mark.unit_testing
def test_system_sleeper_sleep_method_seconds_zero_value() -> None:
    """
    Test SystemSleeper sleep method accepts zero seconds.
    """
    sleeper = SystemSleeper(monotonic_clock=MockMonotonicClock())

    with patch('clock_pattern.sleepers.system_sleeper.sleep') as sleep_mock:
        sleeper.sleep(seconds=0)

    sleep_mock.assert_called_once_with(0)


@mark.unit_testing
def test_system_sleeper_sleep_method_seconds_positive_random_value() -> None:
    """
    Test SystemSleeper sleep method accepts random positive seconds.
    """
    seconds = FloatMother.positive()
    sleeper = SystemSleeper(monotonic_clock=MockMonotonicClock())

    with patch('clock_pattern.sleepers.system_sleeper.sleep') as sleep_mock:
        sleeper.sleep(seconds=seconds)

    sleep_mock.assert_called_once_with(seconds)


@mark.unit_testing
def test_system_sleeper_minimum_duration_method_sleeps_remaining_seconds() -> None:
    """
    Test SystemSleeper minimum_duration method sleeps remaining seconds.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = SystemSleeper(monotonic_clock=monotonic_clock)

    with patch('clock_pattern.sleepers.system_sleeper.sleep') as sleep_mock, sleeper.minimum_duration(seconds=2):
        monotonic_clock.advance(seconds=0.5)

    sleep_mock.assert_called_once_with(1.5)


@mark.unit_testing
def test_system_sleeper_minimum_duration_method_does_not_sleep_if_elapsed_time_is_enough() -> None:
    """
    Test SystemSleeper minimum_duration method does not sleep if elapsed time is enough.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = SystemSleeper(monotonic_clock=monotonic_clock)

    with patch('clock_pattern.sleepers.system_sleeper.sleep') as sleep_mock, sleeper.minimum_duration(seconds=2):
        monotonic_clock.advance(seconds=2)

    sleep_mock.assert_not_called()


@mark.unit_testing
def test_system_sleeper_minimum_duration_method_does_not_sleep_if_elapsed_time_is_more_than_enough() -> None:
    """
    Test SystemSleeper minimum_duration method does not sleep if elapsed time is more than enough.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = SystemSleeper(monotonic_clock=monotonic_clock)

    with patch('clock_pattern.sleepers.system_sleeper.sleep') as sleep_mock, sleeper.minimum_duration(seconds=2):
        monotonic_clock.advance(seconds=3)

    sleep_mock.assert_not_called()


@mark.unit_testing
def test_system_sleeper_minimum_duration_method_seconds_invalid_type() -> None:
    """
    Test SystemSleeper minimum_duration method raises TypeError if seconds has invalid type.
    """
    sleeper = SystemSleeper(monotonic_clock=MockMonotonicClock())

    with (
        assert_raises(
            expected_exception=TypeError,
            match=r'SystemSleeper seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
        ),
        sleeper.minimum_duration(seconds=FloatMother.invalid_type()),
    ):
        pass


@mark.unit_testing
def test_system_sleeper_minimum_duration_method_seconds_negative_random_value() -> None:
    """
    Test SystemSleeper minimum_duration method raises ValueError if seconds is random negative.
    """
    seconds = FloatMother.negative()
    sleeper = SystemSleeper(monotonic_clock=MockMonotonicClock())

    with (
        assert_raises(
            expected_exception=ValueError,
            match=rf'SystemSleeper seconds <<<{seconds}>>> must be greater than or equal to zero.',
        ),
        sleeper.minimum_duration(seconds=seconds),
    ):
        pass


@mark.unit_testing
def test_system_sleeper_minimum_duration_method_seconds_negative_limit_value() -> None:
    """
    Test SystemSleeper minimum_duration method raises ValueError if seconds is negative limit.
    """
    sleeper = SystemSleeper(monotonic_clock=MockMonotonicClock())

    with (
        assert_raises(
            expected_exception=ValueError,
            match=r'SystemSleeper seconds <<<-1.0>>> must be greater than or equal to zero.',
        ),
        sleeper.minimum_duration(seconds=-1.0),
    ):
        pass


@mark.unit_testing
def test_system_sleeper_minimum_duration_method_seconds_zero_value() -> None:
    """
    Test SystemSleeper minimum_duration method accepts zero seconds.
    """
    sleeper = SystemSleeper(monotonic_clock=MockMonotonicClock())

    with patch('clock_pattern.sleepers.system_sleeper.sleep') as sleep_mock, sleeper.minimum_duration(seconds=0):
        pass

    sleep_mock.assert_not_called()


@mark.unit_testing
def test_system_sleeper_minimum_duration_method_seconds_positive_random_value() -> None:
    """
    Test SystemSleeper minimum_duration method accepts random positive seconds.
    """
    seconds = FloatMother.positive()
    sleeper = SystemSleeper(monotonic_clock=MockMonotonicClock())

    with patch('clock_pattern.sleepers.system_sleeper.sleep') as sleep_mock, sleeper.minimum_duration(seconds=seconds):
        pass

    sleep_mock.assert_called_once_with(seconds)


@mark.unit_testing
def test_system_sleeper_minimum_duration_method_sleeps_if_context_body_raises() -> None:
    """
    Test SystemSleeper minimum_duration method sleeps remaining seconds if the context body raises.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = SystemSleeper(monotonic_clock=monotonic_clock)

    with (
        patch('clock_pattern.sleepers.system_sleeper.sleep') as sleep_mock,
        assert_raises(expected_exception=RuntimeError, match='work failed'),
        sleeper.minimum_duration(seconds=2),
    ):
        monotonic_clock.advance(seconds=0.5)
        raise RuntimeError('work failed')

    sleep_mock.assert_called_once_with(1.5)
