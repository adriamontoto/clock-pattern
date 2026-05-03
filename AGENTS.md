# AGENTS.md

## Project Overview

Clock Pattern is a typed Python package that turns time into an injectable dependency. The package exposes an abstract `Clock` interface plus concrete clock implementations for production and tests.

Key paths:

- `clock_pattern/models/clock.py`: abstract `Clock` contract with `now()` and `today()`.
- `clock_pattern/clocks/system_clock.py`: timezone-aware system clock.
- `clock_pattern/clocks/utc_clock.py`: UTC clock implementation.
- `clock_pattern/clocks/testing/`: `FixedClock` and `MockClock` test utilities.
- `tests/`: pytest suite organized to mirror `clock_pattern/`.
- `pyproject.toml`: package metadata and tool configuration.
- `Makefile`: canonical local workflow.

This is a single-package Python project, not a monorepo. It supports Python `>=3.11` and CI tests Python `3.11`, `3.12`, `3.13`, and `3.14`.

## Setup Commands

Run commands from the repository root.

- Show available project commands: `make help`
- Create the virtual environment, install all dependency groups, and install hooks: `make setup`
- Install all dependency groups into an existing environment: `make install`
- Install one dependency group: `make install GROUP=test`, `make install GROUP=lint`, `make install GROUP=format`, `make install GROUP=audit`, or `make install GROUP=release`

The Makefile defaults to:

- `UV_BIN=uv`
- `PYTHON_VERSION=3.14`
- `PYTHON_VIRTUAL_ENVIRONMENT=.venv`

If Python 3.14 is unavailable locally, pass a supported version explicitly, for example:

```bash
make setup PYTHON_VERSION=3.13
```

After setup, activate the environment when useful:

```bash
source .venv/bin/activate
```

There is no database or application server to start.

## Development Workflow

- Prefer the Make targets over ad hoc tool invocations.
- Keep changes scoped to the requested behavior; avoid unrelated cleanup.
- Add or update tests for behavior changes.
- For public API changes, update exports in `clock_pattern/__init__.py` or package `__init__.py` files as needed.
- Keep `clock_pattern/py.typed` present so package typing remains advertised.
- This repository currently has no lockfile; avoid introducing dependency lockfile churn unless the task is explicitly about dependency management.

Use this local verification loop for code changes:

```bash
make format
make lint
make test
make coverage
```

For documentation-only changes, run the smallest relevant check and state what was skipped if full verification is not needed.

`make clean` removes the virtual environment and generated files. Treat it as destructive and do not run it unless the task calls for cleanup.

## Testing Instructions

- Run all tests: `make test`
- Run coverage: `make coverage`
- Run tests directly after setup: `.venv/bin/python3.14 -m pytest --config-file pyproject.toml`
- Run a specific file: `.venv/bin/python3.14 -m pytest tests/clocks/test_utc_clock.py --config-file pyproject.toml`
- Run a focused test expression: `.venv/bin/python3.14 -m pytest -k "system_clock" --config-file pyproject.toml`

If setup used a different `PYTHON_VERSION`, adjust the `.venv/bin/python3.14` path or activate the environment and use `python -m pytest ...`.

Test conventions:

- Tests live under `tests/` and mirror package structure.
- Test files use `test_*.py` naming.
- Existing tests use `pytest.mark.unit_testing`.
- Assertions are plain `assert`; Ruff permits `assert` in test files.
- Test data helpers come from `object_mother_pattern` where useful.
- Keep clock tests deterministic. Prefer `FixedClock` or `MockClock` when testing code that depends on time.

Coverage is configured in `pyproject.toml` with branch coverage enabled for `clock_pattern`. CI expects 100% minimum coverage for published reports, so consider uncovered branches and failure paths when changing behavior.

## Code Style

The canonical style is defined in `pyproject.toml`.

- Format with Ruff: `make format`
- Lint and type-check with Ruff and mypy: `make lint`
- Ruff line length is `120`.
- Ruff format uses single quotes and spaces for indentation.
- Mypy runs in strict mode.
- Imports are sorted by Ruff/isort with `clock_pattern` as first-party.
- Public modules and classes use docstrings following the existing PEP 257 style.
- Keep runtime code compatible with Python `>=3.11`.
- When using `typing.override`, preserve the existing compatibility pattern that imports from `typing` on Python 3.12+ and from `typing_extensions` otherwise.
- Use existing `value_object_pattern` validators for argument validation when nearby code does so.

Architecture conventions:

- New clock implementations should subclass `clock_pattern.models.clock.Clock`.
- `now()` returns `datetime`; `today()` returns `date`.
- Clocks that return real time should be timezone-aware.
- Test-only clocks belong under `clock_pattern/clocks/testing/`.
- Export user-facing production clocks from `clock_pattern/clocks/__init__.py` and, when appropriate, `clock_pattern/__init__.py`.

## Build And Release

- Build distributions locally: `make build`
- Build output is written to `dist/`.
- Do not publish packages manually from an agent session.
- Releases are managed in CI on pushes to `master` using `python-semantic-release`.
- Version is read from `clock_pattern/__init__.py`.
- Changelog generation uses templates in `docs/changelog_template/`.

Semantic-release is configured for Conventional Commits:

- Minor release tags: `feat`
- Patch release tags: `fix`, `perf`, `build`
- Other conventional types such as `docs`, `test`, `refactor`, and `ci` may be valid for commit hygiene but do not bump by default according to the local semantic-release config.

## Security

- Run dependency audit when security or dependency changes are involved: `make audit`
- Run secret scanning when touching configuration, CI, release, or credential-adjacent files: `make secrets`
- Never read or print secrets. Do not inspect `.env` files; use examples or placeholders instead.
- Security vulnerabilities should be handled through GitHub Security Advisories, not public issues.

## CI And Pull Requests

CI runs on pushes and pull requests targeting `master`, plus a scheduled daily run. The main checks are:

- Tests and coverage on Ubuntu and Windows across Python `3.11` through `3.14`
- Format check with `make format` followed by a clean working tree assertion
- Lint and type check with `make lint`
- CodeQL analysis
- Secret scanning
- Dependency audit

Before opening or updating a PR, run:

```bash
make format
make lint
make test
make coverage
```

PRs should use `.github/pull_request_template.md`. Commits are expected to follow Conventional Commits and the repository accepts signed and signed-off commits.

## Agent Notes

- Inspect the relevant files before editing.
- Preserve existing project structure and naming.
- Prefer small, reviewable diffs.
- Do not create, switch, delete, or rewrite Git branches unless explicitly asked.
- Do not commit unless explicitly asked.
- Do not run externally visible release or publish steps from a local agent session.
