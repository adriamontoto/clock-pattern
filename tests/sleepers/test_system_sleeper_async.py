"""
Test SystemSleeperAsync sleeper.
"""

from unittest.mock import patch

from object_mother_pattern import FloatMother
from pytest import mark, raises as assert_raises

from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.sleepers import SystemSleeperAsync


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_happy_path() -> None:
    """
    Test SystemSleeperAsync sleeper happy path.
    """
    with patch('clock_pattern.sleepers.system_sleeper_async.sleep') as sleep_mock:
        await SystemSleeperAsync(monotonic_clock=MockMonotonicClock()).sleep(seconds=1)

    sleep_mock.assert_awaited_once_with(1)


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_sleep_method_seconds_invalid_type() -> None:
    """
    Test SystemSleeperAsync sleep method raises TypeError if seconds has invalid type.
    """
    sleeper = SystemSleeperAsync(monotonic_clock=MockMonotonicClock())

    with assert_raises(
        expected_exception=TypeError,
        match=r'SystemSleeperAsync seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
    ):
        await sleeper.sleep(seconds=FloatMother.invalid_type())


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_sleep_method_seconds_negative_random_value() -> None:
    """
    Test SystemSleeperAsync sleep method raises ValueError if seconds is random negative.
    """
    seconds = FloatMother.negative()
    sleeper = SystemSleeperAsync(monotonic_clock=MockMonotonicClock())

    with assert_raises(
        expected_exception=ValueError,
        match=rf'SystemSleeperAsync seconds <<<{seconds}>>> must be greater than or equal to zero.',
    ):
        await sleeper.sleep(seconds=seconds)


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_sleep_method_seconds_negative_limit_value() -> None:
    """
    Test SystemSleeperAsync sleep method raises ValueError if seconds is negative limit.
    """
    sleeper = SystemSleeperAsync(monotonic_clock=MockMonotonicClock())

    with assert_raises(
        expected_exception=ValueError,
        match=r'SystemSleeperAsync seconds <<<-1.0>>> must be greater than or equal to zero.',
    ):
        await sleeper.sleep(seconds=-1.0)


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_sleep_method_seconds_zero_value() -> None:
    """
    Test SystemSleeperAsync sleep method accepts zero seconds.
    """
    sleeper = SystemSleeperAsync(monotonic_clock=MockMonotonicClock())

    with patch('clock_pattern.sleepers.system_sleeper_async.sleep') as sleep_mock:
        await sleeper.sleep(seconds=0)

    sleep_mock.assert_awaited_once_with(0)


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_sleep_method_seconds_positive_random_value() -> None:
    """
    Test SystemSleeperAsync sleep method accepts random positive seconds.
    """
    seconds = FloatMother.positive()
    sleeper = SystemSleeperAsync(monotonic_clock=MockMonotonicClock())

    with patch('clock_pattern.sleepers.system_sleeper_async.sleep') as sleep_mock:
        await sleeper.sleep(seconds=seconds)

    sleep_mock.assert_awaited_once_with(seconds)


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_minimum_duration_method_sleeps_remaining_seconds() -> None:
    """
    Test SystemSleeperAsync minimum_duration method sleeps remaining seconds.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = SystemSleeperAsync(monotonic_clock=monotonic_clock)

    with patch('clock_pattern.sleepers.system_sleeper_async.sleep') as sleep_mock:
        async with sleeper.minimum_duration(seconds=2):
            monotonic_clock.advance(seconds=0.5)

    sleep_mock.assert_awaited_once_with(1.5)


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_minimum_duration_method_does_not_sleep_if_elapsed_time_is_enough() -> None:
    """
    Test SystemSleeperAsync minimum_duration method does not sleep if elapsed time is enough.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = SystemSleeperAsync(monotonic_clock=monotonic_clock)

    with patch('clock_pattern.sleepers.system_sleeper_async.sleep') as sleep_mock:
        async with sleeper.minimum_duration(seconds=2):
            monotonic_clock.advance(seconds=2)

    sleep_mock.assert_not_awaited()


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_minimum_duration_method_does_not_sleep_if_elapsed_time_is_more_than_enough() -> (
    None
):
    """
    Test SystemSleeperAsync minimum_duration method does not sleep if elapsed time is more than enough.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = SystemSleeperAsync(monotonic_clock=monotonic_clock)

    with patch('clock_pattern.sleepers.system_sleeper_async.sleep') as sleep_mock:
        async with sleeper.minimum_duration(seconds=2):
            monotonic_clock.advance(seconds=3)

    sleep_mock.assert_not_awaited()


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_minimum_duration_method_seconds_invalid_type() -> None:
    """
    Test SystemSleeperAsync minimum_duration method raises TypeError if seconds has invalid type.
    """
    sleeper = SystemSleeperAsync(monotonic_clock=MockMonotonicClock())

    with assert_raises(
        expected_exception=TypeError,
        match=r'SystemSleeperAsync seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
    ):
        async with sleeper.minimum_duration(seconds=FloatMother.invalid_type()):
            pass


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_minimum_duration_method_seconds_negative_random_value() -> None:
    """
    Test SystemSleeperAsync minimum_duration method raises ValueError if seconds is random negative.
    """
    seconds = FloatMother.negative()
    sleeper = SystemSleeperAsync(monotonic_clock=MockMonotonicClock())

    with assert_raises(
        expected_exception=ValueError,
        match=rf'SystemSleeperAsync seconds <<<{seconds}>>> must be greater than or equal to zero.',
    ):
        async with sleeper.minimum_duration(seconds=seconds):
            pass


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_minimum_duration_method_seconds_negative_limit_value() -> None:
    """
    Test SystemSleeperAsync minimum_duration method raises ValueError if seconds is negative limit.
    """
    sleeper = SystemSleeperAsync(monotonic_clock=MockMonotonicClock())

    with assert_raises(
        expected_exception=ValueError,
        match=r'SystemSleeperAsync seconds <<<-1.0>>> must be greater than or equal to zero.',
    ):
        async with sleeper.minimum_duration(seconds=-1.0):
            pass


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_minimum_duration_method_seconds_zero_value() -> None:
    """
    Test SystemSleeperAsync minimum_duration method accepts zero seconds.
    """
    sleeper = SystemSleeperAsync(monotonic_clock=MockMonotonicClock())

    with patch('clock_pattern.sleepers.system_sleeper_async.sleep') as sleep_mock:
        async with sleeper.minimum_duration(seconds=0):
            pass

    sleep_mock.assert_not_awaited()


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_minimum_duration_method_seconds_positive_random_value() -> None:
    """
    Test SystemSleeperAsync minimum_duration method accepts random positive seconds.
    """
    seconds = FloatMother.positive()
    sleeper = SystemSleeperAsync(monotonic_clock=MockMonotonicClock())

    with patch('clock_pattern.sleepers.system_sleeper_async.sleep') as sleep_mock:
        async with sleeper.minimum_duration(seconds=seconds):
            pass

    sleep_mock.assert_awaited_once_with(seconds)


@mark.unit_testing
@mark.asyncio
async def test_system_sleeper_async_minimum_duration_method_sleeps_if_context_body_raises() -> None:
    """
    Test SystemSleeperAsync minimum_duration method sleeps remaining seconds if the context body raises.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = SystemSleeperAsync(monotonic_clock=monotonic_clock)

    with (
        patch('clock_pattern.sleepers.system_sleeper_async.sleep') as sleep_mock,
        assert_raises(expected_exception=RuntimeError, match='work failed'),
    ):
        async with sleeper.minimum_duration(seconds=2):
            monotonic_clock.advance(seconds=0.5)
            raise RuntimeError('work failed')

    sleep_mock.assert_awaited_once_with(1.5)
