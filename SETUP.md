# Setup

Signal is developed Linux-first. Windows + Docker Desktop is a secondary validation target. This document records only dependencies that are real at the current implementation stage.

## Phase 1 prerequisites

- Git
- Python 3.12

Docker is planned for later runtime components and is **not required for Phase 1**.

## Fresh Linux setup

Clone the repository:

```bash
git clone https://github.com/Alokik24/Signal.git
cd Signal
```

Create and activate a clean virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

If Debian/Ubuntu reports that `ensurepip` is unavailable, install the matching venv package first:

```bash
sudo apt install python3.12-venv
```

Install the pinned project dependencies:

```bash
python -m pip install -r requirements.txt
```

Do not install the project's dependencies globally.

## Validate the Phase 1 foundation

Run formatting, linting, and tests through the active Python interpreter:

```bash
python -m ruff format --check .
python -m ruff check .
python -m pytest
```

Start the API from the repository root:

```bash
python -m uvicorn src.signal.main:app --reload
```

In another terminal, verify the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Clean-environment validation

For a meaningful setup test, remove the virtual environment and recreate it from the repository:

```bash
deactivate
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m ruff format --check .
python -m ruff check .
python -m pytest
```

This verifies that Signal does not accidentally depend on globally installed packages.

## Dependency policy

`requirements.txt` contains the pinned direct runtime and development/test requirements used by Signal at this stage. Update it deliberately when a dependency changes. Do not add packages merely to create a capability or keyword; use the Phase 0 capability register and build-vs-integrate rule.

## CI

GitHub Actions installs the same `requirements.txt` and runs the same formatting, linting, and test checks. A local pass and a CI pass are both expected before considering the Phase 1 foundation validated.

## Later phases

Additional prerequisites such as PostgreSQL, DuckDB, Ollama/local inference, Node/React, n8n, or Docker services will be added here only when their corresponding implementation becomes real. Paid external model providers remain optional.
