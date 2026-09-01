"""
Test the asynchronous mock retrier.
"""

from math import inf, nan
from re import escape
from typing import Any, cast

from object_mother_pattern import BooleanMother, FloatMother, IntegerMother
from pytest import mark, raises as assert_raises

from clock_pattern.retriers import RetrierAsync
from clock_pattern.retriers.testing import MockRetrierAsync


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_happy_path() -> None:
    """
    Test MockRetrierAsync implements RetrierAsync and returns the prepared value.
    """

    async def operation() -> str:
        return 'ignored'

    retrier = MockRetrierAsync()
    retrier.prepare_retry_method_return_value(value='done')

    result = await retrier.retry(operation=operation, attempts=3)

    assert isinstance(retrier, RetrierAsync)
    assert result == 'done'
    retrier.assert_retry_method_was_called_once_with(operation=operation, attempts=3)


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_returns_unprepared_none_value() -> None:
    """
    Test MockRetrierAsync returns None when no return value or exception is prepared.
    """

    async def operation() -> str:
        return 'ignored'

    assert await MockRetrierAsync().retry(operation=operation, attempts=1) is None


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_prepare_retry_method_exception() -> None:
    """
    Test MockRetrierAsync raises the prepared exception after recording the call.
    """

    async def operation() -> str:
        return 'ignored'

    retrier = MockRetrierAsync()
    retrier.prepare_retry_method_exception(exception=ValueError('failed'))

    with assert_raises(expected_exception=ValueError, match=escape('failed')):
        await retrier.retry(operation=operation, attempts=1)

    retrier.assert_retry_method_was_called_once_with(operation=operation, attempts=1)


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_assert_retry_method_was_called_once() -> None:
    """
    Test MockRetrierAsync confirms retry was awaited exactly once.
    """

    async def operation() -> str:
        return 'ignored'

    retrier = MockRetrierAsync()
    await retrier.retry(operation=operation, attempts=1)

    retrier.assert_retry_method_was_called_once()


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_assert_retry_method_was_called_once_after_multiple_calls() -> None:
    """
    Test MockRetrierAsync called-once assertion fails after multiple retry calls.
    """

    async def operation() -> str:
        return 'ignored'

    retrier = MockRetrierAsync()
    await retrier.retry(operation=operation, attempts=1)
    await retrier.retry(operation=operation, attempts=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=escape('Expected mock to have been awaited once. Awaited 2 times.'),
    ):
        retrier.assert_retry_method_was_called_once()


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_assert_retry_method_was_called_once_with_custom_values() -> None:
    """
    Test MockRetrierAsync exact call assertion accepts all custom retry arguments.
    """

    async def operation() -> str:
        return 'ignored'

    retrier = MockRetrierAsync()
    await retrier.retry(
        operation=operation,
        attempts=3,
        delay_seconds=0.25,
        backoff=2,
        jitter=True,
        retry_on=(ValueError, RuntimeError),
    )

    retrier.assert_retry_method_was_called_once_with(
        operation=operation,
        attempts=3,
        delay_seconds=0.25,
        backoff=2,
        jitter=True,
        retry_on=(ValueError, RuntimeError),
    )


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_assert_retry_method_was_called_once_with_different_arguments() -> None:
    """
    Test MockRetrierAsync exact call assertion fails when expected arguments differ.
    """

    async def operation() -> str:
        return 'ignored'

    retrier = MockRetrierAsync()
    await retrier.retry(operation=operation, attempts=1)

    with assert_raises(expected_exception=AssertionError, match=escape('expected await not found.')):
        retrier.assert_retry_method_was_called_once_with(operation=operation, attempts=2)


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_assert_retry_method_was_called_once_with_after_multiple_calls() -> None:
    """
    Test MockRetrierAsync exact call assertion fails after multiple retry calls.
    """

    async def operation() -> str:
        return 'ignored'

    retrier = MockRetrierAsync()
    await retrier.retry(operation=operation, attempts=1)
    await retrier.retry(operation=operation, attempts=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=escape('Expected mock to have been awaited once. Awaited 2 times.'),
    ):
        retrier.assert_retry_method_was_called_once_with(operation=operation, attempts=1)


@mark.unit_testing
def test_mock_retrier_async_assert_retry_method_was_not_called() -> None:
    """
    Test MockRetrierAsync confirms retry was not awaited.
    """
    MockRetrierAsync().assert_retry_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_assert_retry_method_was_not_called_after_call() -> None:
    """
    Test MockRetrierAsync not-called assertion fails after a retry call.
    """

    async def operation() -> str:
        return 'ignored'

    retrier = MockRetrierAsync()
    await retrier.retry(operation=operation, attempts=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=escape('Expected mock to not have been awaited. Awaited 1 times.'),
    ):
        retrier.assert_retry_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_attempts_invalid_type() -> None:
    """
    Test MockRetrierAsync rejects a non-integer attempt count.
    """
    attempts = IntegerMother.invalid_type()

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'MockRetrierAsync attempts <<<{attempts}>>> must be an integer. Got <<<{type(attempts).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        await MockRetrierAsync().retry(operation=operation, attempts=cast(Any, attempts))


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_attempts_negative_random_value() -> None:
    """
    Test MockRetrierAsync rejects a generated negative attempt count.
    """
    attempts = IntegerMother.negative()

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'MockRetrierAsync attempts <<<{attempts}>>> must be a positive integer.'),
    ):
        await MockRetrierAsync().retry(operation=operation, attempts=attempts)


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_attempts_zero_value() -> None:
    """
    Test MockRetrierAsync rejects zero attempts.
    """

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrierAsync attempts <<<0>>> must be a positive integer.'),
    ):
        await MockRetrierAsync().retry(operation=operation, attempts=0)


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_attempts_positive_random_value() -> None:
    """
    Test MockRetrierAsync accepts a generated positive attempt count.
    """
    attempts = IntegerMother.positive()

    async def operation() -> str:
        return 'ignored'

    assert await MockRetrierAsync().retry(operation=operation, attempts=attempts) is None


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_delay_seconds_invalid_type() -> None:
    """
    Test MockRetrierAsync rejects a non-numeric delay.
    """
    delay_seconds = FloatMother.invalid_type()

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'MockRetrierAsync delay_seconds <<<{delay_seconds}>>> must be an integer or float. Got <<<{type(delay_seconds).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        await MockRetrierAsync().retry(
            operation=operation,
            attempts=1,
            delay_seconds=cast(Any, delay_seconds),
        )


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_delay_seconds_negative_random_value() -> None:
    """
    Test MockRetrierAsync rejects a generated negative delay.
    """
    delay_seconds = FloatMother.negative()

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'MockRetrierAsync delay_seconds <<<{delay_seconds}>>> must be greater than or equal to zero.'),
    ):
        await MockRetrierAsync().retry(operation=operation, attempts=1, delay_seconds=delay_seconds)


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_delay_seconds_non_finite_value() -> None:
    """
    Test MockRetrierAsync rejects a non-finite delay.
    """

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrierAsync delay_seconds <<<inf>>> must be finite and representable as a float.'),
    ):
        await MockRetrierAsync().retry(operation=operation, attempts=1, delay_seconds=inf)


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_delay_seconds_zero_value() -> None:
    """
    Test MockRetrierAsync accepts a zero delay.
    """

    async def operation() -> str:
        return 'ignored'

    assert await MockRetrierAsync().retry(operation=operation, attempts=1, delay_seconds=0) is None


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_delay_seconds_positive_random_value() -> None:
    """
    Test MockRetrierAsync accepts a generated positive delay.
    """
    delay_seconds = FloatMother.positive()

    async def operation() -> str:
        return 'ignored'

    assert await MockRetrierAsync().retry(operation=operation, attempts=1, delay_seconds=delay_seconds) is None


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_backoff_invalid_type() -> None:
    """
    Test MockRetrierAsync rejects a non-numeric backoff.
    """
    backoff = FloatMother.invalid_type()

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'MockRetrierAsync backoff <<<{backoff}>>> must be an integer or float. Got <<<{type(backoff).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        await MockRetrierAsync().retry(operation=operation, attempts=1, backoff=cast(Any, backoff))


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_backoff_negative_random_value() -> None:
    """
    Test MockRetrierAsync rejects a generated negative backoff.
    """
    backoff = FloatMother.negative()

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'MockRetrierAsync backoff <<<{backoff}>>> must be greater than zero.'),
    ):
        await MockRetrierAsync().retry(operation=operation, attempts=1, backoff=backoff)


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_backoff_zero_value() -> None:
    """
    Test MockRetrierAsync rejects zero backoff.
    """

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrierAsync backoff <<<0>>> must be greater than zero.'),
    ):
        await MockRetrierAsync().retry(operation=operation, attempts=1, backoff=0)


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_backoff_non_finite_value() -> None:
    """
    Test MockRetrierAsync rejects a non-finite backoff.
    """

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrierAsync backoff <<<nan>>> must be finite and representable as a float.'),
    ):
        await MockRetrierAsync().retry(operation=operation, attempts=1, backoff=nan)


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_backoff_positive_random_value() -> None:
    """
    Test MockRetrierAsync accepts a generated positive backoff.
    """
    backoff = FloatMother.positive()

    async def operation() -> str:
        return 'ignored'

    assert await MockRetrierAsync().retry(operation=operation, attempts=1, backoff=backoff) is None


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_jitter_invalid_type() -> None:
    """
    Test MockRetrierAsync rejects a non-boolean jitter flag.
    """
    jitter = BooleanMother.invalid_type()

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'MockRetrierAsync jitter <<<{jitter}>>> must be a boolean. Got <<<{type(jitter).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        await MockRetrierAsync().retry(operation=operation, attempts=1, jitter=cast(Any, jitter))


@mark.unit_testing
@mark.asyncio
async def test_mock_retrier_async_retry_on_tuple_value() -> None:
    """
    Test MockRetrierAsync accepts a non-empty tuple of Exception types.
    """

    async def operation() -> str:
        return 'ignored'

    assert await MockRetrierAsync().retry(operation=operation, attempts=1, retry_on=(ValueError, RuntimeError)) is None


@mark.unit_testing
def test_mock_retrier_async_assert_retry_method_attempts_invalid_value() -> None:
    """
    Test MockRetrierAsync exact assertion validates the expected attempt count.
    """

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrierAsync attempts <<<0>>> must be a positive integer.'),
    ):
        MockRetrierAsync().assert_retry_method_was_called_once_with(operation=operation, attempts=0)


@mark.unit_testing
def test_mock_retrier_async_assert_retry_method_delay_seconds_invalid_value() -> None:
    """
    Test MockRetrierAsync exact assertion validates the expected delay.
    """

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrierAsync delay_seconds <<<-1>>> must be greater than or equal to zero.'),
    ):
        MockRetrierAsync().assert_retry_method_was_called_once_with(
            operation=operation,
            attempts=1,
            delay_seconds=-1,
        )


@mark.unit_testing
def test_mock_retrier_async_assert_retry_method_backoff_invalid_value() -> None:
    """
    Test MockRetrierAsync exact assertion validates the expected backoff.
    """

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrierAsync backoff <<<0>>> must be greater than zero.'),
    ):
        MockRetrierAsync().assert_retry_method_was_called_once_with(
            operation=operation,
            attempts=1,
            backoff=0,
        )


@mark.unit_testing
def test_mock_retrier_async_assert_retry_method_jitter_invalid_type() -> None:
    """
    Test MockRetrierAsync exact assertion validates the expected jitter flag.
    """
    jitter = BooleanMother.invalid_type()

    async def operation() -> str:
        return 'ignored'

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'MockRetrierAsync jitter <<<{jitter}>>> must be a boolean. Got <<<{type(jitter).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        MockRetrierAsync().assert_retry_method_was_called_once_with(
            operation=operation,
            attempts=1,
            jitter=cast(Any, jitter),
        )
