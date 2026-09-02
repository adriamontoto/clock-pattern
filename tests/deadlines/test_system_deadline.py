"""
Test SystemDeadline deadline.
"""

import signal as signal_module
from collections.abc import Iterator
from contextlib import contextmanager
from threading import Thread
from time import monotonic, sleep
from unittest.mock import Mock, call, patch

from object_mother_pattern import FloatMother
from pytest import mark, raises as assert_raises

from clock_pattern.deadlines import Deadline, SystemDeadline, TimeoutExpiredError
from clock_pattern.monotonic_clocks import SystemMonotonicClock
from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

_SIGNAL_TIMEOUT_SUPPORTED = all(hasattr(signal_module, name) for name in ('SIGALRM', 'ITIMER_REAL', 'getitimer', 'setitimer'))  # noqa: E501  # fmt: skip


@contextmanager
def _mock_signal_timeout() -> Iterator[tuple[Mock, Mock, Mock, Mock]]:
    """
    Mock the Unix signal slot used by SystemDeadline.
    """
    with (
        patch('clock_pattern.deadlines.system_deadline._SIGNAL_TIMEOUT_SUPPORTED', True),
        patch.object(signal_module, 'SIGALRM', 14, create=True),
        patch.object(signal_module, 'ITIMER_REAL', 0, create=True),
        patch.object(signal_module, 'getsignal', return_value=signal_module.SIG_DFL) as getsignal_mock,
        patch.object(signal_module, 'getitimer', return_value=(0.0, 0.0), create=True) as getitimer_mock,
        patch.object(signal_module, 'signal') as signal_mock,
        patch.object(signal_module, 'setitimer', create=True) as setitimer_mock,
    ):
        yield getsignal_mock, getitimer_mock, signal_mock, setitimer_mock


@mark.unit_testing
def test_system_deadline_happy_path() -> None:
    """
    Test SystemDeadline deadline happy path.
    """
    monotonic_clock = MockMonotonicClock()
    deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)

    assert isinstance(deadline, Deadline)
    assert type(deadline.elapsed_seconds) is float
    assert deadline.elapsed_seconds == 0.0
    assert type(deadline.remaining_seconds) is float
    assert deadline.remaining_seconds == 1.0
    assert deadline.expired is False


@mark.unit_testing
def test_system_deadline_elapsed_seconds_property() -> None:
    """
    Test SystemDeadline elapsed_seconds property.
    """
    monotonic_clock = MockMonotonicClock(current_seconds=10)
    deadline = SystemDeadline(seconds=2, monotonic_clock=monotonic_clock)

    monotonic_clock.advance(seconds=0.5)

    assert deadline.elapsed_seconds == 0.5


@mark.unit_testing
def test_system_deadline_remaining_seconds_property_when_time_remains() -> None:
    """
    Test SystemDeadline remaining_seconds property when time remains.
    """
    monotonic_clock = MockMonotonicClock()
    deadline = SystemDeadline(seconds=2, monotonic_clock=monotonic_clock)

    monotonic_clock.advance(seconds=0.5)

    assert deadline.remaining_seconds == 1.5


@mark.unit_testing
def test_system_deadline_remaining_seconds_property_when_deadline_expired() -> None:
    """
    Test SystemDeadline remaining_seconds property returns zero when deadline expired.
    """
    monotonic_clock = MockMonotonicClock()
    deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)

    monotonic_clock.advance(seconds=2)

    assert deadline.remaining_seconds == 0.0


@mark.unit_testing
def test_system_deadline_expired_property_returns_true_when_elapsed_seconds_reaches_deadline() -> None:
    """
    Test SystemDeadline expired property returns true when elapsed seconds reaches deadline.
    """
    monotonic_clock = MockMonotonicClock()
    deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)

    monotonic_clock.advance(seconds=1)

    assert deadline.expired is True


@mark.unit_testing
def test_system_deadline_raise_if_expired_method_does_not_raise_before_deadline() -> None:
    """
    Test SystemDeadline raise_if_expired method returns before the deadline.
    """
    deadline = SystemDeadline(seconds=1, monotonic_clock=MockMonotonicClock())

    assert deadline.raise_if_expired() is None


@mark.unit_testing
def test_system_deadline_raise_if_expired_method_reports_measured_elapsed_seconds() -> None:
    """
    Test SystemDeadline raise_if_expired method reports measured elapsed seconds.
    """
    monotonic_clock = MockMonotonicClock()
    deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)
    monotonic_clock.advance(seconds=2)

    with assert_raises(
        expected_exception=TimeoutExpiredError,
        match=r'Deadline expired after <<<2.0>>> seconds\.',
    ) as exception_info:
        deadline.raise_if_expired()

    assert exception_info.value.elapsed_seconds == 2.0


@mark.unit_testing
def test_system_deadline_enter_method_returns_deadline() -> None:
    """
    Test SystemDeadline context manager enter method returns deadline.
    """
    deadline = SystemDeadline(seconds=1, monotonic_clock=MockMonotonicClock())

    with _mock_signal_timeout() as (_, _, signal_mock, setitimer_mock), deadline as active_deadline:
        assert active_deadline is deadline

    assert setitimer_mock.call_args_list == [call(0, 1.0), call(0, 0.0, 0.0)]
    assert signal_mock.call_args_list[-1] == call(14, signal_module.SIG_DFL)


@mark.unit_testing
def test_system_deadline_enter_method_raises_before_body_when_seconds_is_zero() -> None:
    """
    Test SystemDeadline context manager enter method raises before the body when seconds is zero.
    """
    deadline = SystemDeadline(seconds=0, monotonic_clock=MockMonotonicClock())

    with (
        _mock_signal_timeout() as (getsignal_mock, getitimer_mock, signal_mock, setitimer_mock),
        assert_raises(expected_exception=TimeoutExpiredError, match=r'Deadline expired after <<<0.0>>> seconds\.'),
        deadline,
    ):
        raise AssertionError('expired deadline body must not run')

    getsignal_mock.assert_not_called()
    getitimer_mock.assert_not_called()
    signal_mock.assert_not_called()
    setitimer_mock.assert_not_called()


@mark.unit_testing
def test_system_deadline_enter_method_raises_before_body_when_deadline_already_expired() -> None:
    """
    Test SystemDeadline context manager enter method raises before the body when deadline already expired.
    """
    monotonic_clock = MockMonotonicClock()
    deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)
    monotonic_clock.advance(seconds=1)

    with (
        _mock_signal_timeout() as (getsignal_mock, getitimer_mock, signal_mock, setitimer_mock),
        assert_raises(
            expected_exception=TimeoutExpiredError,
            match=r'Deadline expired after <<<1.0>>> seconds\.',
        ),
        deadline,
    ):
        raise AssertionError('expired deadline body must not run')

    getsignal_mock.assert_not_called()
    getitimer_mock.assert_not_called()
    signal_mock.assert_not_called()
    setitimer_mock.assert_not_called()


@mark.unit_testing
def test_system_deadline_enter_method_raises_if_deadline_expires_during_signal_setup() -> None:
    """
    Test SystemDeadline context manager enter method raises if the deadline expires during signal setup.
    """
    monotonic_clock = MockMonotonicClock()
    deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)

    with (
        patch.object(monotonic_clock, 'current_seconds', side_effect=[0.0, 1.0]),
        _mock_signal_timeout() as (_, _, signal_mock, setitimer_mock),
        assert_raises(
            expected_exception=TimeoutExpiredError,
            match=r'Deadline expired after <<<1.0>>> seconds\.',
        ),
        deadline,
    ):
        raise AssertionError('expired deadline body must not run')

    assert signal_mock.call_args_list[-1] == call(14, signal_module.SIG_DFL)
    setitimer_mock.assert_not_called()


@mark.unit_testing
def test_system_deadline_exit_method_raises_if_successful_block_reaches_deadline() -> None:
    """
    Test SystemDeadline context manager exit method raises if a successful block reaches the deadline.
    """
    monotonic_clock = MockMonotonicClock()
    deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)

    with (
        _mock_signal_timeout(),
        assert_raises(
            expected_exception=TimeoutExpiredError,
            match=r'Deadline expired after <<<2.0>>> seconds\.',
        ),
        deadline,
    ):
        monotonic_clock.advance(seconds=2)


@mark.unit_testing
def test_system_deadline_exit_method_preserves_block_exception_after_deadline() -> None:
    """
    Test SystemDeadline context manager exit method preserves a block exception after the deadline.
    """
    monotonic_clock = MockMonotonicClock()
    deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)

    with _mock_signal_timeout(), assert_raises(expected_exception=RuntimeError, match=r'block failed'), deadline:
        monotonic_clock.advance(seconds=2)
        raise RuntimeError('block failed')


@mark.unit_testing
@mark.skipif(not _SIGNAL_TIMEOUT_SUPPORTED, reason='Unix signal timeout required')
def test_system_deadline_context_interrupts_blocking_sleep() -> None:
    """
    Test SystemDeadline context manager interrupts a blocking sleep near the deadline.
    """
    started_at = monotonic()

    with (
        assert_raises(
            expected_exception=TimeoutExpiredError,
            match=r'Deadline expired after <<<0\.\d+>>> seconds\.',
        ) as exception_info,
        SystemDeadline(seconds=0.05, monotonic_clock=SystemMonotonicClock()),
    ):
        sleep(2)

    assert exception_info.value.elapsed_seconds >= 0.05
    assert monotonic() - started_at < 1.0


@mark.unit_testing
def test_system_deadline_enter_method_rejects_unsupported_signal_timeouts() -> None:
    """
    Test SystemDeadline context manager rejects platforms without Unix signal timeouts.
    """
    deadline = SystemDeadline(seconds=1, monotonic_clock=MockMonotonicClock())

    with (
        patch('clock_pattern.deadlines.system_deadline._SIGNAL_TIMEOUT_SUPPORTED', False),
        patch.object(signal_module, 'getsignal') as getsignal_mock,
        assert_raises(
            expected_exception=RuntimeError,
            match=r'SystemDeadline context manager requires Unix SIGALRM support.',
        ),
        deadline,
    ):
        pass

    getsignal_mock.assert_not_called()


@mark.unit_testing
def test_system_deadline_enter_method_rejects_worker_thread() -> None:
    """
    Test SystemDeadline context manager rejects worker-thread entry.
    """
    errors: list[BaseException] = []

    def _enter_deadline() -> None:
        try:
            with SystemDeadline(seconds=1, monotonic_clock=MockMonotonicClock()):
                pass
        except BaseException as error:
            errors.append(error)

    thread = Thread(target=_enter_deadline)
    thread.start()
    thread.join(timeout=1)

    assert thread.is_alive() is False
    assert len(errors) == 1
    assert type(errors[0]) is RuntimeError
    assert str(errors[0]) == 'SystemDeadline context manager requires the main thread of the main interpreter.'


@mark.unit_testing
def test_system_deadline_enter_method_rejects_existing_signal_handler() -> None:
    """
    Test SystemDeadline context manager rejects an existing SIGALRM handler.
    """
    deadline = SystemDeadline(seconds=1, monotonic_clock=MockMonotonicClock())

    with (
        _mock_signal_timeout() as (getsignal_mock, _, signal_mock, setitimer_mock),
        assert_raises(
            expected_exception=RuntimeError,
            match=r'SystemDeadline context manager cannot replace an existing SIGALRM handler or timer.',
        ),
    ):
        getsignal_mock.return_value = signal_module.SIG_IGN
        with deadline:
            pass

    signal_mock.assert_not_called()
    setitimer_mock.assert_not_called()


@mark.unit_testing
def test_system_deadline_enter_method_rejects_existing_signal_timer() -> None:
    """
    Test SystemDeadline context manager rejects an existing real-time signal timer.
    """
    deadline = SystemDeadline(seconds=1, monotonic_clock=MockMonotonicClock())

    with (
        _mock_signal_timeout() as (_, getitimer_mock, signal_mock, setitimer_mock),
        assert_raises(
            expected_exception=RuntimeError,
            match=r'SystemDeadline context manager cannot replace an existing SIGALRM handler or timer.',
        ),
    ):
        getitimer_mock.return_value = (1.0, 0.0)
        with deadline:
            pass

    signal_mock.assert_not_called()
    setitimer_mock.assert_not_called()


@mark.unit_testing
def test_system_deadline_enter_method_rejects_nested_deadlines() -> None:
    """
    Test SystemDeadline context manager rejects nested deadlines.
    """
    outer_deadline = SystemDeadline(seconds=2, monotonic_clock=MockMonotonicClock())
    inner_deadline = SystemDeadline(seconds=1, monotonic_clock=MockMonotonicClock())

    with _mock_signal_timeout() as (getsignal_mock, _, _, _), outer_deadline:
        getsignal_mock.return_value = signal_module.SIG_IGN
        with (
            assert_raises(
                expected_exception=RuntimeError,
                match=r'SystemDeadline context manager cannot replace an existing SIGALRM handler or timer.',
            ),
            inner_deadline,
        ):
            pass


@mark.unit_testing
def test_system_deadline_enter_method_rejects_repeated_entry() -> None:
    """
    Test SystemDeadline context manager rejects repeated entry.
    """
    deadline = SystemDeadline(seconds=1, monotonic_clock=MockMonotonicClock())

    with _mock_signal_timeout(), deadline:
        pass

    with (
        _mock_signal_timeout(),
        assert_raises(
            expected_exception=RuntimeError,
            match=r'SystemDeadline context manager cannot be entered more than once.',
        ),
        deadline,
    ):
        pass


@mark.unit_testing
def test_system_deadline_enter_method_converts_signal_thread_error() -> None:
    """
    Test SystemDeadline context manager converts a signal main-interpreter error.
    """
    deadline = SystemDeadline(seconds=1, monotonic_clock=MockMonotonicClock())

    with (
        _mock_signal_timeout() as (_, _, signal_mock, setitimer_mock),
        assert_raises(
            expected_exception=RuntimeError,
            match=r'SystemDeadline context manager requires the main thread of the main interpreter.',
        ),
    ):
        signal_mock.side_effect = ValueError('signals unavailable')
        with deadline:
            pass

    setitimer_mock.assert_not_called()


@mark.unit_testing
def test_system_deadline_enter_method_restores_handler_if_timer_setup_fails() -> None:
    """
    Test SystemDeadline context manager restores the signal handler if timer setup fails.
    """
    deadline = SystemDeadline(seconds=1, monotonic_clock=MockMonotonicClock())

    with (
        _mock_signal_timeout() as (_, _, signal_mock, setitimer_mock),
        assert_raises(
            expected_exception=OSError,
            match=r'timer setup failed',
        ),
    ):
        setitimer_mock.side_effect = OSError('timer setup failed')
        with deadline:
            pass

    assert signal_mock.call_args_list[-1] == call(14, signal_module.SIG_DFL)


@mark.unit_testing
def test_system_deadline_exit_method_raises_timer_cleanup_error_after_successful_block() -> None:
    """
    Test SystemDeadline context manager raises a timer cleanup error after a successful block.
    """
    deadline = SystemDeadline(seconds=1, monotonic_clock=MockMonotonicClock())

    with (
        _mock_signal_timeout() as (_, _, _, setitimer_mock),
        assert_raises(
            expected_exception=OSError,
            match=r'timer cleanup failed',
        ),
    ):
        setitimer_mock.side_effect = [None, OSError('timer cleanup failed')]
        with deadline:
            pass


@mark.unit_testing
def test_system_deadline_exit_method_preserves_block_error_if_timer_cleanup_fails() -> None:
    """
    Test SystemDeadline context manager preserves a block error if timer cleanup fails.
    """
    deadline = SystemDeadline(seconds=1, monotonic_clock=MockMonotonicClock())

    with (
        _mock_signal_timeout() as (_, _, _, setitimer_mock),
        assert_raises(
            expected_exception=RuntimeError,
            match=r'block failed',
        ) as exception_info,
    ):
        setitimer_mock.side_effect = [None, OSError('timer cleanup failed')]
        with deadline:
            raise RuntimeError('block failed')

    assert exception_info.value.__notes__ == ["SystemDeadline signal cleanup failed: OSError('timer cleanup failed')"]


@mark.unit_testing
def test_system_deadline_exit_method_raises_handler_cleanup_error_after_successful_block() -> None:
    """
    Test SystemDeadline context manager raises a handler cleanup error after a successful block.
    """
    deadline = SystemDeadline(seconds=1, monotonic_clock=MockMonotonicClock())

    with (
        _mock_signal_timeout() as (_, _, signal_mock, _),
        assert_raises(
            expected_exception=OSError,
            match=r'handler cleanup failed',
        ),
    ):
        signal_mock.side_effect = [None, OSError('handler cleanup failed')]
        with deadline:
            pass


@mark.unit_testing
def test_system_deadline_seconds_invalid_type() -> None:
    """
    Test SystemDeadline raises TypeError if seconds has invalid type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'SystemDeadline seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
    ):
        SystemDeadline(seconds=FloatMother.invalid_type(), monotonic_clock=MockMonotonicClock())


@mark.unit_testing
def test_system_deadline_seconds_negative_random_value() -> None:
    """
    Test SystemDeadline raises ValueError if seconds is random negative.
    """
    seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=rf'SystemDeadline seconds <<<{seconds}>>> must be greater than or equal to zero.',
    ):
        SystemDeadline(seconds=seconds, monotonic_clock=MockMonotonicClock())


@mark.unit_testing
def test_system_deadline_seconds_negative_limit_value() -> None:
    """
    Test SystemDeadline raises ValueError if seconds is negative limit.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'SystemDeadline seconds <<<-1.0>>> must be greater than or equal to zero.',
    ):
        SystemDeadline(seconds=-1.0, monotonic_clock=MockMonotonicClock())


@mark.unit_testing
def test_system_deadline_seconds_non_finite_value() -> None:
    """
    Test SystemDeadline raises ValueError if seconds is non-finite.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'SystemDeadline seconds <<<inf>>> must be finite and representable as a float.',
    ):
        SystemDeadline(seconds=float('inf'), monotonic_clock=MockMonotonicClock())


@mark.unit_testing
def test_system_deadline_seconds_zero_value() -> None:
    """
    Test SystemDeadline accepts zero seconds.
    """
    deadline = SystemDeadline(seconds=0, monotonic_clock=MockMonotonicClock())

    assert deadline.expired is True


@mark.unit_testing
def test_system_deadline_seconds_positive_random_value() -> None:
    """
    Test SystemDeadline accepts random positive seconds.
    """
    seconds = FloatMother.positive()
    deadline = SystemDeadline(seconds=seconds, monotonic_clock=MockMonotonicClock())

    assert deadline.remaining_seconds == seconds
