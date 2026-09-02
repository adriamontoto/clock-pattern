"""
System-backed deadline implementation.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import Self, override  # pragma: no cover
else:
    from typing_extensions import Self, override  # pragma: no cover

import signal as signal_module
from threading import current_thread, main_thread
from types import FrameType, TracebackType
from typing import NoReturn

from value_object_pattern.usables import PositiveOrZeroNumberValueObject

from clock_pattern.deadlines.errors import TimeoutExpiredError
from clock_pattern.deadlines.models import Deadline
from clock_pattern.monotonic_clocks import MonotonicClock

_SIGNAL_TIMEOUT_SUPPORTED = all(
    hasattr(signal_module, name) for name in ('SIGALRM', 'ITIMER_REAL', 'getitimer', 'setitimer')
)


class SystemDeadline(Deadline):
    """
    Expose monotonic deadline state and enforce Unix main-thread context timeouts.

    Example:
    ```python
    from clock_pattern import SystemDeadline, SystemMonotonicClock

    with SystemDeadline(seconds=1, monotonic_clock=SystemMonotonicClock()) as deadline:
        print(deadline.remaining_seconds)
    ```
    """

    _monotonic_clock: MonotonicClock
    _seconds: PositiveOrZeroNumberValueObject
    _started_at: float
    _entered: bool
    _previous_signal_handler: signal_module.Handlers
    _previous_timer: tuple[float, float]

    def __init__(self, *, seconds: float, monotonic_clock: MonotonicClock) -> None:
        """
        Create a system deadline that starts immediately.

        Args:
            seconds (float): Duration before the deadline expires.
            monotonic_clock (MonotonicClock): Monotonic clock used to measure elapsed seconds.

        Raises:
            TypeError: If `seconds` is not an integer or float.
            ValueError: If `seconds` is negative or non-finite.

        Example:
        ```python
        from clock_pattern import SystemDeadline
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)
        print(deadline.remaining_seconds)
        # >>> 1.0
        ```
        """
        self._monotonic_clock = monotonic_clock
        self._seconds = PositiveOrZeroNumberValueObject(value=seconds, title='SystemDeadline', parameter='seconds')
        self._started_at = self._monotonic_clock.current_seconds()
        self._entered = False
        self._previous_signal_handler = signal_module.SIG_DFL
        self._previous_timer = (0.0, 0.0)

    @property
    @override
    def elapsed_seconds(self) -> float:
        """
        Retrieve elapsed seconds since this deadline started.

        Returns:
            float: Elapsed seconds since creation.

        Example:
        ```python
        from clock_pattern import SystemDeadline
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)
        monotonic_clock.advance(seconds=0.25)
        print(deadline.elapsed_seconds)
        # >>> 0.25
        ```
        """
        return self._monotonic_clock.current_seconds() - self._started_at

    @property
    @override
    def remaining_seconds(self) -> float:
        """
        Retrieve remaining seconds before expiry.

        Returns:
            float: Remaining seconds, never less than zero.

        Example:
        ```python
        from clock_pattern import SystemDeadline
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)
        monotonic_clock.advance(seconds=0.25)
        print(deadline.remaining_seconds)
        # >>> 0.75
        ```
        """
        return max(0.0, self._seconds.value - self.elapsed_seconds)

    @property
    @override
    def expired(self) -> bool:
        """
        Check whether the deadline has expired.

        Returns:
            bool: `True` when elapsed seconds are greater than or equal to the configured duration.

        Example:
        ```python
        from clock_pattern import SystemDeadline
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)
        monotonic_clock.advance(seconds=1)
        print(deadline.expired)
        # >>> True
        ```
        """
        return self.elapsed_seconds >= self._seconds.value

    @override
    def raise_if_expired(self) -> None:
        """
        Raise if this deadline expired.

        Raises:
            TimeoutExpiredError: If the configured duration elapsed.

        Example:
        ```python
        from clock_pattern import SystemDeadline
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)
        monotonic_clock.advance(seconds=1)
        deadline.raise_if_expired()
        ```
        """
        elapsed_seconds = self.elapsed_seconds
        if elapsed_seconds >= self._seconds.value:
            self._raise_timeout_expired_error(elapsed_seconds=elapsed_seconds)

    @override
    def __enter__(self) -> Self:
        """
        Arm a Unix main-thread timeout and return this deadline.

        Raises:
            RuntimeError: If the context manager is entered more than once.
            RuntimeError: If the context manager is not entered from the main thread of the main interpreter.
            RuntimeError: If the context manager is used on a platform without Unix SIGALRM support.
            RuntimeError: If the context manager is used when a SIGALRM handler or timer is already configured.
            TimeoutExpiredError: If the deadline already expired.

        Returns:
            Self: This deadline instance.

        Example:
        ```python
        from clock_pattern import SystemDeadline, SystemMonotonicClock

        with SystemDeadline(seconds=1, monotonic_clock=SystemMonotonicClock()) as deadline:
            print(deadline.remaining_seconds)
        ```
        """
        if self._entered:
            raise RuntimeError('SystemDeadline context manager cannot be entered more than once.')

        if current_thread() is not main_thread():
            raise RuntimeError('SystemDeadline context manager requires the main thread of the main interpreter.')

        if not _SIGNAL_TIMEOUT_SUPPORTED:
            raise RuntimeError('SystemDeadline context manager requires Unix SIGALRM support.')

        self.raise_if_expired()

        previous_signal_handler = signal_module.getsignal(signal_module.SIGALRM)
        previous_timer = signal_module.getitimer(signal_module.ITIMER_REAL)
        if previous_signal_handler != signal_module.SIG_DFL or previous_timer != (0.0, 0.0):
            raise RuntimeError('SystemDeadline context manager cannot replace an existing SIGALRM handler or timer.')

        self._previous_signal_handler = previous_signal_handler  # type: ignore[ty:invalid-assignment]
        self._previous_timer = previous_timer
        try:
            signal_module.signal(signal_module.SIGALRM, self._handle_timeout)

        except ValueError as error:
            raise RuntimeError('SystemDeadline context manager requires the main thread of the main interpreter.') from error  # noqa: E501  # fmt: skip

        elapsed_seconds = self.elapsed_seconds
        remaining_seconds = max(0.0, self._seconds.value - elapsed_seconds)
        if remaining_seconds == 0.0:
            signal_module.signal(signal_module.SIGALRM, self._previous_signal_handler)
            self._raise_timeout_expired_error(elapsed_seconds=elapsed_seconds)

        try:
            signal_module.setitimer(signal_module.ITIMER_REAL, remaining_seconds)

        except BaseException:
            signal_module.signal(signal_module.SIGALRM, self._previous_signal_handler)
            raise

        self._entered = True
        return self

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """
        Disarm the timeout, restore signal state, and propagate expiry or body errors.

        Args:
            exc_type (type[BaseException] | None): Exception type raised by the managed block, if any.
            exc_value (BaseException | None): Exception raised by the managed block, if any.
            traceback (TracebackType | None): Traceback raised by the managed block, if any.

        Raises:
            TimeoutExpiredError: If the managed block completed after the deadline.

        Returns:
            bool | None: `None`, so exceptions from the managed block are not suppressed.

        Example:
        ```python
        from clock_pattern import SystemDeadline, SystemMonotonicClock

        with SystemDeadline(seconds=1, monotonic_clock=SystemMonotonicClock()) as deadline:
            print(deadline.remaining_seconds)
        ```
        """
        cleanup_error = self._restore_signal_state()
        if cleanup_error is not None:
            if exc_value is None:
                raise cleanup_error

            exc_value.add_note(f'SystemDeadline signal cleanup failed: {cleanup_error!r}')

        if exc_value is None:
            self.raise_if_expired()

        return None

    def _handle_timeout(self, _signal_number: int, _frame: FrameType | None) -> None:
        """
        Raise a `TimeoutExpiredError` when the Unix SIGALRM signal is received.

        Args:
            _signal_number (int): Signal number received.
            _frame (FrameType | None): Current stack frame (ignored).

        Raises:
            TimeoutExpiredError: Always raised when the signal is received.
        """
        self._raise_timeout_expired_error(elapsed_seconds=self.elapsed_seconds)

    def _raise_timeout_expired_error(self, *, elapsed_seconds: float) -> NoReturn:
        """
        Raise a `TimeoutExpiredError` with the measured elapsed duration.

        Args:
            elapsed_seconds (float): Measured elapsed seconds when expiry was observed.

        Raises:
            TimeoutExpiredError: Always raised with the measured elapsed duration.
        """
        raise TimeoutExpiredError(elapsed_seconds=elapsed_seconds)

    def _restore_signal_state(self) -> BaseException | None:
        """
        Restore the previous SIGALRM signal handler and timer.

        Returns:
            BaseException | None: Any exception raised during cleanup, or `None` if cleanup succeeded.
        """
        try:
            signal_module.setitimer(signal_module.ITIMER_REAL, *self._previous_timer)

        except BaseException as error:
            return error

        try:
            signal_module.signal(signal_module.SIGALRM, self._previous_signal_handler)

        except BaseException as error:
            return error

        return None
