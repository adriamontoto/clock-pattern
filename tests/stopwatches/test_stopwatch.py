"""
Test Stopwatch stopwatch.
"""

from pytest import mark, raises as assert_raises

from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.stopwatches import Stopwatch


@mark.unit_testing
def test_stopwatch_happy_path() -> None:
    """
    Test Stopwatch stopwatch happy path.
    """
    monotonic_clock = MockMonotonicClock()
    stopwatch = Stopwatch(monotonic_clock=monotonic_clock)

    stopwatch.start()
    monotonic_clock.advance(seconds=1)
    elapsed_seconds = stopwatch.end()

    assert elapsed_seconds == 1.0
    assert stopwatch.elapsed_seconds == 1.0
    assert stopwatch.is_running is False


@mark.unit_testing
def test_stopwatch_elapsed_seconds_property_returns_zero_when_not_started() -> None:
    """
    Test Stopwatch elapsed_seconds property returns zero when not started.
    """
    assert Stopwatch(monotonic_clock=MockMonotonicClock()).elapsed_seconds == 0.0


@mark.unit_testing
def test_stopwatch_elapsed_seconds_property_uses_current_seconds_while_running() -> None:
    """
    Test Stopwatch elapsed_seconds property uses current seconds while running.
    """
    monotonic_clock = MockMonotonicClock()
    stopwatch = Stopwatch(monotonic_clock=monotonic_clock).start()

    monotonic_clock.advance(seconds=0.5)

    assert stopwatch.elapsed_seconds == 0.5


@mark.unit_testing
def test_stopwatch_elapsed_seconds_property_stays_fixed_after_end() -> None:
    """
    Test Stopwatch elapsed_seconds property stays fixed after end.
    """
    monotonic_clock = MockMonotonicClock()
    stopwatch = Stopwatch(monotonic_clock=monotonic_clock).start()
    monotonic_clock.advance(seconds=0.5)
    stopwatch.end()

    monotonic_clock.advance(seconds=1)

    assert stopwatch.elapsed_seconds == 0.5


@mark.unit_testing
def test_stopwatch_is_running_property_returns_true_when_started_and_not_ended() -> None:
    """
    Test Stopwatch is_running property returns true when started and not ended.
    """
    stopwatch = Stopwatch(monotonic_clock=MockMonotonicClock()).start()

    assert stopwatch.is_running is True


@mark.unit_testing
def test_stopwatch_start_method_returns_self() -> None:
    """
    Test Stopwatch start method returns self.
    """
    stopwatch = Stopwatch(monotonic_clock=MockMonotonicClock())

    assert stopwatch.start() is stopwatch


@mark.unit_testing
def test_stopwatch_start_method_raises_runtime_error_when_already_running() -> None:
    """
    Test Stopwatch start method raises RuntimeError when already running.
    """
    stopwatch = Stopwatch(monotonic_clock=MockMonotonicClock()).start()

    with assert_raises(expected_exception=RuntimeError, match=r'Stopwatch is already running.'):
        stopwatch.start()


@mark.unit_testing
def test_stopwatch_start_method_restarts_after_end() -> None:
    """
    Test Stopwatch start method restarts after end.
    """
    monotonic_clock = MockMonotonicClock()
    stopwatch = Stopwatch(monotonic_clock=monotonic_clock).start()
    monotonic_clock.advance(seconds=1)
    stopwatch.end()

    stopwatch.start()
    monotonic_clock.advance(seconds=2)

    assert stopwatch.end() == 2.0


@mark.unit_testing
def test_stopwatch_end_method_raises_runtime_error_when_not_started() -> None:
    """
    Test Stopwatch end method raises RuntimeError when not started.
    """
    with assert_raises(expected_exception=RuntimeError, match=r'Stopwatch has not been started.'):
        Stopwatch(monotonic_clock=MockMonotonicClock()).end()


@mark.unit_testing
def test_stopwatch_end_method_raises_runtime_error_when_already_ended() -> None:
    """
    Test Stopwatch end method raises RuntimeError when already ended.
    """
    stopwatch = Stopwatch(monotonic_clock=MockMonotonicClock()).start()
    stopwatch.end()

    with assert_raises(expected_exception=RuntimeError, match=r'Stopwatch has already ended.'):
        stopwatch.end()


@mark.unit_testing
def test_stopwatch_context_manager_happy_path() -> None:
    """
    Test Stopwatch context manager happy path.
    """
    monotonic_clock = MockMonotonicClock()

    with Stopwatch(monotonic_clock=monotonic_clock) as stopwatch:
        monotonic_clock.advance(seconds=1)

    assert stopwatch.elapsed_seconds == 1.0
    assert stopwatch.is_running is False


@mark.unit_testing
def test_stopwatch_exit_method_does_not_end_when_not_running() -> None:
    """
    Test Stopwatch exit method does not end when not running.
    """
    stopwatch = Stopwatch(monotonic_clock=MockMonotonicClock())

    assert stopwatch.__exit__(None, None, None) is None
    assert stopwatch.elapsed_seconds == 0.0
