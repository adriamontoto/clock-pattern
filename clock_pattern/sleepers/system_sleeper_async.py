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

from value_object_pattern import UnionValueObject
from value_object_pattern.usables import PositiveOrZeroFloatValueObject, PositiveOrZeroIntegerValueObject

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

        Raises:
            TypeError: If `monotonic_clock` is not a `MonotonicClock`.

        Example:
        ```python
        from clock_pattern import SystemSleeperAsync
        from clock_pattern.monotonic_clocks import SystemMonotonicClock

        sleeper = SystemSleeperAsync(monotonic_clock=SystemMonotonicClock())
        await sleeper.sleep(seconds=1)
        ```
        """
        if not isinstance(monotonic_clock, MonotonicClock):
            raise TypeError(f'SystemSleeperAsync monotonic_clock <<<{monotonic_clock}>>> must be a MonotonicClock. Got <<<{type(monotonic_clock).__name__}>>> type.')  # noqa: E501  # fmt: skip

        self._monotonic_clock = monotonic_clock

    @override
    async def sleep(self, *, seconds: int | float) -> None:
        """
        Pause asynchronous execution for `seconds`.

        Args:
            seconds (int | float): The number of seconds to pause execution.

        Raises:
            TypeError: If `seconds` is not a positive-or-zero integer or float.

        Example:
        ```python
        from clock_pattern import SystemSleeperAsync
        from clock_pattern.monotonic_clocks import SystemMonotonicClock

        sleeper = SystemSleeperAsync(monotonic_clock=SystemMonotonicClock())
        await sleeper.sleep(seconds=1)
        ```
        """
        UnionValueObject[PositiveOrZeroIntegerValueObject | PositiveOrZeroFloatValueObject](
            value=seconds,  # type: ignore[arg-type]
            title='SystemSleeperAsync',
            parameter='seconds',
        )

        await sleep(seconds)

    @override
    @asynccontextmanager
    async def minimum_duration(self, *, seconds: int | float) -> AsyncIterator[None]:
        """
        Create an async context manager that ensures the enclosed work takes at least `seconds`.

        Args:
            seconds (int | float): The minimum elapsed duration for the enclosed asynchronous work.

        Returns:
            AbstractAsyncContextManager[None]: An async context manager that awaits any remaining duration when the
            enclosed work exits.

        Raises:
            TypeError: If `seconds` is not a positive-or-zero integer or float.

        Example:
        ```python
        from clock_pattern import SystemSleeperAsync
        from clock_pattern.monotonic_clocks import SystemMonotonicClock

        sleeper = SystemSleeperAsync(monotonic_clock=SystemMonotonicClock())

        async with sleeper.minimum_duration(seconds=1):
            pass
        ```
        """
        UnionValueObject[PositiveOrZeroIntegerValueObject | PositiveOrZeroFloatValueObject](
            value=seconds,  # type: ignore[arg-type]
            title='SystemSleeperAsync',
            parameter='seconds',
        )

        started_time = self._monotonic_clock.current_seconds()
        try:
            yield

        finally:
            elapsed_seconds = self._monotonic_clock.current_seconds() - started_time
            remaining_seconds = seconds - elapsed_seconds

            if remaining_seconds > 0:
                await self.sleep(seconds=remaining_seconds)
