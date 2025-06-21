"""
UtcClock module.
"""

from datetime import UTC

from .system_clock import SystemClock


class UtcClock(SystemClock):
    """
    UtcClock class is responsible of retrieving the current UTC date/datetime.

    Example:
    ```python
    from clock_pattern.clocks import UtcClock

    clock = UtcClock()
    print(clock.now())
    # >>> 2025-06-16 13:57:26.210964+00:00
    ```
    """

    def __init__(self) -> None:
        """
        UtcClock constructor.

        Example:
        ```python
        from clock_pattern.clocks import UtcClock

        clock = UtcClock()
        print(clock.now())
        # >>> 2025-06-16 13:57:26.210964+00:00
        ```
        """
        super().__init__(timezone=UTC)
