# Timezone Guide

Timezone behavior is part of the clock choice. Clock Pattern makes that choice visible instead of burying it inside
ad-hoc datetime calls.

## UTC By Default

`SystemClock` defaults to UTC, and `UtcClock` is a convenience wrapper around that production choice:

```python
from clock_pattern import SystemClock, UtcClock

default_clock = SystemClock()
utc_clock = UtcClock()

print(default_clock.timezone)
# >>> UTC
print(utc_clock.timezone)
# >>> UTC
```

UTC is usually the right default for persistence, event payloads, audit fields, and cross-service timestamps.

## Local Timezones

Use `SystemClock` with an IANA timezone string when a business rule belongs to a local calendar:

```python
from clock_pattern import SystemClock

clock = SystemClock(timezone='America/New_York')
```

The timezone string must be valid for Python's `zoneinfo.ZoneInfo`. Empty strings, untrimmed strings, invalid names, and
unsupported types are rejected by the underlying value-object validators.

## `today()` Follows The Clock Timezone

`today()` is calculated from `datetime.now(tz=clock.timezone).date()`. This matters near midnight:

```python
from clock_pattern import SystemClock

utc_clock = SystemClock(timezone='UTC')
new_york_clock = SystemClock(timezone='America/New_York')
```

At the same instant, these clocks can produce different dates. For billing days, holiday windows, regional business
hours, and legal deadlines, choose the timezone that owns the rule.

## Naive Datetimes In Test Clocks

`FixedClock` and `MockClock.prepare_now_method_return_value()` normalize naive datetimes to UTC:

```python
from datetime import datetime

from clock_pattern.clocks.testing import FixedClock

clock = FixedClock(instant=datetime(year=2025, month=1, day=1, hour=10))

print(clock.now().isoformat())
# >>> 2025-01-01T10:00:00+00:00
```

Timezone-aware datetimes are preserved as provided.

## Timezone Checklist

- Use UTC for timestamps that cross service, database, queue, or API boundaries.
- Use a local timezone for business rules that are explicitly local-calendar rules.
- Treat `today()` as timezone-sensitive.
- Avoid comparing date-only values produced by clocks with different timezone assumptions.
- Prefer fixed test clocks for date-boundary cases so tests do not depend on the current real time.

