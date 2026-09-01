"""
Test MockSleeperAsync sleeper.
"""

from object_mother_pattern import FloatMother
from pytest import mark, raises as assert_raises

from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.sleepers.testing import MockSleeperAsync


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_happy_path() -> None:
    """
    Test MockSleeperAsync sleeper happy path.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)

    await sleeper.sleep(seconds=1)

    assert sleeper.sleep_calls == (1,)
    assert monotonic_clock.current_seconds() == 1.0
    sleeper.assert_sleep_method_was_called_once_with(seconds=1)


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_records_sleep_calls_in_order() -> None:
    """
    Test MockSleeperAsync records sleep calls in order and advances its monotonic clock.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)

    await sleeper.sleep(seconds=1)
    await sleeper.sleep(seconds=2)

    assert type(sleeper.sleep_calls) is tuple
    assert sleeper.sleep_calls == (1, 2)
    assert monotonic_clock.current_seconds() == 3.0


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_sleep_method_seconds_invalid_type() -> None:
    """
    Test MockSleeperAsync sleep method raises TypeError if seconds has invalid type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'MockSleeperAsync seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
    ):
        await MockSleeperAsync(monotonic_clock=MockMonotonicClock()).sleep(seconds=FloatMother.invalid_type())


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_sleep_method_seconds_negative_random_value() -> None:
    """
    Test MockSleeperAsync sleep method raises ValueError if seconds is random negative.
    """
    seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=rf'MockSleeperAsync seconds <<<{seconds}>>> must be greater than or equal to zero.',
    ):
        await MockSleeperAsync(monotonic_clock=MockMonotonicClock()).sleep(seconds=seconds)


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_sleep_method_seconds_negative_limit_value() -> None:
    """
    Test MockSleeperAsync sleep method raises ValueError if seconds is negative limit.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'MockSleeperAsync seconds <<<-1.0>>> must be greater than or equal to zero.',
    ):
        await MockSleeperAsync(monotonic_clock=MockMonotonicClock()).sleep(seconds=-1.0)


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_sleep_method_seconds_zero_value() -> None:
    """
    Test MockSleeperAsync sleep method accepts zero seconds.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)

    await sleeper.sleep(seconds=0)

    assert sleeper.sleep_calls == (0,)
    assert monotonic_clock.current_seconds() == 0.0
    sleeper.assert_sleep_method_was_called_once_with(seconds=0)


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_sleep_method_seconds_positive_random_value() -> None:
    """
    Test MockSleeperAsync sleep method accepts random positive seconds.
    """
    seconds = FloatMother.positive()
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)

    await sleeper.sleep(seconds=seconds)

    assert sleeper.sleep_calls == (seconds,)
    assert monotonic_clock.current_seconds() == seconds
    sleeper.assert_sleep_method_was_called_once_with(seconds=seconds)


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_minimum_duration_method_sleeps_remaining_seconds() -> None:
    """
    Test MockSleeperAsync minimum_duration method sleeps remaining seconds.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)

    async with sleeper.minimum_duration(seconds=2):
        monotonic_clock.advance(seconds=0.5)

    assert sleeper.sleep_calls == (1.5,)
    assert monotonic_clock.current_seconds() == 2.0
    sleeper.assert_sleep_method_was_called_once_with(seconds=1.5)


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_minimum_duration_method_does_not_sleep_if_elapsed_time_is_enough() -> None:
    """
    Test MockSleeperAsync minimum_duration method does not sleep if elapsed time is enough.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)

    async with sleeper.minimum_duration(seconds=2):
        monotonic_clock.advance(seconds=2)

    assert sleeper.sleep_calls == ()
    assert monotonic_clock.current_seconds() == 2.0
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_minimum_duration_method_does_not_sleep_if_elapsed_time_is_more_than_enough() -> None:
    """
    Test MockSleeperAsync minimum_duration method does not sleep if elapsed time is more than enough.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)

    async with sleeper.minimum_duration(seconds=2):
        monotonic_clock.advance(seconds=3)

    assert sleeper.sleep_calls == ()
    assert monotonic_clock.current_seconds() == 3.0
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_minimum_duration_method_seconds_invalid_type() -> None:
    """
    Test MockSleeperAsync minimum_duration method raises TypeError if seconds has invalid type.
    """
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())

    with assert_raises(
        expected_exception=TypeError,
        match=r'MockSleeperAsync seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
    ):
        async with sleeper.minimum_duration(seconds=FloatMother.invalid_type()):
            pass


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_minimum_duration_method_seconds_negative_random_value() -> None:
    """
    Test MockSleeperAsync minimum_duration method raises ValueError if seconds is random negative.
    """
    seconds = FloatMother.negative()
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())

    with assert_raises(
        expected_exception=ValueError,
        match=rf'MockSleeperAsync seconds <<<{seconds}>>> must be greater than or equal to zero.',
    ):
        async with sleeper.minimum_duration(seconds=seconds):
            pass


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_minimum_duration_method_seconds_negative_limit_value() -> None:
    """
    Test MockSleeperAsync minimum_duration method raises ValueError if seconds is negative limit.
    """
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())

    with assert_raises(
        expected_exception=ValueError,
        match=r'MockSleeperAsync seconds <<<-1.0>>> must be greater than or equal to zero.',
    ):
        async with sleeper.minimum_duration(seconds=-1.0):
            pass


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_minimum_duration_method_seconds_zero_value() -> None:
    """
    Test MockSleeperAsync minimum_duration method accepts zero seconds.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)

    async with sleeper.minimum_duration(seconds=0):
        pass

    assert sleeper.sleep_calls == ()
    assert monotonic_clock.current_seconds() == 0.0
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_minimum_duration_method_seconds_positive_random_value() -> None:
    """
    Test MockSleeperAsync minimum_duration method accepts random positive seconds.
    """
    seconds = FloatMother.positive()
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)

    async with sleeper.minimum_duration(seconds=seconds):
        pass

    assert sleeper.sleep_calls == (seconds,)
    assert monotonic_clock.current_seconds() == seconds
    sleeper.assert_sleep_method_was_called_once_with(seconds=seconds)


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_minimum_duration_method_sleeps_if_context_body_raises() -> None:
    """
    Test MockSleeperAsync minimum_duration method sleeps remaining seconds if the context body raises.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)

    with assert_raises(expected_exception=RuntimeError, match='work failed'):
        async with sleeper.minimum_duration(seconds=2):
            monotonic_clock.advance(seconds=0.5)
            raise RuntimeError('work failed')

    assert sleeper.sleep_calls == (1.5,)
    assert monotonic_clock.current_seconds() == 2.0


@mark.unit_testing
def test_mock_sleeper_async_assert_sleep_method_was_not_called() -> None:
    """
    Test MockSleeperAsync asserts sleep method was not called.
    """
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())

    assert sleeper.sleep_calls == ()
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_assert_sleep_method_was_not_called_after_call() -> None:
    """
    Test MockSleeperAsync raises AssertionError when sleep method was called.
    """
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())
    await sleeper.sleep(seconds=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=r'^Expected mock to not have been awaited\. Awaited 1 times\.$',
    ):
        sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_assert_sleep_method_was_called_once_with_different_seconds() -> None:
    """
    Test MockSleeperAsync raises AssertionError when sleep method was awaited with different seconds.
    """
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())
    await sleeper.sleep(seconds=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=r'^expected await not found\.\nExpected: mock\(seconds=2\)\n  Actual: mock\(seconds=1\)$',
    ):
        sleeper.assert_sleep_method_was_called_once_with(seconds=2)


@mark.unit_testing
@mark.asyncio
async def test_mock_sleeper_async_assert_sleep_method_was_called_once_with_after_multiple_calls() -> None:
    """
    Test MockSleeperAsync raises AssertionError when sleep method was awaited multiple times.
    """
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())
    await sleeper.sleep(seconds=1)
    await sleeper.sleep(seconds=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=r'^Expected mock to have been awaited once\. Awaited 2 times\.$',
    ):
        sleeper.assert_sleep_method_was_called_once_with(seconds=1)


@mark.unit_testing
def test_mock_sleeper_async_assert_sleep_method_seconds_invalid_type() -> None:
    """
    Test MockSleeperAsync assert sleep method raises TypeError if seconds has invalid type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'MockSleeperAsync seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
    ):
        MockSleeperAsync(monotonic_clock=MockMonotonicClock()).assert_sleep_method_was_called_once_with(
            seconds=FloatMother.invalid_type(),
        )


@mark.unit_testing
def test_mock_sleeper_async_assert_sleep_method_seconds_negative_limit_value() -> None:
    """
    Test MockSleeperAsync assert sleep method raises ValueError if seconds is negative limit.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'MockSleeperAsync seconds <<<-1.0>>> must be greater than or equal to zero.',
    ):
        MockSleeperAsync(monotonic_clock=MockMonotonicClock()).assert_sleep_method_was_called_once_with(seconds=-1.0)
