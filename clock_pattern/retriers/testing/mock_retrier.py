"""
Testing synchronous retrier with call assertions.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from collections.abc import Callable
from typing import Any, TypeVar, cast
from unittest.mock import Mock

from value_object_pattern.usables import (
    BooleanValueObject,
    PositiveIntegerValueObject,
    PositiveNumberValueObject,
    PositiveOrZeroNumberValueObject,
)

from clock_pattern.retriers.models import Retrier

T = TypeVar('T')


class MockRetrier(Retrier):
    """
    Test double for `Retrier` with prepared return values, exceptions, and call assertions.

    Example:
    ```python
    from clock_pattern.retriers.testing import MockRetrier


    def operation() -> str:
        return 'ignored'


    retrier = MockRetrier()
    retrier.prepare_retry_method_return_value(value='done')

    result = retrier.retry(operation=operation, attempts=3)
    print(result)
    # >>> done

    retrier.assert_retry_method_was_called_once_with(operation=operation, attempts=3)
    ```
    """

    _retry_mock: Mock
    _return_value: Any
    _exception: BaseException | None

    def __init__(self) -> None:
        """
        Create a mock retrier.

        Example:
        ```python
        from clock_pattern.retriers.testing import MockRetrier

        retrier = MockRetrier()
        retrier.prepare_retry_method_return_value(value='done')
        ```
        """
        self._retry_mock = Mock()
        self._return_value = None
        self._exception = None

    @override
    def retry(
        self,
        *,
        operation: Callable[[], T],
        attempts: int,
        delay_seconds: float = 0.0,
        backoff: float = 1.0,
        jitter: bool = False,
        retry_on: type[Exception] | tuple[type[Exception], ...] = Exception,
    ) -> T:
        """
        Record a retry call and return or raise the prepared result.

        Args:
            operation (Callable[[], T]): Operation to execute.
            attempts (int): Maximum number of attempts, including the first call.
            delay_seconds (float, optional): Finite, non-negative initial delay between failed attempts. Defaults
            to 0.0 seconds.
            backoff (float, optional): Finite, positive multiplier applied to the delay after each failed attempt.
            Defaults to 1.0 (no backoff).
            jitter (bool, optional): Whether to randomize each delay. Defaults to `False`.
            retry_on (type[Exception] | tuple[type[Exception], ...], optional): Exception types that should be retried.
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
        from clock_pattern.retriers.testing import MockRetrier

        operation = lambda: 'ignored'
        retrier = MockRetrier()
        retrier.prepare_retry_method_return_value(value='done')

        print(retrier.retry(operation=operation, attempts=3))
        # >>> done

        retrier.assert_retry_method_was_called_once_with(operation=operation, attempts=3)
        ```
        """
        PositiveIntegerValueObject(value=attempts, title='MockRetrier', parameter='attempts')
        PositiveOrZeroNumberValueObject(value=delay_seconds, title='MockRetrier', parameter='delay_seconds')
        PositiveNumberValueObject(value=backoff, title='MockRetrier', parameter='backoff')
        BooleanValueObject(value=jitter, title='MockRetrier', parameter='jitter')

        self._retry_mock(
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

    def prepare_retry_method_return_value(self, *, value: object) -> None:
        """
        Prepare the value returned by `retry()`.

        Args:
            value (object): Value returned by `retry()`.

        Example:
        ```python
        from clock_pattern.retriers.testing import MockRetrier

        retrier = MockRetrier()
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
        from clock_pattern.retriers.testing import MockRetrier

        retrier = MockRetrier()
        retrier.prepare_retry_method_exception(exception=ValueError('failed'))
        ```
        """
        self._exception = exception

    def assert_retry_method_was_called_once(self) -> None:
        """
        Assert that `retry()` was called exactly once.

        Example:
        ```python
        from clock_pattern.retriers.testing import MockRetrier

        retrier = MockRetrier()
        retrier.prepare_retry_method_return_value(value='done')
        retrier.retry(operation=lambda: 'ignored', attempts=3)
        retrier.assert_retry_method_was_called_once()
        ```
        """
        self._retry_mock.assert_called_once()

    def assert_retry_method_was_called_once_with(
        self,
        *,
        operation: Callable[[], Any],
        attempts: int,
        delay_seconds: float = 0.0,
        backoff: float = 1.0,
        jitter: bool = False,
        retry_on: type[Exception] | tuple[type[Exception], ...] = Exception,
    ) -> None:
        """
        Assert that `retry()` was called exactly once with the provided arguments.

        Args:
            operation (Callable[[], Any]): Expected operation callable.
            attempts (int): Expected maximum number of attempts.
            delay_seconds (float, optional): Expected finite, non-negative initial delay. Defaults to 0.0 seconds.
            backoff (float, optional): Expected finite, positive delay multiplier. Defaults to 1.0.
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
        from clock_pattern.retriers.testing import MockRetrier

        operation = lambda: 'done'
        retrier = MockRetrier()
        retrier.retry(operation=operation, attempts=3)

        retrier.assert_retry_method_was_called_once_with(operation=operation, attempts=3)
        ```
        """
        PositiveIntegerValueObject(value=attempts, title='MockRetrier', parameter='attempts')
        PositiveOrZeroNumberValueObject(value=delay_seconds, title='MockRetrier', parameter='delay_seconds')
        PositiveNumberValueObject(value=backoff, title='MockRetrier', parameter='backoff')
        BooleanValueObject(value=jitter, title='MockRetrier', parameter='jitter')

        self._retry_mock.assert_called_once_with(
            operation=operation,
            attempts=attempts,
            delay_seconds=delay_seconds,
            backoff=backoff,
            jitter=jitter,
            retry_on=retry_on,
        )

    def assert_retry_method_was_not_called(self) -> None:
        """
        Assert that `retry()` was not called.

        Example:
        ```python
        from clock_pattern.retriers.testing import MockRetrier

        retrier = MockRetrier()
        retrier.assert_retry_method_was_not_called()
        ```
        """
        self._retry_mock.assert_not_called()
