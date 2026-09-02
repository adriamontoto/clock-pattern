# API And Usage Reference

Use this file when choosing Clock Pattern imports or replacing direct time, sleep, timeout, poll, or retry code.

## Core Imports

```python
from clock_pattern import (
    Clock,
    Deadline,
    MonotonicClock,
    Poller,
    PollerAsync,
    Retrier,
    RetrierAsync,
    Sleeper,
    SleeperAsync,
    Stopwatch,
    SystemClock,
    SystemDeadline,
    SystemMonotonicClock,
    SystemPoller,
    SystemPollerAsync,
    SystemRetrier,
    SystemRetrierAsync,
    SystemSleeper,
    SystemSleeperAsync,
    TimeoutExpiredError,
    UtcClock,
)
```

## Wall-Clock Time

- `Clock` is the abstract contract for `now() -> datetime` and `today() -> date`.
- `UtcClock()` is the default production choice for persistence, messages, logs, audit fields, and cross-service
  timestamps.
- `SystemClock(timezone='Area/City')` reads system time in a configured timezone.
- `SystemClock()` defaults to UTC.
- `SystemClock.timezone` exposes the configured `tzinfo`.

Inject clocks into services:

```python
from clock_pattern import Clock


class TrialPolicy:
    def __init__(self, *, clock: Clock) -> None:
        self._clock = clock

    def expires_today(self) -> bool:
        return self._clock.today().day == 1
```

## Custom Clocks

Subclass `Clock` when a project has logical time, event replay, simulation, or infrastructure-owned time.

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

## Sleepers

- `Sleeper.sleep(seconds=...)` replaces direct `time.sleep()`.
- `Sleeper.minimum_duration(seconds=...)` returns a sync context manager that sleeps for the remaining duration when the
  block completes too quickly.
- `SleeperAsync.sleep(seconds=...)` replaces direct `asyncio.sleep()`.
- `SleeperAsync.minimum_duration(seconds=...)` returns an async context manager.
- `SystemSleeper` and `SystemSleeperAsync` are production implementations.

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

## Monotonic Time

Use `MonotonicClock.current_seconds() -> float` and `SystemMonotonicClock()` for elapsed-duration behavior. Monotonic
time is not affected by wall-clock changes, DST changes, or timezone boundaries.

## Stopwatch

`Stopwatch(monotonic_clock=...)` measures elapsed seconds.

- `.start()` starts the stopwatch and returns itself.
- `.end()` stops the stopwatch and returns elapsed seconds.
- `.elapsed_seconds` is `0.0` before start, live while running, and fixed after end.
- `.is_running` reports whether it is currently running.
- It can be used as a context manager.

```python
from clock_pattern import Stopwatch, SystemMonotonicClock

with Stopwatch(monotonic_clock=SystemMonotonicClock()) as stopwatch:
    pass

print(stopwatch.elapsed_seconds)
```

## Deadlines

Use `Deadline` as the injectable contract. Create a production timeout with
`SystemDeadline(seconds=..., monotonic_clock=...)`.

- `.elapsed_seconds` and `.remaining_seconds` expose timing state.
- `.expired` reports whether the timeout has elapsed.
- `.raise_if_expired()` raises `TimeoutExpiredError` after expiry; `error.elapsed_seconds` contains the measured elapsed
  duration as a float.
- `SystemDeadline` context managers interrupt Python code and interruptible system calls with a Unix main-thread
  `SIGALRM` timer.
- Context use cannot run on Windows or a worker thread, be nested, or replace another `SIGALRM` owner.
- Long-running C code may delay signal handling; properties and `raise_if_expired()` remain cooperative outside a
  context.

```python
from clock_pattern import SystemDeadline, SystemMonotonicClock, TimeoutExpiredError

try:
    with SystemDeadline(seconds=5, monotonic_clock=SystemMonotonicClock()):
        pass
except TimeoutExpiredError as error:
    print(error.elapsed_seconds)
```

## Polling

Use `Poller` as the injectable contract. In production, construct a `SystemMonotonicClock`, inject it into a
`SystemSleeper` and `SystemPoller`, then call
`poller.poll_until(condition=..., timeout_seconds=..., interval_seconds=0.1)` when success is a predicate. It raises
`TimeoutExpiredError` when the timeout expires.

Use `PollerAsync` as the async contract and `SystemPollerAsync` as its production implementation. Inject a
`SystemSleeperAsync` and their shared monotonic clock. The async poller accepts sync or async conditions.

## Retrying

Use `Retrier` as the injectable contract and `SystemRetrier` as the production implementation for sync operations that
should retry on configured exceptions.

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
    retry_on=ConnectionError,
)
```

- `attempts` must be a positive integer.
- `delay_seconds` defaults to `0.0`.
- `backoff` defaults to `1.0`; values above `1.0` increase the delay.
- `jitter=True` applies full jitter between zero and the current delay.
- `retry_on` defaults to `Exception` and may be an exception type or non-empty tuple of exception types.
- Falsey successful return values are returned; only configured exceptions trigger retry.

Use `RetrierAsync` as the async contract and `SystemRetrierAsync` as its production implementation.
