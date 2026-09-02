"""
System-backed asynchronous sleeper.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from asyncio import sleep
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from value_object_pattern.usables import PositiveOrZeroNumberValueObject

from clock_pattern.monotonic_clocks.models import MonotonicClock
from clock_pattern.sleepers.models import SleeperAsync


class SystemSleeperAsync(SleeperAsync):
    """
    Pause asynchronous execution using `asyncio.sleep`.

    Example:
    ```python
    from clock_pattern import SystemSleeperAsync
    from clock_pattern.monotonic_clocks import SystemMonotonicClock

    sleeper = SystemSleeperAsync(monotonic_clock=SystemMonotonicClock())
    await sleeper.sleep(seconds=1)
    ```
    """

    _monotonic_clock: MonotonicClock

    def __init__(self, *, monotonic_clock: MonotonicClock) -> None:
        """
        Create a system-backed asynchronous sleeper.

        Args:
            monotonic_clock (MonotonicClock): The monotonic clock to use .

        Example:
        ```python
        from clock_pattern import SystemSleeperAsync
        from clock_pattern.monotonic_clocks import SystemMonotonicClock

        sleeper = SystemSleeperAsync(monotonic_clock=SystemMonotonicClock())
        await sleeper.sleep(seconds=1)
        ```
        """
        self._monotonic_clock = monotonic_clock

    @override
    async def sleep(self, *, seconds: float) -> None:
        """
        Pause asynchronous execution for `seconds`.

        Args:
            seconds (float): The number of seconds to pause execution.

        Raises:
            TypeError: If `seconds` is not an integer or float.
            ValueError: If `seconds` is negative.

        Example:
        ```python
        from clock_pattern import SystemSleeperAsync
        from clock_pattern.monotonic_clocks import SystemMonotonicClock

        sleeper = SystemSleeperAsync(monotonic_clock=SystemMonotonicClock())
        await sleeper.sleep(seconds=1)
        ```
        """
        PositiveOrZeroNumberValueObject(value=seconds, title='SystemSleeperAsync', parameter='seconds')

        await sleep(seconds)

    @override
    @asynccontextmanager
    async def minimum_duration(self, *, seconds: float) -> AsyncIterator[None]:
        """
        Create an async context manager that ensures the enclosed work takes at least `seconds`.

        Args:
            seconds (float): The minimum elapsed duration for the enclosed asynchronous work.

        Raises:
            TypeError: If `seconds` is not an integer or float.
            ValueError: If `seconds` is negative.

        Returns:
            AbstractAsyncContextManager[None]: An async context manager that awaits any remaining duration when the
            enclosed work exits.

        Example:
        ```python
        from clock_pattern import SystemSleeperAsync
        from clock_pattern.monotonic_clocks import SystemMonotonicClock

        sleeper = SystemSleeperAsync(monotonic_clock=SystemMonotonicClock())

        async with sleeper.minimum_duration(seconds=1):
            pass
        ```
        """
        PositiveOrZeroNumberValueObject(value=seconds, title='SystemSleeperAsync', parameter='seconds')

        started_time = self._monotonic_clock.current_seconds()
        try:
            yield

        finally:
            elapsed_seconds = self._monotonic_clock.current_seconds() - started_time
            remaining_seconds = seconds - elapsed_seconds

            if remaining_seconds > 0:
                await self.sleep(seconds=remaining_seconds)
