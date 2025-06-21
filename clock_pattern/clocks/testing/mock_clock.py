"""
MockClock module.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from datetime import UTC, date, datetime
from unittest.mock import Mock

from value_object_pattern.usables import NotNoneValueObject
from value_object_pattern.usables.dates import DateValueObject, DatetimeValueObject

from clock_pattern.models.clock import Clock


class MockClock(Clock):
    """
    MockModel is responsible of mocking Clock class implementation for testing purposes.

    Example:
    ```python
    from datetime import datetime

    from clock_pattern.clocks.testing import MockClock

    return_datetime = datetime(year=1999, month=1, day=1)
    clock = MockClock()

    clock.prepare_now_method_return_value(now=return_datetime)
    print(clock.now())
    # >>> 1999-01-01 00:00:00+00:00

    clock.assert_now_method_was_called_once()
    ```
    """

    _now_mock: Mock
    _today_mock: Mock
    _now_datetime: datetime | None
    _today_date: date | None

    def __init__(self) -> None:
        """
        MockClock constructor.

        Example:
        ```python
        from datetime import datetime

        from clock_pattern.clocks.testing import MockClock

        return_datetime = datetime(year=1999, month=1, day=1)
        clock = MockClock()

        clock.prepare_now_method_return_value(now=return_datetime)
        print(clock.now())
        # >>> 1999-01-01 00:00:00+00:00

        clock.assert_now_method_was_called_once()
        ```
        """
        self._now_mock = Mock()
        self._today_mock = Mock()
        self._now_datetime = None
        self._today_date = None

    @override
    def now(self) -> datetime:
        """
        Retrieve the current datetime (now). Use `MockClock.prepare_now_method_return_value` to prepare the return value
        for this method.

        Raises:
            TypeError: If `now` method return value is not configured.

        Returns:
            datetime: The current datetime.

        Example:
        ```python
        from datetime import datetime

        from clock_pattern.clocks.testing import MockClock

        return_datetime = datetime(year=1999, month=1, day=1)
        clock = MockClock()

        clock.prepare_now_method_return_value(now=return_datetime)
        print(clock.now())
        # >>> 1999-01-01 00:00:00+00:00

        clock.assert_now_method_was_called_once()
        ```
        """
        NotNoneValueObject(value=self._now_datetime, title='MockClock', parameter='now')

        self._now_mock()

        return self._now_datetime  # type: ignore[return-value]

    def prepare_now_method_return_value(self, *, now: datetime) -> None:
        """
        Prepare now method to return the provided datetime `now`. If the provided datetime `now` has not timezone UTC
        will be set.

        Args:
            now (datetime): Datetime to return.

        Raises:
            TypeError: If `now` is not of type datetime.

        Example:
        ```python
        from datetime import datetime

        from clock_pattern.clocks.testing import MockClock

        return_datetime = datetime(year=1999, month=1, day=1)
        clock = MockClock()

        clock.prepare_now_method_return_value(now=return_datetime)
        print(clock.now())
        # >>> 1999-01-01 00:00:00+00:00

        clock.assert_now_method_was_called_once()
        ```
        """
        DatetimeValueObject(value=now, title='MockClock', parameter='now')

        if now.tzinfo is None:
            now = now.replace(tzinfo=UTC)

        self._now_datetime = now

    def assert_now_method_was_called_once(self) -> None:
        """
        Assert that the now method was called once.

        Example:
        ```python
        from datetime import datetime

        from clock_pattern.clocks.testing import MockClock

        return_datetime = datetime(year=1999, month=1, day=1)
        clock = MockClock()

        clock.prepare_now_method_return_value(now=return_datetime)
        print(clock.now())
        # >>> 1999-01-01 00:00:00+00:00

        clock.assert_now_method_was_called_once()
        ```
        """
        self._now_mock.assert_called_once_with()

    def assert_now_method_was_not_called(self) -> None:
        """
        Assert that the now method was not called.

        Example:
        ```python
        from datetime import date

        from clock_pattern.clocks.testing import MockClock

        return_date = date(year=1999, month=1, day=1)
        clock = MockClock()

        clock.prepare_today_method_return_value(today=return_date)
        print(clock.today())
        # >>> 2025-06-16

        clock.assert_now_method_was_not_called()
        ```
        """
        self._now_mock.assert_not_called()

    @override
    def today(self) -> date:
        """
        Retrieve the current date (today). Use `MockClock.prepare_today_method_return_value` to prepare the return value
        for this method.

        Raises:
            ValueError: If `today` method return value is not configured.

        Returns:
            date: The current date.

        Example:
        ```python
        from datetime import date

        from clock_pattern.clocks.testing import MockClock

        return_date = date(year=1999, month=1, day=1)
        clock = MockClock()

        clock.prepare_today_method_return_value(today=return_date)
        print(clock.today())
        # >>> 2025-06-16

        clock.assert_today_method_was_called_once()
        ```
        """
        NotNoneValueObject(value=self._today_date, title='MockClock', parameter='today')

        self._today_mock()

        return self._today_date  # type: ignore[return-value]

    def prepare_today_method_return_value(self, *, today: date) -> None:
        """
        Prepare today method to return the provided date `today`.

        Args:
            today (date): Date to return.

        Raises:
            TypeError: If `today` is not of type date.

        Example:
        ```python
        from datetime import date

        from clock_pattern.clocks.testing import MockClock

        return_date = date(year=1999, month=1, day=1)
        clock = MockClock()

        clock.prepare_today_method_return_value(today=return_date)
        print(clock.today())
        # >>> 2025-06-16

        clock.assert_today_method_was_called_once()
        ```
        """
        DateValueObject(value=today, title='MockClock', parameter='today')
        self._today_date = today

    def assert_today_method_was_called_once(self) -> None:
        """
        Assert that the today method was called once.

        Example:
        ```python
        from datetime import date

        from clock_pattern.clocks.testing import MockClock

        return_date = date(year=1999, month=1, day=1)
        clock = MockClock()

        clock.prepare_today_method_return_value(today=return_date)
        print(clock.today())
        # >>> 2025-06-16

        clock.assert_today_method_was_called_once()
        ```
        """
        self._today_mock.assert_called_once_with()

    def assert_today_method_was_not_called(self) -> None:
        """
        Assert that the today method was not called.

        Example:
        ```python
        from datetime import datetime

        from clock_pattern.clocks.testing import MockClock

        return_datetime = datetime(year=1999, month=1, day=1)
        clock = MockClock()

        clock.prepare_now_method_return_value(now=return_datetime)
        print(clock.now())
        # >>> 1999-01-01 00:00:00+00:00

        clock.assert_today_method_was_not_called()
        ```
        """
        self._today_mock.assert_not_called()
