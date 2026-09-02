"""
Abstract synchronous poller contract.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable


class Poller(ABC):
    """
    Define the interface for synchronous condition polling.

    Example:
    ```python
    from clock_pattern import SystemMonotonicClock, SystemPoller, SystemSleeper
    from clock_pattern.pollers.models import Poller


    class CacheWaiter:
        def __init__(self, *, poller: Poller) -> None:
            self._poller = poller

        def wait(self) -> None:
            self._poller.poll_until(condition=lambda: True, timeout_seconds=1)


    monotonic_clock = SystemMonotonicClock()
    sleeper = SystemSleeper(monotonic_clock=monotonic_clock)
    CacheWaiter(poller=SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock)).wait()
    ```
    """

    @abstractmethod
    def poll_until(
        self,
        *,
        condition: Callable[[], bool],
        timeout_seconds: int | float,
        interval_seconds: int | float = 0.1,
    ) -> None:
        """
        Poll a condition until it succeeds or the timeout expires.

        Args:
            condition (Callable[[], bool]): Condition checked until it returns `True`.
            timeout_seconds (int | float): Maximum duration to wait.
            interval_seconds (int | float, optional): Duration between condition checks. Defaults to 0.1 seconds.

        Example:
        ```python
        from clock_pattern import SystemMonotonicClock, SystemPoller, SystemSleeper
        from clock_pattern.pollers.models import Poller


        def wait_until_ready(*, poller: Poller) -> None:
            poller.poll_until(condition=lambda: True, timeout_seconds=1)


        monotonic_clock = SystemMonotonicClock()
        sleeper = SystemSleeper(monotonic_clock=monotonic_clock)
        wait_until_ready(poller=SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock))
        ```
        """
