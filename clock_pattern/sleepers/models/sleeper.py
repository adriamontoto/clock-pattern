"""
Abstract synchronous sleeper contract.
"""

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager


class Sleeper(ABC):
    """
    Define the interface for objects that can pause synchronous execution.

    Example:
    ```python
    from clock_pattern import SystemSleeper
    from clock_pattern.monotonic_clocks import SystemMonotonicClock

    sleeper = SystemSleeper(monotonic_clock=SystemMonotonicClock())
    sleeper.sleep(seconds=1)
    ```
    """

    @abstractmethod
    def sleep(self, *, seconds: float) -> None:
        """
        Pause synchronous execution for `seconds`.

        Args:
            seconds (float): The number of seconds to pause execution.

        Example:
        ```python
        from clock_pattern import SystemSleeper
        from clock_pattern.monotonic_clocks import SystemMonotonicClock

        sleeper = SystemSleeper(monotonic_clock=SystemMonotonicClock())
        sleeper.sleep(seconds=1)
        ```
        """

    @abstractmethod
    def minimum_duration(self, *, seconds: float) -> AbstractContextManager[None]:
        """
        Create a context manager that ensures the enclosed work takes at least `seconds`.

        Args:
            seconds (float): The minimum duration the enclosed work should take.

        Returns:
            AbstractContextManager[None]: A context manager that enforces the minimum duration.

        Example:
        ```python
        from clock_pattern import SystemSleeper
        from clock_pattern.monotonic_clocks import SystemMonotonicClock

        sleeper = SystemSleeper(monotonic_clock=SystemMonotonicClock())

        with sleeper.minimum_duration(seconds=1):
            pass
        ```
        """
