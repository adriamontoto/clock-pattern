"""
Testing asynchronous poller with call assertions.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from collections.abc import Awaitable, Callable
from unittest.mock import AsyncMock

from value_object_pattern.usables import PositiveNumberValueObject, PositiveOrZeroNumberValueObject

from clock_pattern.pollers.models import PollerAsync


class MockPollerAsync(PollerAsync):
    """
    Test double for `PollerAsync` with prepared exceptions and call assertions.

    Example:
    ```python
    from clock_pattern.pollers.testing import MockPollerAsync

    poller = MockPollerAsync()
    condition = lambda: True

    await poller.poll_until(condition=condition, timeout_seconds=1)
    poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=1)
    ```
    """

    _poll_until_mock: AsyncMock
    _exception: BaseException | None

    def __init__(self) -> None:
        """
        Create an async mock poller.

        Example:
        ```python
        from clock_pattern.pollers.testing import MockPollerAsync

        poller = MockPollerAsync()
        poller.assert_poll_until_method_was_not_called()
        ```
        """
        self._poll_until_mock = AsyncMock()
        self._exception = None

    @override
    async def poll_until(
        self,
        *,
        condition: Callable[[], bool | Awaitable[bool]],
        timeout_seconds: int | float,
        interval_seconds: int | float = 0.1,
    ) -> None:
        """
        Record an async poll call and optionally raise the prepared exception.

        Args:
            condition (Callable[[], bool | Awaitable[bool]]): Condition passed by the code under test.
            timeout_seconds (int | float): Timeout requested by the code under test.
            interval_seconds (int | float): Poll interval requested by the code under test.

        Raises:
            TypeError: If `timeout_seconds` is not an integer or a float.
            ValueError: If `timeout_seconds` is negative.
            TypeError: If `interval_seconds` is not an integer or a float.
            ValueError: If `interval_seconds` is not positive.
            TypeError: If `condition` does not return a boolean.
            TimeoutExpiredError: If the timeout expires before `condition` returns `True`.
        """
        PositiveOrZeroNumberValueObject(value=timeout_seconds, title='MockPollerAsync', parameter='timeout_seconds')
        PositiveNumberValueObject(value=interval_seconds, title='MockPollerAsync', parameter='interval_seconds')

        await self._poll_until_mock(
            condition=condition,
            timeout_seconds=timeout_seconds,
            interval_seconds=interval_seconds,
        )

        if self._exception is not None:
            raise self._exception

    def prepare_poll_until_method_exception(self, *, exception: BaseException) -> None:
        """
        Prepare an exception raised by `poll_until()`.

        Args:
            exception (BaseException): Exception raised by `poll_until()`.

        """
        self._exception = exception

    def assert_poll_until_method_was_called_once_with(
        self,
        *,
        condition: Callable[[], bool | Awaitable[bool]],
        timeout_seconds: int | float,
        interval_seconds: int | float = 0.1,
    ) -> None:
        """
        Assert that `poll_until()` was awaited exactly once with the provided arguments.

        Args:
            condition (Callable[[], bool | Awaitable[bool]]): Expected condition callable.
            timeout_seconds (int | float): Expected timeout.
            interval_seconds (int | float): Expected poll interval.

        Raises:
            TypeError: If `timeout_seconds` is not an integer or a float.
            ValueError: If `timeout_seconds` is negative.
            TypeError: If `interval_seconds` is not an integer or a float.
            ValueError: If `interval_seconds` is not positive.
            TypeError: If `condition` does not return a boolean.
        """
        PositiveOrZeroNumberValueObject(value=timeout_seconds, title='MockPollerAsync', parameter='timeout_seconds')
        PositiveNumberValueObject(value=interval_seconds, title='MockPollerAsync', parameter='interval_seconds')

        self._poll_until_mock.assert_awaited_once_with(
            condition=condition,
            timeout_seconds=timeout_seconds,
            interval_seconds=interval_seconds,
        )

    def assert_poll_until_method_was_not_called(self) -> None:
        """
        Assert that `poll_until()` was not awaited.

        Example:
        ```python
        from clock_pattern.pollers.testing import MockPollerAsync

        poller = MockPollerAsync()
        poller.assert_poll_until_method_was_not_called()
        ```
        """
        self._poll_until_mock.assert_not_awaited()
