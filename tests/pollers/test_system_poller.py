"""
Test SystemPoller poller.
"""

from re import escape
from typing import Any, cast
from unittest.mock import Mock

from object_mother_pattern import FloatMother
from pytest import mark, raises as assert_raises

from clock_pattern.deadlines import TimeoutExpiredError
from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.pollers import Poller, SystemPoller
from clock_pattern.sleepers.models import Sleeper
from clock_pattern.sleepers.testing import MockSleeper


@mark.unit_testing
def test_system_poller_happy_path() -> None:
    """
    Test SystemPoller is a Poller with explicitly injected dependencies.
    """
    monotonic_clock = MockMonotonicClock()
    poller = SystemPoller(
        sleeper=MockSleeper(monotonic_clock=monotonic_clock),
        monotonic_clock=monotonic_clock,
    )

    assert isinstance(poller, Poller)

    poller.poll_until(condition=lambda: True, timeout_seconds=1)


@mark.unit_testing
def test_system_poller_poll_until_method_evaluates_condition_immediately_without_sleeping() -> None:
    """
    Test SystemPoller evaluates a successful condition once without sleeping.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)
    condition = Mock(return_value=True)

    SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
        condition=condition,
        timeout_seconds=1,
    )

    assert condition.call_count == 1
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
def test_system_poller_poll_until_method_sleeps_until_condition_returns_true() -> None:
    """
    Test SystemPoller sleeps between false and true condition results.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)
    condition = Mock(side_effect=(False, True))

    SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
        condition=condition,
        timeout_seconds=1,
        interval_seconds=0.25,
    )

    assert condition.call_count == 2
    assert sleeper.sleep_calls == (0.25,)


@mark.unit_testing
def test_system_poller_poll_until_method_caps_sleep_to_remaining_seconds_after_condition_work() -> None:
    """
    Test SystemPoller accounts for condition work when capping the next sleep.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)
    condition_call_count = 0

    def condition() -> bool:
        nonlocal condition_call_count
        condition_call_count += 1

        if condition_call_count == 1:
            monotonic_clock.advance(seconds=0.75)
            return False

        return True

    SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
        condition=condition,
        timeout_seconds=1,
        interval_seconds=2,
    )

    assert condition_call_count == 2
    assert sleeper.sleep_calls == (0.25,)
    assert monotonic_clock.current_seconds() == 1.0


@mark.unit_testing
def test_system_poller_poll_until_method_accepts_true_condition_at_zero_timeout() -> None:
    """
    Test SystemPoller lets an immediately true condition win at a zero timeout.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)
    condition = Mock(return_value=True)

    SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
        condition=condition,
        timeout_seconds=0,
    )

    assert condition.call_count == 1
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
def test_system_poller_poll_until_method_rejects_false_condition_at_zero_timeout_without_sleeping() -> None:
    """
    Test SystemPoller raises immediately for a false condition at a zero timeout.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)
    condition = Mock(return_value=False)

    with assert_raises(
        expected_exception=TimeoutExpiredError,
        match=escape('Deadline expired after <<<0.0>>> seconds.'),
    ):
        SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
            condition=condition,
            timeout_seconds=0,
        )

    assert condition.call_count == 1
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
def test_system_poller_poll_until_method_does_not_sleep_again_after_timeout_expires() -> None:
    """
    Test SystemPoller stops before an additional sleep after deadline expiry.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)
    condition = Mock(return_value=False)

    with assert_raises(
        expected_exception=TimeoutExpiredError,
        match=escape('Deadline expired after <<<1.0>>> seconds.'),
    ):
        SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=0.25,
        )

    assert condition.call_count == 5
    assert sleeper.sleep_calls == (0.25, 0.25, 0.25, 0.25)


@mark.unit_testing
def test_system_poller_poll_until_method_propagates_condition_exception() -> None:
    """
    Test SystemPoller propagates the original condition exception unchanged.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)
    exception = RuntimeError('condition failed')
    condition = Mock(side_effect=exception)

    with assert_raises(expected_exception=RuntimeError, match=escape('condition failed')) as exception_info:
        SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
            condition=condition,
            timeout_seconds=1,
        )

    assert exception_info.value is exception
    assert condition.call_count == 1
    sleeper.assert_sleep_method_was_not_called()


@mark.unit_testing
def test_system_poller_poll_until_method_propagates_sleeper_exception() -> None:
    """
    Test SystemPoller propagates the original sleeper exception unchanged.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = Mock(spec=Sleeper)
    exception = RuntimeError('sleep failed')
    sleeper.sleep.side_effect = exception
    condition = Mock(return_value=False)

    with assert_raises(expected_exception=RuntimeError, match=escape('sleep failed')) as exception_info:
        SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
            condition=condition,
            timeout_seconds=1,
            interval_seconds=0.25,
        )

    assert exception_info.value is exception
    assert condition.call_count == 1
    sleeper.sleep.assert_called_once_with(seconds=0.25)


@mark.unit_testing
def test_system_poller_preserves_injected_sleeper() -> None:
    """
    Test SystemPoller stores the injected sleeper directly.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)

    assert SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock)._sleeper is sleeper


@mark.unit_testing
def test_system_poller_preserves_injected_monotonic_clock() -> None:
    """
    Test SystemPoller stores the injected monotonic clock directly.
    """
    monotonic_clock = MockMonotonicClock()

    poller = SystemPoller(
        sleeper=MockSleeper(monotonic_clock=monotonic_clock),
        monotonic_clock=monotonic_clock,
    )

    assert poller._monotonic_clock is monotonic_clock


@mark.unit_testing
def test_system_poller_condition_invalid_type() -> None:
    """
    Test SystemPoller lets invocation raise naturally for a non-callable condition.
    """
    condition = FloatMother.create()

    with assert_raises(
        expected_exception=TypeError,
        match=escape("'float' object is not callable"),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=cast(Any, condition), timeout_seconds=1)


@mark.unit_testing
def test_system_poller_condition_invalid_return_type() -> None:
    """
    Test SystemPoller poll_until requires an exact boolean condition result.
    """
    condition_result = 1

    with assert_raises(
        expected_exception=TypeError,
        match=escape('SystemPoller condition <<<1>>> must be a boolean. Got <<<int>>> type.'),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(
            condition=cast(Any, lambda: condition_result),
            timeout_seconds=1,
        )


@mark.unit_testing
def test_system_poller_timeout_seconds_invalid_type() -> None:
    """
    Test SystemPoller rejects a timeout with an invalid primitive type.
    """
    timeout_seconds = FloatMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(
            f'SystemPoller timeout_seconds <<<{timeout_seconds}>>> must be an integer or float. '
            f'Got <<<{type(timeout_seconds).__name__}>>> type.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=timeout_seconds)


@mark.unit_testing
def test_system_poller_timeout_seconds_negative_random_value() -> None:
    """
    Test SystemPoller rejects a generated negative timeout.
    """
    timeout_seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'SystemPoller timeout_seconds <<<{timeout_seconds}>>> must be greater than or equal to zero.'),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=timeout_seconds)


@mark.unit_testing
def test_system_poller_timeout_seconds_negative_limit_value() -> None:
    """
    Test SystemPoller rejects the explicit negative timeout boundary.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('SystemPoller timeout_seconds <<<-1.0>>> must be greater than or equal to zero.'),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=-1.0)


@mark.unit_testing
def test_system_poller_timeout_seconds_positive_random_value() -> None:
    """
    Test SystemPoller accepts a generated positive timeout.
    """
    timeout_seconds = FloatMother.positive()

    monotonic_clock = MockMonotonicClock()
    SystemPoller(
        sleeper=MockSleeper(monotonic_clock=monotonic_clock),
        monotonic_clock=monotonic_clock,
    ).poll_until(condition=lambda: True, timeout_seconds=timeout_seconds)


@mark.unit_testing
def test_system_poller_timeout_seconds_integer_value() -> None:
    """
    Test SystemPoller accepts an integer timeout.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)

    with assert_raises(
        expected_exception=TimeoutExpiredError,
        match=escape('Deadline expired after <<<1.0>>> seconds.'),
    ):
        SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
            condition=lambda: False,
            timeout_seconds=1,
            interval_seconds=1,
        )


@mark.unit_testing
def test_system_poller_timeout_seconds_positive_infinity_value() -> None:
    """
    Test SystemPoller rejects a positive infinity timeout.
    """
    timeout_seconds = float('inf')

    with assert_raises(
        expected_exception=ValueError,
        match=escape(
            f'SystemPoller timeout_seconds <<<{timeout_seconds}>>> must be finite and representable as a float.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=timeout_seconds)


@mark.unit_testing
def test_system_poller_timeout_seconds_negative_infinity_value() -> None:
    """
    Test SystemPoller rejects a negative infinity timeout.
    """
    timeout_seconds = float('-inf')

    with assert_raises(
        expected_exception=ValueError,
        match=escape(
            f'SystemPoller timeout_seconds <<<{timeout_seconds}>>> must be finite and representable as a float.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=timeout_seconds)


@mark.unit_testing
def test_system_poller_timeout_seconds_nan_value() -> None:
    """
    Test SystemPoller rejects a not-a-number timeout.
    """
    timeout_seconds = float('nan')

    with assert_raises(
        expected_exception=ValueError,
        match=escape(
            f'SystemPoller timeout_seconds <<<{timeout_seconds}>>> must be finite and representable as a float.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=timeout_seconds)


@mark.unit_testing
def test_system_poller_interval_seconds_invalid_type() -> None:
    """
    Test SystemPoller rejects an interval with an invalid primitive type.
    """
    interval_seconds = FloatMother.invalid_type()

    with assert_raises(
        expected_exception=TypeError,
        match=escape(
            f'SystemPoller interval_seconds <<<{interval_seconds}>>> must be an integer or float. '
            f'Got <<<{type(interval_seconds).__name__}>>> type.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(
            condition=lambda: True,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )


@mark.unit_testing
def test_system_poller_interval_seconds_negative_random_value() -> None:
    """
    Test SystemPoller rejects a generated negative interval.
    """
    interval_seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=escape(f'SystemPoller interval_seconds <<<{interval_seconds}>>> must be greater than zero.'),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(
            condition=lambda: True,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )


@mark.unit_testing
def test_system_poller_interval_seconds_negative_limit_value() -> None:
    """
    Test SystemPoller rejects the explicit negative interval boundary.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('SystemPoller interval_seconds <<<-1.0>>> must be greater than zero.'),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=1, interval_seconds=-1.0)


@mark.unit_testing
def test_system_poller_interval_seconds_zero_value() -> None:
    """
    Test SystemPoller rejects a zero interval.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=escape('SystemPoller interval_seconds <<<0>>> must be greater than zero.'),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(condition=lambda: True, timeout_seconds=1, interval_seconds=0)


@mark.unit_testing
def test_system_poller_interval_seconds_positive_random_value() -> None:
    """
    Test SystemPoller accepts a generated positive interval.
    """
    interval_seconds = FloatMother.positive()
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)
    condition = Mock(side_effect=(False, True))

    SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
        condition=condition,
        timeout_seconds=interval_seconds,
        interval_seconds=interval_seconds,
    )

    assert sleeper.sleep_calls == (interval_seconds,)


@mark.unit_testing
def test_system_poller_interval_seconds_preserves_integer_value() -> None:
    """
    Test SystemPoller preserves an integer interval when sleeping.
    """
    monotonic_clock = MockMonotonicClock()
    sleeper = MockSleeper(monotonic_clock=monotonic_clock)
    condition = Mock(side_effect=(False, True))

    SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
        condition=condition,
        timeout_seconds=2,
        interval_seconds=1,
    )

    assert sleeper.sleep_calls == (1,)
    assert type(sleeper.sleep_calls[0]) is int


@mark.unit_testing
def test_system_poller_interval_seconds_positive_infinity_value() -> None:
    """
    Test SystemPoller rejects a positive infinity interval.
    """
    interval_seconds = float('inf')

    with assert_raises(
        expected_exception=ValueError,
        match=escape(
            f'SystemPoller interval_seconds <<<{interval_seconds}>>> must be finite and representable as a float.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(
            condition=lambda: True,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )


@mark.unit_testing
def test_system_poller_interval_seconds_negative_infinity_value() -> None:
    """
    Test SystemPoller rejects a negative infinity interval.
    """
    interval_seconds = float('-inf')

    with assert_raises(
        expected_exception=ValueError,
        match=escape(
            f'SystemPoller interval_seconds <<<{interval_seconds}>>> must be finite and representable as a float.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(
            condition=lambda: True,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )


@mark.unit_testing
def test_system_poller_interval_seconds_nan_value() -> None:
    """
    Test SystemPoller rejects a not-a-number interval.
    """
    interval_seconds = float('nan')

    with assert_raises(
        expected_exception=ValueError,
        match=escape(
            f'SystemPoller interval_seconds <<<{interval_seconds}>>> must be finite and representable as a float.'
        ),
    ):
        monotonic_clock = MockMonotonicClock()
        SystemPoller(
            sleeper=MockSleeper(monotonic_clock=monotonic_clock),
            monotonic_clock=monotonic_clock,
        ).poll_until(
            condition=lambda: True,
            timeout_seconds=1,
            interval_seconds=interval_seconds,
        )
