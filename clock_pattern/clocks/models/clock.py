"""
Abstract clock contract for injectable wall-clock time sources.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime


class Clock(ABC):
    """
    Define the interface for objects that provide the current datetime and date.

    Example:
    ```python
    from clock_pattern import UtcClock
    from clock_pattern.clocks.models import Clock


    class TimestampService:
        def __init__(self, *, clock: Clock) -> None:
            self._clock = clock

        def issued_at(self) -> str:
            return self._clock.now().isoformat()


    service = TimestampService(clock=UtcClock())
    print(service.issued_at())
    ```
    """

    @abstractmethod
    def now(self) -> datetime:
        """
        Retrieve the current datetime from the clock implementation.

        Returns:
            datetime: The datetime produced by the concrete clock.

        Example:
        ```python
        from clock_pattern import UtcClock

        clock = UtcClock()
        print(clock.now())
        # >>> 2025-06-16 13:57:26.210964+00:00
        ```
        """

    @abstractmethod
    def today(self) -> date:
        """
        Retrieve the current date from the clock implementation.

        Returns:
            date: The date produced by the concrete clock.

        Example:
        ```python
        from clock_pattern import UtcClock

        clock = UtcClock()
        print(clock.today())
        # >>> 2025-06-16
        ```
        """
