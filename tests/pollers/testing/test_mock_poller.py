"""
Test MockPoller poller.
"""

from re import escape
from typing import Any, cast
from unittest.mock import Mock

from object_mother_pattern import FloatMother
from pytest import mark, raises as assert_raises

from clock_pattern.deadlines import TimeoutExpiredError
from clock_pattern.pollers import Poller
from clock_pattern.pollers.testing import MockPoller


@mark.unit_testing
def test_mock_poller_happy_path() -> None:
    """
    Test MockPoller implements Poller and records original default arguments.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)

    assert isinstance(poller, Poller)

    poller.poll_until(condition=condition, timeout_seconds=1)

    poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=1)
    recorded_call = poller._poll_until_mock.call_args
    assert recorded_call is not None
    assert recorded_call.kwargs == {
        'condition': condition,
        'timeout_seconds': 1,
        'interval_seconds': 0.1,
    }
    assert type(recorded_call.kwargs['timeout_seconds']) is int
    assert type(recorded_call.kwargs['interval_seconds']) is float


@mark.unit_testing
def test_mock_poller_records_explicit_arguments() -> None:
    """
    Test MockPoller records explicit arguments unchanged.
    """
    poller = MockPoller()
    condition = Mock(return_value=False)

    poller.poll_until(condition=condition, timeout_seconds=2.5, interval_seconds=0.25)

    poller.assert_poll_until_method_was_called_once_with(
        condition=condition,
        timeout_seconds=2.5,
        interval_seconds=0.25,
    )
    recorded_call = poller._poll_until_mock.call_args
    assert recorded_call is not None
    assert recorded_call.kwargs == {
        'condition': condition,
        'timeout_seconds': 2.5,
        'interval_seconds': 0.25,
    }


@mark.unit_testing
def test_mock_poller_prepare_poll_until_method_exception_records_call_before_raising() -> None:
    """
    Test MockPoller records the poll call before raising the prepared exception.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    exception = TimeoutExpiredError(elapsed_seconds=1.0)
    poller.prepare_poll_until_method_exception(exception=exception)

    with assert_raises(
        expected_exception=TimeoutExpiredError,
        match=escape('Deadline expired after <<<1.0>>> seconds.'),
    ) as exception_info:
        poller.poll_until(condition=condition, timeout_seconds=1)

    assert exception_info.value is exception
    poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=1)


@mark.unit_testing
def test_mock_poller_assert_poll_until_method_was_called_once_with_different_arguments() -> None:
    """
    Test MockPoller raises the complete assertion failure for different arguments.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    poller.poll_until(condition=condition, timeout_seconds=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=escape(f'expected call not found.\nExpected: mock(condition={condition!r}, timeout_seconds=2, interval_seconds=0.1)\n  Actual: mock(condition={condition!r}, timeout_seconds=1, interval_seconds=0.1)'),  # noqa: E501
    ):  # fmt: skip
        poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=2)


@mark.unit_testing
def test_mock_poller_assert_poll_until_method_was_called_once_with_after_multiple_calls() -> None:
    """
    Test MockPoller raises the complete assertion failure after multiple calls.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    poller.poll_until(condition=condition, timeout_seconds=1)
    poller.poll_until(condition=condition, timeout_seconds=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=escape(
            "Expected 'mock' to be called once. Called 2 times.\n"
            f'Calls: [call(condition={condition!r}, timeout_seconds=1, interval_seconds=0.1),\n'
            f' call(condition={condition!r}, timeout_seconds=1, interval_seconds=0.1)].'
        ),
    ):
        poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=1)


@mark.unit_testing
def test_mock_poller_assert_poll_until_method_was_not_called() -> None:
    """
    Test MockPoller asserts poll_until was not called.
    """
    MockPoller().assert_poll_until_method_was_not_called()


@mark.unit_testing
def test_mock_poller_assert_poll_until_method_was_not_called_after_call() -> None:
    """
    Test MockPoller raises the complete not-called assertion failure after a call.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    poller.poll_until(condition=condition, timeout_seconds=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=escape(
            "Expected 'mock' to not have been called. Called 1 times.\n"
            f'Calls: [call(condition={condition!r}, timeout_seconds=1, interval_seconds=0.1)].'
        ),
    ):
        poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
def test_mock_poller_condition_invalid_type() -> None:
    """
    Test MockPoller records a non-callable condition without runtime validation.
    """
    poller = MockPoller()
    condition = cast(Any, FloatMother.invalid_type())

    poller.poll_until(condition=condition, timeout_seconds=1)

    poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=1)


@mark.unit_testing
def test_mock_poller_timeout_seconds_invalid_type() -> None:
    """
    Test MockPoller poll and assertion methods reject an invalid timeout primitive type.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    timeout_seconds = FloatMother.invalid_type()
    expected_message = (
        f'MockPoller timeout_seconds <<<{timeout_seconds}>>> must be an integer or float. '
        f'Got <<<{type(timeout_seconds).__name__}>>> type.'
    )

    with assert_raises(expected_exception=TypeError, match=escape(expected_message)):
        poller.poll_until(condition=condition, timeout_seconds=timeout_seconds)

    with assert_raises(expected_exception=TypeError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=timeout_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
def test_mock_poller_timeout_seconds_negative_random_value() -> None:
    """
    Test MockPoller poll and assertion methods reject a generated negative timeout.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    timeout_seconds = FloatMother.negative()
    expected_message = f'MockPoller timeout_seconds <<<{timeout_seconds}>>> must be greater than or equal to zero.'

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.poll_until(condition=condition, timeout_seconds=timeout_seconds)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=timeout_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
def test_mock_poller_timeout_seconds_negative_limit_value() -> None:
    """
    Test MockPoller poll and assertion methods reject the explicit negative timeout boundary.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    expected_message = 'MockPoller timeout_seconds <<<-1.0>>> must be greater than or equal to zero.'

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.poll_until(condition=condition, timeout_seconds=-1.0)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=-1.0)

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
def test_mock_poller_timeout_seconds_zero_value() -> None:
    """
    Test MockPoller poll and assertion methods accept a zero timeout.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)

    poller.poll_until(condition=condition, timeout_seconds=0)

    poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=0)
    recorded_call = poller._poll_until_mock.call_args
    assert recorded_call is not None
    assert recorded_call.kwargs['timeout_seconds'] == 0
    assert type(recorded_call.kwargs['timeout_seconds']) is int


@mark.unit_testing
def test_mock_poller_timeout_seconds_positive_random_value() -> None:
    """
    Test MockPoller poll and assertion methods accept a generated positive timeout.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    timeout_seconds = FloatMother.positive()

    poller.poll_until(condition=condition, timeout_seconds=timeout_seconds)

    poller.assert_poll_until_method_was_called_once_with(
        condition=condition,
        timeout_seconds=timeout_seconds,
    )


@mark.unit_testing
def test_mock_poller_timeout_seconds_positive_infinity_value() -> None:
    """
    Test MockPoller poll and assertion methods reject a positive infinity timeout.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    timeout_seconds = float('inf')
    expected_message = (
        f'MockPoller timeout_seconds <<<{timeout_seconds}>>> must be finite and representable as a float.'
    )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.poll_until(condition=condition, timeout_seconds=timeout_seconds)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=timeout_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
def test_mock_poller_timeout_seconds_negative_infinity_value() -> None:
    """
    Test MockPoller poll and assertion methods reject a negative infinity timeout.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    timeout_seconds = float('-inf')
    expected_message = (
        f'MockPoller timeout_seconds <<<{timeout_seconds}>>> must be finite and representable as a float.'
    )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.poll_until(condition=condition, timeout_seconds=timeout_seconds)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=timeout_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
def test_mock_poller_timeout_seconds_nan_value() -> None:
    """
    Test MockPoller poll and assertion methods reject a not-a-number timeout.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    timeout_seconds = float('nan')
    expected_message = (
        f'MockPoller timeout_seconds <<<{timeout_seconds}>>> must be finite and representable as a float.'
    )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.poll_until(condition=condition, timeout_seconds=timeout_seconds)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=timeout_seconds,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
def test_mock_poller_interval_seconds_invalid_type() -> None:
    """
    Test MockPoller poll and assertion methods reject an invalid interval primitive type.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    interval_seconds = FloatMother.invalid_type()
    expected_message = (
        f'MockPoller interval_seconds <<<{interval_seconds}>>> must be an integer or float. '
        f'Got <<<{type(interval_seconds).__name__}>>> type.'
    )

    with assert_raises(expected_exception=TypeError, match=escape(expected_message)):
        poller.poll_until(
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
def test_mock_poller_interval_seconds_negative_random_value() -> None:
    """
    Test MockPoller poll and assertion methods reject a generated negative interval.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    interval_seconds = FloatMother.negative()
    expected_message = f'MockPoller interval_seconds <<<{interval_seconds}>>> must be greater than zero.'

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.poll_until(
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
def test_mock_poller_interval_seconds_negative_limit_value() -> None:
    """
    Test MockPoller poll and assertion methods reject the explicit negative interval boundary.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    expected_message = 'MockPoller interval_seconds <<<-1.0>>> must be greater than zero.'

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.poll_until(condition=condition, timeout_seconds=1, interval_seconds=-1.0)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=-1.0,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
def test_mock_poller_interval_seconds_zero_value() -> None:
    """
    Test MockPoller poll and assertion methods reject a zero interval.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    expected_message = 'MockPoller interval_seconds <<<0>>> must be greater than zero.'

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.poll_until(condition=condition, timeout_seconds=1, interval_seconds=0)

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.assert_poll_until_method_was_called_once_with(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=0,
        )

    poller.assert_poll_until_method_was_not_called()


@mark.unit_testing
def test_mock_poller_interval_seconds_positive_random_value() -> None:
    """
    Test MockPoller poll and assertion methods accept a generated positive interval.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    interval_seconds = FloatMother.positive()

    poller.poll_until(
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
def test_mock_poller_interval_seconds_preserves_integer_values() -> None:
    """
    Test MockPoller preserves integer durations when recording and asserting.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)

    poller.poll_until(condition=condition, timeout_seconds=2, interval_seconds=1)

    poller.assert_poll_until_method_was_called_once_with(
        condition=condition,
        timeout_seconds=2,
        interval_seconds=1,
    )
    recorded_call = poller._poll_until_mock.call_args
    assert recorded_call is not None
    assert recorded_call.kwargs['timeout_seconds'] == 2
    assert recorded_call.kwargs['interval_seconds'] == 1
    assert type(recorded_call.kwargs['timeout_seconds']) is int
    assert type(recorded_call.kwargs['interval_seconds']) is int


@mark.unit_testing
def test_mock_poller_interval_seconds_positive_infinity_value() -> None:
    """
    Test MockPoller poll and assertion methods reject a positive infinity interval.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    interval_seconds = float('inf')
    expected_message = (
        f'MockPoller interval_seconds <<<{interval_seconds}>>> must be finite and representable as a float.'
    )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.poll_until(
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
def test_mock_poller_interval_seconds_negative_infinity_value() -> None:
    """
    Test MockPoller poll and assertion methods reject a negative infinity interval.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    interval_seconds = float('-inf')
    expected_message = (
        f'MockPoller interval_seconds <<<{interval_seconds}>>> must be finite and representable as a float.'
    )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.poll_until(
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
def test_mock_poller_interval_seconds_nan_value() -> None:
    """
    Test MockPoller poll and assertion methods reject a not-a-number interval.
    """
    poller = MockPoller()
    condition = Mock(return_value=True)
    interval_seconds = float('nan')
    expected_message = (
        f'MockPoller interval_seconds <<<{interval_seconds}>>> must be finite and representable as a float.'
    )

    with assert_raises(expected_exception=ValueError, match=escape(expected_message)):
        poller.poll_until(
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
def test_mock_poller_prepare_poll_until_method_exception_stores_argument_without_runtime_validation() -> None:
    """
    Test MockPoller stores the prepared exception argument directly.
    """
    poller = MockPoller()
    exception = cast(BaseException, FloatMother.invalid_type())

    poller.prepare_poll_until_method_exception(exception=exception)

    assert poller._exception is exception
