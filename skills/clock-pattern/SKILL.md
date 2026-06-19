---
name: clock-pattern
description: Use this skill whenever a Python task uses or should use the clock-pattern package. Use it for injectable time, Clock abstractions, UtcClock, SystemClock, timezone-aware dates, deterministic time tests, FixedClock, MockClock, monotonic clocks, sleepers, minimum-duration guards, Stopwatch, Deadline, Poller, Retrier, async polling/retrying, or replacing datetime.now(), date.today(), time.sleep(), or asyncio.sleep() with testable dependencies.
compatibility: Designed for Agent Skills-compatible coding agents. Guidance is authored from clock-pattern 0.7.0 and Python 3.11+; verify the consuming project's pinned package version before relying on newer APIs.
---

# Clock Pattern

Use this skill to help users apply the `clock-pattern` Python package in their own projects. The package turns
wall-clock time, elapsed time, sleeping, deadlines, polling, and retries into injectable dependencies so production code
stays explicit and tests stay deterministic.

## First Steps

1. Inspect the consuming project before editing:
   - Check dependency files for `clock-pattern` and its pinned version.
   - Find direct calls to `datetime.now()`, `date.today()`, `time.sleep()`, `asyncio.sleep()`, manual timeout loops, or
     retry loops.
   - Check existing dependency injection and test-double conventions.
2. Choose the boundary:
   - Use `Clock` for business rules that need the current datetime or date.
   - Use `Sleeper` or `SleeperAsync` for code that needs to wait.
   - Use monotonic helpers for elapsed durations, deadlines, polling, and retries.
3. Prefer package-provided implementations before writing local wrappers.
4. Keep real time out of unit tests. Use fixed clocks, mock clocks, manual monotonic clocks, and mock sleepers.
5. Add focused tests for timezone behavior, date-boundary behavior, elapsed-duration behavior, and retry/poll timeout
   paths when those rules matter.

## What To Load

- Read [references/api-and-usage.md](references/api-and-usage.md) when choosing imports, production wiring, custom
  clocks, sleepers, deadlines, pollers, retriers, or monotonic-time helpers.
- Read [references/testing.md](references/testing.md) when writing deterministic tests, replacing global time patches,
  or asserting sleep, poll, retry, or clock interactions.
- Read [references/timezones.md](references/timezones.md) when `today()`, UTC, local calendar rules, IANA timezone
  strings, or date boundaries matter.

## Default Implementation Pattern

Inject `Clock` into domain code instead of reading global time:

```python
from clock_pattern import Clock, UtcClock


class TimestampService:
    def __init__(self, *, clock: Clock) -> None:
        self._clock = clock

    def issued_at(self) -> str:
        return self._clock.now().isoformat()


service = TimestampService(clock=UtcClock())
```

Use `SystemClock` when a business rule belongs to a local calendar:

```python
from clock_pattern import SystemClock

clock = SystemClock(timezone='Europe/Madrid')
```

Use monotonic-time helpers for elapsed duration behavior:

```python
from clock_pattern import Poller, Retrier, Stopwatch, deadline

with Stopwatch() as stopwatch:
    process_batch()

with deadline(seconds=5) as timeout:
    while not job_is_done():
        timeout.raise_if_expired()

Poller().poll_until(condition=lambda: cache.exists(key), timeout_seconds=5, interval_seconds=0.1)
Retrier().retry(operation=lambda: client.send(message), attempts=3, delay_seconds=0.2, backoff=2, jitter=True)
```

## Review Checklist

- Time-sensitive domain code depends on `Clock`, `Sleeper`, `SleeperAsync`, or a package helper instead of global time.
- Production timestamps default to `UtcClock` unless a local calendar rule requires `SystemClock(timezone='Area/City')`.
- `today()` is treated as timezone-sensitive.
- Timeouts, polling, retries, and elapsed-duration logic use monotonic time rather than wall-clock datetimes.
- Unit tests avoid real `SystemClock`, `UtcClock`, real sleeping, and current real time.
- Exact date/datetime assertions use explicit fixed values.
- Async code uses `SleeperAsync`, `PollerAsync`, or `RetrierAsync` rather than sync helpers.

## Common Mistakes

- Do not call `datetime.now()` or `date.today()` inside code that should be testable through injected time.
- Do not derive a date in a different timezone from the clock that owns the rule.
- Do not use wall-clock datetimes to measure elapsed durations or enforce timeouts.
- Do not use real sleeps in unit tests.
- Do not hide clocks or sleepers in module globals when constructor injection fits the project style.
