"""
Clock module.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime


class Clock(ABC):
    """
    Clock class.

    ***This class is abstract and should not be instantiated directly***.

    Example:
    ```python
    from clock_pattern import SystemClock

    clock = SystemClock()
    print(clock.now())
    # >>> 2025-06-16 13:57:26.210964+00:00
    ```
    """

    @abstractmethod
    def now(self) -> datetime:
        """
        Retrieve the current datetime (now).

        Returns:
            datetime: The current datetime.

        Example:
        ```python
        from clock_pattern import SystemClock

        clock = SystemClock()
        print(clock.now())
        # >>> 2025-06-16 13:57:26.210964+00:00
        ```
        """

    @abstractmethod
    def today(self) -> date:
        """
        Retrieve the current date (today).

        Returns:
            date: The current date.

        Example:
        ```python
        from clock_pattern import SystemClock

        clock = SystemClock()
        print(clock.today())
        # >>> 2025-06-16
        ```
        """
