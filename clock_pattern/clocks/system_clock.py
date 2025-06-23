"""
SystemClock module.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from datetime import UTC, date, datetime, tzinfo
from zoneinfo import ZoneInfo

from value_object_pattern.usables.dates import StringTimezoneValueObject, TimezoneValueObject

from clock_pattern.models.clock import Clock


class SystemClock(Clock):
    """
    SystemClock class is responsible of retrieving the current date/datetime with the provided timezone.

    Example:
    ```python
    from clock_pattern import SystemClock

    clock = SystemClock()
    print(clock.now())
    # >>> 2025-06-16 13:57:26.210964+00:00
    ```
    """

    _timezone: tzinfo

    def __init__(self, *, timezone: str | tzinfo = UTC) -> None:
        """
        SystemClock constructor is responsible to store which `timezone` the user wants to use when retrieving the
        current date/datetime.

        Args:
            timezone: (str | tzinfo, optional): Timezone of the date/datetime to retrieve. Default to UTC.

        Raises:
            TypeError: If `timezone` is not of type tzinfo.
            TypeError: If `timezone` is not of type string.
            ValueError: If `timezone` is not a valid timezone.

        Example:
        ```python
        from clock_pattern import SystemClock

        clock = SystemClock()
        print(clock.now())
        # >>> 2025-06-16 13:57:26.210964+00:00
        ```
        """
        if isinstance(timezone, tzinfo):
            timezone = str(TimezoneValueObject(value=timezone, title='SystemClock', parameter='timezone'))

        StringTimezoneValueObject(value=timezone, title='SystemClock', parameter='timezone')

        self._timezone = ZoneInfo(timezone)

    @override
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
        return datetime.now(tz=self._timezone)

    @override
    def today(self) -> date:
        """
        Retrieve the current date (today).

        Returns:
            date: The current date.

        Example:
        ```python
        from clock_pattern import SystemClock

        clock = SystemClock()
        print(clock.now())
        # >>> 2025-06-16
        ```
        """
        return datetime.now(tz=self._timezone).date()

    @property
    def timezone(self) -> tzinfo:
        """
        Retrieve the timezone of the clock.

        Returns:
            tzinfo: The timezone of the clock.

        Example:
        ```python
        from clock_pattern import SystemClock

        clock = SystemClock()
        print(clock.timezone)
        # >>> UTC
        ```
        """
        return self._timezone
