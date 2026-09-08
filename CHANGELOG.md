# CHANGELOG

<!-- version list -->

## v0.11.0 (2026-09-08)

### 📦 Build System

- Install typing-extensions when python is < 3.12
  ([`d60404c`](https://github.com/adriamontoto/clock-pattern/commit/d60404c5056d774b448d1278cb5fd7f8cbbf913c))

### 🧹 Chores

- Update semantic releases configuration
  ([`471ac3a`](https://github.com/adriamontoto/clock-pattern/commit/471ac3a02f01b0f67db2490402d8f66a51c176d8))

### 🤖 Continuous Integration

- Bump https://github.com/commitizen-tools/commitizen from v4.7.1 to 4.18.0
  ([#97](https://github.com/adriamontoto/clock-pattern/pull/97),
  [`33c0241`](https://github.com/adriamontoto/clock-pattern/commit/33c0241740db4f9e21d88f8cdbf51b770abecd7f))

- Bump https://github.com/gitleaks/gitleaks from v8.27.0 to 8.30.1
  ([#98](https://github.com/adriamontoto/clock-pattern/pull/98),
  [`ce15619`](https://github.com/adriamontoto/clock-pattern/commit/ce156196d950fb3eca4e32d4e2fa221df4a4eb80))

- Bump https://github.com/pre-commit/pre-commit-hooks from v5.0.0 to 6.0.0
  ([#96](https://github.com/adriamontoto/clock-pattern/pull/96),
  [`5b10e9a`](https://github.com/adriamontoto/clock-pattern/commit/5b10e9a9b03b33b61e9551ffd7abed1d30e86a9b))

- Bump the actions-minor-patch group with 3 updates
  ([#99](https://github.com/adriamontoto/clock-pattern/pull/99),
  [`036531e`](https://github.com/adriamontoto/clock-pattern/commit/036531efd326e88506d1d1cd317405310790145b))

- Fix github actions and precommit have no cooldown per sematic version
  ([`75cd9c6`](https://github.com/adriamontoto/clock-pattern/commit/75cd9c68177342c95f3bc0135f37dc36e75d1af5))

- Update python-semantic-release version and remove click constraint
  ([`716998d`](https://github.com/adriamontoto/clock-pattern/commit/716998d93f3835246abd11fb02263956a3631f7e))

### 📚 Documentation

- Add examples of the repository
  ([`a3b91a3`](https://github.com/adriamontoto/clock-pattern/commit/a3b91a33b5da21de78168aa68889774ab70ca2a9))

- Update deepwiki references
  ([`d210300`](https://github.com/adriamontoto/clock-pattern/commit/d2103009f15cd19671ff2497346c3ed5583fd174))

### ✨ Features

- Enhance timeout handling in pollers with cooperative checks
  ([`d94283b`](https://github.com/adriamontoto/clock-pattern/commit/d94283b3608191795112e3444a1c656653d201e6))

- Implement set and advance methods to fixed clock
  ([`df88206`](https://github.com/adriamontoto/clock-pattern/commit/df882069838eb82aabfffce7c1c39a1e92c69c82))

- Make sleeper do not wait for all time when cancellation error is raised
  ([`a4e96de`](https://github.com/adriamontoto/clock-pattern/commit/a4e96de9264da3a6c9ab1fe37a45ea49678a4bec))

- **pollers**: Enhance SystemPollerAsync with timeout handling and cancellation propagation
  ([`34a2520`](https://github.com/adriamontoto/clock-pattern/commit/34a25209c2881099d30926ae6d271a253ecf9e9d))

- **retriers**: Implement max_delay_seconds parameter to SystemRetrier and SystemRetrierAsync
  ([`c2fd63f`](https://github.com/adriamontoto/clock-pattern/commit/c2fd63f21c28ce6a4f133ed034d5256c7a2e4148))


## v0.10.0 (2026-09-02)

### 📦 Build System

- Add constraint for clock dependency
  ([`311c5e1`](https://github.com/adriamontoto/clock-pattern/commit/311c5e1eac3da9b30154e79b27418e25c525b6a2))

### ✨ Features

- Implement deadlines
  ([`bb9b51b`](https://github.com/adriamontoto/clock-pattern/commit/bb9b51b6358404ab183930a83af408bec3c0f1ac))

- Implement pollers
  ([`2e9ebcb`](https://github.com/adriamontoto/clock-pattern/commit/2e9ebcba1794d201aca10bfa09256a8f65da05c4))

- Implement retriers
  ([`99bb631`](https://github.com/adriamontoto/clock-pattern/commit/99bb6314cd8ae22eb1fc7adc6168cbc2ad85981f))


## v0.9.0 (2026-08-23)

### ✨ Features

- Implement Sleeper and SleeperAsync for sync and async sleeping
  ([`22083c1`](https://github.com/adriamontoto/clock-pattern/commit/22083c1c826c3a2be33787a9c52edf35ee675e2e))

- Implement stopwatch
  ([`572637f`](https://github.com/adriamontoto/clock-pattern/commit/572637f5b3cadfa007309556086409ef9b2f804e))


## v0.8.0 (2026-08-18)

### ✨ Features

- Implement monotonic clock
  ([`2eeb586`](https://github.com/adriamontoto/clock-pattern/commit/2eeb5860768659fbee66095f9417608b6620d281))


## v0.7.0 (2026-05-20)

### ✨ Features

- Introduce AGENTS.md
  ([`f4ad97e`](https://github.com/adriamontoto/clock-pattern/commit/f4ad97e1363f6fb3ccc50e0056d6ecc012861638))


## v0.6.0 (2025-12-10)

### ✨ Features

- Support python 3.14
  ([`85c3c3f`](https://github.com/adriamontoto/clock-pattern/commit/85c3c3f6fd7c69c276e2fb950bef09670f6d00e4))


## v0.5.0 (2025-06-23)

### ✨ Features

- Improve package imports
  ([`30a5c71`](https://github.com/adriamontoto/clock-pattern/commit/30a5c71cfcc15520239c8bd1f1efabc0ce673bb8))


## v0.4.0 (2025-06-21)

### ✨ Features

- Implement mock clock
  ([`0876d5b`](https://github.com/adriamontoto/clock-pattern/commit/0876d5bcead93748ec855d87eec260b8d3677c38))


## v0.3.0 (2025-06-21)

### ✨ Features

- Implement fixed time clock
  ([`d4aab23`](https://github.com/adriamontoto/clock-pattern/commit/d4aab23e6910a22e76064954faeb58f0d13e471b))


## v0.2.0 (2025-06-21)

### ✨ Features

- Implement UTC clock
  ([`f61d1e5`](https://github.com/adriamontoto/clock-pattern/commit/f61d1e57d5fe02a9c48e2882446b14a417ab7cc7))


## v0.1.0 (2025-06-21)

### ✨ Features

- Implement clock interface
  ([`b4b2614`](https://github.com/adriamontoto/clock-pattern/commit/b4b261471a351f1c738944be76ebbf63ee93077b))

- Implement system clock
  ([`1caab11`](https://github.com/adriamontoto/clock-pattern/commit/1caab1195a78f8e302ac66c735d1a607d1479d1d))
