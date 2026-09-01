"""
Timezone-aware clock backed by the operating system time.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from datetime import UTC, date, datetime, tzinfo
from zoneinfo import ZoneInfo

from clock_pattern.clocks.models import Clock
from value_object_pattern.usables.dates import StringTimezoneValueObject, TimezoneValueObject


class SystemClock(Clock):
    """
    Return the current system datetime and date in a configured timezone.

    `SystemClock` is the general-purpose production clock. It accepts either an IANA timezone string supported by
    `zoneinfo.ZoneInfo` or a `tzinfo` instance. The default timezone is UTC, so datetimes are timezone-aware unless the
    provided timezone object has different behavior.

    Example:
    ```python
    from clock_pattern import SystemClock

    clock = SystemClock(timezone='Europe/Madrid')
    print(clock.now())
    # >>> 2025-06-16 15:57:26.210964+02:00
    ```
    """

    _timezone: tzinfo

    def __init__(self, *, timezone: str | tzinfo = UTC) -> None:
        """
        Create a clock that reads system time in `timezone`.

        The timezone may be a valid timezone name such as `'UTC'` or `'Europe/Madrid'`, or a `tzinfo` object accepted by
        the project value-object validators. String values must be non-empty, trimmed, and valid for `ZoneInfo`.

        Args:
            timezone: Timezone used to produce `now()` and `today()`. Defaults to UTC.

        Raises:
            TypeError: If `timezone` is not a string or `tzinfo` instance.
            ValueError: If `timezone` is not a valid timezone.

        Example:
        ```python
        from clock_pattern import SystemClock

        clock = SystemClock(timezone='UTC')
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
        Retrieve the current timezone-aware system datetime.

        Returns:
            datetime: Current datetime in the configured timezone.

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
        Retrieve the current date in the configured timezone.

        The returned date is derived from `datetime.now(tz=timezone).date()`, so it follows the clock timezone rather
        than the machine's local timezone.

        Returns:
            date: Current date in the configured timezone.

        Example:
        ```python
        from clock_pattern import SystemClock

        clock = SystemClock()
        print(clock.today())
        # >>> 2025-06-16
        ```
        """
        return datetime.now(tz=self._timezone).date()

    @property
    def timezone(self) -> tzinfo:
        """
        Retrieve the timezone used by the clock.

        Returns:
            tzinfo: Timezone used by `now()` and `today()`.

        Example:
        ```python
        from clock_pattern import SystemClock

        clock = SystemClock()
        print(clock.timezone)
        # >>> UTC
        ```
        """
        return self._timezone
