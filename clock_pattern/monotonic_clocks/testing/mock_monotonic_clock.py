"""
Controllable mock monotonic clock for deterministic tests.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

from unittest.mock import Mock

from value_object_pattern.usables import PositiveOrZeroNumberValueObject

from clock_pattern.monotonic_clocks.models import MonotonicClock


class MockMonotonicClock(MonotonicClock):
    """
    Test double for `MonotonicClock` with explicitly controlled seconds.

    Example:
    ```python
    from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

    monotonic_clock = MockMonotonicClock()
    monotonic_clock.advance(seconds=1)
    print(monotonic_clock.current_seconds())
    # >>> 1.0
    ```
    """

    _current_seconds: PositiveOrZeroNumberValueObject
    _current_seconds_mock: Mock

    def __init__(self, *, current_seconds: float = 0.0) -> None:
        """
        Create a mock monotonic clock.

        Args:
            current_seconds (float): Initial monotonic timestamp in seconds. Defaults to zero.

        Raises:
            TypeError: If `current_seconds` is not an integer or float.
            ValueError: If `current_seconds` is negative or non-finite.

        Example:
        ```python
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock(current_seconds=10)
        print(monotonic_clock.current_seconds())
        # >>> 10.0
        ```
        """
        self._current_seconds = PositiveOrZeroNumberValueObject(
            value=current_seconds,
            title='MockMonotonicClock',
            parameter='current_seconds',
        )
        self._current_seconds_mock = Mock()

    @override
    def current_seconds(self) -> float:
        """
        Retrieve the configured monotonic timestamp.

        Returns:
            float: Current mock monotonic timestamp.

        Example:
        ```python
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock(current_seconds=1.5)
        print(monotonic_clock.current_seconds())
        # >>> 1.5
        ```
        """
        self._current_seconds_mock()

        return self._current_seconds.value

    def assert_current_seconds_method_was_called_once(self) -> None:
        """
        Assert that `current_seconds()` was called exactly once.
        """
        self._current_seconds_mock.assert_called_once_with()

    def assert_current_seconds_method_was_not_called(self) -> None:
        """
        Assert that `current_seconds()` was not called.
        """
        self._current_seconds_mock.assert_not_called()

    def advance(self, *, seconds: float) -> None:
        """
        Advance the clock by `seconds`.

        Args:
            seconds (float): Seconds to add to the current timestamp.

        Raises:
            TypeError: If `seconds` is not an integer or float.
            ValueError: If `seconds` is negative or non-finite.

        Example:
        ```python
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        monotonic_clock.advance(seconds=1)
        print(monotonic_clock.current_seconds())
        # >>> 1.0
        ```
        """
        PositiveOrZeroNumberValueObject(value=seconds, title='MockMonotonicClock', parameter='seconds')

        self._current_seconds = PositiveOrZeroNumberValueObject(
            value=self._current_seconds.value + seconds,
            title='MockMonotonicClock',
            parameter='current_seconds',
        )

    def set_current_seconds(self, *, current_seconds: float) -> None:
        """
        Set the current monotonic timestamp.

        Args:
            current_seconds (float): Replacement monotonic timestamp in seconds.

        Raises:
            TypeError: If `current_seconds` is not an integer or float.
            ValueError: If `current_seconds` is negative, non-finite, or lower than the current timestamp.

        Example:
        ```python
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        monotonic_clock.set_current_seconds(current_seconds=2)
        print(monotonic_clock.current_seconds())
        # >>> 2.0
        ```
        """
        new_current_seconds = PositiveOrZeroNumberValueObject(
            value=current_seconds,
            title='MockMonotonicClock',
            parameter='current_seconds',
        )

        if new_current_seconds.value < self._current_seconds.value:
            raise ValueError(f'MockMonotonicClock current_seconds <<<{new_current_seconds.value}>>> must be greater than or equal to current seconds <<<{self._current_seconds.value}>>>.')  # noqa: E501 # fmt: skip

        self._current_seconds = new_current_seconds
