"""
Test the asynchronous system retrier.
"""

from asyncio import CancelledError
from math import inf, nan
from re import escape
from typing import Any, cast

from object_mother_pattern import BooleanMother, FloatMother, IntegerMother
from pytest import mark, raises as assert_raises

from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.retriers import RetrierAsync, SystemRetrierAsync
from clock_pattern.sleepers.testing import MockSleeperAsync


class _FalseyMockSleeperAsync(MockSleeperAsync):
    """
    Represent a valid injected async sleeper whose truth value is false.
    """

    def __bool__(self) -> bool:
        """
        Return false so constructor fallback behavior can be tested.
        """
        return False


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_happy_path_returns_falsey_value() -> None:
    """
    Test SystemRetrierAsync implements RetrierAsync and returns a successful falsey value.
    """

    async def operation() -> int:
        return 0

    retrier = SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock()))

    assert isinstance(retrier, RetrierAsync)
    assert await retrier.retry(operation=operation, attempts=1) == 0


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_retries_until_operation_succeeds() -> None:
    """
    Test SystemRetrierAsync retries a configured exception until the operation succeeds.
    """
    operation_calls = 0
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())

    async def operation() -> str:
        nonlocal operation_calls
        operation_calls += 1

        if operation_calls == 1:
            raise ValueError('temporary failure')

        return 'done'

    result = await SystemRetrierAsync(sleeper=sleeper).retry(
        operation=operation,
        attempts=2,
        delay_seconds=0.25,
        retry_on=ValueError,
    )

    assert result == 'done'
    assert operation_calls == 2
    assert sleeper.sleep_calls == (0.25,)


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_raises_last_retryable_exception_when_attempts_are_exhausted() -> None:
    """
    Test SystemRetrierAsync re-raises the final retryable exception after all attempts.
    """
    operation_calls = 0
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())

    async def operation() -> None:
        nonlocal operation_calls
        operation_calls += 1
        raise ValueError(f'failure {operation_calls}')

    with assert_raises(expected_exception=ValueError, match=escape('failure 3')):
        await SystemRetrierAsync(sleeper=sleeper).retry(
            operation=operation,
            attempts=3,
            delay_seconds=0.25,
            retry_on=ValueError,
        )

    assert operation_calls == 3
    assert sleeper.sleep_calls == (0.25, 0.25)


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_raises_non_retryable_exception_without_retrying() -> None:
    """
    Test SystemRetrierAsync propagates a non-retryable exception immediately.
    """
    operation_calls = 0
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())

    async def operation() -> None:
        nonlocal operation_calls
        operation_calls += 1
        raise RuntimeError('not retryable')

    with assert_raises(expected_exception=RuntimeError, match=escape('not retryable')):
        await SystemRetrierAsync(sleeper=sleeper).retry(
            operation=operation,
            attempts=3,
            delay_seconds=1,
            retry_on=ValueError,
        )

    assert operation_calls == 1
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_does_not_retry_cancellation() -> None:
    """
    Test SystemRetrierAsync propagates asynchronous cancellation immediately.
    """
    operation_calls = 0
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())

    async def operation() -> None:
        nonlocal operation_calls
        operation_calls += 1
        raise CancelledError

    with assert_raises(expected_exception=CancelledError):
        await SystemRetrierAsync(sleeper=sleeper).retry(operation=operation, attempts=3, delay_seconds=1)

    assert operation_calls == 1
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_does_not_sleep_when_delay_is_zero() -> None:
    """
    Test SystemRetrierAsync retries without sleeping when delay_seconds is zero.
    """
    operation_calls = 0
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())

    async def operation() -> str:
        nonlocal operation_calls
        operation_calls += 1

        if operation_calls == 1:
            raise ValueError('temporary failure')

        return 'done'

    result = await SystemRetrierAsync(sleeper=sleeper).retry(operation=operation, attempts=2, delay_seconds=0)

    assert result == 'done'
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_applies_backoff_between_attempts() -> None:
    """
    Test SystemRetrierAsync multiplies the delay after each failed attempt.
    """
    operation_calls = 0
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())

    async def operation() -> str:
        nonlocal operation_calls
        operation_calls += 1

        if operation_calls < 3:
            raise ValueError('temporary failure')

        return 'done'

    result = await SystemRetrierAsync(sleeper=sleeper).retry(
        operation=operation,
        attempts=3,
        delay_seconds=0.25,
        backoff=2,
    )

    assert result == 'done'
    assert sleeper.sleep_calls == (0.25, 0.5)


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_applies_full_jitter_with_current_delay_bounds() -> None:
    """
    Test SystemRetrierAsync calls the injected jitter function with each current delay.
    """
    operation_calls = 0
    random_uniform_calls: list[tuple[float, float]] = []
    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())

    async def operation() -> str:
        nonlocal operation_calls
        operation_calls += 1

        if operation_calls < 3:
            raise ValueError('temporary failure')

        return 'done'

    def random_uniform(minimum: float, maximum: float) -> float:
        random_uniform_calls.append((minimum, maximum))
        return maximum / 2

    result = await SystemRetrierAsync(sleeper=sleeper, random_uniform=random_uniform).retry(
        operation=operation,
        attempts=3,
        delay_seconds=1,
        backoff=2,
        jitter=True,
    )

    assert result == 'done'
    assert random_uniform_calls == [(0.0, 1.0), (0.0, 2.0)]
    assert sleeper.sleep_calls == (0.5, 1.0)


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_preserves_falsey_injected_sleeper() -> None:
    """
    Test SystemRetrierAsync uses a valid injected sleeper even when it is falsey.
    """
    operation_calls = 0
    sleeper = _FalseyMockSleeperAsync(monotonic_clock=MockMonotonicClock())

    async def operation() -> str:
        nonlocal operation_calls
        operation_calls += 1

        if operation_calls == 1:
            raise ValueError('temporary failure')

        return 'done'

    result = await SystemRetrierAsync(sleeper=sleeper).retry(operation=operation, attempts=2, delay_seconds=0.25)

    assert result == 'done'
    assert sleeper.sleep_calls == (0.25,)


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_attempts_invalid_type() -> None:
    """
    Test SystemRetrierAsync rejects a non-integer attempt count.
    """
    attempts = IntegerMother.invalid_type()

    async def operation() -> str:
        return 'done'

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'AsyncSystemRetrier attempts <<<{attempts}>>> must be an integer. Got <<<{type(attempts).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        await SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock())).retry(
            operation=operation,
            attempts=cast(Any, attempts),
        )


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_attempts_negative_random_value() -> None:
    """
    Test SystemRetrierAsync rejects a generated negative attempt count.
    """
    attempts = IntegerMother.negative()

    async def operation() -> str:
        return 'done'

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'AsyncSystemRetrier attempts <<<{attempts}>>> must be a positive integer.'),
    ):
        await SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock())).retry(
            operation=operation,
            attempts=attempts,
        )


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_attempts_zero_value() -> None:
    """
    Test SystemRetrierAsync rejects zero attempts.
    """

    async def operation() -> str:
        return 'done'

    with assert_raises(
        expected_exception=ValueError,
        match=escape('AsyncSystemRetrier attempts <<<0>>> must be a positive integer.'),
    ):
        await SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock())).retry(
            operation=operation,
            attempts=0,
        )


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_attempts_positive_random_value() -> None:
    """
    Test SystemRetrierAsync accepts a generated positive attempt count.
    """
    attempts = IntegerMother.positive()

    async def operation() -> str:
        return 'done'

    retrier = SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock()))

    assert await retrier.retry(operation=operation, attempts=attempts) == 'done'


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_delay_seconds_invalid_type() -> None:
    """
    Test SystemRetrierAsync rejects a non-numeric delay.
    """
    delay_seconds = FloatMother.invalid_type()

    async def operation() -> str:
        return 'done'

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'AsyncSystemRetrier delay_seconds <<<{delay_seconds}>>> must be an integer or float. Got <<<{type(delay_seconds).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        await SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock())).retry(
            operation=operation,
            attempts=1,
            delay_seconds=cast(Any, delay_seconds),
        )


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_delay_seconds_negative_random_value() -> None:
    """
    Test SystemRetrierAsync rejects a generated negative delay.
    """
    delay_seconds = FloatMother.negative()

    async def operation() -> str:
        return 'done'

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'AsyncSystemRetrier delay_seconds <<<{delay_seconds}>>> must be greater than or equal to zero.'),
    ):
        await SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock())).retry(
            operation=operation,
            attempts=1,
            delay_seconds=delay_seconds,
        )


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_delay_seconds_non_finite_value() -> None:
    """
    Test SystemRetrierAsync rejects a non-finite delay.
    """

    async def operation() -> str:
        return 'done'

    with assert_raises(
        expected_exception=ValueError,
        match=escape('AsyncSystemRetrier delay_seconds <<<inf>>> must be finite and representable as a float.'),
    ):
        await SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock())).retry(
            operation=operation,
            attempts=1,
            delay_seconds=inf,
        )


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_delay_seconds_positive_random_value() -> None:
    """
    Test SystemRetrierAsync accepts a generated positive delay.
    """
    delay_seconds = FloatMother.positive()

    async def operation() -> str:
        return 'done'

    retrier = SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock()))

    assert await retrier.retry(operation=operation, attempts=1, delay_seconds=delay_seconds) == 'done'


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_backoff_invalid_type() -> None:
    """
    Test SystemRetrierAsync rejects a non-numeric backoff.
    """
    backoff = FloatMother.invalid_type()

    async def operation() -> str:
        return 'done'

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'AsyncSystemRetrier backoff <<<{backoff}>>> must be an integer or float. Got <<<{type(backoff).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        await SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock())).retry(
            operation=operation,
            attempts=1,
            backoff=cast(Any, backoff),
        )


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_backoff_negative_random_value() -> None:
    """
    Test SystemRetrierAsync rejects a generated negative backoff.
    """
    backoff = FloatMother.negative()

    async def operation() -> str:
        return 'done'

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'AsyncSystemRetrier backoff <<<{backoff}>>> must be greater than zero.'),
    ):
        await SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock())).retry(
            operation=operation,
            attempts=1,
            backoff=backoff,
        )


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_backoff_zero_value() -> None:
    """
    Test SystemRetrierAsync rejects zero backoff.
    """

    async def operation() -> str:
        return 'done'

    with assert_raises(
        expected_exception=ValueError,
        match=escape('AsyncSystemRetrier backoff <<<0>>> must be greater than zero.'),
    ):
        await SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock())).retry(
            operation=operation,
            attempts=1,
            backoff=0,
        )


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_backoff_non_finite_value() -> None:
    """
    Test SystemRetrierAsync rejects a non-finite backoff.
    """

    async def operation() -> str:
        return 'done'

    with assert_raises(
        expected_exception=ValueError,
        match=escape('AsyncSystemRetrier backoff <<<nan>>> must be finite and representable as a float.'),
    ):
        await SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock())).retry(
            operation=operation,
            attempts=1,
            backoff=nan,
        )


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_backoff_positive_random_value() -> None:
    """
    Test SystemRetrierAsync accepts a generated positive backoff.
    """
    backoff = FloatMother.positive()

    async def operation() -> str:
        return 'done'

    retrier = SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock()))

    assert await retrier.retry(operation=operation, attempts=1, backoff=backoff) == 'done'


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_jitter_invalid_type() -> None:
    """
    Test SystemRetrierAsync rejects a non-boolean jitter flag.
    """
    jitter = BooleanMother.invalid_type()

    async def operation() -> str:
        return 'done'

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'AsyncSystemRetrier jitter <<<{jitter}>>> must be a boolean. Got <<<{type(jitter).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        await SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock())).retry(
            operation=operation,
            attempts=1,
            jitter=cast(Any, jitter),
        )


@mark.unit_testing
@mark.asyncio
async def test_system_retrier_async_retry_on_tuple_value() -> None:
    """
    Test SystemRetrierAsync accepts a non-empty tuple of Exception types.
    """

    async def operation() -> str:
        return 'done'

    result = await SystemRetrierAsync(sleeper=MockSleeperAsync(monotonic_clock=MockMonotonicClock())).retry(
        operation=operation,
        attempts=1,
        retry_on=(ValueError, RuntimeError),
    )

    assert result == 'done'
