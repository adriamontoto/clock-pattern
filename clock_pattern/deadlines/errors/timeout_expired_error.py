"""
Deadline exceptions.
"""


class TimeoutExpiredError(TimeoutError):
    """
    Raised when a deadline timeout expires.
    """

    _elapsed_seconds: float

    def __init__(self, *, elapsed_seconds: float) -> None:
        """
        Create a `TimeoutExpiredError` with the configured duration.

        Args:
            elapsed_seconds (float): Duration in seconds that expired.
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
        """
        return self._elapsed_seconds
