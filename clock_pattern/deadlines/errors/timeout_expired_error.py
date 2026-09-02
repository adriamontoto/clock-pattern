"""
Deadline exceptions.
"""


class TimeoutExpiredError(TimeoutError):
    """
    Raised when a deadline timeout expires.

    Example:
    ```python
    from clock_pattern import TimeoutExpiredError

    error = TimeoutExpiredError(elapsed_seconds=1.5)
    print(error)
    # >>> Deadline expired after <<<1.5>>> seconds.
    ```
    """

    _elapsed_seconds: float

    def __init__(self, *, elapsed_seconds: float) -> None:
        """
        Create a `TimeoutExpiredError` with the configured duration.

        Args:
            elapsed_seconds (float): Duration in seconds that expired.

        Example:
        ```python
        from clock_pattern import TimeoutExpiredError

        error = TimeoutExpiredError(elapsed_seconds=1.5)
        print(error)
        # >>> Deadline expired after <<<1.5>>> seconds.
        ```
        """
        self._elapsed_seconds = elapsed_seconds

        message = f'Deadline expired after <<<{self._elapsed_seconds}>>> seconds.'
        super().__init__(message)

    @property
    def elapsed_seconds(self) -> float:
        """
        Retrieve the duration in seconds that expired.

        Returns:
            float: Duration in seconds that expired.

        Example:
        ```python
        from clock_pattern import TimeoutExpiredError

        error = TimeoutExpiredError(elapsed_seconds=1.5)
        print(error.elapsed_seconds)
        # >>> 1.5
        ```
        """
        return self._elapsed_seconds
