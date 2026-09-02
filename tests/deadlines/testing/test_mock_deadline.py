"""
Test MockDeadline deadline.
"""

from object_mother_pattern import FloatMother
from pytest import mark, raises as assert_raises

from clock_pattern.deadlines import Deadline, TimeoutExpiredError
from clock_pattern.deadlines.testing import MockDeadline


@mark.unit_testing
def test_mock_deadline_happy_path() -> None:
    """
    Test MockDeadline deadline happy path.
    """
    deadline = MockDeadline(seconds=2)

    assert isinstance(deadline, Deadline)
    assert type(deadline.elapsed_seconds) is float
    assert deadline.elapsed_seconds == 0.0
    assert type(deadline.remaining_seconds) is float
    assert deadline.remaining_seconds == 2.0
    assert deadline.expired is False


@mark.unit_testing
def test_mock_deadline_initial_elapsed_seconds() -> None:
    """
    Test MockDeadline accepts initial elapsed seconds.
    """
    deadline = MockDeadline(seconds=2, elapsed_seconds=0.5)

    assert deadline.elapsed_seconds == 0.5
    assert deadline.remaining_seconds == 1.5


@mark.unit_testing
def test_mock_deadline_remaining_seconds_property_returns_zero_when_deadline_expired() -> None:
    """
    Test MockDeadline remaining_seconds property returns zero when deadline expired.
    """
    assert MockDeadline(seconds=1, elapsed_seconds=2).remaining_seconds == 0.0


@mark.unit_testing
def test_mock_deadline_expired_property_returns_true_when_elapsed_seconds_reaches_deadline() -> None:
    """
    Test MockDeadline expired property returns true when elapsed seconds reaches deadline.
    """
    assert MockDeadline(seconds=1, elapsed_seconds=1).expired is True


@mark.unit_testing
def test_mock_deadline_raise_if_expired_method_does_not_raise_before_deadline() -> None:
    """
    Test MockDeadline raise_if_expired method records a non-expired check.
    """
    deadline = MockDeadline(seconds=1)

    assert deadline.raise_if_expired() is None
    deadline.assert_raise_if_expired_method_was_called_once()


@mark.unit_testing
def test_mock_deadline_raise_if_expired_method_reports_controlled_elapsed_seconds() -> None:
    """
    Test MockDeadline raise_if_expired method reports controlled elapsed seconds.
    """
    deadline = MockDeadline(seconds=1, elapsed_seconds=2)

    with assert_raises(
        expected_exception=TimeoutExpiredError,
        match=r'Deadline expired after <<<2.0>>> seconds\.',
    ) as exception_info:
        deadline.raise_if_expired()

    assert exception_info.value.elapsed_seconds == 2.0
    deadline.assert_raise_if_expired_method_was_called_once()


@mark.unit_testing
def test_mock_deadline_assert_raise_if_expired_method_was_not_called() -> None:
    """
    Test MockDeadline asserts raise_if_expired was not called.
    """
    MockDeadline(seconds=1).assert_raise_if_expired_method_was_not_called()


@mark.unit_testing
def test_mock_deadline_enter_method_raises_before_expired_body() -> None:
    """
    Test MockDeadline context manager rejects an already-expired entry.
    """
    with (
        assert_raises(
            expected_exception=TimeoutExpiredError,
            match=r'Deadline expired after <<<1.0>>> seconds\.',
        ),
        MockDeadline(seconds=1, elapsed_seconds=1),
    ):
        raise AssertionError('expired deadline body must not run')


@mark.unit_testing
def test_mock_deadline_exit_method_raises_after_successful_expired_body() -> None:
    """
    Test MockDeadline context manager checks expiry after a successful body.
    """
    deadline = MockDeadline(seconds=1)

    with (
        assert_raises(
            expected_exception=TimeoutExpiredError,
            match=r'Deadline expired after <<<2.0>>> seconds\.',
        ),
        deadline,
    ):
        deadline.advance(seconds=2)


@mark.unit_testing
def test_mock_deadline_exit_method_preserves_body_exception_after_expiry() -> None:
    """
    Test MockDeadline context manager preserves a body exception after expiry.
    """
    deadline = MockDeadline(seconds=1)

    with assert_raises(expected_exception=RuntimeError, match=r'block failed'), deadline:
        deadline.advance(seconds=2)
        raise RuntimeError('block failed')

    deadline.assert_raise_if_expired_method_was_called_once()


@mark.unit_testing
def test_mock_deadline_advance_method_happy_path() -> None:
    """
    Test MockDeadline advance method happy path.
    """
    deadline = MockDeadline(seconds=3, elapsed_seconds=1)

    deadline.advance(seconds=1.5)

    assert deadline.elapsed_seconds == 2.5
    assert deadline.remaining_seconds == 0.5


@mark.unit_testing
def test_mock_deadline_advance_method_zero_value() -> None:
    """
    Test MockDeadline advance method accepts zero.
    """
    deadline = MockDeadline(seconds=1)

    deadline.advance(seconds=0)

    assert deadline.elapsed_seconds == 0.0


@mark.unit_testing
def test_mock_deadline_advance_method_positive_random_value() -> None:
    """
    Test MockDeadline advance method accepts random positive seconds.
    """
    seconds = FloatMother.positive()
    deadline = MockDeadline(seconds=seconds + 1)

    deadline.advance(seconds=seconds)

    assert deadline.elapsed_seconds == seconds


@mark.unit_testing
def test_mock_deadline_enter_method_returns_deadline() -> None:
    """
    Test MockDeadline context manager enter method returns deadline.
    """
    deadline = MockDeadline(seconds=1)

    with deadline as active_deadline:
        assert active_deadline is deadline


@mark.unit_testing
def test_mock_deadline_seconds_invalid_type() -> None:
    """
    Test MockDeadline raises TypeError if seconds has invalid type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'MockDeadline seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
    ):
        MockDeadline(seconds=FloatMother.invalid_type())


@mark.unit_testing
def test_mock_deadline_seconds_negative_random_value() -> None:
    """
    Test MockDeadline raises ValueError if seconds is random negative.
    """
    seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=rf'MockDeadline seconds <<<{seconds}>>> must be greater than or equal to zero.',
    ):
        MockDeadline(seconds=seconds)


@mark.unit_testing
def test_mock_deadline_seconds_negative_limit_value() -> None:
    """
    Test MockDeadline raises ValueError if seconds is negative limit.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'MockDeadline seconds <<<-1.0>>> must be greater than or equal to zero.',
    ):
        MockDeadline(seconds=-1.0)


@mark.unit_testing
def test_mock_deadline_seconds_non_finite_value() -> None:
    """
    Test MockDeadline raises ValueError if seconds is non-finite.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'MockDeadline seconds <<<inf>>> must be finite and representable as a float.',
    ):
        MockDeadline(seconds=float('inf'))


@mark.unit_testing
def test_mock_deadline_seconds_zero_value() -> None:
    """
    Test MockDeadline accepts zero seconds.
    """
    deadline = MockDeadline(seconds=0)

    assert deadline.remaining_seconds == 0.0
    assert deadline.expired is True


@mark.unit_testing
def test_mock_deadline_seconds_positive_random_value() -> None:
    """
    Test MockDeadline accepts random positive seconds.
    """
    seconds = FloatMother.positive()
    deadline = MockDeadline(seconds=seconds)

    assert deadline.remaining_seconds == seconds


@mark.unit_testing
def test_mock_deadline_elapsed_seconds_invalid_type() -> None:
    """
    Test MockDeadline raises TypeError if elapsed_seconds has invalid type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'MockDeadline elapsed_seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
    ):
        MockDeadline(seconds=1, elapsed_seconds=FloatMother.invalid_type())


@mark.unit_testing
def test_mock_deadline_elapsed_seconds_negative_random_value() -> None:
    """
    Test MockDeadline raises ValueError if elapsed_seconds is random negative.
    """
    elapsed_seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=rf'MockDeadline elapsed_seconds <<<{elapsed_seconds}>>> must be greater than or equal to zero.',
    ):
        MockDeadline(seconds=1, elapsed_seconds=elapsed_seconds)


@mark.unit_testing
def test_mock_deadline_elapsed_seconds_negative_limit_value() -> None:
    """
    Test MockDeadline raises ValueError if elapsed_seconds is negative limit.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'MockDeadline elapsed_seconds <<<-1.0>>> must be greater than or equal to zero.',
    ):
        MockDeadline(seconds=1, elapsed_seconds=-1.0)


@mark.unit_testing
def test_mock_deadline_elapsed_seconds_non_finite_value() -> None:
    """
    Test MockDeadline raises ValueError if elapsed_seconds is non-finite.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'MockDeadline elapsed_seconds <<<inf>>> must be finite and representable as a float.',
    ):
        MockDeadline(seconds=1, elapsed_seconds=float('inf'))


@mark.unit_testing
def test_mock_deadline_elapsed_seconds_zero_value() -> None:
    """
    Test MockDeadline accepts zero elapsed_seconds.
    """
    assert MockDeadline(seconds=1, elapsed_seconds=0).elapsed_seconds == 0.0


@mark.unit_testing
def test_mock_deadline_elapsed_seconds_positive_random_value() -> None:
    """
    Test MockDeadline accepts random positive elapsed_seconds.
    """
    elapsed_seconds = FloatMother.positive()

    assert MockDeadline(seconds=elapsed_seconds + 1, elapsed_seconds=elapsed_seconds).elapsed_seconds == elapsed_seconds


@mark.unit_testing
def test_mock_deadline_advance_method_invalid_type() -> None:
    """
    Test MockDeadline advance method raises TypeError if seconds has invalid type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match=r'MockDeadline seconds <<<.*>>> must be an integer or float. Got <<<.*>>> type.',
    ):
        MockDeadline(seconds=1).advance(seconds=FloatMother.invalid_type())


@mark.unit_testing
def test_mock_deadline_advance_method_negative_random_value() -> None:
    """
    Test MockDeadline advance method raises ValueError if seconds is random negative.
    """
    seconds = FloatMother.negative()

    with assert_raises(
        expected_exception=ValueError,
        match=rf'MockDeadline seconds <<<{seconds}>>> must be greater than or equal to zero.',
    ):
        MockDeadline(seconds=1).advance(seconds=seconds)


@mark.unit_testing
def test_mock_deadline_advance_method_negative_limit_value() -> None:
    """
    Test MockDeadline advance method raises ValueError if seconds is negative limit.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'MockDeadline seconds <<<-1.0>>> must be greater than or equal to zero.',
    ):
        MockDeadline(seconds=1).advance(seconds=-1.0)


@mark.unit_testing
def test_mock_deadline_advance_method_non_finite_value() -> None:
    """
    Test MockDeadline advance method raises ValueError if seconds is non-finite.
    """
    with assert_raises(
        expected_exception=ValueError,
        match=r'MockDeadline seconds <<<inf>>> must be finite and representable as a float.',
    ):
        MockDeadline(seconds=1).advance(seconds=float('inf'))
