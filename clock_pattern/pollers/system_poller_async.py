"""
System-backed asynchronous polling helper.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from asyncio import timeout
from collections.abc import Awaitable, Callable
from inspect import isawaitable

from value_object_pattern.usables import BooleanValueObject, PositiveNumberValueObject, PositiveOrZeroNumberValueObject

from clock_pattern.deadlines import SystemDeadline, TimeoutExpiredError
from clock_pattern.monotonic_clocks.models import MonotonicClock
from clock_pattern.pollers.models import PollerAsync
from clock_pattern.sleepers.models import SleeperAsync


class SystemPollerAsync(PollerAsync):
    """
    Poll an asynchronous condition until it succeeds or a timeout expires.

    Example:
    ```python
    from clock_pattern import SystemMonotonicClock, SystemPollerAsync, SystemSleeperAsync

    monotonic_clock = SystemMonotonicClock()
    sleeper = SystemSleeperAsync(monotonic_clock=monotonic_clock)
    poller = SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock)
    await poller.poll_until(condition=lambda: True, timeout_seconds=1)
    ```
    """

    _sleeper: SleeperAsync
    _monotonic_clock: MonotonicClock

    def __init__(self, *, sleeper: SleeperAsync, monotonic_clock: MonotonicClock) -> None:
        """
        Create an asynchronous poller.

        Args:
            sleeper (SleeperAsync): Async sleeper used between condition checks.
            monotonic_clock (MonotonicClock): Monotonic clock used for timeout measurement.

        Example:
        ```python
        from clock_pattern import SystemMonotonicClock, SystemPollerAsync, SystemSleeperAsync

        monotonic_clock = SystemMonotonicClock()
        sleeper = SystemSleeperAsync(monotonic_clock=monotonic_clock)
        poller = SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock)
        await poller.poll_until(condition=lambda: True, timeout_seconds=1)
        ```
        """
        self._monotonic_clock = monotonic_clock
        self._sleeper = sleeper

    @override
    async def poll_until(
        self,
        *,
        condition: Callable[[], bool | Awaitable[bool]],
        timeout_seconds: float,
        interval_seconds: float = 0.1,
    ) -> None:
        """
        Poll `condition` until it returns or awaits to `True`.

        The timeout covers condition evaluation and sleeping, cancelling overdue awaits through asyncio. Blocking
        synchronous code and coroutines that suppress cancellation cannot be forcibly interrupted. Injected-clock checks
        also reject results after a positive timeout. A zero timeout allows one immediate evaluation, but cancels it if
        it suspends. External cancellation and condition exceptions propagate.

        Args:
            condition (Callable[[], bool | Awaitable[bool]]): Sync or async condition checked until it is true.
            timeout_seconds (float): Maximum duration to wait.
            interval_seconds (float): Duration between condition checks. Defaults to `0.1`.

        Raises:
            TypeError: If `timeout_seconds` is not an integer or a float.
            ValueError: If `timeout_seconds` is negative.
            TypeError: If `interval_seconds` is not an integer or a float.
            ValueError: If `interval_seconds` is not positive.
            TypeError: If `condition` does not return a boolean.
            TimeoutExpiredError: If the timeout expires before `condition` returns `True`.

        Example:
        ```python
        from clock_pattern import SystemMonotonicClock, SystemPollerAsync, SystemSleeperAsync

        monotonic_clock = SystemMonotonicClock()
        sleeper = SystemSleeperAsync(monotonic_clock=monotonic_clock)
        await SystemPollerAsync(sleeper=sleeper, monotonic_clock=monotonic_clock).poll_until(
            condition=lambda: True,
            timeout_seconds=1,
            interval_seconds=0.1,
        )
        ```
        """
        PositiveOrZeroNumberValueObject(value=timeout_seconds, title='SystemPollerAsync', parameter='timeout_seconds')
        PositiveNumberValueObject(value=interval_seconds, title='SystemPollerAsync', parameter='interval_seconds')

        deadline = SystemDeadline(seconds=timeout_seconds, monotonic_clock=self._monotonic_clock)

        timeout_context = timeout(timeout_seconds)
        try:
            async with timeout_context:
                await self._poll_until(
                    condition=condition,
                    deadline=deadline,
                    timeout_seconds=timeout_seconds,
                    interval_seconds=interval_seconds,
                )

        except TimeoutError as error:
            if timeout_context.expired():
                raise TimeoutExpiredError(elapsed_seconds=deadline.elapsed_seconds) from error

            raise

    async def _poll_until(
        self,
        *,
        condition: Callable[[], bool | Awaitable[bool]],
        deadline: SystemDeadline,
        timeout_seconds: float,
        interval_seconds: float,
    ) -> None:
        """
        Poll using the injected clock while the enclosing asyncio timeout bounds awaits.

        Args:
            condition (Callable[[], bool | Awaitable[bool]]): Sync or async condition checked until it is true.
            deadline (SystemDeadline): Deadline used to check for timeout expiration.
            timeout_seconds (float): Maximum duration to wait.
            interval_seconds (float): Duration between condition checks.

        Raises:
            TypeError: If `condition` does not return a boolean.
            TimeoutExpiredError: If the timeout expires before `condition` returns `True`.
        """
        while True:
            condition_result = condition()

            if isawaitable(condition_result):
                condition_result = await condition_result

            condition_result = BooleanValueObject(value=condition_result, title='SystemPollerAsync', parameter='condition').value  # noqa: E501  # fmt: skip
            if timeout_seconds > 0 and deadline.elapsed_seconds > timeout_seconds:
                deadline.raise_if_expired()

            if condition_result:
                return

            deadline.raise_if_expired()
            await self._sleeper.sleep(seconds=min(interval_seconds, deadline.remaining_seconds))
