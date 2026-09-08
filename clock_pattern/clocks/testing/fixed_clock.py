"""
Deterministic clock that stays fixed until explicitly adjusted.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from datetime import UTC, date, datetime, timedelta

from value_object_pattern.usables.dates import DatetimeValueObject

from clock_pattern.clocks.models import Clock


class FixedClock(Clock):
    """
    Return a fixed datetime and the date derived from it.

    `FixedClock` is useful when a test only needs stable time. Naive datetimes are normalized to UTC during
    initialization and `set()`. Use `advance()` to simulate elapsed time, or `set()` to choose another instant.
    Use `MockClock` when a test also needs to assert whether `now()` or `today()` was called.

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
            instant (datetime): Datetime returned by `now()` and used by `today()`.

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
        self.set(instant=instant)

    def set(self, *, instant: datetime) -> None:
        """
        Set the instant returned by both clock methods, allowing forward or backward jumps.

        Args:
            instant (datetime): Datetime returned by `now()` and used by `today()`.

        Raises:
            TypeError: If `instant` is not a datetime.

        Example:
        ```python
        from datetime import UTC, datetime

        from clock_pattern.clocks.testing import FixedClock

        clock = FixedClock(instant=datetime(2025, 2, 1, tzinfo=UTC))
        clock.set(instant=datetime(2025, 1, 1, tzinfo=UTC))
        print(clock.now())
        # >>> 2025-01-01 00:00:00+00:00
        ```
        """
        DatetimeValueObject(value=instant, title='FixedClock', parameter='instant')

        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=UTC)

        self._instant = instant

    def advance(self, *, delta: timedelta) -> None:
        """
        Advance by a non-negative elapsed duration, preserving the clock's timezone.

        Args:
            delta (timedelta): Non-negative elapsed duration to add to the instant.

        Raises:
            ValueError: If `delta` is negative.
            OverflowError: If the resulting instant is outside datetime's range.

        Example:
        ```python
        from datetime import UTC, datetime, timedelta

        from clock_pattern.clocks.testing import FixedClock

        clock = FixedClock(instant=datetime(2025, 12, 31, 23, 59, tzinfo=UTC))
        clock.advance(delta=timedelta(minutes=2))
        print(clock.now())
        # >>> 2026-01-01 00:01:00+00:00
        ```
        """
        if delta < timedelta(0):
            raise ValueError(f'FixedClock delta <<<{delta}>>> must be greater than or equal to zero.')

        if delta:
            self._instant = (self._instant.astimezone(UTC) + delta).astimezone(self._instant.tzinfo)

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
