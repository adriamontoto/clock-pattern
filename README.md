<a name="readme-top"></a>

# 🕰️ Clock Pattern

<p align="center">
    <a href="https://github.com/adriamontoto/clock-pattern/actions/workflows/ci.yaml?event=push&branch=master" target="_blank">
        <img src="https://github.com/adriamontoto/clock-pattern/actions/workflows/ci.yaml/badge.svg?event=push&branch=master" alt="CI Pipeline">
    </a>
    <a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/adriamontoto/clock-pattern" target="_blank">
        <img src="https://coverage-badge.samuelcolvin.workers.dev/adriamontoto/clock-pattern.svg" alt="Coverage Pipeline">
    </a>
    <a href="https://pypi.org/project/clock-pattern" target="_blank">
        <img src="https://img.shields.io/pypi/v/clock-pattern?color=%2334D058&label=pypi%20package" alt="Package Version">
    </a>
    <a href="https://pypi.org/project/clock-pattern/" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/clock-pattern.svg?color=%2334D058" alt="Supported Python Versions">
    </a>
    <a href="https://pepy.tech/projects/clock-pattern" target="_blank">
        <img src="https://static.pepy.tech/badge/clock-pattern/month" alt="Package Downloads">
    </a>
</p>

The **Clock Pattern** is a Python 🐍 package that turns time into an injectable dependency 🧩. Instead of scattering
`datetime.now()` or `date.today()` through application code, domain services depend on a small `Clock` interface. That
keeps time-sensitive logic deterministic in tests, makes timezone choices explicit, and lets production code swap clock
implementations without touching business rules.
<br><br>

## Table of Contents

- [📥 Installation](#installation)
- [📚 Documentation](#documentation)
- [⚡ Quick Start](#quick-start)
- [🧩 Why Inject a Clock?](#why-inject-a-clock)
- [📚 Public API](#public-api)
- [🌍 Timezone Behavior](#timezone-behavior)
- [🧪 Testing Time-Sensitive Code](#testing-time-sensitive-code)
- [🎄 Real-Life Case: Christmas Detector Service](#real-life-case-christmas-detector-service)
- [🤝 Contributing](#contributing)
- [🔑 License](#license)

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="installation"></a>

## 📥 Installation

You can install **Clock Pattern** using `pip`:

```bash
pip install clock-pattern
```

You can install the companion AI-agent skill from [skills.sh](https://www.skills.sh/) with Vercel's `skills` CLI:

```bash
npx skills add adriamontoto/clock-pattern
```

Review the skill source in [`skills/clock-pattern`](skills/clock-pattern) before installing it in sensitive
environments.

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="documentation"></a>

## 📚 Documentation

The root README is the entry point. Deeper guides live in this repository and are linked here:

- [`docs/README.md`](docs/README.md): Documentation hub.
- [`docs/usage/README.md`](docs/usage/README.md): Core usage patterns and service composition.
- [`docs/timezones/README.md`](docs/timezones/README.md): Timezone behavior, UTC defaults, and date-boundary guidance.
- [`docs/testing/README.md`](docs/testing/README.md): `FixedClock`, `MockClock`, and deterministic test patterns.


<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="quick-start"></a>

## ⚡ Quick Start

Inject a `Clock` into code that needs the current time. Production code can pass a real clock, while tests can pass a
fixed or mock clock.

```python
from clock_pattern import Clock, UtcClock


class TimestampService:
    def __init__(self, *, clock: Clock) -> None:
        self._clock = clock

    def issued_at(self) -> str:
        return self._clock.now().isoformat()


service = TimestampService(clock=UtcClock())
print(service.issued_at())
```

Use [`SystemClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/system_clock.py) when
you need a specific timezone:

```python
from clock_pattern import SystemClock

clock = SystemClock(timezone='Europe/Madrid')
print(clock.now())
# >>> 2025-06-16 15:57:26.210964+02:00
```

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="why-inject-a-clock"></a>

## 🧩 Why Inject a Clock?

Time is global state. Reading it directly from the operating system makes behavior depend on the moment a test happens
to run, the machine timezone, daylight-saving transitions, and the speed of the test suite.

Clock Pattern keeps those decisions explicit:

- Domain code depends on `Clock`, not on Python's global datetime functions.
- Tests can choose exact dates and datetimes without monkeypatching built-in modules.
- Production wiring decides whether the application uses UTC or another timezone.
- Custom clocks can be introduced for logical time, simulation, replay, or high-precision infrastructure.

The package exposes two methods:

| Method | Returns | Typical use |
| --- | --- | --- |
| `now()` | `datetime` | Timestamps, expiration windows, and audit fields. |
| `today()` | `date` | Calendar rules, billing days, holiday checks, date-only decisions. |

Clock Pattern also includes injectable helpers for elapsed-duration behavior: monotonic clocks, sleepers, stopwatches,
deadlines, pollers, and retriers. These use monotonic seconds instead of wall-clock datetimes so system clock changes do
not affect timeout or retry behavior.

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="public-api"></a>

## 📚 Public API

Use the top-level package for contracts and production helpers, and each feature's `testing` package for test doubles.

### Wall-Clock API

| API | Import path | Purpose |
| --- | --- | --- |
| [`Clock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/models/clock.py) | `from clock_pattern import Clock` | Abstract contract for code that needs `now()` or `today()`. |
| [`SystemClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/system_clock.py) | `from clock_pattern import SystemClock` | Production clock backed by system time in a configured timezone. |
| [`UtcClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/utc_clock.py) | `from clock_pattern import UtcClock` | Production clock fixed to UTC. |

### Elapsed-Time API

| API | Import path | Purpose |
| --- | --- | --- |
| `MonotonicClock` | `from clock_pattern import MonotonicClock` | Abstract contract for elapsed-time sources. |
| `SystemMonotonicClock` | `from clock_pattern import SystemMonotonicClock` | Production monotonic clock for elapsed-time measurement. |
| `Sleeper` / `SleeperAsync` | `from clock_pattern import Sleeper, SleeperAsync` | Abstract contracts for injectable sync and async sleeping. |
| `SystemSleeper` / `SystemSleeperAsync` | `from clock_pattern import SystemSleeper, SystemSleeperAsync` | Injectable sync and async sleeping. |
| `Stopwatch` | `from clock_pattern import Stopwatch` | Measure elapsed seconds with `.start()`, `.end()`, or a context manager. |
| `Deadline` | `from clock_pattern import Deadline` | Abstract contract for injectable deadline state. |
| `SystemDeadline` | `from clock_pattern import SystemDeadline` | Monotonic deadline with an interrupting Unix main-thread context. |
| `TimeoutExpiredError` | `from clock_pattern import TimeoutExpiredError` | Error raised when a deadline or poll timeout expires. |
| `Poller` / `PollerAsync` | `from clock_pattern import Poller, PollerAsync` | Abstract contracts for condition polling. |
| `SystemPoller` / `SystemPollerAsync` | `from clock_pattern import SystemPoller, SystemPollerAsync` | Production polling implementations. |
| `Retrier` / `RetrierAsync` | `from clock_pattern import Retrier, RetrierAsync` | Abstract contracts for retrying operations. |
| `SystemRetrier` / `SystemRetrierAsync` | `from clock_pattern import SystemRetrier, SystemRetrierAsync` | Production retry implementations. |

### Test Doubles

| API | Import path | Purpose |
| --- | --- | --- |
| [`FixedClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/testing/fixed_clock.py) | `from clock_pattern.clocks.testing import FixedClock` | Test clock that always returns the same datetime and derived date. |
| [`MockClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/testing/mock_clock.py) | `from clock_pattern.clocks.testing import MockClock` | Test clock with prepared return values and call assertions. |
| `MockMonotonicClock` | `from clock_pattern.monotonic_clocks.testing import MockMonotonicClock` | Controllable elapsed-time source with call assertions. |
| `MockDeadline` | `from clock_pattern.deadlines.testing import MockDeadline` | Controllable deadline with expiry call assertions. |
| `MockSleeper` / `MockSleeperAsync` | `from clock_pattern.sleepers.testing import MockSleeper, MockSleeperAsync` | Sleeping test doubles that advance a mock monotonic clock. |
| `MockPoller` / `MockPollerAsync` | `from clock_pattern.pollers.testing import MockPoller, MockPollerAsync` | Polling test doubles with call assertions. |
| `MockRetrier` / `MockRetrierAsync` | `from clock_pattern.retriers.testing import MockRetrier, MockRetrierAsync` | Retry test doubles with prepared results. |

```python
from clock_pattern import Stopwatch, SystemDeadline, SystemMonotonicClock, SystemPoller, SystemRetrier, SystemSleeper

monotonic_clock = SystemMonotonicClock()
sleeper = SystemSleeper(monotonic_clock=monotonic_clock)
poller = SystemPoller(sleeper=sleeper, monotonic_clock=monotonic_clock)

with Stopwatch(monotonic_clock=monotonic_clock) as stopwatch:
    pass

with sleeper.minimum_duration(seconds=2):
    pass

with SystemDeadline(seconds=5, monotonic_clock=monotonic_clock):
    pass

poller.poll_until(condition=lambda: True, timeout_seconds=5, interval_seconds=0.1)
SystemRetrier(sleeper=sleeper).retry(
    operation=lambda: 'done',
    attempts=3,
    delay_seconds=0.2,
    backoff=2,
    jitter=True,
)
```

`SystemDeadline` context managers use `SIGALRM` to interrupt Python code and interruptible system calls. Context use is
limited to Unix main-thread execution, cannot be nested or share an existing alarm, and may be delayed by C code that
does not return control to the Python interpreter. Deadline properties and `raise_if_expired()` remain cooperative when
used outside a context manager. `TimeoutExpiredError.elapsed_seconds` exposes the measured elapsed duration reported by
either timeout path.

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="timezone-behavior"></a>

## 🌍 Timezone Behavior

`SystemClock` accepts either an IANA timezone string or a `tzinfo` instance. It converts strings to `ZoneInfo`, preserves
`tzinfo` instances directly, and uses the resulting timezone for both `now()` and `today()`.

```python
from datetime import UTC

from clock_pattern import SystemClock

utc_clock = SystemClock(timezone=UTC)
madrid_clock = SystemClock(timezone='Europe/Madrid')

print(utc_clock.timezone)
# >>> UTC
print(madrid_clock.timezone)
# >>> Europe/Madrid
```

`UtcClock` is a convenience clock for the common production choice of UTC.

`today()` is calculated in the clock timezone. Around midnight, `SystemClock(timezone='UTC').today()` and
`SystemClock(timezone='America/New_York').today()` may return different dates. For more details, see
[`docs/timezones/README.md`](docs/timezones/README.md).

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="testing-time-sensitive-code"></a>

## 🧪 Testing Time-Sensitive Code

Use `FixedClock` when the test only needs a stable instant:

```python
from datetime import datetime

from clock_pattern.clocks.testing import FixedClock

clock = FixedClock(instant=datetime(year=2025, month=1, day=1, hour=10, minute=30))

assert clock.now().isoformat() == '2025-01-01T10:30:00+00:00'
assert clock.today().isoformat() == '2025-01-01'
```

Use `MockClock` when the test also needs to prove that time was requested:

```python
from datetime import date

from clock_pattern.clocks.testing import MockClock

clock = MockClock()
clock.prepare_today_method_return_value(today=date(year=2025, month=1, day=7))

assert clock.today() == date(year=2025, month=1, day=7)
clock.assert_today_method_was_called_once()
clock.assert_now_method_was_not_called()
```

More testing recipes are available in [`docs/testing/README.md`](docs/testing/README.md).

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="real-life-case-christmas-detector-service"></a>

## 🎄 Real-Life Case: Christmas Detector Service

This service checks whether the current date falls within a Christmas holiday range. The service depends on `Clock`, so
production code can use [`UtcClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/utc_clock.py)
and tests can use [`MockClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/testing/mock_clock.py)
without changing the service.

```python
from datetime import date

from clock_pattern import Clock, UtcClock
from clock_pattern.clocks.testing import MockClock


class ChristmasDetectorService:
    def __init__(self, *, clock: Clock) -> None:
        self._clock = clock
        self._christmas_start = date(year=2024, month=12, day=24)
        self._christmas_end = date(year=2025, month=1, day=6)

    def is_christmas(self) -> bool:
        return self._christmas_start <= self._clock.today() <= self._christmas_end


clock = UtcClock()
service = ChristmasDetectorService(clock=clock)

print(service.is_christmas())
# >>> False


def test_christmas_detector_is_christmas() -> None:
    clock = MockClock()
    service = ChristmasDetectorService(clock=clock)

    today = date(year=2024, month=12, day=25)
    clock.prepare_today_method_return_value(today=today)

    assert service.is_christmas() is True
    clock.assert_today_method_was_called_once()


def test_christmas_detector_is_not_christmas() -> None:
    clock = MockClock()
    service = ChristmasDetectorService(clock=clock)

    today = date(year=2025, month=1, day=7)
    clock.prepare_today_method_return_value(today=today)

    assert service.is_christmas() is False
    clock.assert_today_method_was_called_once()
```

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="contributing"></a>

## 🤝 Contributing

We love community help! Before you open an issue or pull request, please read:

- [`🤝 How to Contribute`](https://github.com/adriamontoto/clock-pattern/blob/master/.github/CONTRIBUTING.md)
- [`🧭 Code of Conduct`](https://github.com/adriamontoto/clock-pattern/blob/master/.github/CODE_OF_CONDUCT.md)
- [`🔐 Security Policy`](https://github.com/adriamontoto/clock-pattern/blob/master/.github/SECURITY.md)

_Thank you for helping make **🕰️ Clock Pattern** package awesome! 🌟_

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="license"></a>

## 🔑 License

This project is licensed under the terms of the [`MIT license`](https://github.com/adriamontoto/clock-pattern/blob/master/LICENSE.md).

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p>
