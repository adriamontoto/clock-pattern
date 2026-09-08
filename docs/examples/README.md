# Practical Examples

These self-contained examples compose production helpers with fake time. They require no network access or real sleeping. Application services accept contracts; production wiring supplies system implementations.

## Token expiration with FixedClock

Use wall-clock time for an expiration timestamp that can be stored or sent to another process. In production, inject `UtcClock()` into the policy. This example covers expiration timing only, not token signing or authentication.

```python
from datetime import UTC, datetime, timedelta

from clock_pattern import Clock
from clock_pattern.clocks.testing import FixedClock


class ExpirationPolicy:
    def __init__(self, *, clock: Clock) -> None:
        self._clock = clock

    def expired(self, *, expires_at: datetime) -> bool:
        return self._clock.now() >= expires_at


clock = FixedClock(instant=datetime(2025, 1, 1, tzinfo=UTC))
policy = ExpirationPolicy(clock=clock)
expires_at = clock.now() + timedelta(minutes=15)

assert not policy.expired(expires_at=expires_at)
clock.advance(delta=timedelta(minutes=15))
assert policy.expired(expires_at=expires_at)

# Rewind explicitly to test another point in the same scenario.
clock.set(instant=datetime(2025, 1, 1, 0, 10, tzinfo=UTC))
assert not policy.expired(expires_at=expires_at)
```

## An in-process cache TTL

Use monotonic time for a local cache lifetime so wall-clock adjustments do not affect it. Inject `SystemMonotonicClock()` in production. Monotonic readings are process-local timing values, not persisted timestamps.

```python
from clock_pattern import MonotonicClock
from clock_pattern.monotonic_clocks.testing import MockMonotonicClock


class CachedStatus:
    def __init__(self, *, value: str, clock: MonotonicClock) -> None:
        self._value = value
        self._clock = clock
        self._expires_at = clock.current_seconds() + 30

    def get(self) -> str | None:
        if self._clock.current_seconds() >= self._expires_at:
            return None
        return self._value


clock = MockMonotonicClock()
cached = CachedStatus(value='ready', clock=clock)
clock.advance(seconds=29)
assert cached.get() == 'ready'
clock.advance(seconds=1)
assert cached.get() is None
```

## Poll a background job

Here the job client is simulated, but the polling implementation is real. The fake sleeper advances the shared monotonic clock immediately. In production, supply an async job-status request and wire `SystemMonotonicClock` with `SystemSleeperAsync`. Run this block inside an async function or a notebook supporting top-level `await`.

```python
from unittest.mock import AsyncMock

from clock_pattern import SystemPollerAsync
from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.sleepers.testing import MockSleeperAsync

clock = MockMonotonicClock()
sleeper = MockSleeperAsync(monotonic_clock=clock)
fetch_status = AsyncMock(side_effect=['queued', 'running', 'complete'])


async def job_finished() -> bool:
    return await fetch_status() == 'complete'


await SystemPollerAsync(sleeper=sleeper, monotonic_clock=clock).poll_until(
    condition=job_finished,
    timeout_seconds=10,
    interval_seconds=1,
)

assert fetch_status.await_count == 3
assert sleeper.sleep_calls == (1.0, 1.0)
assert clock.current_seconds() == 2.0
```

`timeout_seconds` also cancels an awaited job request that stalls. The poller raises `TimeoutExpiredError`, lets cleanup run, and preserves external cancellation. Requests must yield to the event loop and propagate cancellation; blocking synchronous code cannot be interrupted. See the [timeout semantics](../usage/README.md) for fake-clock behavior.

## Retry a transient failure with a capped delay

Retry only failures the operation can safely recover from. This example retries a read; retrying writes requires the operation to be safe to repeat. In production, wire `SystemSleeper` with `SystemMonotonicClock`.

```python
from unittest.mock import Mock

from clock_pattern import SystemRetrier
from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.sleepers.testing import MockSleeper

clock = MockMonotonicClock()
sleeper = MockSleeper(monotonic_clock=clock)
fetch_status = Mock(side_effect=[ConnectionError('offline')] * 4 + ['ready'])

status = SystemRetrier(sleeper=sleeper).retry(
    operation=fetch_status,
    attempts=5,
    delay_seconds=1,
    backoff=2,
    max_delay_seconds=3,
    retry_on=ConnectionError,
)

assert status == 'ready'
assert fetch_status.call_count == 5
assert sleeper.sleep_calls == (1.0, 2.0, 3.0, 3.0)
assert clock.current_seconds() == 9.0
```

Use `jitter=True` to randomize each sleep between zero and its capped delay. `max_delay_seconds` limits individual sleeps, not total execution time. The same arguments work with `SystemRetrierAsync` and `MockRetrierAsync`; await `retry()` and supply an async operation and sleeper.
