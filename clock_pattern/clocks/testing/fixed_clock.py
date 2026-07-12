"""
Deterministic clock that always returns the same instant.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from datetime import UTC, date, datetime

from value_object_pattern.usables.dates import DatetimeValueObject

from clock_pattern.clocks.models import Clock


class FixedClock(Clock):
    """
    Return a fixed datetime and the date derived from it.

    `FixedClock` is useful when a test only needs stable time. Naive datetimes are normalized to UTC during
    initialization. Use `MockClock` when a test also needs to assert whether `now()` or `today()` was called.

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
        Create a fixed clock for `instant`.

        If `instant` is naive, UTC is added as its timezone. A timezone-aware `instant` is preserved as provided.

        Args:
            instant: Datetime returned by `now()` and used by `today()`.

        Raises:
            TypeError: If `instant` is not a datetime.

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
        Retrieve the fixed datetime.

        Returns:
            datetime: The configured instant.

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
        Retrieve the date portion of the fixed datetime.

        Returns:
            date: Date derived from the configured instant.

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
