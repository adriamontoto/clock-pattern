"""
Test the synchronous mock retrier.
"""

from math import inf, nan
from re import escape
from typing import Any, cast

from object_mother_pattern import BooleanMother, FloatMother, IntegerMother
from pytest import mark, raises as assert_raises

from clock_pattern.retriers import Retrier
from clock_pattern.retriers.testing import MockRetrier


@mark.unit_testing
def test_mock_retrier_happy_path() -> None:
    """
    Test MockRetrier implements Retrier and returns the prepared value.
    """

    def operation() -> str:
        return 'ignored'

    retrier = MockRetrier()
    retrier.prepare_retry_method_return_value(value='done')

    result = retrier.retry(operation=operation, attempts=3)

    assert isinstance(retrier, Retrier)
    assert result == 'done'
    retrier.assert_retry_method_was_called_once_with(operation=operation, attempts=3)


@mark.unit_testing
def test_mock_retrier_returns_unprepared_none_value() -> None:
    """
    Test MockRetrier returns None when no return value or exception is prepared.
    """
    assert MockRetrier().retry(operation=lambda: 'ignored', attempts=1) is None


@mark.unit_testing
def test_mock_retrier_prepare_retry_method_exception() -> None:
    """
    Test MockRetrier raises the prepared exception after recording the call.
    """

    def operation() -> str:
        return 'ignored'

    retrier = MockRetrier()
    retrier.prepare_retry_method_exception(exception=ValueError('failed'))

    with assert_raises(expected_exception=ValueError, match=escape('failed')):
        retrier.retry(operation=operation, attempts=1)

    retrier.assert_retry_method_was_called_once_with(operation=operation, attempts=1)


@mark.unit_testing
def test_mock_retrier_assert_retry_method_was_called_once() -> None:
    """
    Test MockRetrier confirms retry was called exactly once.
    """
    retrier = MockRetrier()
    retrier.retry(operation=lambda: 'ignored', attempts=1)

    retrier.assert_retry_method_was_called_once()


@mark.unit_testing
def test_mock_retrier_assert_retry_method_was_called_once_after_multiple_calls() -> None:
    """
    Test MockRetrier called-once assertion fails after multiple retry calls.
    """
    retrier = MockRetrier()
    retrier.retry(operation=lambda: 'ignored', attempts=1)
    retrier.retry(operation=lambda: 'ignored', attempts=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=escape("Expected 'mock' to have been called once. Called 2 times."),
    ):
        retrier.assert_retry_method_was_called_once()


@mark.unit_testing
def test_mock_retrier_assert_retry_method_was_called_once_with_custom_values() -> None:
    """
    Test MockRetrier exact call assertion accepts all custom retry arguments.
    """

    def operation() -> str:
        return 'ignored'

    retrier = MockRetrier()
    retrier.retry(
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
def test_mock_retrier_assert_retry_method_was_called_once_with_different_arguments() -> None:
    """
    Test MockRetrier exact call assertion fails when expected arguments differ.
    """

    def operation() -> str:
        return 'ignored'

    retrier = MockRetrier()
    retrier.retry(operation=operation, attempts=1)

    with assert_raises(expected_exception=AssertionError, match=escape('expected call not found.')):
        retrier.assert_retry_method_was_called_once_with(operation=operation, attempts=2)


@mark.unit_testing
def test_mock_retrier_assert_retry_method_was_called_once_with_after_multiple_calls() -> None:
    """
    Test MockRetrier exact call assertion fails after multiple retry calls.
    """

    def operation() -> str:
        return 'ignored'

    retrier = MockRetrier()
    retrier.retry(operation=operation, attempts=1)
    retrier.retry(operation=operation, attempts=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=escape("Expected 'mock' to be called once. Called 2 times."),
    ):
        retrier.assert_retry_method_was_called_once_with(operation=operation, attempts=1)


@mark.unit_testing
def test_mock_retrier_assert_retry_method_was_not_called() -> None:
    """
    Test MockRetrier confirms retry was not called.
    """
    MockRetrier().assert_retry_method_was_not_called()


@mark.unit_testing
def test_mock_retrier_assert_retry_method_was_not_called_after_call() -> None:
    """
    Test MockRetrier not-called assertion fails after a retry call.
    """
    retrier = MockRetrier()
    retrier.retry(operation=lambda: 'ignored', attempts=1)

    with assert_raises(
        expected_exception=AssertionError,
        match=escape("Expected 'mock' to not have been called. Called 1 times."),
    ):
        retrier.assert_retry_method_was_not_called()


@mark.unit_testing
def test_mock_retrier_attempts_invalid_type() -> None:
    """
    Test MockRetrier rejects a non-integer attempt count.
    """
    attempts = IntegerMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'MockRetrier attempts <<<{attempts}>>> must be an integer. Got <<<{type(attempts).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        MockRetrier().retry(operation=lambda: 'ignored', attempts=cast(Any, attempts))


@mark.unit_testing
def test_mock_retrier_attempts_negative_random_value() -> None:
    """
    Test MockRetrier rejects a generated negative attempt count.
    """
    attempts = IntegerMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'MockRetrier attempts <<<{attempts}>>> must be a positive integer.'),
    ):
        MockRetrier().retry(operation=lambda: 'ignored', attempts=attempts)


@mark.unit_testing
def test_mock_retrier_attempts_zero_value() -> None:
    """
    Test MockRetrier rejects zero attempts.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrier attempts <<<0>>> must be a positive integer.'),
    ):
        MockRetrier().retry(operation=lambda: 'ignored', attempts=0)


@mark.unit_testing
def test_mock_retrier_attempts_positive_random_value() -> None:
    """
    Test MockRetrier accepts a generated positive attempt count.
    """
    attempts = IntegerMother.positive()

    assert MockRetrier().retry(operation=lambda: 'ignored', attempts=attempts) is None


@mark.unit_testing
def test_mock_retrier_delay_seconds_invalid_type() -> None:
    """
    Test MockRetrier rejects a non-numeric delay.
    """
    delay_seconds = FloatMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'MockRetrier delay_seconds <<<{delay_seconds}>>> must be an integer or float. Got <<<{type(delay_seconds).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        MockRetrier().retry(
            operation=lambda: 'ignored',
            attempts=1,
            delay_seconds=cast(Any, delay_seconds),
        )


@mark.unit_testing
def test_mock_retrier_delay_seconds_negative_random_value() -> None:
    """
    Test MockRetrier rejects a generated negative delay.
    """
    delay_seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'MockRetrier delay_seconds <<<{delay_seconds}>>> must be greater than or equal to zero.'),
    ):
        MockRetrier().retry(operation=lambda: 'ignored', attempts=1, delay_seconds=delay_seconds)


@mark.unit_testing
def test_mock_retrier_delay_seconds_non_finite_value() -> None:
    """
    Test MockRetrier rejects a non-finite delay.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrier delay_seconds <<<inf>>> must be finite and representable as a float.'),
    ):
        MockRetrier().retry(operation=lambda: 'ignored', attempts=1, delay_seconds=inf)


@mark.unit_testing
def test_mock_retrier_delay_seconds_zero_value() -> None:
    """
    Test MockRetrier accepts a zero delay.
    """
    assert MockRetrier().retry(operation=lambda: 'ignored', attempts=1, delay_seconds=0) is None


@mark.unit_testing
def test_mock_retrier_delay_seconds_positive_random_value() -> None:
    """
    Test MockRetrier accepts a generated positive delay.
    """
    delay_seconds = FloatMother.positive()

    assert MockRetrier().retry(operation=lambda: 'ignored', attempts=1, delay_seconds=delay_seconds) is None


@mark.unit_testing
def test_mock_retrier_backoff_invalid_type() -> None:
    """
    Test MockRetrier rejects a non-numeric backoff.
    """
    backoff = FloatMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'MockRetrier backoff <<<{backoff}>>> must be an integer or float. Got <<<{type(backoff).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        MockRetrier().retry(operation=lambda: 'ignored', attempts=1, backoff=cast(Any, backoff))


@mark.unit_testing
def test_mock_retrier_backoff_negative_random_value() -> None:
    """
    Test MockRetrier rejects a generated negative backoff.
    """
    backoff = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'MockRetrier backoff <<<{backoff}>>> must be greater than zero.'),
    ):
        MockRetrier().retry(operation=lambda: 'ignored', attempts=1, backoff=backoff)


@mark.unit_testing
def test_mock_retrier_backoff_zero_value() -> None:
    """
    Test MockRetrier rejects zero backoff.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrier backoff <<<0>>> must be greater than zero.'),
    ):
        MockRetrier().retry(operation=lambda: 'ignored', attempts=1, backoff=0)


@mark.unit_testing
def test_mock_retrier_backoff_non_finite_value() -> None:
    """
    Test MockRetrier rejects a non-finite backoff.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrier backoff <<<nan>>> must be finite and representable as a float.'),
    ):
        MockRetrier().retry(operation=lambda: 'ignored', attempts=1, backoff=nan)


@mark.unit_testing
def test_mock_retrier_backoff_positive_random_value() -> None:
    """
    Test MockRetrier accepts a generated positive backoff.
    """
    backoff = FloatMother.positive()

    assert MockRetrier().retry(operation=lambda: 'ignored', attempts=1, backoff=backoff) is None


@mark.unit_testing
def test_mock_retrier_jitter_invalid_type() -> None:
    """
    Test MockRetrier rejects a non-boolean jitter flag.
    """
    jitter = BooleanMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'MockRetrier jitter <<<{jitter}>>> must be a boolean. Got <<<{type(jitter).__name__}>>> type.'),
    ):
        MockRetrier().retry(operation=lambda: 'ignored', attempts=1, jitter=cast(Any, jitter))


@mark.unit_testing
def test_mock_retrier_retry_on_tuple_value() -> None:
    """
    Test MockRetrier accepts a non-empty tuple of Exception types.
    """
    assert (
        MockRetrier().retry(
            operation=lambda: 'ignored',
            attempts=1,
            retry_on=(ValueError, RuntimeError),
        )
        is None
    )


@mark.unit_testing
def test_mock_retrier_assert_retry_method_attempts_invalid_value() -> None:
    """
    Test MockRetrier exact assertion validates the expected attempt count.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrier attempts <<<0>>> must be a positive integer.'),
    ):
        MockRetrier().assert_retry_method_was_called_once_with(operation=lambda: 'ignored', attempts=0)


@mark.unit_testing
def test_mock_retrier_assert_retry_method_delay_seconds_invalid_value() -> None:
    """
    Test MockRetrier exact assertion validates the expected delay.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrier delay_seconds <<<-1>>> must be greater than or equal to zero.'),
    ):
        MockRetrier().assert_retry_method_was_called_once_with(
            operation=lambda: 'ignored',
            attempts=1,
            delay_seconds=-1,
        )


@mark.unit_testing
def test_mock_retrier_assert_retry_method_backoff_invalid_value() -> None:
    """
    Test MockRetrier exact assertion validates the expected backoff.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('MockRetrier backoff <<<0>>> must be greater than zero.'),
    ):
        MockRetrier().assert_retry_method_was_called_once_with(
            operation=lambda: 'ignored',
            attempts=1,
            backoff=0,
        )


@mark.unit_testing
def test_mock_retrier_assert_retry_method_jitter_invalid_type() -> None:
    """
    Test MockRetrier exact assertion validates the expected jitter flag.
    """
    jitter = BooleanMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'MockRetrier jitter <<<{jitter}>>> must be a boolean. Got <<<{type(jitter).__name__}>>> type.'),
    ):
        MockRetrier().assert_retry_method_was_called_once_with(
            operation=lambda: 'ignored',
            attempts=1,
            jitter=cast(Any, jitter),
        )
