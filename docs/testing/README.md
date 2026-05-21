# Testing Guide

Clock Pattern is most useful when tests need stable time. Instead of freezing global modules or patching Python internals,
pass a test clock into the code under test.

## Choose The Right Test Clock

| Test clock | Use when | Behavior |
| --- | --- | --- |
| `FixedClock` | The test needs one stable datetime and date. | Always returns the configured instant and its date. |
| `MockClock` | The test also needs call assertions. | Requires prepared return values and records `now()` / `today()` calls. |

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
- Prepare mock return values before calling `now()` or `today()`.
- Cover date-boundary behavior with fixed values near midnight when timezone rules matter.
- Avoid real `SystemClock` or `UtcClock` in unit tests for business logic.

