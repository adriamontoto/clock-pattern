"""
Abstract synchronous retrier contract.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeVar

T = TypeVar('T')


class Retrier(ABC):
    """
    Define the interface for retrying synchronous operations.

    Example:
    ```python
    from clock_pattern import SystemRetrier
    from clock_pattern.retriers.models import Retrier


    class MessageSender:
        def __init__(self, *, retrier: Retrier) -> None:
            self._retrier = retrier

        def send(self) -> str:
            return self._retrier.retry(operation=lambda: 'sent', attempts=3)


    sender = MessageSender(retrier=SystemRetrier())
    print(sender.send())
    # >>> sent
    ```
    """

    @abstractmethod
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
        Retry an operation until it succeeds or attempts are exhausted.

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

        Returns:
            T: Return value from the operation.

        Example:
        ```python
        from clock_pattern import SystemRetrier
        from clock_pattern.retriers.models import Retrier


        class MessageSender:
            def __init__(self, *, retrier: Retrier) -> None:
                self._retrier = retrier

            def send(self) -> str:
                return self._retrier.retry(operation=lambda: 'sent', attempts=3)


        sender = MessageSender(retrier=SystemRetrier())
        print(sender.send())
        # >>> sent
        ```
        """
