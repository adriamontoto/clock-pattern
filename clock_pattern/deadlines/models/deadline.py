"""
Abstract deadline contract for injectable timeout state.
"""

from abc import abstractmethod
from contextlib import AbstractContextManager


class Deadline(AbstractContextManager['Deadline']):
    """
    Define the interface for injectable deadlines.

    Example:
    ```python
    from clock_pattern import SystemDeadline, SystemMonotonicClock

    with SystemDeadline(seconds=1, monotonic_clock=SystemMonotonicClock()) as deadline:
        print(deadline.remaining_seconds)
    ```
    """

    @property
    @abstractmethod
    def elapsed_seconds(self) -> float:
        """
        Retrieve elapsed seconds since the deadline started.

        Returns:
            float: Elapsed seconds since the deadline started.

        Example:
        ```python
        from clock_pattern import SystemDeadline
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)
        monotonic_clock.advance(seconds=0.25)
        print(deadline.elapsed_seconds)
        # >>> 0.25
        ```
        """

    @property
    @abstractmethod
    def remaining_seconds(self) -> float:
        """
        Retrieve remaining seconds before expiry.

        Returns:
            float: Remaining seconds, never less than zero.

        Example:
        ```python
        from clock_pattern import SystemDeadline
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)
        monotonic_clock.advance(seconds=0.25)
        print(deadline.remaining_seconds)
        # >>> 0.75
        ```
        """

    @property
    @abstractmethod
    def expired(self) -> bool:
        """
        Check whether the deadline has expired.

        Returns:
            bool: `True` when the configured duration has elapsed.

        Example:
        ```python
        from clock_pattern import SystemDeadline
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)
        monotonic_clock.advance(seconds=1)
        print(deadline.expired)
        # >>> True
        ```
        """

    @abstractmethod
    def raise_if_expired(self) -> None:
        """
        Raise when the configured duration has elapsed.

        Raises:
            TimeoutExpiredError: If the deadline expired.

        Example:
        ```python
        from clock_pattern import SystemDeadline
        from clock_pattern.monotonic_clocks.testing import MockMonotonicClock

        monotonic_clock = MockMonotonicClock()
        deadline = SystemDeadline(seconds=1, monotonic_clock=monotonic_clock)
        monotonic_clock.advance(seconds=1)
        deadline.raise_if_expired()
        ```
        """
