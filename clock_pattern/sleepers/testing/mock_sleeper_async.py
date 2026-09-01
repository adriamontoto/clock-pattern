"""
Testing asynchronous sleeper with call assertions.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

from value_object_pattern.usables import PositiveOrZeroNumberValueObject

from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.sleepers.models import SleeperAsync


class MockSleeperAsync(SleeperAsync):
    """
    Test double for `SleeperAsync` that records sleep calls and advances a monotonic clock.

    Example:
    ```python
    from clock_pattern.sleepers.testing import MockSleeperAsync
    from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

    sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())
    await sleeper.sleep(seconds=1)

    sleeper.assert_sleep_method_was_called_once_with(seconds=1)
    ```
    """

    _sleep_mock: AsyncMock
    _monotonic_clock: MockMonotonicClock
    _sleep_calls: list[float]

    def __init__(self, *, monotonic_clock: MockMonotonicClock) -> None:
        """
        Create an async mock sleeper.

        Args:
            monotonic_clock (MockMonotonicClock): Monotonic clock advanced by sleep calls.

        Example:
        ```python
        from clock_pattern.sleepers.testing import MockSleeperAsync
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())
        await sleeper.sleep(seconds=1)

        sleeper.assert_sleep_method_was_called_once_with(seconds=1)
        ```
        """
        self._sleep_mock = AsyncMock()
        self._monotonic_clock = monotonic_clock
        self._sleep_calls = []

    @override
    async def sleep(self, *, seconds: int | float) -> None:
        """
        Record an async sleep call and advance the monotonic clock.

        Args:
            seconds (int | float): Seconds to record and advance.

        Raises:
            TypeError: If `seconds` is not an integer or float.
            ValueError: If `seconds` is negative.

        Example:
        ```python
        from clock_pattern.sleepers.testing import MockSleeperAsync
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())
        await sleeper.sleep(seconds=1)

        sleeper.assert_sleep_method_was_called_once_with(seconds=1)
        ```
        """
        PositiveOrZeroNumberValueObject(value=seconds, title='MockSleeperAsync', parameter='seconds')

        await self._sleep_mock(seconds=seconds)
        self._sleep_calls.append(seconds)
        self._monotonic_clock.advance(seconds=seconds)

    def assert_sleep_method_was_called_once_with(self, *, seconds: int | float) -> None:
        """
        Assert that `sleep()` was awaited exactly once with `seconds`.

        Args:
            seconds (int | float): Expected sleep duration.

        Raises:
            TypeError: If `seconds` is not an integer or float.
            ValueError: If `seconds` is negative.

        Example:
        ```python
        from clock_pattern.sleepers.testing import MockSleeperAsync
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())
        await sleeper.sleep(seconds=1)

        sleeper.assert_sleep_method_was_called_once_with(seconds=1)
        ```
        """
        PositiveOrZeroNumberValueObject(value=seconds, title='MockSleeperAsync', parameter='seconds')

        self._sleep_mock.assert_awaited_once_with(seconds=seconds)

    def assert_sleep_method_was_not_called(self) -> None:
        """
        Assert that `sleep()` was not awaited.

        Example:
        ```python
        from clock_pattern.sleepers.testing import MockSleeperAsync
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())

        sleeper.assert_sleep_method_was_not_called()
        ```
        """
        self._sleep_mock.assert_not_awaited()

    @override
    @asynccontextmanager
    async def minimum_duration(self, *, seconds: int | float) -> AsyncIterator[None]:
        """
        Create an async context manager that ensures the enclosed work takes at least `seconds`.

        Args:
            seconds (int | float): The minimum elapsed duration for the enclosed asynchronous work.

        Raises:
            TypeError: If `seconds` is not an integer or float.
            ValueError: If `seconds` is negative.

        Returns:
            AbstractAsyncContextManager[None]: An async context manager that records a sleep call for any remaining
            duration when the enclosed work exits.

        Example:
        ```python
        from clock_pattern.sleepers.testing import MockSleeperAsync
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())
        async with sleeper.minimum_duration(seconds=1):
            pass
        ```
        """
        PositiveOrZeroNumberValueObject(value=seconds, title='MockSleeperAsync', parameter='seconds')

        started_time = self._monotonic_clock.current_seconds()
        try:
            yield

        finally:
            elapsed_seconds = self._monotonic_clock.current_seconds() - started_time
            remaining_seconds = seconds - elapsed_seconds

            if remaining_seconds > 0:
                await self.sleep(seconds=remaining_seconds)

    @property
    def sleep_calls(self) -> tuple[float, ...]:
        """
        Retrieve recorded sleep durations.

        Returns:
            tuple[float, ...]: Recorded sleep durations.

        Example:
        ```python
        from clock_pattern.sleepers.testing import MockSleeperAsync
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        sleeper = MockSleeperAsync(monotonic_clock=MockMonotonicClock())
        await sleeper.sleep(seconds=1)
        await sleeper.sleep(seconds=2)

        assert sleeper.sleep_calls == (1.0, 2.0)
        ```
        """
        return tuple(self._sleep_calls)
