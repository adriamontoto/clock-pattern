"""
Elapsed-time stopwatch helper.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import Self, override  # pragma: no cover
else:
    from typing_extensions import Self, override  # pragma: no cover

from contextlib import AbstractContextManager
from types import TracebackType

from clock_pattern.monotonic_clocks.models import MonotonicClock


class Stopwatch(AbstractContextManager['Stopwatch']):
    """
    Measure elapsed seconds with an injectable monotonic clock.

    Example:
    ```python
    from clock_pattern import Stopwatch
    from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

    monotonic_clock = MockMonotonicClock()
    stopwatch = Stopwatch(monotonic_clock=monotonic_clock)

    with stopwatch:
        monotonic_clock.advance(seconds=1)

    print(stopwatch.elapsed_seconds)
    # >>> 1.0
    ```
    """

    _monotonic_clock: MonotonicClock
    _started_at: float | None
    _ended_at: float | None

    def __init__(self, *, monotonic_clock: MonotonicClock) -> None:
        """
        Create a stopwatch.

        Args:
            monotonic_clock (MonotonicClock): Monotonic clock used to measure elapsed seconds.

        Example:
        ```python
        from clock_pattern import Stopwatch
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        stopwatch = Stopwatch(monotonic_clock=MockMonotonicClock())
        print(stopwatch.elapsed_seconds)
        # >>> 0.0
        ```
        """
        self._monotonic_clock = monotonic_clock
        self._started_at = None
        self._ended_at = None

    def start(self) -> Self:
        """
        Start the stopwatch.

        Raises:
            RuntimeError: If the stopwatch is already running.

        Returns:
            Self: This stopwatch instance.

        Example:
        ```python
        from clock_pattern import Stopwatch
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        stopwatch = Stopwatch(monotonic_clock=MockMonotonicClock())
        stopwatch.start()
        print(stopwatch.is_running)
        # >>> True
        ```
        """
        if self._started_at is not None and self._ended_at is None:
            raise RuntimeError('Stopwatch is already running.')

        self._started_at = self._monotonic_clock.current_seconds()
        self._ended_at = None

        return self

    def end(self) -> float:
        """
        Stop the stopwatch and return elapsed seconds.

        Raises:
            RuntimeError: If the stopwatch has not started or has already ended.

        Returns:
            float: Elapsed seconds between `start()` and `end()`.

        Example:
        ```python
        from clock_pattern import Stopwatch
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        stopwatch = Stopwatch(monotonic_clock=monotonic_clock).start()
        monotonic_clock.advance(seconds=1)
        print(stopwatch.end())
        # >>> 1.0
        ```
        """
        if self._started_at is None:
            raise RuntimeError('Stopwatch has not been started.')

        if self._ended_at is not None:
            raise RuntimeError('Stopwatch has already ended.')

        self._ended_at = self._monotonic_clock.current_seconds()

        return self.elapsed_seconds

    @property
    def elapsed_seconds(self) -> float:
        """
        Retrieve elapsed seconds.

        Returns:
            float: Elapsed seconds, or zero when the stopwatch has not started.

        Example:
        ```python
        from clock_pattern import Stopwatch
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        stopwatch = Stopwatch(monotonic_clock=monotonic_clock).start()
        monotonic_clock.advance(seconds=0.5)
        print(stopwatch.elapsed_seconds)
        # >>> 0.5
        ```
        """
        if self._started_at is None:
            return 0.0

        current_seconds = self._ended_at if self._ended_at is not None else self._monotonic_clock.current_seconds()

        return current_seconds - self._started_at

    @property
    def is_running(self) -> bool:
        """
        Check whether the stopwatch has started and not ended.

        Returns:
            bool: `True` when the stopwatch is currently running.

        Example:
        ```python
        from clock_pattern import Stopwatch
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        stopwatch = Stopwatch(monotonic_clock=MockMonotonicClock()).start()
        print(stopwatch.is_running)
        # >>> True
        ```
        """
        return self._started_at is not None and self._ended_at is None

    @override
    def __enter__(self) -> Self:
        """
        Start the stopwatch when entering a context manager.

        Returns:
            Self: This stopwatch instance after `start()`.

        Example:
        ```python
        from clock_pattern import Stopwatch
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        with Stopwatch(monotonic_clock=MockMonotonicClock()) as stopwatch:
            print(stopwatch.is_running)
        # >>> True
        ```
        """
        return self.start()

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """
        End the stopwatch when leaving a context manager.

        Args:
            exc_type: Exception type raised by the managed block, if any.
            exc_value: Exception raised by the managed block, if any.
            traceback: Traceback raised by the managed block, if any.

        Returns:
            bool | None: `None`, so exceptions from the managed block are not suppressed.

        Example:
        ```python
        from clock_pattern import Stopwatch
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        with Stopwatch(monotonic_clock=monotonic_clock) as stopwatch:
            monotonic_clock.advance(seconds=1)

        print(stopwatch.elapsed_seconds)
        # >>> 1.0
        ```
        """
        if self.is_running:
            self.end()

        return None
