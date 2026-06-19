# Timezone Reference

Use this file when UTC, local timezones, `today()`, or date-boundary behavior matters.

## UTC Defaults

`SystemClock()` defaults to UTC, and `UtcClock()` is a convenience wrapper around that production choice.

```python
from clock_pattern import SystemClock, UtcClock

default_clock = SystemClock()
utc_clock = UtcClock()
```

UTC is usually the right default for persistence, event payloads, audit fields, logs, queues, and cross-service
timestamps.

## Local Calendar Rules

Use `SystemClock(timezone='Area/City')` when a business rule belongs to a local calendar.

```python
from clock_pattern import SystemClock

clock = SystemClock(timezone='America/New_York')
```

Timezone strings must be valid IANA timezone names supported by Python `zoneinfo.ZoneInfo`. Empty strings, untrimmed
strings, invalid names, and unsupported types are rejected.

## `today()` Is Timezone-Sensitive

`today()` is calculated in the clock timezone. Around midnight, two clocks can return different dates at the same
instant.

Use the timezone that owns the rule:

- UTC for cross-service timestamps and storage boundaries.
- Local timezone for billing days, holiday windows, regional business hours, and legal deadlines.

Avoid comparing date-only values produced by clocks with different timezone assumptions unless that difference is the
behavior under test.

## Test Clock Timezones

`FixedClock` and `MockClock.prepare_now_method_return_value()` normalize naive datetimes to UTC. Timezone-aware
datetimes are preserved.

```python
from datetime import datetime

from clock_pattern.clocks.testing import FixedClock

clock = FixedClock(instant=datetime(year=2025, month=1, day=1, hour=10))

assert clock.now().isoformat() == '2025-01-01T10:00:00+00:00'
```

Use explicit timezone-aware examples when the test is about a local calendar boundary.
