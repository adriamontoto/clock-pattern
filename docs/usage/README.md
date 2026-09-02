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

The primitive contracts live in each feature's `models` package and are also re-exported from `clock_pattern`:

```python
from clock_pattern.clocks.models import Clock
from clock_pattern.monotonic_clocks.models import MonotonicClock
from clock_pattern.sleepers.models import Sleeper, SleeperAsync
```

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
from clock_pattern import UtcClock

clock = UtcClock()
expires_at = clock.now()
```

Use `today()` when the rule is calendar-based:

```python
from clock_pattern import UtcClock

clock = UtcClock()
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

## Use Sleepers And Minimum Duration

Inject `Sleeper` when a use case needs to wait. Production code can use `SystemSleeper`; tests can use `MockSleeper`.

```python
from clock_pattern import Sleeper, SystemMonotonicClock, SystemSleeper


class UseCase:
    def __init__(self, *, sleeper: Sleeper) -> None:
        self._sleeper = sleeper

    def execute(self) -> None:
        with self._sleeper.minimum_duration(seconds=2):
            pass


use_case = UseCase(sleeper=SystemSleeper(monotonic_clock=SystemMonotonicClock()))
```

Async code can depend on `SleeperAsync` and use `SystemSleeperAsync`.

## Measure Elapsed Time And Deadlines

Use `Stopwatch` for elapsed-time measurement, `Deadline` as the injectable timeout contract, and `SystemDeadline` for a
production monotonic deadline.

```python
from clock_pattern import Stopwatch, SystemDeadline, SystemMonotonicClock

monotonic_clock = SystemMonotonicClock()

with Stopwatch(monotonic_clock=monotonic_clock) as stopwatch:
    pass

print(stopwatch.elapsed_seconds)

with SystemDeadline(seconds=5, monotonic_clock=monotonic_clock):
    pass
```

`SystemDeadline` context managers use `SIGALRM` to interrupt Python code and interruptible system calls. They require a
Unix main thread, cannot be nested or replace an existing alarm, and may be delayed by C code that does not return
control to the Python interpreter. Reading deadline properties or calling `raise_if_expired()` outside a context remains
cooperative and works without signal interruption. When expiry is observed, `TimeoutExpiredError.elapsed_seconds`
contains the measured elapsed duration as a float.

## Poll And Retry

Use `Poller` as the injectable contract and `SystemPoller` when the success condition is a predicate in production. It
raises `TimeoutExpiredError` when the timeout expires.

```python
from clock_pattern import SystemMonotonicClock, SystemPoller, SystemSleeper

monotonic_clock = SystemMonotonicClock()
sleeper = SystemSleeper(monotonic_clock=monotonic_clock)
poller = SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock)

poller.poll_until(
    condition=lambda: True,
    timeout_seconds=5,
    interval_seconds=0.1,
)
```

Use `Retrier` as the injectable contract and `SystemRetrier` when an operation should be retried after configured
exceptions. Successful falsey values are returned as-is; only exceptions trigger retries by default.

```python
from clock_pattern import SystemMonotonicClock, SystemRetrier, SystemSleeper

monotonic_clock = SystemMonotonicClock()
sleeper = SystemSleeper(monotonic_clock=monotonic_clock)

result = SystemRetrier(sleeper=sleeper).retry(
    operation=lambda: 'done',
    attempts=3,
    delay_seconds=0.2,
    backoff=2,
    jitter=True,
)
```

Async contracts are available as `PollerAsync` and `RetrierAsync`; their production implementations are
`SystemPollerAsync` and `SystemRetrierAsync`.

## Usage Checklist

- Inject `Clock` instead of calling `datetime.now()` directly in domain code.
- Inject `Sleeper` / `SleeperAsync` instead of calling `time.sleep()` or `asyncio.sleep()` directly in domain code.
- Prefer `UtcClock` for persistence, messages, and audit timestamps unless a business rule requires another timezone.
- Use `SystemClock(timezone='Area/City')` for calendar rules tied to a local jurisdiction.
- Use monotonic-time helpers for elapsed durations, deadlines, polling, and retries.
- Keep test clocks in tests so production code does not depend on testing utilities.
- Prefer explicit constructor injection over hidden module globals.
