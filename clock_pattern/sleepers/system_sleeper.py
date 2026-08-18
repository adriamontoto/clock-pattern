"""
System-backed synchronous sleeper.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from collections.abc import Iterator
from contextlib import contextmanager
from time import sleep

from value_object_pattern import UnionValueObject
from value_object_pattern.usables import PositiveOrZeroFloatValueObject, PositiveOrZeroIntegerValueObject

from clock_pattern.monotonic_clocks.models import MonotonicClock
from clock_pattern.sleepers.models import Sleeper


class SystemSleeper(Sleeper):
    """
    Pause synchronous execution using the operating system sleep function.

    Example:
    ```python
    from clock_pattern import SystemSleeper
    from clock_pattern.monotonic_clocks import SystemMonotonicClock

    sleeper = SystemSleeper(monotonic_clock=SystemMonotonicClock())
    sleeper.sleep(seconds=1)
    ```
    """

    _monotonic_clock: MonotonicClock

    def __init__(self, *, monotonic_clock: MonotonicClock) -> None:
        """
        Create a system-backed synchronous sleeper.

        Args:
            monotonic_clock (MonotonicClock): The monotonic clock to use.

        Raises:
            TypeError: If `monotonic_clock` is not a `MonotonicClock`.

        Example:
        ```python
        from clock_pattern import SystemSleeper
        from clock_pattern.monotonic_clocks import SystemMonotonicClock

        sleeper = SystemSleeper(monotonic_clock=SystemMonotonicClock())
        sleeper.sleep(seconds=1)
        ```
        """
        if not isinstance(monotonic_clock, MonotonicClock):
            raise TypeError(f'SystemSleeper monotonic_clock <<<{monotonic_clock}>>> must be a MonotonicClock. Got <<<{type(monotonic_clock).__name__}>>> type.')  # noqa: E501  # fmt: skip

        self._monotonic_clock = monotonic_clock

    @override
    def sleep(self, *, seconds: int | float) -> None:
        """
        Pause synchronous execution for `seconds`.

        Args:
            seconds (int | float): The number of seconds to pause execution.

        Raises:
            TypeError: If `seconds` is not an integer.
            ValueError: If `seconds` is not a positive or zero integer.
            TypeError: If `seconds` is not a float.
            ValueError: If `seconds` is not a positive or zero float.

        Example:
        ```python
        from clock_pattern import SystemSleeper
        from clock_pattern.monotonic_clocks import SystemMonotonicClock

        sleeper = SystemSleeper(monotonic_clock=SystemMonotonicClock())
        sleeper.sleep(seconds=1)
        ```
        """
        UnionValueObject[PositiveOrZeroIntegerValueObject | PositiveOrZeroFloatValueObject](
            value=seconds,  # type: ignore[arg-type]
            title='SystemSleeper',
            parameter='seconds',
        )

        sleep(seconds)

    @override
    @contextmanager
    def minimum_duration(self, *, seconds: int | float) -> Iterator[None]:
        """
        Create a context manager that ensures the enclosed work takes at least `seconds`.

        Args:
            seconds (int | float): The minimum elapsed duration for the enclosed synchronous work.

        Returns:
            AbstractContextManager[None]: A context manager that sleeps for any remaining duration when the enclosed
            work exits.

        Raises:
            TypeError: If `seconds` is not an integer.
            ValueError: If `seconds` is not a positive or zero integer.
            TypeError: If `seconds` is not a float.
            ValueError: If `seconds` is not a positive or zero float.

        Example:
        ```python
        from clock_pattern import SystemSleeper
        from clock_pattern.monotonic_clocks import SystemMonotonicClock

        sleeper = SystemSleeper(monotonic_clock=SystemMonotonicClock())

        with sleeper.minimum_duration(seconds=1):
            pass
        ```
        """
        UnionValueObject[PositiveOrZeroIntegerValueObject | PositiveOrZeroFloatValueObject](
            value=seconds,  # type: ignore[arg-type]
            title='SystemSleeper',
            parameter='seconds',
        )

        started_time = self._monotonic_clock.current_seconds()
        try:
            yield

        finally:
            elapsed_seconds = self._monotonic_clock.current_seconds() - started_time
            remaining_seconds = seconds - elapsed_seconds

            if remaining_seconds > 0:
                self.sleep(seconds=remaining_seconds)
