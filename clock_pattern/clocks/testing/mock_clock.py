"""
Testing clock with prepared return values and call assertions.
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

from clock_pattern.clocks.models import Clock


class MockClock(Clock):
    """
    Test double for `Clock` with explicit return values and interaction assertions.

    `MockClock` is useful when tests need both deterministic time and proof that a service requested `now()` or
    `today()`. Return values must be prepared before calling the corresponding method. Naive datetimes passed to
    `prepare_now_method_return_value()` are normalized to UTC.

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
        Create a mock clock with no prepared return values and no recorded calls.

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
        Retrieve the prepared datetime and record a `now()` call.

        Call `prepare_now_method_return_value()` before using this method.

        Raises:
            TypeError: If the `now()` return value has not been prepared.

        Returns:
            datetime: Prepared datetime.

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
        Prepare the datetime returned by `now()`.

        If `now` is naive, UTC is added as its timezone. A timezone-aware datetime is preserved as provided.

        Args:
            now: Datetime returned by the next and subsequent `now()` calls.

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
        Assert that `now()` was called exactly once.

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
        Assert that `now()` was not called.

        Example:
        ```python
        from datetime import date

        from clock_pattern.clocks.testing import MockClock

        return_date = date(year=1999, month=1, day=1)
        clock = MockClock()

        clock.prepare_today_method_return_value(today=return_date)
        print(clock.today())
        # >>> 1999-01-01

        clock.assert_now_method_was_not_called()
        ```
        """
        self._now_mock.assert_not_called()

    @override
    def today(self) -> date:
        """
        Retrieve the prepared date and record a `today()` call.

        Call `prepare_today_method_return_value()` before using this method.

        Raises:
            TypeError: If the `today()` return value has not been prepared.

        Returns:
            date: Prepared date.

        Example:
        ```python
        from datetime import date

        from clock_pattern.clocks.testing import MockClock

        return_date = date(year=1999, month=1, day=1)
        clock = MockClock()

        clock.prepare_today_method_return_value(today=return_date)
        print(clock.today())
        # >>> 1999-01-01

        clock.assert_today_method_was_called_once()
        ```
        """
        NotNoneValueObject(value=self._today_date, title='MockClock', parameter='today')

        self._today_mock()

        return self._today_date  # type: ignore[return-value]

    def prepare_today_method_return_value(self, *, today: date) -> None:
        """
        Prepare the date returned by `today()`.

        Args:
            today: Date returned by the next and subsequent `today()` calls.

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
        # >>> 1999-01-01

        clock.assert_today_method_was_called_once()
        ```
        """
        DateValueObject(value=today, title='MockClock', parameter='today')
        self._today_date = today

    def assert_today_method_was_called_once(self) -> None:
        """
        Assert that `today()` was called exactly once.

        Example:
        ```python
        from datetime import date

        from clock_pattern.clocks.testing import MockClock

        return_date = date(year=1999, month=1, day=1)
        clock = MockClock()

        clock.prepare_today_method_return_value(today=return_date)
        print(clock.today())
        # >>> 1999-01-01

        clock.assert_today_method_was_called_once()
        ```
        """
        self._today_mock.assert_called_once_with()

    def assert_today_method_was_not_called(self) -> None:
        """
        Assert that `today()` was not called.

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
