"""
Test the synchronous system retrier.
"""

from math import inf, nan
from re import escape

from object_mother_pattern import BooleanMother, FloatMother, IntegerMother
from pytest import mark, raises as assert_raises

from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.retriers import Retrier, SystemRetrier
from clock_pattern.sleepers.testing import MockSleeper


class _FalseyMockSleeper(MockSleeper):
    """
    Represent a valid injected sleeper whose truth value is false.
    """

    def __bool__(self) -> bool:
        """
        Return false so constructor fallback behavior can be tested.
        """
        return False


@mark.unit_testing
def test_system_retrier_happy_path_returns_falsey_value() -> None:
    """
    Test SystemRetrier implements Retrier and returns a successful falsey value.
    """
    retrier = SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock()))

    assert isinstance(retrier, Retrier)
    assert retrier.retry(operation=lambda: 0, attempts=1) == 0


@mark.unit_testing
def test_system_retrier_retries_until_operation_succeeds() -> None:
    """
    Test SystemRetrier retries a configured exception until the operation succeeds.
    """
    operation_calls = 0
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())

    def operation() -> str:
        nonlocal operation_calls
        operation_calls += 1

        if operation_calls == 1:
            raise ValueError('temporary failure')

        return 'done'

    result = SystemRetrier(sleeper=sleeper).retry(
        operation=operation,
        attempts=2,
        delay_seconds=0.25,
        retry_on=ValueError,
    )

    assert result == 'done'
    assert operation_calls == 2
    assert sleeper.sleep_calls == (0.25,)


@mark.unit_testing
def test_system_retrier_raises_last_retryable_exception_when_attempts_are_exhausted() -> None:
    """
    Test SystemRetrier re-raises the final retryable exception after all attempts.
    """
    operation_calls = 0
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())

    def operation() -> None:
        nonlocal operation_calls
        operation_calls += 1
        raise ValueError(f'failure {operation_calls}')

    with assert_raises(expected_exception=ValueError, match=escape('failure 3')):
        SystemRetrier(sleeper=sleeper).retry(
            operation=operation,
            attempts=3,
            delay_seconds=0.25,
            retry_on=ValueError,
        )

    assert operation_calls == 3
    assert sleeper.sleep_calls == (0.25, 0.25)


@mark.unit_testing
def test_system_retrier_raises_non_retryable_exception_without_retrying() -> None:
    """
    Test SystemRetrier propagates a non-retryable exception immediately.
    """
    operation_calls = 0
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())

    def operation() -> None:
        nonlocal operation_calls
        operation_calls += 1
        raise RuntimeError('not retryable')

    with assert_raises(expected_exception=RuntimeError, match=escape('not retryable')):
        SystemRetrier(sleeper=sleeper).retry(
            operation=operation,
            attempts=3,
            delay_seconds=1,
            retry_on=ValueError,
        )

    assert operation_calls == 1
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
def test_system_retrier_does_not_retry_control_flow_exception() -> None:
    """
    Test SystemRetrier propagates a control-flow exception immediately.
    """
    operation_calls = 0
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())

    def operation() -> None:
        nonlocal operation_calls
        operation_calls += 1
        raise KeyboardInterrupt

    with assert_raises(expected_exception=KeyboardInterrupt):
        SystemRetrier(sleeper=sleeper).retry(operation=operation, attempts=3, delay_seconds=1)

    assert operation_calls == 1
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
def test_system_retrier_does_not_sleep_when_delay_is_zero() -> None:
    """
    Test SystemRetrier retries without sleeping when delay_seconds is zero.
    """
    operation_calls = 0
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())

    def operation() -> str:
        nonlocal operation_calls
        operation_calls += 1

        if operation_calls == 1:
            raise ValueError('temporary failure')

        return 'done'

    assert SystemRetrier(sleeper=sleeper).retry(operation=operation, attempts=2, delay_seconds=0) == 'done'
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
def test_system_retrier_applies_backoff_between_attempts() -> None:
    """
    Test SystemRetrier multiplies the delay after each failed attempt.
    """
    operation_calls = 0
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())

    def operation() -> str:
        nonlocal operation_calls
        operation_calls += 1

        if operation_calls < 3:
            raise ValueError('temporary failure')

        return 'done'

    result = SystemRetrier(sleeper=sleeper).retry(
        operation=operation,
        attempts=3,
        delay_seconds=0.25,
        backoff=2,
    )

    assert result == 'done'
    assert sleeper.sleep_calls == (0.25, 0.5)


@mark.unit_testing
def test_system_retrier_applies_full_jitter_with_current_delay_bounds() -> None:
    """
    Test SystemRetrier calls the injected jitter function with each current delay.
    """
    operation_calls = 0
    random_uniform_calls: list[tuple[float, float]] = []
    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())

    def operation() -> str:
        nonlocal operation_calls
        operation_calls += 1

        if operation_calls < 3:
            raise ValueError('temporary failure')

        return 'done'

    def random_uniform(minimum: float, maximum: float) -> float:
        random_uniform_calls.append((minimum, maximum))
        return maximum / 2

    result = SystemRetrier(sleeper=sleeper, random_uniform=random_uniform).retry(
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
def test_system_retrier_preserves_falsey_injected_sleeper() -> None:
    """
    Test SystemRetrier uses a valid injected sleeper even when it is falsey.
    """
    operation_calls = 0
    sleeper = _FalseyMockSleeper(monotonic_clock=MockMonotonicClock())

    def operation() -> str:
        nonlocal operation_calls
        operation_calls += 1

        if operation_calls == 1:
            raise ValueError('temporary failure')

        return 'done'

    assert SystemRetrier(sleeper=sleeper).retry(operation=operation, attempts=2, delay_seconds=0.25) == 'done'
    assert sleeper.sleep_calls == (0.25,)


@mark.unit_testing
def test_system_retrier_attempts_invalid_type() -> None:
    """
    Test SystemRetrier rejects a non-integer attempt count.
    """
    attempts = IntegerMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'SystemRetrier attempts <<<{attempts}>>> must be an integer. Got <<<{type(attempts).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock())).retry(
            operation=lambda: 'done',
            attempts=attempts,
        )


@mark.unit_testing
def test_system_retrier_attempts_negative_random_value() -> None:
    """
    Test SystemRetrier rejects a generated negative attempt count.
    """
    attempts = IntegerMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'SystemRetrier attempts <<<{attempts}>>> must be a positive integer.'),
    ):
        SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock())).retry(
            operation=lambda: 'done',
            attempts=attempts,
        )


@mark.unit_testing
def test_system_retrier_attempts_zero_value() -> None:
    """
    Test SystemRetrier rejects zero attempts.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('SystemRetrier attempts <<<0>>> must be a positive integer.'),
    ):
        SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock())).retry(
            operation=lambda: 'done',
            attempts=0,
        )


@mark.unit_testing
def test_system_retrier_attempts_positive_random_value() -> None:
    """
    Test SystemRetrier accepts a generated positive attempt count.
    """
    attempts = IntegerMother.positive()

    retrier = SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock()))

    assert retrier.retry(operation=lambda: 'done', attempts=attempts) == 'done'


@mark.unit_testing
def test_system_retrier_delay_seconds_invalid_type() -> None:
    """
    Test SystemRetrier rejects a non-numeric delay.
    """
    delay_seconds = FloatMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'SystemRetrier delay_seconds <<<{delay_seconds}>>> must be an integer or float. Got <<<{type(delay_seconds).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock())).retry(
            operation=lambda: 'done',
            attempts=1,
            delay_seconds=delay_seconds,
        )


@mark.unit_testing
def test_system_retrier_delay_seconds_negative_random_value() -> None:
    """
    Test SystemRetrier rejects a generated negative delay.
    """
    delay_seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'SystemRetrier delay_seconds <<<{delay_seconds}>>> must be greater than or equal to zero.'),
    ):
        SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock())).retry(
            operation=lambda: 'done',
            attempts=1,
            delay_seconds=delay_seconds,
        )


@mark.unit_testing
def test_system_retrier_delay_seconds_non_finite_value() -> None:
    """
    Test SystemRetrier rejects a non-finite delay.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('SystemRetrier delay_seconds <<<inf>>> must be finite and representable as a float.'),
    ):
        SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock())).retry(
            operation=lambda: 'done',
            attempts=1,
            delay_seconds=inf,
        )


@mark.unit_testing
def test_system_retrier_delay_seconds_positive_random_value() -> None:
    """
    Test SystemRetrier accepts a generated positive delay.
    """
    delay_seconds = FloatMother.positive()

    retrier = SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock()))

    assert retrier.retry(operation=lambda: 'done', attempts=1, delay_seconds=delay_seconds) == 'done'


@mark.unit_testing
def test_system_retrier_backoff_invalid_type() -> None:
    """
    Test SystemRetrier rejects a non-numeric backoff.
    """
    backoff = FloatMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'SystemRetrier backoff <<<{backoff}>>> must be an integer or float. Got <<<{type(backoff).__name__}>>> type.'),  # noqa: E501
    ):  # fmt: skip
        SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock())).retry(
            operation=lambda: 'done',
            attempts=1,
            backoff=backoff,
        )


@mark.unit_testing
def test_system_retrier_backoff_negative_random_value() -> None:
    """
    Test SystemRetrier rejects a generated negative backoff.
    """
    backoff = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'SystemRetrier backoff <<<{backoff}>>> must be greater than zero.'),
    ):
        SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock())).retry(
            operation=lambda: 'done',
            attempts=1,
            backoff=backoff,
        )


@mark.unit_testing
def test_system_retrier_backoff_zero_value() -> None:
    """
    Test SystemRetrier rejects zero backoff.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('SystemRetrier backoff <<<0>>> must be greater than zero.'),
    ):
        SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock())).retry(
            operation=lambda: 'done',
            attempts=1,
            backoff=0,
        )


@mark.unit_testing
def test_system_retrier_backoff_non_finite_value() -> None:
    """
    Test SystemRetrier rejects a non-finite backoff.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('SystemRetrier backoff <<<nan>>> must be finite and representable as a float.'),
    ):
        SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock())).retry(
            operation=lambda: 'done',
            attempts=1,
            backoff=nan,
        )


@mark.unit_testing
def test_system_retrier_backoff_positive_random_value() -> None:
    """
    Test SystemRetrier accepts a generated positive backoff.
    """
    backoff = FloatMother.positive()

    retrier = SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock()))

    assert retrier.retry(operation=lambda: 'done', attempts=1, backoff=backoff) == 'done'


@mark.unit_testing
def test_system_retrier_jitter_invalid_type() -> None:
    """
    Test SystemRetrier rejects a non-boolean jitter flag.
    """
    jitter = BooleanMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(f'SystemRetrier jitter <<<{jitter}>>> must be a boolean. Got <<<{type(jitter).__name__}>>> type.'),
    ):
        SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock())).retry(
            operation=lambda: 'done',
            attempts=1,
            jitter=jitter,
        )


@mark.unit_testing
def test_system_retrier_retry_on_tuple_value() -> None:
    """
    Test SystemRetrier accepts a non-empty tuple of Exception types.
    """
    result = SystemRetrier(sleeper=MockSleeper(monotonic_clock=MockMonotonicClock())).retry(
        operation=lambda: 'done',
        attempts=1,
        retry_on=(ValueError, RuntimeError),
    )

    assert result == 'done'
