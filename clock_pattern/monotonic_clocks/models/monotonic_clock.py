"""
Abstract monotonic clock contract for injectable elapsed-time sources.
"""

from abc import ABC, abstractmethod


class MonotonicClock(ABC):
    """
    Define the interface for objects that provide seconds that never decrease.

    Example:
    ```python
    from clock_pattern import SystemMonotonicClock
    from clock_pattern.monotonic_clocks.models import MonotonicClock


    def current_elapsed_marker(*, monotonic_clock: MonotonicClock) -> float:
        return monotonic_clock.current_seconds()


    print(current_elapsed_marker(monotonic_clock=SystemMonotonicClock()))
    # >>> 1512340.134454
    ```
    """

    @abstractmethod
    def current_seconds(self) -> float:
        """
        Retrieve the current monotonic timestamp in seconds.

        Returns:
            float: The monotonic timestamp produced by the concrete clock.

        Example:
        ```python
        from clock_pattern import SystemMonotonicClock
        from clock_pattern.monotonic_clocks.models import MonotonicClock


        def current_elapsed_marker(*, monotonic_clock: MonotonicClock) -> float:
            return monotonic_clock.current_seconds()


        print(current_elapsed_marker(monotonic_clock=SystemMonotonicClock()))
        # >>> 1512340.134454
        ```
        """
