"""
System monotonic clock implementation.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from time import monotonic

from clock_pattern.monotonic_clocks.models import MonotonicClock


class SystemMonotonicClock(MonotonicClock):
    """
    Return monotonically increasing seconds from the operating system.

    Example:
    ```python
    from clock_pattern import SystemMonotonicClock

    monotonic_clock = SystemMonotonicClock()
    print(monotonic_clock.current_seconds())
    # >>> 1512340.134454
    ```
    """

    @override
    def current_seconds(self) -> float:
        """
        Retrieve the current monotonic timestamp in seconds.

        Returns:
            float: Current monotonic timestamp in seconds.

        Example:
        ```python
        from clock_pattern import SystemMonotonicClock

        monotonic_clock = SystemMonotonicClock()
        print(monotonic_clock.current_seconds())
        # >>> 1512340.134454
        ```
        """
        return monotonic()
