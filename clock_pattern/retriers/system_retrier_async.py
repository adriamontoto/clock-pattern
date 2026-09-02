"""
System-backed asynchronous retry helper.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from collections.abc import Awaitable, Callable
from random import uniform
from typing import TypeVar

from value_object_pattern.usables import (
    BooleanValueObject,
    PositiveIntegerValueObject,
    PositiveNumberValueObject,
    PositiveOrZeroNumberValueObject,
)

from clock_pattern.retriers.models import RetrierAsync
from clock_pattern.sleepers.models import SleeperAsync

T = TypeVar('T')


class SystemRetrierAsync(RetrierAsync):
    """
    Retry asynchronous operations that raise configured exception types.

    Example:
    ```python
    from clock_pattern import SystemMonotonicClock, SystemRetrierAsync, SystemSleeperAsync


    async def get_value() -> str:
        return 'done'


    retrier = SystemRetrierAsync(sleeper=SystemSleeperAsync(monotonic_clock=SystemMonotonicClock()))
    result = await retrier.retry(operation=get_value, attempts=3)
    print(result)
    # >>> done
    ```
    """

    _sleeper: SleeperAsync
    _random_uniform: Callable[[float, float], float]

    def __init__(self, *, sleeper: SleeperAsync, random_uniform: Callable[[float, float], float] = uniform) -> None:
        """
        Create an asynchronous retrier.

        Args:
            sleeper (Sleeper): Sleeper used between retry attempts.
            random_uniform (Callable[[float, float], float], optional): Random function used when jitter is enabled.
            Defaults to `random.uniform`.

        Example:
        ```python
        from clock_pattern import SystemMonotonicClock, SystemRetrierAsync, SystemSleeperAsync


        async def get_value() -> str:
            return 'done'


        retrier = SystemRetrierAsync(sleeper=SystemSleeperAsync(monotonic_clock=SystemMonotonicClock()))
        result = await retrier.retry(operation=get_value, attempts=3)
        print(result)
        # >>> done
        ```
        """
        self._sleeper = sleeper
        self._random_uniform = random_uniform

    @override
    async def retry(
        self,
        *,
        operation: Callable[[], Awaitable[T]],
        attempts: int,
        delay_seconds: float = 0.0,
        backoff: float = 1.0,
        jitter: bool = False,
        retry_on: type[Exception] | tuple[type[Exception], ...] = Exception,
    ) -> T:
        """
        Retry `operation` until it returns or attempts are exhausted.

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
            T: Return value awaited from `operation`.

        Example:
        ```python
        from clock_pattern import SystemMonotonicClock, SystemRetrierAsync, SystemSleeperAsync


        async def get_value() -> str:
            return 'done'


        result = await SystemRetrierAsync(sleeper=SystemSleeperAsync(monotonic_clock=SystemMonotonicClock())).retry(
            operation=get_value,
            attempts=3,
            delay_seconds=0.1,
        )
        print(result)
        # >>> done
        ```
        """
        PositiveIntegerValueObject(value=attempts, title='AsyncSystemRetrier', parameter='attempts')
        PositiveOrZeroNumberValueObject(value=delay_seconds, title='AsyncSystemRetrier', parameter='delay_seconds')
        PositiveNumberValueObject(value=backoff, title='AsyncSystemRetrier', parameter='backoff')
        BooleanValueObject(value=jitter, title='AsyncSystemRetrier', parameter='jitter')

        current_delay_seconds = delay_seconds
        for attempt_number in range(1, attempts + 1):
            try:
                return await operation()

            except retry_on:
                if attempt_number == attempts:
                    raise

                sleep_seconds = self._random_uniform(0.0, current_delay_seconds) if jitter else current_delay_seconds
                if sleep_seconds > 0:
                    await self._sleeper.sleep(seconds=sleep_seconds)

                current_delay_seconds *= backoff

        raise RuntimeError('SystemRetrierAsync attempts loop ended unexpectedly.')  # pragma: no cover
