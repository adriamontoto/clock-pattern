"""
System-backed synchronous polling helper.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from collections.abc import Callable

from value_object_pattern.usables import BooleanValueObject, PositiveNumberValueObject, PositiveOrZeroNumberValueObject

from clock_pattern.deadlines import SystemDeadline
from clock_pattern.monotonic_clocks.models import MonotonicClock
from clock_pattern.pollers.models import Poller
from clock_pattern.sleepers.models import Sleeper


class SystemPoller(Poller):
    """
    Poll a synchronous condition until it succeeds or a timeout expires.

    Example:
    ```python
    from clock_pattern import SystemMonotonicClock, SystemPoller, SystemSleeper

    monotonic_clock = SystemMonotonicClock()
    sleeper = SystemSleeper(monotonic_clock=monotonic_clock)
    poller = SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock)
    poller.poll_until(condition=lambda: True, timeout_seconds=1)
    ```
    """

    _sleeper: Sleeper
    _monotonic_clock: MonotonicClock

    def __init__(self, *, sleeper: Sleeper, monotonic_clock: MonotonicClock) -> None:
        """
        Create a synchronous poller.

        Args:
            sleeper (Sleeper): Sleeper used between condition checks.
            monotonic_clock (MonotonicClock): Monotonic clock used for timeout measurement.

        Example:
        ```python
        from clock_pattern import SystemMonotonicClock, SystemPoller, SystemSleeper

        monotonic_clock = SystemMonotonicClock()
        sleeper = SystemSleeper(monotonic_clock=monotonic_clock)
        poller = SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock)
        poller.poll_until(condition=lambda: True, timeout_seconds=1)
        ```
        """
        self._monotonic_clock = monotonic_clock
        self._sleeper = sleeper

    @override
    def poll_until(
        self,
        *,
        condition: Callable[[], bool],
        timeout_seconds: float,
        interval_seconds: float = 0.1,
    ) -> None:
        """
        Poll `condition` until it returns `True`.

        Args:
            condition (Callable[[], bool]): Condition checked until it returns `True`.
            timeout_seconds (float): Maximum duration to wait.
            interval_seconds (float): Duration between condition checks. Defaults to `0.1`.

        Raises:
            TypeError: If `timeout_seconds` is not an integer or a float.
            ValueError: If `timeout_seconds` is negative.
            TypeError: If `interval_seconds` is not an integer or a float.
            ValueError: If `interval_seconds` is not positive.
            TypeError: If `condition` does not return a boolean.
            TimeoutExpiredError: If the timeout expires before `condition` returns `True`.

        Example:
        ```python
        from clock_pattern import SystemMonotonicClock, SystemPoller, SystemSleeper

        monotonic_clock = SystemMonotonicClock()
        sleeper = SystemSleeper(monotonic_clock=monotonic_clock)
        SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
            condition=lambda: True,
            timeout_seconds=1,
            interval_seconds=0.1,
        )
        ```
        """
        PositiveOrZeroNumberValueObject(value=timeout_seconds, title='SystemPoller', parameter='timeout_seconds')
        PositiveNumberValueObject(value=interval_seconds, title='SystemPoller', parameter='interval_seconds')

        deadline = SystemDeadline(seconds=timeout_seconds, monotonic_clock=self._monotonic_clock)
        while True:
            condition_result = BooleanValueObject(value=condition(), title='SystemPoller', parameter='condition').value
            if condition_result:
                return

            deadline.raise_if_expired()
            self._sleeper.sleep(seconds=min(interval_seconds, deadline.remaining_seconds))
