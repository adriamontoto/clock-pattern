# Usage Guide

Clock Pattern is intentionally small. It gives application code a stable contract for asking "what time is it?" without
coupling that code to the operating system clock.

## Depend On `Clock`

Inject `Clock` into classes that make time-sensitive decisions:

```python
from datetime import timedelta

from clock_pattern import Clock


class TrialPolicy:
    def __init__(self, *, clock: Clock) -> None:
        self._clock = clock

    def trial_expires_at(self) -> str:
        expires_at = self._clock.now() + timedelta(days=14)
        return expires_at.isoformat()
```

This keeps the policy independent from any concrete time source.

## Wire A Production Clock

Use `UtcClock` when the application standardizes on UTC:

```python
from clock_pattern import UtcClock

clock = UtcClock()
```

Use `SystemClock` when the application needs a specific timezone:

```python
from clock_pattern import SystemClock

clock = SystemClock(timezone='Europe/Madrid')
```

Both production clocks return timezone-aware datetimes.

## Choose `now()` Or `today()`

Use `now()` when time-of-day matters:

```python
expires_at = clock.now()
```

Use `today()` when the rule is calendar-based:

```python
is_first_day = clock.today().day == 1
```

Avoid deriving a date in service code from a different timezone than the clock used by the application. `today()` already
uses the configured clock timezone.

## Custom Clocks

Create a custom clock by subclassing `Clock` and implementing `now()` and `today()`:

```python
from datetime import date, datetime

from clock_pattern import Clock


class LogicalClock(Clock):
    def __init__(self, *, instant: datetime) -> None:
        self._instant = instant

    def now(self) -> datetime:
        return self._instant

    def today(self) -> date:
        return self._instant.date()
```

Custom clocks are useful for simulations, event replay, deterministic workflows, or infrastructure that owns a logical
time source.

## Usage Checklist

- Inject `Clock` instead of calling `datetime.now()` directly in domain code.
- Prefer `UtcClock` for persistence, messages, and audit timestamps unless a business rule requires another timezone.
- Use `SystemClock(timezone='Area/City')` for calendar rules tied to a local jurisdiction.
- Keep test clocks in tests so production code does not depend on testing utilities.
- Prefer explicit constructor injection over hidden module globals.

