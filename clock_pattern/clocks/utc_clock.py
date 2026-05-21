"""
UTC production clock implementation.
"""

from datetime import UTC

from .system_clock import SystemClock


class UtcClock(SystemClock):
    """
    Return the current system datetime and date in UTC.

    `UtcClock` is a convenience specialization of `SystemClock` for applications that standardize persistence,
    messaging, logging, or domain timestamps on UTC.

    Example:
    ```python
    from clock_pattern import UtcClock

    clock = UtcClock()
    print(clock.now())
    # >>> 2025-06-16 13:57:26.210964+00:00
    ```
    """

    def __init__(self) -> None:
        """
        Create a system-backed clock fixed to UTC.

        Example:
        ```python
        from clock_pattern import UtcClock

        clock = UtcClock()
        print(clock.now())
        # >>> 2025-06-16 13:57:26.210964+00:00
        ```
        """
        super().__init__(timezone=UTC)
