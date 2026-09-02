"""
Abstract asynchronous poller contract.
"""

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable


class PollerAsync(ABC):
    """
    Define the interface for asynchronous condition polling.

    Example:
    ```python
    from clock_pattern import SystemMonotonicClock, SystemPollerAsync, SystemSleeperAsync
    from clock_pattern.pollers.models import PollerAsync


    class CacheWaiter:
        def __init__(self, *, poller: PollerAsync) -> None:
            self._poller = poller

        async def wait(self) -> None:
            await self._poller.poll_until(condition=lambda: True, timeout_seconds=1)


    monotonic_clock = SystemMonotonicClock()
    sleeper = SystemSleeperAsync(monotonic_clock=monotonic_clock)
    await CacheWaiter(poller=SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock)).wait()
    ```
    """

    @abstractmethod
    async def poll_until(
        self,
        *,
        condition: Callable[[], bool | Awaitable[bool]],
        timeout_seconds: float,
        interval_seconds: float = 0.1,
    ) -> None:
        """
        Poll a condition until it succeeds or the timeout expires.

        Args:
            condition (Callable[[], bool | Awaitable[bool]]): Sync or async condition checked until it succeeds.
            timeout_seconds (float): Maximum duration to wait.
            interval_seconds (float, optional): Duration between condition checks. Defaults to 0.1 seconds.

        Example:
        ```python
        from clock_pattern import SystemMonotonicClock, SystemPollerAsync, SystemSleeperAsync
        from clock_pattern.pollers.models import PollerAsync


        async def wait_until_ready(*, poller: PollerAsync) -> None:
            await poller.poll_until(condition=lambda: True, timeout_seconds=1)


        monotonic_clock = SystemMonotonicClock()
        sleeper = SystemSleeperAsync(monotonic_clock=monotonic_clock)
        await wait_until_ready(poller=SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock))
        ```
        """
