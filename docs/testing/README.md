# Testing Guide

Clock Pattern is most useful when tests need stable time. Instead of freezing global modules or patching Python internals,
pass a test clock into the code under test.

## Choose The Right Test Clock

| Test clock | Use when | Behavior |
| --- | --- | --- |
| `FixedClock` | The test needs one stable datetime and date. | Always returns the configured instant and its date. |
| `MockClock` | The test also needs call assertions. | Requires prepared return values and records `now()` / `today()` calls. |
| `MockMonotonicClock` | The test needs deterministic elapsed time. | Advances only when the test tells it to. |
| `MockDeadline` | The unit depends directly on a deadline. | Advances explicitly and records expiry checks. |
| `MockSleeper` / `MockSleeperAsync` | The test needs sleep assertions without real waiting. | Records sleep calls and advances a mock monotonic clock. |

## FixedClock

Use `FixedClock` for simple deterministic tests:

```python
from datetime import datetime

from clock_pattern.clocks.testing import FixedClock

clock = FixedClock(instant=datetime(year=2025, month=1, day=1, hour=10, minute=30))

assert clock.now().isoformat() == '2025-01-01T10:30:00+00:00'
assert clock.today().isoformat() == '2025-01-01'
```

If the provided datetime is naive, UTC is added. If it already has a timezone, that timezone is preserved.

## MockClock

Use `MockClock` when behavior depends on whether the code requested a datetime or a date:

```python
from datetime import date

from clock_pattern.clocks.testing import MockClock

clock = MockClock()
clock.prepare_today_method_return_value(today=date(year=2025, month=1, day=7))

assert clock.today() == date(year=2025, month=1, day=7)
clock.assert_today_method_was_called_once()
clock.assert_now_method_was_not_called()
```

`MockClock.now()` must be prepared with `prepare_now_method_return_value()`. `MockClock.today()` must be prepared with
`prepare_today_method_return_value()`. Calling either method before preparing it raises a validation error.

## Elapsed-Time Test Doubles

Use `MockMonotonicClock` and mock sleepers when testing minimum durations, deadlines, pollers, or retriers.

```python
from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.sleepers.testing import MockSleeper

monotonic_clock = MockMonotonicClock()
sleeper = MockSleeper(monotonic_clock=monotonic_clock)

with sleeper.minimum_duration(seconds=2):
    monotonic_clock.advance(seconds=1.5)

sleeper.assert_sleep_method_was_called_once_with(seconds=0.5)
```

Use `MockDeadline` when the code under test accepts the `Deadline` contract directly:

```python
from clock_pattern.deadlines.testing import MockDeadline

deadline = MockDeadline(seconds=2)
deadline.advance(seconds=1)

assert deadline.remaining_seconds == 1.0
deadline.raise_if_expired()
deadline.assert_raise_if_expired_method_was_called_once()
```

When used as a context manager, `MockDeadline` raises before an already-expired body starts and checks expiry after a
successful body. Advance it inside the context to test timeout handling without real signals or waiting.

Poller and retrier test doubles implement their subsystem contracts and live under the corresponding testing packages:

```python
from clock_pattern.pollers.testing import MockPoller
from clock_pattern.retriers.testing import MockRetrier

poller = MockPoller()
retrier = MockRetrier()
```

## Service Example

```python
from datetime import date

from clock_pattern import Clock
from clock_pattern.clocks.testing import MockClock


class RenewalPolicy:
    def __init__(self, *, clock: Clock) -> None:
        self._clock = clock

    def should_renew(self) -> bool:
        return self._clock.today().day == 1


def test_should_renew_on_first_day_of_month() -> None:
    clock = MockClock()
    clock.prepare_today_method_return_value(today=date(year=2025, month=5, day=1))

    policy = RenewalPolicy(clock=clock)

    assert policy.should_renew() is True
    clock.assert_today_method_was_called_once()
    clock.assert_now_method_was_not_called()
```

## Testing Checklist

- Prefer explicit dates and datetimes over generated values when assertions depend on exact output.
- Use `FixedClock` for stable time values.
- Use `MockClock` for interaction assertions.
- Use `MockMonotonicClock` for elapsed-duration tests.
- Use `MockDeadline` when a unit accepts an injected deadline.
- Use mock sleepers, pollers, and retriers to avoid real waiting in unit tests.
- Prepare mock return values before calling `now()` or `today()`.
- Cover date-boundary behavior with fixed values near midnight when timezone rules matter.
- Avoid real `SystemClock` or `UtcClock` in unit tests for business logic.
