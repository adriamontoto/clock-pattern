# Clock Pattern Documentation

Clock Pattern makes time an explicit dependency. Application code depends on `Clock`, production wiring chooses a real
clock, and tests choose deterministic clocks.

Use this page as the documentation hub:

| Guide | Purpose |
| --- | --- |
| [Usage Guide](usage/README.md) | How to inject clocks, sleepers, deadlines, pollers, and retriers. |
| [Timezone Guide](timezones/README.md) | UTC defaults, `SystemClock` timezone configuration, and date-boundary guidance. |
| [Testing Guide](testing/README.md) | How to use clock and elapsed-time test doubles for deterministic tests. |

## Wall-Clock API

The wall-clock contract and production clocks are re-exported from the top-level package:

```python
from clock_pattern import Clock, SystemClock, UtcClock
```

## Elapsed-Time API

Elapsed-time contracts, implementations, the stopwatch, and timeout error are also available from the top-level
package:

```python
from clock_pattern import (
    Deadline,
    MonotonicClock,
    Poller,
    PollerAsync,
    Retrier,
    RetrierAsync,
    Sleeper,
    SleeperAsync,
    Stopwatch,
    SystemDeadline,
    SystemMonotonicClock,
    SystemPoller,
    SystemPollerAsync,
    SystemRetrier,
    SystemRetrierAsync,
    SystemSleeper,
    SystemSleeperAsync,
    TimeoutExpiredError,
)
```

Contracts can instead be imported from their owning `models` packages when that makes a dependency boundary clearer:

```python
from clock_pattern.clocks.models import Clock
from clock_pattern.deadlines.models import Deadline
from clock_pattern.monotonic_clocks.models import MonotonicClock
from clock_pattern.pollers.models import Poller, PollerAsync
from clock_pattern.retriers.models import Retrier, RetrierAsync
from clock_pattern.sleepers.models import Sleeper, SleeperAsync
```

## Test Doubles

Test doubles live under each feature's `testing` package:

```python
from clock_pattern.clocks.testing import FixedClock, MockClock
from clock_pattern.deadlines.testing import MockDeadline
from clock_pattern.monotonic_clocks.testing import MockMonotonicClock
from clock_pattern.pollers.testing import MockPoller, MockPollerAsync
from clock_pattern.retriers.testing import MockRetrier, MockRetrierAsync
from clock_pattern.sleepers.testing import MockSleeper, MockSleeperAsync
```

## Clock Contract

Every clock exposes two methods:

| Method | Return type | Meaning |
| --- | --- | --- |
| `now()` | `datetime` | Current or prepared datetime for the clock implementation. |
| `today()` | `date` | Current or prepared date for the clock implementation. |

`SystemClock` and `UtcClock` read real system time. `FixedClock` and `MockClock` are test utilities and should usually
stay in test code.

Elapsed-duration helpers use `MonotonicClock` instead of wall-clock datetimes. Use them for sleeps, minimum durations,
stopwatches, deadlines, polling, and retries.

## Recommended Flow

1. Accept `Clock` in domain services, application services, or use cases.
2. Wire `UtcClock` or `SystemClock` at the application boundary.
3. Use `FixedClock` when a test needs a stable instant.
4. Use `MockClock` when a test also needs to assert that time was requested.
5. Keep timezone choices explicit, especially for date-only rules around midnight.
