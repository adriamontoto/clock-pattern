"""
Testing synchronous sleeper with call assertions.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import Mock

from value_object_pattern.usables import PositiveOrZeroNumberValueObject

from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.sleepers.models import Sleeper


class MockSleeper(Sleeper):
    """
    Test double for `Sleeper` that records sleep calls and advances a monotonic clock.

    Example:
    ```python
    from clock_pattern.sleepers.testing import MockSleeper
    from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

    sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())
    sleeper.sleep(seconds=1)

    sleeper.assert_sleep_method_was_called_once_with(seconds=1)
    ```
    """

    _sleep_mock: Mock
    _monotonic_clock: MockMonotonicClock
    _sleep_calls: list[float]

    def __init__(self, *, monotonic_clock: MockMonotonicClock) -> None:
        """
        Create a mock sleeper.

        Args:
            monotonic_clock (MockMonotonicClock): Monotonic clock advanced by sleep calls.

        Example:
        ```python
        from clock_pattern.sleepers.testing import MockSleeper
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())
        sleeper.sleep(seconds=1)

        sleeper.assert_sleep_method_was_called_once_with(seconds=1)
        ```
        """
        self._sleep_mock = Mock()
        self._monotonic_clock = monotonic_clock
        self._sleep_calls = []

    @override
    def sleep(self, *, seconds: float) -> None:
        """
        Record a sleep call and advance the monotonic clock.

        Args:
            seconds (float): Seconds to record and advance.

        Raises:
            TypeError: If `seconds` is not an integer or float.
            ValueError: If `seconds` is negative.

        Example:
        ```python
        from clock_pattern.sleepers.testing import MockSleeper
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())
        sleeper.sleep(seconds=1)

        sleeper.assert_sleep_method_was_called_once_with(seconds=1)
        ```
        """
        PositiveOrZeroNumberValueObject(value=seconds, title='MockSleeper', parameter='seconds')

        self._sleep_mock(seconds=seconds)
        self._sleep_calls.append(seconds)
        self._monotonic_clock.advance(seconds=seconds)

    def assert_sleep_method_was_called_once_with(self, *, seconds: float) -> None:
        """
        Assert that `sleep()` was called exactly once with `seconds`.

        Args:
            seconds (float): Expected sleep duration.

        Raises:
            TypeError: If `seconds` is not an integer or float.
            ValueError: If `seconds` is negative.

        Example:
        ```python
        from clock_pattern.sleepers.testing import MockSleeper
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())
        sleeper.sleep(seconds=1)

        sleeper.assert_sleep_method_was_called_once_with(seconds=1)
        ```
        """
        PositiveOrZeroNumberValueObject(value=seconds, title='MockSleeper', parameter='seconds')

        self._sleep_mock.assert_called_once_with(seconds=seconds)

    def assert_sleep_method_was_not_called(self) -> None:
        """
        Assert that `sleep()` was not called.

        Example:
        ```python
        from clock_pattern.sleepers.testing import MockSleeper
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())

        sleeper.assert_sleep_method_was_not_called()
        ```
        """
        self._sleep_mock.assert_not_called()

    @override
    @contextmanager
    def minimum_duration(self, *, seconds: float) -> Iterator[None]:
        """
        Create a context manager that ensures the enclosed work takes at least `seconds`.

        Args:
            seconds (float): The minimum elapsed duration for the enclosed synchronous work.

        Raises:
            TypeError: If `seconds` is not an integer or float.
            ValueError: If `seconds` is negative.

        Returns:
            AbstractContextManager[None]: A context manager that records a sleep call for any remaining duration when
            the enclosed work exits.

        Example:
        ```python
        from clock_pattern.sleepers.testing import MockSleeper
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())
        with sleeper.minimum_duration(seconds=1):
            pass

        sleeper.assert_sleep_method_was_called_once_with(seconds=1)
        ```
        """
        PositiveOrZeroNumberValueObject(value=seconds, title='MockSleeper', parameter='seconds')

        started_time = self._monotonic_clock.current_seconds()
        try:
            yield

        finally:
            elapsed_seconds = self._monotonic_clock.current_seconds() - started_time
            remaining_seconds = seconds - elapsed_seconds

            if remaining_seconds > 0:
                self.sleep(seconds=remaining_seconds)

    @property
    def sleep_calls(self) -> tuple[float, ...]:
        """
        Retrieve recorded sleep durations.

        Returns:
            tuple[float, ...]: Recorded sleep durations.

        Example:
        ```python
        from clock_pattern.sleepers.testing import MockSleeper
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        sleeper = MockSleeper(monotonic_clock=MockMonotonicClock())
        sleeper.sleep(seconds=1)
        sleeper.sleep(seconds=2)

        assert sleeper.sleep_calls == (1, 2)
        ```
        """
        return tuple(self._sleep_calls)
