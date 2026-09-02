"""
Testing synchronous poller with call assertions.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from collections.abc import Callable
from unittest.mock import Mock

from value_object_pattern.usables import PositiveNumberValueObject, PositiveOrZeroNumberValueObject

from clock_pattern.pollers.models import Poller


class MockPoller(Poller):
    """
    Test double for `Poller` with prepared exceptions and call assertions.

    Example:
    ```python
    from clock_pattern.pollers.testing import MockPoller

    poller = MockPoller()
    condition = lambda: True

    poller.poll_until(condition=condition, timeout_seconds=1)
    poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=1)
    ```
    """

    _poll_until_mock: Mock
    _exception: BaseException | None

    def __init__(self) -> None:
        """
        Create a mock poller.

        Example:
        ```python
        from clock_pattern.pollers.testing import MockPoller

        poller = MockPoller()
        poller.assert_poll_until_method_was_not_called()
        ```
        """
        self._poll_until_mock = Mock()
        self._exception = None

    @override
    def poll_until(
        self,
        *,
        condition: Callable[[], bool],
        timeout_seconds: float,
        interval_seconds: float = 0.1,
    ) -> None:
        """
        Record a poll call and optionally raise the prepared exception.

        Args:
            condition (Callable[[], bool]): Condition passed by the code under test.
            timeout_seconds (float): Timeout requested by the code under test.
            interval_seconds (float): Poll interval requested by the code under test.

        Raises:
            TypeError: If `timeout_seconds` is not an integer or a float.
            ValueError: If `timeout_seconds` is negative.
            TypeError: If `interval_seconds` is not an integer or a float.
            ValueError: If `interval_seconds` is not positive.
            TypeError: If `condition` does not return a boolean.
            TimeoutExpiredError: If the timeout expires before `condition` returns `True`.

        Example:
        ```python
        from clock_pattern.pollers.testing import MockPoller

        poller = MockPoller()
        condition = lambda: True
        poller.poll_until(condition=condition, timeout_seconds=1)
        poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=1)
        ```
        """
        PositiveOrZeroNumberValueObject(value=timeout_seconds, title='MockPoller', parameter='timeout_seconds')
        PositiveNumberValueObject(value=interval_seconds, title='MockPoller', parameter='interval_seconds')

        self._poll_until_mock(
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

        Example:
        ```python
        from clock_pattern import TimeoutExpiredError
        from clock_pattern.pollers.testing import MockPoller

        poller = MockPoller()
        poller.prepare_poll_until_method_exception(exception=TimeoutExpiredError(elapsed_seconds=1.0))
        ```
        """
        self._exception = exception

    def assert_poll_until_method_was_called_once_with(
        self,
        *,
        condition: Callable[[], bool],
        timeout_seconds: float,
        interval_seconds: float = 0.1,
    ) -> None:
        """
        Assert that `poll_until()` was called exactly once with the provided arguments.

        Args:
            condition (Callable[[], bool]): Expected condition callable.
            timeout_seconds (float): Expected timeout.
            interval_seconds (float): Expected poll interval.

        Raises:
            TypeError: If `timeout_seconds` is not an integer or a float.
            ValueError: If `timeout_seconds` is negative.
            TypeError: If `interval_seconds` is not an integer or a float.
            ValueError: If `interval_seconds` is not positive.
            TypeError: If `condition` does not return a boolean.

        Example:
        ```python
        from clock_pattern.pollers.testing import MockPoller

        poller = MockPoller()
        condition = lambda: True
        poller.poll_until(condition=condition, timeout_seconds=1)
        poller.assert_poll_until_method_was_called_once_with(condition=condition, timeout_seconds=1)
        ```
        """
        PositiveOrZeroNumberValueObject(value=timeout_seconds, title='MockPoller', parameter='timeout_seconds')
        PositiveNumberValueObject(value=interval_seconds, title='MockPoller', parameter='interval_seconds')

        self._poll_until_mock.assert_called_once_with(
            condition=condition,
            timeout_seconds=timeout_seconds,
            interval_seconds=interval_seconds,
        )

    def assert_poll_until_method_was_not_called(self) -> None:
        """
        Assert that `poll_until()` was not called.

        Example:
        ```python
        from clock_pattern.pollers.testing import MockPoller

        poller = MockPoller()
        poller.assert_poll_until_method_was_not_called()
        ```
        """
        self._poll_until_mock.assert_not_called()
