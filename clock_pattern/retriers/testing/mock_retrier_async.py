"""
Testing asynchronous retrier with call assertions.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast
from unittest.mock import AsyncMock

from value_object_pattern.usables import (
    BooleanValueObject,
    PositiveIntegerValueObject,
    PositiveNumberValueObject,
    PositiveOrZeroNumberValueObject,
)

from clock_pattern.retriers.models import RetrierAsync

T = TypeVar('T')


class MockRetrierAsync(RetrierAsync):
    """
    Test double for `RetrierAsync` with prepared return values, exceptions, and call assertions.

    Example:
    ```python
    from clock_pattern.retriers.testing import MockRetrierAsync


    async def get_value() -> str:
        return 'ignored'


    retrier = MockRetrierAsync()
    retrier.prepare_retry_method_return_value(value='done')

    result = await retrier.retry(operation=get_value, attempts=3)
    print(result)
    # >>> done

    retrier.assert_retry_method_was_called_once_with(operation=get_value, attempts=3)
    ```
    """

    _retry_mock: AsyncMock
    _return_value: Any
    _exception: BaseException | None

    def __init__(self) -> None:
        """
        Create an async mock retrier.

        Example:
        ```python
        from clock_pattern.retriers.testing import MockRetrierAsync

        retrier = MockRetrierAsync()
        retrier.prepare_retry_method_return_value(value='done')
        ```
        """
        self._retry_mock = AsyncMock()
        self._return_value = None
        self._exception = None

    @override
    async def retry(
        self,
        *,
        operation: Callable[[], Awaitable[T]],
        attempts: int,
        delay_seconds: int | float = 0.0,
        backoff: int | float = 1.0,
        jitter: bool = False,
        retry_on: type[Exception] | tuple[type[Exception], ...] = Exception,
    ) -> T:
        """
        Record an async retry call and return or raise the prepared result.

        Args:
            operation (Callable[[], Awaitable[T]]): Async operation passed by the code under test.
            attempts (int): Maximum number of attempts requested by the code under test.
            delay_seconds (int | float, optional): Finite, non-negative initial delay requested by the code under test.
            Defaults to 0.0 seconds.
            backoff (int | float, optional): Finite, positive delay multiplier requested by the code under test.
            Defaults to 1.0.
            jitter (bool, optional): Whether jitter was requested. Defaults to False.
            retry_on (type[Exception] | tuple[type[Exception], ...], optional): Exception types requested for retry.
            Defaults to `Exception` (retry on any exception).

        Raises:
            TypeError: If the `attempts` is not an integer.
            ValueError: If the `attempts` is not a positive integer.
            TypeError: If the `delay_seconds` is not an integer or float.
            ValueError: If the `delay_seconds` is negative.
            TypeError: If the `backoff` is not an integer or float.
            ValueError: If the `backoff` is not positive.
            TypeError: If the `jitter` is not a boolean.

        Returns:
            T: Prepared return value.

        Example:
        ```python
        from clock_pattern.retriers.testing import MockRetrierAsync


        async def operation() -> str:
            return 'ignored'


        retrier = MockRetrierAsync()
        retrier.prepare_retry_method_return_value(value='done')

        print(await retrier.retry(operation=operation, attempts=3))
        # >>> done

        retrier.assert_retry_method_was_called_once_with(operation=operation, attempts=3)
        ```
        """
        PositiveIntegerValueObject(value=attempts, title='MockRetrierAsync', parameter='attempts')
        PositiveOrZeroNumberValueObject(value=delay_seconds, title='MockRetrierAsync', parameter='delay_seconds')
        PositiveNumberValueObject(value=backoff, title='MockRetrierAsync', parameter='backoff')
        BooleanValueObject(value=jitter, title='MockRetrierAsync', parameter='jitter')

        await self._retry_mock(
            operation=operation,
            attempts=attempts,
            delay_seconds=delay_seconds,
            backoff=backoff,
            jitter=jitter,
            retry_on=retry_on,
        )

        if self._exception is not None:
            raise self._exception

        return cast(T, self._return_value)

    def prepare_retry_method_return_value(self, *, value: Any) -> None:
        """
        Prepare the value returned by `retry()`.

        Args:
            value (Any): Value returned by `retry()`.

        Example:
        ```python
        from clock_pattern.retriers.testing import MockRetrierAsync

        retrier = MockRetrierAsync()
        retrier.prepare_retry_method_return_value(value='done')
        ```
        """
        self._return_value = value

    def prepare_retry_method_exception(self, *, exception: BaseException) -> None:
        """
        Prepare the exception raised by `retry()`.

        Args:
            exception (BaseException): Exception raised by `retry()`.

        Example:
        ```python
        from clock_pattern.retriers.testing import MockRetrierAsync

        retrier = MockRetrierAsync()
        retrier.prepare_retry_method_exception(exception=ValueError('failed'))
        ```
        """
        self._exception = exception

    def assert_retry_method_was_called_once(self) -> None:
        """
        Assert that `retry()` was awaited exactly once.

        Example:
        ```python
        from clock_pattern.retriers.testing import MockRetrierAsync


        async def get_value() -> str:
            return 'ignored'


        retrier = MockRetrierAsync()
        retrier.prepare_retry_method_return_value(value='done')
        await retrier.retry(operation=get_value, attempts=3)
        retrier.assert_retry_method_was_called_once()
        ```
        """
        self._retry_mock.assert_awaited_once()

    def assert_retry_method_was_called_once_with(
        self,
        *,
        operation: Callable[[], Awaitable[Any]],
        attempts: int,
        delay_seconds: int | float = 0.0,
        backoff: int | float = 1.0,
        jitter: bool = False,
        retry_on: type[Exception] | tuple[type[Exception], ...] = Exception,
    ) -> None:
        """
        Assert that `retry()` was awaited exactly once with the provided arguments.

        Args:
            operation (Callable[[], Awaitable[Any]]): Expected async operation callable.
            attempts (int): Expected maximum number of attempts.
            delay_seconds (int | float, optional): Expected finite, non-negative initial delay. Defaults to 0.0 seconds.
            backoff (int | float, optional): Expected finite, positive delay multiplier. Defaults to 1.0.
            jitter (bool, optional): Expected jitter flag. Defaults to False.
            retry_on (type[Exception] | tuple[type[Exception], ...], optional): Expected retryable exception types.
            Defaults to `Exception` (retry on any exception).

        Raises:
            TypeError: If the `attempts` is not an integer.
            ValueError: If the `attempts` is not a positive integer.
            TypeError: If the `delay_seconds` is not an integer or float.
            ValueError: If the `delay_seconds` is negative.
            TypeError: If the `backoff` is not an integer or float.
            ValueError: If the `backoff` is not positive.
            TypeError: If the `jitter` is not a boolean.

        Example:
        ```python
        from clock_pattern.retriers.testing import MockRetrierAsync


        async def operation() -> str:
            return 'done'


        retrier = MockRetrierAsync()
        await retrier.retry(operation=operation, attempts=3)

        retrier.assert_retry_method_was_called_once_with(operation=operation, attempts=3)
        ```
        """
        PositiveIntegerValueObject(value=attempts, title='MockRetrierAsync', parameter='attempts')
        PositiveOrZeroNumberValueObject(value=delay_seconds, title='MockRetrierAsync', parameter='delay_seconds')
        PositiveNumberValueObject(value=backoff, title='MockRetrierAsync', parameter='backoff')
        BooleanValueObject(value=jitter, title='MockRetrierAsync', parameter='jitter')

        self._retry_mock.assert_awaited_once_with(
            operation=operation,
            attempts=attempts,
            delay_seconds=delay_seconds,
            backoff=backoff,
            jitter=jitter,
            retry_on=retry_on,
        )

    def assert_retry_method_was_not_called(self) -> None:
        """
        Assert that `retry()` was not awaited.

        Example:
        ```python
        from clock_pattern.retriers.testing import MockRetrierAsync

        retrier = MockRetrierAsync()
        retrier.assert_retry_method_was_not_called()
        ```
        """
        self._retry_mock.assert_not_awaited()
