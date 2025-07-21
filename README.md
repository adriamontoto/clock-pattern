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
    <a href="https://deepwiki.com/adriamontoto/clock-pattern" target="_blank">
        <img src="https://img.shields.io/badge/DeepWiki-adriamontoto%2Fclock--pattern-blue.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAyCAYAAAAnWDnqAAAAAXNSR0IArs4c6QAAA05JREFUaEPtmUtyEzEQhtWTQyQLHNak2AB7ZnyXZMEjXMGeK/AIi+QuHrMnbChYY7MIh8g01fJoopFb0uhhEqqcbWTp06/uv1saEDv4O3n3dV60RfP947Mm9/SQc0ICFQgzfc4CYZoTPAswgSJCCUJUnAAoRHOAUOcATwbmVLWdGoH//PB8mnKqScAhsD0kYP3j/Yt5LPQe2KvcXmGvRHcDnpxfL2zOYJ1mFwrryWTz0advv1Ut4CJgf5uhDuDj5eUcAUoahrdY/56ebRWeraTjMt/00Sh3UDtjgHtQNHwcRGOC98BJEAEymycmYcWwOprTgcB6VZ5JK5TAJ+fXGLBm3FDAmn6oPPjR4rKCAoJCal2eAiQp2x0vxTPB3ALO2CRkwmDy5WohzBDwSEFKRwPbknEggCPB/imwrycgxX2NzoMCHhPkDwqYMr9tRcP5qNrMZHkVnOjRMWwLCcr8ohBVb1OMjxLwGCvjTikrsBOiA6fNyCrm8V1rP93iVPpwaE+gO0SsWmPiXB+jikdf6SizrT5qKasx5j8ABbHpFTx+vFXp9EnYQmLx02h1QTTrl6eDqxLnGjporxl3NL3agEvXdT0WmEost648sQOYAeJS9Q7bfUVoMGnjo4AZdUMQku50McDcMWcBPvr0SzbTAFDfvJqwLzgxwATnCgnp4wDl6Aa+Ax283gghmj+vj7feE2KBBRMW3FzOpLOADl0Isb5587h/U4gGvkt5v60Z1VLG8BhYjbzRwyQZemwAd6cCR5/XFWLYZRIMpX39AR0tjaGGiGzLVyhse5C9RKC6ai42ppWPKiBagOvaYk8lO7DajerabOZP46Lby5wKjw1HCRx7p9sVMOWGzb/vA1hwiWc6jm3MvQDTogQkiqIhJV0nBQBTU+3okKCFDy9WwferkHjtxib7t3xIUQtHxnIwtx4mpg26/HfwVNVDb4oI9RHmx5WGelRVlrtiw43zboCLaxv46AZeB3IlTkwouebTr1y2NjSpHz68WNFjHvupy3q8TFn3Hos2IAk4Ju5dCo8B3wP7VPr/FGaKiG+T+v+TQqIrOqMTL1VdWV1DdmcbO8KXBz6esmYWYKPwDL5b5FA1a0hwapHiom0r/cKaoqr+27/XcrS5UwSMbQAAAABJRU5ErkJggg==" alt="Project Documentation">
    </a>
</p>

The **Clock Pattern** is a Python 🐍 package that turns time into an injectable dependency 🧩. By replacing ad-hoc datetime.now() calls with a swappable Clock interface 🕰️ you unlock deterministic tests 🧪, decouple business logic from the OS clock, and gain the freedom to swap in high-precision or logical clocks without touching domain code.
<br><br>

## Table of Contents

- [📥 Installation](#installation)
- [📚 Documentation](#documentation)
- [💻 Utilization](#utilization)
  - [📚 Available Clocks](#available-clocks)
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

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="documentation"></a>

## 📚 Documentation

This [project's documentation](https://deepwiki.com/adriamontoto/clock-pattern) is powered by DeepWiki, which provides a comprehensive overview of the **Clock Pattern** and its usage.

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="utilization"></a>

## 💻 Utilization

The **Clock Pattern** library is designed to be straightforward. Simply import the desired clock and use its `now()` or `today()` methods to get the current datetime/date. This approach allows for easy dependency injection and testing.

Here is a basic example of how to use the [`SystemClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/system_clock.py) clock:

```python
from datetime import timezone

from clock_pattern import SystemClock

clock = SystemClock(timezone=timezone.utc)
print(clock.now())
# >>> 2025-06-16 13:57:26.210964+00:00
```

<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="available-clocks"></a>

## 📚 Available Clocks

The package offers several clock implementations to suit different needs:

- [`clock_pattern.SystemClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/system_clock.py): The standard clock implementation that returns the system's current datetime/date with the provided timezone.
- [`clock_pattern.UtcClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/utc_clock.py): A clock implementation that returns the system's current datetime/date in UTC. Ideal for production environments.
- [`clock_pattern.clocks.testing.FixedClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/testing/fixed_clock.py): A clock that always returns a fixed, preset datetime/date. It is perfect for basic testing as it allows you to control the datetime/date within your test environment, ensuring deterministic results.
- [`clock_pattern.clocks.testing.MockClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/testing/mock_clock.py): A clock that allows you to mock the system clock. It is perfect for more complex testing as it allows you to control the datetime/date within your test environment and if or not the methods are called or not.
<p align="right">
    <a href="#readme-top">🔼 Back to top</a>
</p><br><br>

<a name="real-life-case-christmas-detector-service"></a>

## 🎄 Real-Life Case: Christmas Detector Service

Below is an example of a real-life scenario where Clock Pattern can create clean and testable code. We have a `ChristmasDetectorService` that checks if the curren date falls within a specific Christmas holiday range. Using the Clock Pattern, in this case [`UtcClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/utc_clock.py) and [`MockClock`](https://github.com/adriamontoto/clock-pattern/blob/master/clock_pattern/clocks/testing/mock_clock.py), we can decouple the service from the python `datetime.now()` and `datetime.today()` functions, making it easy to test for different dates without changing the system's time.

```python
from datetime import date

from clock_pattern import Clock, UtcClock
from clock_pattern.clocks.testing import MockClock


class ChristmasDetectorService:
    def __init__(self, clock: Clock) -> None:
        self.clock = clock
        self.christmas_start = date(year=2024, month=12, day=24)
        self.christmas_end = date(year=2025, month=1, day=6)

    def is_christmas(self) -> bool:
        return self.christmas_start <= self.clock.today() <= self.christmas_end


clock = UtcClock()
christmas_detector_service = ChristmasDetectorService(clock=clock)

print(christmas_detector_service.is_christmas())
# >>> False


def test_christmas_detector_is_christmas() -> None:
    clock = MockClock()
    christmas_detector_service = ChristmasDetectorService(clock=clock)

    today = date(year=2024, month=12, day=25)
    clock.prepare_today_method_return_value(today=today)

    assert christmas_detector_service.is_christmas() is True
    clock.assert_today_method_was_called_once()


def test_christmas_detector_is_not_christmas() -> None:
    clock = MockClock()
    christmas_detector_service = ChristmasDetectorService(clock=clock)

    today = date(year=2025, month=1, day=7)
    clock.prepare_today_method_return_value(today=today)

    assert christmas_detector_service.is_christmas() is False
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
