"""
Abstract asynchronous retrier contract.
"""

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar('T')


class RetrierAsync(ABC):
    """
    Define the interface for retrying asynchronous operations.

    Example:
    ```python
    from clock_pattern import SystemRetrierAsync
    from clock_pattern.retriers.models import RetrierAsync


    class MessageSender:
        def __init__(self, *, retrier: RetrierAsync) -> None:
            self._retrier = retrier

        async def send(self) -> str:
            async def operation() -> str:
                return 'sent'

            return await self._retrier.retry(operation=operation, attempts=3)


    sender = MessageSender(retrier=SystemRetrierAsync())
    print(await sender.send())
    # >>> sent
    ```
    """

    @abstractmethod
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
        Retry an async operation until it succeeds or attempts are exhausted.

        Args:
            operation (Callable[[], T]): Operation to execute.
            attempts (int): Maximum number of attempts, including the first call.
            delay_seconds (int | float, optional): Finite, non-negative initial delay between failed attempts. Defaults
            to 0.0 seconds.
            backoff (int | float, optional): Finite, positive multiplier applied to the delay after each failed attempt.
            Defaults to 1.0 (no backoff).
            jitter (bool, optional): Whether to randomize each delay. Defaults to `False`.
            retry_on (type[Exception] | tuple[type[Exception], ...], optional): Exception types that should be retried.
            Defaults to `Exception` (retry on any exception).

        Returns:
            T: Return value awaited from the operation.

        Example:
        ```python
        from clock_pattern import SystemRetrierAsync
        from clock_pattern.retriers.models import RetrierAsync


        class MessageSender:
            def __init__(self, *, retrier: RetrierAsync) -> None:
                self._retrier = retrier

            async def send(self) -> str:
                async def operation() -> str:
                    return 'sent'

                return await self._retrier.retry(operation=operation, attempts=3)


        sender = MessageSender(retrier=SystemRetrierAsync())
        print(await sender.send())
        # >>> sent
        ```
        """
