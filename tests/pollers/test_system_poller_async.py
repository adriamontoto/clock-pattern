"""
Test SystemPollerAsync poller.
"""

from re import escape
from typing import Any, cast
from unittest.mock import AsyncMock, Mock

from object_mother_pattern import FloatMother
from pytest import mark, raises as assert_raises

from clock_pattern.deadlines import TimeoutExpiredError
from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.pollers import PollerAsync, SystemPollerAsync
from clock_pattern.sleepers.models import SleeperAsync
from clock_pattern.sleepers.testing import MockSleeperAsync


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_happy_path() -> None:
    """
    Test SystemPollerAsync is a PollerAsync with explicitly injected dependencies.
    """
    monotonic_clock = MockMonotonicClock()
    poller = SystemPollerAsync(
        sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
        monotonic_clock=monotonic_clock,
    )

    assert isinstance(poller, PollerAsync)

    await poller.poll_until(condition=lambda: True, timeout_seconds=1)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_poll_until_method_evaluates_sync_condition_immediately_without_sleeping() -> None:
    """
    Test SystemPollerAsync evaluates a successful synchronous condition once without sleeping.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)
    condition = Mock(return_value=True)

    await SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
        condition=condition,
        timeout_seconds=1,
    )

    assert condition.call_count == 1
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_poll_until_method_sleeps_until_sync_condition_returns_true() -> None:
    """
    Test SystemPollerAsync sleeps between false and true synchronous condition results.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)
    condition = Mock(side_effect=(False, True))

    await SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
        condition=condition,
        timeout_seconds=1,
        interval_seconds=0.25,
    )

    assert condition.call_count == 2
    assert sleeper.sleep_calls == (0.25,)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_poll_until_method_sleeps_until_awaitable_condition_returns_true() -> None:
    """
    Test SystemPollerAsync awaits false and true condition results.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)
    condition = AsyncMock(side_effect=(False, True))

    await SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
        condition=condition,
        timeout_seconds=1,
        interval_seconds=0.25,
    )

    assert condition.await_count == 2
    assert sleeper.sleep_calls == (0.25,)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_poll_until_method_caps_sleep_after_awaitable_condition_work() -> None:
    """
    Test SystemPollerAsync accounts for awaitable condition work when capping the next sleep.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)
    condition_call_count = 0

    async def condition() -> bool:
        nonlocal condition_call_count
        condition_call_count += 1

        if condition_call_count == 1:
            monotonic_clock.advance(seconds=0.75)
            return False

        return True

    await SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
        condition=condition,
        timeout_seconds=1,
        interval_seconds=2,
    )

    assert condition_call_count == 2
    assert sleeper.sleep_calls == (0.25,)
    assert monotonic_clock.current_seconds() == 1.0


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_poll_until_method_accepts_true_condition_at_zero_timeout() -> None:
    """
    Test SystemPollerAsync lets an immediately true condition win at a zero timeout.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)
    condition = AsyncMock(return_value=True)

    await SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
        condition=condition,
        timeout_seconds=0,
    )

    assert condition.await_count == 1
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_poll_until_method_rejects_false_condition_at_zero_timeout_without_sleeping() -> None:
    """
    Test SystemPollerAsync raises immediately for a false condition at a zero timeout.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)
    condition = AsyncMock(return_value=False)

    with assert_raises(
        expected_exception=TimeoutExpiredError,
        match=escape('Deadline expired after <<<0.0>>> seconds.'),
    ):
        await SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
            condition=condition,
            timeout_seconds=0,
        )

    assert condition.await_count == 1
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_poll_until_method_does_not_sleep_again_after_timeout_expires() -> None:
    """
    Test SystemPollerAsync stops before an additional sleep after deadline expiry.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)
    condition = AsyncMock(return_value=False)

    with assert_raises(
        expected_exception=TimeoutExpiredError,
        match=escape('Deadline expired after <<<1.0>>> seconds.'),
    ):
        await SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=0.25,
        )

    assert condition.await_count == 5
    assert sleeper.sleep_calls == (0.25, 0.25, 0.25, 0.25)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_poll_until_method_propagates_condition_exception() -> None:
    """
    Test SystemPollerAsync propagates the original condition exception unchanged.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)
    exception = RuntimeError('condition failed')
    condition = AsyncMock(side_effect=exception)

    with assert_raises(expected_exception=RuntimeError, match=escape('condition failed')) as exception_info:
        await SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
            condition=condition,
            timeout_seconds=1,
        )

    assert exception_info.value is exception
    assert condition.await_count == 1
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_poll_until_method_propagates_sleeper_exception() -> None:
    """
    Test SystemPollerAsync propagates the original sleeper exception unchanged.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = Mock(spec=SleeperAsync)
    exception = RuntimeError('sleep failed')
    sleeper.sleep.side_effect = exception
    condition = AsyncMock(return_value=False)

    with assert_raises(expected_exception=RuntimeError, match=escape('sleep failed')) as exception_info:
        await SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=0.25,
        )

    assert exception_info.value is exception
    assert condition.await_count == 1
    sleeper.sleep.assert_awaited_once_with(seconds=0.25)


@mark.unit_testing
def test_system_poller_async_preserves_injected_sleeper() -> None:
    """
    Test SystemPollerAsync stores the injected sleeper directly.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)

    assert SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock)._sleeper is sleeper


@mark.unit_testing
def test_system_poller_async_preserves_injected_monotonic_clock() -> None:
    """
    Test SystemPollerAsync stores the injected monotonic clock directly.
    """
    monotonic_clock = MockMonotonicClock()

    poller = SystemPollerAsync(
        sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
        monotonic_clock=monotonic_clock,
    )

    assert poller._monotonic_clock is monotonic_clock


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_condition_invalid_type() -> None:
    """
    Test SystemPollerAsync lets invocation raise naturally for a non-callable condition.
    """
    condition = FloatMother.create()

    with assert_raises(
        expected_exception=TypeError,
        match=escape("'float' object is not callable"),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=cast(Any, condition), timeout_seconds=1)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_condition_invalid_return_type() -> None:
    """
    Test SystemPollerAsync poll_until requires an exact boolean condition result.
    """
    condition = cast(Any, AsyncMock(return_value=1))

    with assert_raises(
        expected_exception=TypeError,
        match=escape('SystemPollerAsync condition <<<1>>> must be a boolean. Got <<<int>>> type.'),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=condition, timeout_seconds=1)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_timeout_seconds_invalid_type() -> None:
    """
    Test SystemPollerAsync rejects a timeout with an invalid primitive type.
    """
    timeout_seconds = FloatMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(
            f'SystemPollerAsync timeout_seconds <<<{timeout_seconds}>>> must be an integer or float. '
            f'Got <<<{type(timeout_seconds).__name__}>>> type.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=timeout_seconds)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_timeout_seconds_negative_random_value() -> None:
    """
    Test SystemPollerAsync rejects a generated negative timeout.
    """
    timeout_seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=escape(
            f'SystemPollerAsync timeout_seconds <<<{timeout_seconds}>>> must be greater than or equal to zero.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=timeout_seconds)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_timeout_seconds_negative_limit_value() -> None:
    """
    Test SystemPollerAsync rejects the explicit negative timeout boundary.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('SystemPollerAsync timeout_seconds <<<-1.0>>> must be greater than or equal to zero.'),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=-1.0)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_timeout_seconds_positive_random_value() -> None:
    """
    Test SystemPollerAsync accepts a generated positive timeout.
    """
    timeout_seconds = FloatMother.positive()

    monotonic_clock = MockMonotonicClock()
    await SystemPollerAsync(
        sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
        monotonic_clock=monotonic_clock,
    ).poll_until(condition=lambda: True, timeout_seconds=timeout_seconds)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_timeout_seconds_integer_value() -> None:
    """
    Test SystemPollerAsync accepts an integer timeout.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)

    with assert_raises(
        expected_exception=TimeoutExpiredError,
        match=escape('Deadline expired after <<<1.0>>> seconds.'),
    ):
        await SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
            condition=lambda: False,
            timeout_seconds=1,
            interval_seconds=1,
        )


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_timeout_seconds_positive_infinity_value() -> None:
    """
    Test SystemPollerAsync rejects a positive infinity timeout.
    """
    timeout_seconds = float('inf')

    with assert_raises(
        expected_exception=ValueError,
        match=escape(
            f'SystemPollerAsync timeout_seconds <<<{timeout_seconds}>>> must be finite and representable as a float.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=timeout_seconds)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_timeout_seconds_negative_infinity_value() -> None:
    """
    Test SystemPollerAsync rejects a negative infinity timeout.
    """
    timeout_seconds = float('-inf')

    with assert_raises(
        expected_exception=ValueError,
        match=escape(
            f'SystemPollerAsync timeout_seconds <<<{timeout_seconds}>>> must be finite and representable as a float.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=timeout_seconds)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_timeout_seconds_nan_value() -> None:
    """
    Test SystemPollerAsync rejects a not-a-number timeout.
    """
    timeout_seconds = float('nan')

    with assert_raises(
        expected_exception=ValueError,
        match=escape(
            f'SystemPollerAsync timeout_seconds <<<{timeout_seconds}>>> must be finite and representable as a float.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=timeout_seconds)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_interval_seconds_invalid_type() -> None:
    """
    Test SystemPollerAsync rejects an interval with an invalid primitive type.
    """
    interval_seconds = FloatMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(
            f'SystemPollerAsync interval_seconds <<<{interval_seconds}>>> must be an integer or float. '
            f'Got <<<{type(interval_seconds).__name__}>>> type.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(
            condition=lambda: True,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_interval_seconds_negative_random_value() -> None:
    """
    Test SystemPollerAsync rejects a generated negative interval.
    """
    interval_seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'SystemPollerAsync interval_seconds <<<{interval_seconds}>>> must be greater than zero.'),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(
            condition=lambda: True,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_interval_seconds_negative_limit_value() -> None:
    """
    Test SystemPollerAsync rejects the explicit negative interval boundary.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('SystemPollerAsync interval_seconds <<<-1.0>>> must be greater than zero.'),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=1, interval_seconds=-1.0)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_interval_seconds_zero_value() -> None:
    """
    Test SystemPollerAsync rejects a zero interval.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('SystemPollerAsync interval_seconds <<<0>>> must be greater than zero.'),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=1, interval_seconds=0)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_interval_seconds_positive_random_value() -> None:
    """
    Test SystemPollerAsync accepts a generated positive interval.
    """
    interval_seconds = FloatMother.positive()
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)
    condition = AsyncMock(side_effect=(False, True))

    await SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
        condition=condition,
        timeout_seconds=interval_seconds,
        interval_seconds=interval_seconds,
    )

    assert sleeper.sleep_calls == (interval_seconds,)


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_interval_seconds_preserves_integer_value() -> None:
    """
    Test SystemPollerAsync preserves an integer interval when sleeping.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeperAsync(monotonic_clock=monotonic_clock)
    condition = AsyncMock(side_effect=(False, True))

    await SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
        condition=condition,
        timeout_seconds=2,
        interval_seconds=1,
    )

    assert sleeper.sleep_calls == (1,)
    assert type(sleeper.sleep_calls[0]) is int


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_interval_seconds_positive_infinity_value() -> None:
    """
    Test SystemPollerAsync rejects a positive infinity interval.
    """
    interval_seconds = float('inf')

    with assert_raises(
        expected_exception=ValueError,
        match=escape(
            f'SystemPollerAsync interval_seconds <<<{interval_seconds}>>> must be finite and representable as a float.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(
            condition=lambda: True,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_interval_seconds_negative_infinity_value() -> None:
    """
    Test SystemPollerAsync rejects a negative infinity interval.
    """
    interval_seconds = float('-inf')

    with assert_raises(
        expected_exception=ValueError,
        match=escape(
            f'SystemPollerAsync interval_seconds <<<{interval_seconds}>>> must be finite and representable as a float.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(
            condition=lambda: True,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )


@mark.unit_testing
@mark.asyncio
async def test_system_poller_async_interval_seconds_nan_value() -> None:
    """
    Test SystemPollerAsync rejects a not-a-number interval.
    """
    interval_seconds = float('nan')

    with assert_raises(
        expected_exception=ValueError,
        match=escape(
            f'SystemPollerAsync interval_seconds <<<{interval_seconds}>>> must be finite and representable as a float.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        await SystemPollerAsync(
            sleeper=MockSleeperAsync(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(
            condition=lambda: True,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )
