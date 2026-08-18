"""
Abstract asynchronous sleeper contract.
"""

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager


class SleeperAsync(ABC):
    """
    Define the interface for objects that can pause asynchronous execution.

    Example:
    ```python
    from clock_pattern import SystemSleeperAsync
    from clock_pattern.monotonic_clocks import SystemMonotonicClock

    sleeper = SystemSleeperAsync(monotonic_clock=SystemMonotonicClock())
    await sleeper.sleep(seconds=1)
    ```
    """

    @abstractmethod
    async def sleep(self, *, seconds: int | float) -> None:
        """
        Pause asynchronous execution for `seconds`.

        Args:
            seconds (int | float): The number of seconds to pause execution.

        Example:
        ```python
        from clock_pattern import SystemSleeperAsync
        from clock_pattern.monotonic_clocks import SystemMonotonicClock

        sleeper = SystemSleeperAsync(monotonic_clock=SystemMonotonicClock())
        await sleeper.sleep(seconds=0.1)
        ```
        """

    @abstractmethod
    def minimum_duration(self, *, seconds: int | float) -> AbstractAsyncContextManager[None]:
        """
        Create an async context manager that ensures the enclosed work takes at least `seconds`.

        Args:
            seconds (int | float): The minimum duration the enclosed work should take.

        Returns:
            AbstractAsyncContextManager[None]: An async context manager that enforces the minimum duration.

        Example:
        ```python
        from clock_pattern import SystemSleeperAsync
        from clock_pattern.monotonic_clocks import SystemMonotonicClock

        sleeper = SystemSleeperAsync(monotonic_clock=SystemMonotonicClock())

        async with sleeper.minimum_duration(seconds=1):
            pass
        ```
        """
