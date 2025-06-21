"""
FixedClock module.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from datetime import UTC, date, datetime

from value_object_pattern.usables.dates import DatetimeValueObject

from clock_pattern.models.clock import Clock


class FixedClock(Clock):
    """
    MockModel is responsible for retrieving the date/datetime provided when `FixedClock` initialization. Use `MockClock`
    for better testing features.

    Example:
    ```python
    from datetime import datetime

    from clock_pattern.clocks.testing import FixedClock

    fixed_datetime = datetime(year=1999, month=1, day=1)
    clock = FixedClock(instant=fixed_datetime)
    print(clock.now())
    # >>> 1999-01-01 00:00:00+00:00
    ```
    """

    _instant: datetime

    def __init__(self, *, instant: datetime) -> None:
        """
        FixedClock constructor is used to provided which date/datetime `instance` will be retrieved. If the provided
        datetime `instant` has not timezone UTC will be set.

        Args:
            instant (datetime): The datetime that will be retrieved.

        Raises:
            ValueError: If `instant` is not of type datetime.

        Example:
        ```python
        from datetime import datetime

        from clock_pattern.clocks.testing import FixedClock

        fixed_datetime = datetime(year=1999, month=1, day=1)
        clock = FixedClock(instant=fixed_datetime)
        print(clock.now())
        # >>> 1999-01-01 00:00:00+00:00
        ```
        """
        DatetimeValueObject(value=instant, title='FixedClock', parameter='instant')

        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=UTC)

        self._instant = instant

    @override
    def now(self) -> datetime:
        """
        Retrieve the current datetime (now).

        Returns:
            datetime: The current datetime.

        Example:
        ```python
        from datetime import datetime

        from clock_pattern.clocks.testing import FixedClock

        fixed_datetime = datetime(year=1999, month=1, day=1)
        clock = FixedClock(instant=fixed_datetime)
        print(clock.now())
        # >>> 1999-01-01 00:00:00+00:00
        ```
        """
        return self._instant

    @override
    def today(self) -> date:
        """
        Retrieve the current date (today).

        Returns:
            date: The current date.

        Example:
        ```python
        from datetime import datetime

        from clock_pattern.clocks.testing import FixedClock

        fixed_datetime = datetime(year=1999, month=1, day=1)
        clock = FixedClock(instant=fixed_datetime)
        print(clock.today())
        # >>> 1999-01-01
        ```
        """
        return self._instant.date()
