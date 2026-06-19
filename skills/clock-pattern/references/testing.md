# Testing Reference

Use this file when writing deterministic tests for code that depends on Clock Pattern.

## Test Imports

```python
from clock_pattern.clocks.testing import FixedClock, MockClock
from clock_pattern.monotonic_clocks.testing import ManualMonotonicClock
from clock_pattern.pollers.testing import MockPoller, MockPollerAsync
from clock_pattern.retriers.testing import MockRetrier, MockRetrierAsync
from clock_pattern.sleepers.testing import MockSleeper, MockSleeperAsync
```

## Choose The Right Test Double

| Test double | Use when |
| --- | --- |
| `FixedClock` | The test needs one stable datetime and date. |
| `MockClock` | The test needs prepared return values and call assertions. |
| `ManualMonotonicClock` | The test needs deterministic elapsed time. |
| `MockSleeper` / `MockSleeperAsync` | The test needs sleep assertions without real waiting. |
| `MockPoller` / `MockPollerAsync` | A service depends on polling but the unit test should not poll. |
| `MockRetrier` / `MockRetrierAsync` | A service depends on retrying but the unit test should not retry. |

## FixedClock

Use `FixedClock` for simple deterministic time. Naive datetimes are normalized to UTC; timezone-aware datetimes are
preserved.

```python
from datetime import datetime

from clock_pattern.clocks.testing import FixedClock

clock = FixedClock(instant=datetime(year=2025, month=1, day=1, hour=10, minute=30))

assert clock.now().isoformat() == '2025-01-01T10:30:00+00:00'
assert clock.today().isoformat() == '2025-01-01'
```

## MockClock

Use `MockClock` when the test needs to prove whether code requested `now()` or `today()`.

```python
from datetime import date

from clock_pattern.clocks.testing import MockClock

clock = MockClock()
clock.prepare_today_method_return_value(today=date(year=2025, month=5, day=1))

assert clock.today() == date(year=2025, month=5, day=1)
clock.assert_today_method_was_called_once()
clock.assert_now_method_was_not_called()
```

Prepare `now()` with `prepare_now_method_return_value(now=...)`. Prepare `today()` with
`prepare_today_method_return_value(today=...)`. Calling an unprepared method raises a validation error.

## ManualMonotonicClock And MockSleepers

Use `ManualMonotonicClock` to advance elapsed time explicitly.

```python
from clock_pattern.monotonic_clocks.testing import ManualMonotonicClock
from clock_pattern.sleepers.testing import MockSleeper

monotonic_clock = ManualMonotonicClock()
sleeper = MockSleeper(monotonic_clock=monotonic_clock)

with sleeper.minimum_duration(seconds=2):
    monotonic_clock.advance(seconds=1.5)

sleeper.assert_sleep_method_was_called_once_with(seconds=0.5)
```

`MockSleeper.sleep(seconds=...)` records calls and advances its manual monotonic clock by the requested duration.
`MockSleeperAsync` provides the same behavior for async code.

## Mock Pollers And Retriers

Use mock pollers and retriers when the unit under test should delegate polling or retrying to a dependency.

```python
from clock_pattern.pollers.testing import MockPoller
from clock_pattern.retriers.testing import MockRetrier

poller = MockPoller()
retrier = MockRetrier()
```

These test doubles record method calls and can be prepared to raise exceptions or return values, depending on the class.

## Testing Checklist

- Prefer explicit dates and datetimes over generated values when assertions depend on exact output.
- Use fixed clocks for stable time values and date-boundary cases.
- Use mock clocks for interaction assertions.
- Use manual monotonic clocks for elapsed-duration tests.
- Use mock sleepers, pollers, and retriers to avoid real waiting or repeated work in unit tests.
- Avoid real `SystemClock`, `UtcClock`, `SystemSleeper`, real polling, and real retrying in unit tests for business
  logic.
