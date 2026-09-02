"""
Test MockPollerAsync poller.
"""

from re import escape
from typing import cast
from unittest.mock import Mock

from object_mother_pattern import FloatMother
from pytest import mark, raises as assert_raises

from clock_pattern.deadlines import TimeoutExpiredError
from clock_pattern.pollers import PollerAsync
from clock_pattern.pollers.testing import MockPollerAsync


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_happy_path() -> None:
    """
    Test MockPollerAsync implements PollerAsync and records original default arguments.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)

    assert isinstance(poller, PollerAsync)

    await poller.poll_until(condition=condition, timeout_seconds=1)

    poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=1)
    recorded_call = poller._poll_until_mock.await_args
    assert recorded_call is not None
    assert recorded_call.kwargs == {
        'condition': condition,
        'timeout_seconds': 1,
        'interval_seconds': 0.1,
    }
    assert type(recorded_call.kwargs['timeout_seconds']) is int
    assert type(recorded_call.kwargs['interval_seconds']) is float


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_records_explicit_arguments() -> None:
    """
    Test MockPollerAsync records explicit arguments unchanged.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=False)

    await poller.poll_until(condition=condition, timeout_seconds=2.5, interval_seconds=0.25)

    poller.assert_poll_until_method_was_called_once_with(
        condition=condition,
        timeout_seconds=2.5,
        interval_seconds=0.25,
    )
    recorded_call = poller._poll_until_mock.await_args
    assert recorded_call is not None
    assert recorded_call.kwargs == {
        'condition': condition,
        'timeout_seconds': 2.5,
        'interval_seconds': 0.25,
    }


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_prepare_poll_until_method_exception_records_call_before_raising() -> None:
    """
    Test MockPollerAsync records the poll call before raising the prepared exception.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    exception = TimeoutExpiredError(elapsed_seconds=1.0)
    poller.prepare_poll_until_method_exception(exception=exception)

    with assert_raises(
        expected_exception=TimeoutExpiredError,
        match=escape('Deadline expired after <<<1.0>>> seconds.'),
    ) as exception_info:
        await poller.poll_until(condition=condition, timeout_seconds=1)

    assert exception_info.value is exception
    poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=1)


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_assert_poll_until_method_was_called_once_with_different_arguments() -> None:
    """
    Test MockPollerAsync raises the complete assertion failure for different arguments.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    await poller.poll_until(condition=condition, timeout_seconds=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=escape(f'expected await not found.\nExpected: mock(condition={condition!r}, timeout_seconds=2, interval_seconds=0.1)\n  Actual: mock(condition={condition!r}, timeout_seconds=1, interval_seconds=0.1)'),  # noqa: E501
    ):  # fmt: skip
        poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=2)


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_assert_poll_until_method_was_called_once_with_after_multiple_calls() -> None:
    """
    Test MockPollerAsync raises the complete assertion failure after multiple awaits.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    await poller.poll_until(condition=condition, timeout_seconds=1)
    await poller.poll_until(condition=condition, timeout_seconds=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=escape('Expected mock to have been awaited once. Awaited 2 times.'),
    ):
        poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=1)


@mark.unit_testing
def test_mock_poller_async_assert_poll_until_method_was_not_called() -> None:
    """
    Test MockPollerAsync asserts poll_until was not awaited.
    """
    MockPollerAsync().assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_assert_poll_until_method_was_not_called_after_call() -> None:
    """
    Test MockPollerAsync raises the complete not-called assertion failure after an await.
    """
    poller = MockPollerAsync()
    await poller.poll_until(condition=lambda: True, timeout_seconds=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=escape('Expected mock to not have been awaited. Awaited 1 times.'),
    ):
        poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_condition_invalid_type() -> None:
    """
    Test MockPollerAsync records a non-callable condition without runtime validation.
    """
    poller = MockPollerAsync()
    condition = FloatMother.invalid_type()

    await poller.poll_until(condition=condition, timeout_seconds=1)

    poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=1)


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_timeout_seconds_invalid_type() -> None:
    """
    Test MockPollerAsync poll and assertion methods reject an invalid timeout primitive type.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    timeout_seconds = FloatMother.invalid_type()
    expected_message = (
        f'MockPollerAsync timeout_seconds <<<{timeout_seconds}>>> must be an integer or float. '
        f'Got <<<{type(timeout_seconds).__name__}>>> type.'
    )

    with assert_raises(expected_exception=TypeError, match=escape(expected_message)):
        await poller.poll_until(condition=condition, timeout_seconds=timeout_seconds)

    with assert_raises(expected_exception=TypeError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=timeout_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_timeout_seconds_negative_random_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods reject a generated negative timeout.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    timeout_seconds = FloatMother.negative()
    expected_message = f'MockPollerAsync timeout_seconds <<<{timeout_seconds}>>> must be greater than or equal to zero.'

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        await poller.poll_until(condition=condition, timeout_seconds=timeout_seconds)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=timeout_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_timeout_seconds_negative_limit_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods reject the explicit negative timeout boundary.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    expected_message = 'MockPollerAsync timeout_seconds <<<-1.0>>> must be greater than or equal to zero.'

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        await poller.poll_until(condition=condition, timeout_seconds=-1.0)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=-1.0)

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_timeout_seconds_zero_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods accept a zero timeout.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)

    await poller.poll_until(condition=condition, timeout_seconds=0)

    poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=0)
    recorded_call = poller._poll_until_mock.await_args
    assert recorded_call is not None
    assert recorded_call.kwargs['timeout_seconds'] == 0
    assert type(recorded_call.kwargs['timeout_seconds']) is int


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_timeout_seconds_positive_random_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods accept a generated positive timeout.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    timeout_seconds = FloatMother.positive()

    await poller.poll_until(condition=condition, timeout_seconds=timeout_seconds)

    poller.assert_poll_until_method_was_called_once_with(
        condition=condition,
        timeout_seconds=timeout_seconds,
    )


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_timeout_seconds_positive_infinity_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods reject a positive infinity timeout.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    timeout_seconds = float('inf')
    expected_message = (
        f'MockPollerAsync timeout_seconds <<<{timeout_seconds}>>> must be finite and representable as a float.'
    )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        await poller.poll_until(condition=condition, timeout_seconds=timeout_seconds)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=timeout_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_timeout_seconds_negative_infinity_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods reject a negative infinity timeout.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    timeout_seconds = float('-inf')
    expected_message = (
        f'MockPollerAsync timeout_seconds <<<{timeout_seconds}>>> must be finite and representable as a float.'
    )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        await poller.poll_until(condition=condition, timeout_seconds=timeout_seconds)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=timeout_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_timeout_seconds_nan_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods reject a not-a-number timeout.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    timeout_seconds = float('nan')
    expected_message = (
        f'MockPollerAsync timeout_seconds <<<{timeout_seconds}>>> must be finite and representable as a float.'
    )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        await poller.poll_until(condition=condition, timeout_seconds=timeout_seconds)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=timeout_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_interval_seconds_invalid_type() -> None:
    """
    Test MockPollerAsync poll and assertion methods reject an invalid interval primitive type.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    interval_seconds = FloatMother.invalid_type()
    expected_message = (
        f'MockPollerAsync interval_seconds <<<{interval_seconds}>>> must be an integer or float. '
        f'Got <<<{type(interval_seconds).__name__}>>> type.'
    )

    with assert_raises(expected_exception=TypeError, match=escape(expected_message)):
        await poller.poll_until(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )

    with assert_raises(expected_exception=TypeError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_interval_seconds_negative_random_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods reject a generated negative interval.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    interval_seconds = FloatMother.negative()
    expected_message = f'MockPollerAsync interval_seconds <<<{interval_seconds}>>> must be greater than zero.'

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        await poller.poll_until(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_interval_seconds_negative_limit_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods reject the explicit negative interval boundary.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    expected_message = 'MockPollerAsync interval_seconds <<<-1.0>>> must be greater than zero.'

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        await poller.poll_until(condition=condition, timeout_seconds=1, interval_seconds=-1.0)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=-1.0,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_interval_seconds_zero_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods reject a zero interval.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    expected_message = 'MockPollerAsync interval_seconds <<<0>>> must be greater than zero.'

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        await poller.poll_until(condition=condition, timeout_seconds=1, interval_seconds=0)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=0,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_interval_seconds_positive_random_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods accept a generated positive interval.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    interval_seconds = FloatMother.positive()

    await poller.poll_until(
        condition=condition,
        timeout_seconds=interval_seconds,
        interval_seconds=interval_seconds,
    )

    poller.assert_poll_until_method_was_called_once_with(
        condition=condition,
        timeout_seconds=interval_seconds,
        interval_seconds=interval_seconds,
    )


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_interval_seconds_preserves_integer_values() -> None:
    """
    Test MockPollerAsync preserves integer durations when recording and asserting.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)

    await poller.poll_until(condition=condition, timeout_seconds=2, interval_seconds=1)

    poller.assert_poll_until_method_was_called_once_with(
        condition=condition,
        timeout_seconds=2,
        interval_seconds=1,
    )
    recorded_call = poller._poll_until_mock.await_args
    assert recorded_call is not None
    assert recorded_call.kwargs['timeout_seconds'] == 2
    assert recorded_call.kwargs['interval_seconds'] == 1
    assert type(recorded_call.kwargs['timeout_seconds']) is int
    assert type(recorded_call.kwargs['interval_seconds']) is int


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_interval_seconds_positive_infinity_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods reject a positive infinity interval.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    interval_seconds = float('inf')
    expected_message = (
        f'MockPollerAsync interval_seconds <<<{interval_seconds}>>> must be finite and representable as a float.'
    )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        await poller.poll_until(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_interval_seconds_negative_infinity_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods reject a negative infinity interval.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    interval_seconds = float('-inf')
    expected_message = (
        f'MockPollerAsync interval_seconds <<<{interval_seconds}>>> must be finite and representable as a float.'
    )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        await poller.poll_until(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
@mark.asyncio
async def test_mock_poller_async_interval_seconds_nan_value() -> None:
    """
    Test MockPollerAsync poll and assertion methods reject a not-a-number interval.
    """
    poller = MockPollerAsync()
    condition = Mock(return_value=True)
    interval_seconds = float('nan')
    expected_message = (
        f'MockPollerAsync interval_seconds <<<{interval_seconds}>>> must be finite and representable as a float.'
    )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        await poller.poll_until(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
def test_mock_poller_async_prepare_poll_until_method_exception_stores_argument_without_runtime_validation() -> None:
    """
    Test MockPollerAsync stores the prepared exception argument directly.
    """
    poller = MockPollerAsync()
    exception = cast(BaseException, FloatMother.invalid_type())

    poller.prepare_poll_until_method_exception(exception=exception)

    assert poller._exception is exception
