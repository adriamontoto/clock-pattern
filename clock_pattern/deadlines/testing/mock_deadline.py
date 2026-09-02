"""
Controllable mock deadline for deterministic tests.
"""

from sys import version_info

if version_info >= (3, 12):
    from typing import Self, override  # pragma: no cover
else:
    from typing_extensions import Self, override  # pragma: no cover

from types import TracebackType
from unittest.mock import Mock

from value_object_pattern.usables import PositiveOrZeroNumberValueObject

from clock_pattern.deadlines.errors import TimeoutExpiredError
from clock_pattern.deadlines.models import Deadline


class MockDeadline(Deadline):
    """
    Test double for `Deadline` with explicitly controlled elapsed seconds.

    Example:
    ```python
    from clock_pattern.deadlines.testing import MockDeadline

    deadline = MockDeadline(seconds=2)
    deadline.advance(seconds=1)
    print(deadline.remaining_seconds)
    # >>> 1.0
    ```
    """

    _seconds: PositiveOrZeroNumberValueObject
    _elapsed_seconds: PositiveOrZeroNumberValueObject
    _raise_if_expired_mock: Mock

    def __init__(self, *, seconds: int | float, elapsed_seconds: int | float = 0.0) -> None:
        """
        Create a mock deadline.

        Args:
            seconds (int | float): Duration before the deadline expires.
            elapsed_seconds (int | float, optional): Initial elapsed duration. Defaults to `0.0`.

        Raises:
            TypeError: If seconds is not an integer or float.
            ValueError: If seconds is negative.
            TypeError: If elapsed_seconds is not an integer or float.
            ValueError: If elapsed_seconds is negative.

        Example:
        ```python
        from clock_pattern.deadlines.testing import MockDeadline

        deadline = MockDeadline(seconds=2, elapsed_seconds=1)
        print(deadline.remaining_seconds)
        # >>> 1.0
        ```
        """
        self._seconds = PositiveOrZeroNumberValueObject(value=seconds, title='MockDeadline', parameter='seconds')
        self._elapsed_seconds = PositiveOrZeroNumberValueObject(value=elapsed_seconds, title='MockDeadline', parameter='elapsed_seconds')  # noqa: E501  # fmt: skip
        self._raise_if_expired_mock = Mock()

    @property
    @override
    def elapsed_seconds(self) -> float:
        """
        Retrieve the controlled elapsed seconds.

        Returns:
            float: Controlled elapsed seconds.

        Example:
        ```python
        from clock_pattern.deadlines.testing import MockDeadline

        deadline = MockDeadline(seconds=2, elapsed_seconds=1)
        print(deadline.elapsed_seconds)
        # >>> 1.0
        ```
        """
        return self._elapsed_seconds.value

    @property
    @override
    def remaining_seconds(self) -> float:
        """
        Retrieve remaining seconds before expiry.

        Returns:
            float: Remaining seconds, never less than zero.

        Example:
        ```python
        from clock_pattern.deadlines.testing import MockDeadline

        deadline = MockDeadline(seconds=2, elapsed_seconds=1)
        print(deadline.remaining_seconds)
        # >>> 1.0
        ```
        """
        return max(0.0, self._seconds.value - self._elapsed_seconds.value)

    @property
    @override
    def expired(self) -> bool:
        """
        Check whether the controlled duration reached the deadline.

        Returns:
            bool: `True` when elapsed seconds are greater than or equal to the configured duration.

        Example:
        ```python
        from clock_pattern.deadlines.testing import MockDeadline

        deadline = MockDeadline(seconds=1, elapsed_seconds=1)
        print(deadline.expired)
        # >>> True
        ```
        """
        return self._elapsed_seconds.value >= self._seconds.value

    @override
    def raise_if_expired(self) -> None:
        """
        Record the expiry check and raise if the controlled duration expired.

        Raises:
            TimeoutExpiredError: If the controlled duration reached the deadline.

        Example:
        ```python
        from clock_pattern.deadlines.testing import MockDeadline

        deadline = MockDeadline(seconds=1)
        deadline.advance(seconds=1)
        deadline.raise_if_expired()
        ```
        """
        self._raise_if_expired_mock()

        elapsed_seconds = self.elapsed_seconds
        if elapsed_seconds >= self._seconds.value:
            raise TimeoutExpiredError(elapsed_seconds=elapsed_seconds)

    def advance(self, *, seconds: int | float) -> None:
        """
        Advance elapsed time by `seconds`.

        Args:
            seconds (int | float): Seconds to add to the elapsed duration.

        Raises:
            TypeError: If `seconds` is not an integer or float.
            ValueError: If `seconds` is negative or non-finite.

        Example:
        ```python
        from clock_pattern.deadlines.testing import MockDeadline

        deadline = MockDeadline(seconds=2)
        deadline.advance(seconds=1)
        print(deadline.elapsed_seconds)
        # >>> 1.0
        ```
        """
        PositiveOrZeroNumberValueObject(value=seconds, title='MockDeadline', parameter='seconds')
        self._elapsed_seconds = PositiveOrZeroNumberValueObject(value=self._elapsed_seconds.value + seconds, title='MockDeadline', parameter='elapsed_seconds')  # noqa: E501  # fmt: skip

    @override
    def __enter__(self) -> Self:
        """
        Return this active mock deadline when entering a context manager.

        Returns:
            Self: This mock deadline instance.

        Example:
        ```python
        from clock_pattern.deadlines.testing import MockDeadline

        with MockDeadline(seconds=1) as deadline:
            print(deadline.remaining_seconds)
        # >>> 1.0
        ```
        """
        self.raise_if_expired()
        return self

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """
        Raise if the mock deadline expired while a successful block ran.

        Args:
            exc_type (type[BaseException]): Exception type raised by the managed block, if any.
            exc_value (BaseException): Exception raised by the managed block, if any.
            traceback (TracebackType): Traceback raised by the managed block, if any.

        Returns:
            bool | None: `None`, so exceptions from the managed block are not suppressed.

        Raises:
            TimeoutExpiredError: If the mock deadline expired.

        Example:
        ```python
        from clock_pattern.deadlines.testing import MockDeadline

        with MockDeadline(seconds=1):
            pass
        ```
        """
        if exc_value is None:
            self.raise_if_expired()

        return None

    def assert_raise_if_expired_method_was_called_once(self) -> None:
        """
        Assert that `raise_if_expired()` was called exactly once.

        Example:
        ```python
        from clock_pattern.deadlines.testing import MockDeadline

        deadline = MockDeadline(seconds=1)
        deadline.raise_if_expired()
        deadline.assert_raise_if_expired_method_was_called_once()
        ```
        """
        self._raise_if_expired_mock.assert_called_once_with()

    def assert_raise_if_expired_method_was_not_called(self) -> None:
        """
        Assert that `raise_if_expired()` was not called.

        Example:
        ```python
        from clock_pattern.deadlines.testing import MockDeadline

        MockDeadline(seconds=1).assert_raise_if_expired_method_was_not_called()
        ```
        """
        self._raise_if_expired_mock.assert_not_called()
