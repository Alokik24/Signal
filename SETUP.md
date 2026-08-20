# Setup

Signal is developed Linux-first. Windows + Docker Desktop is a secondary validation target. The project is being built incrementally; this document records only dependencies that are real at the current implementation stage.

## Phase 1 prerequisites

- Git
- Python 3.12 or 3.13

Docker is part of the planned reproducible runtime, but it is **not required for Phase 1** because no containerized service exists yet.

## Fresh Linux setup

Clone the repository:

```bash
git clone https://github.com/Alokik24/Signal.git
cd Signal
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project and development dependencies:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Validate the Phase 1 foundation

Run formatting, linting, and tests:

```bash
ruff format --check .
ruff check .
pytest
```

Start the API:

```bash
uvicorn signal.main:app --reload
```

In another terminal, verify the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

The interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Clean-environment validation

For a meaningful setup test, remove the virtual environment and recreate it from the repository:

```bash
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ruff format --check .
ruff check .
pytest
```

This verifies that the project does not accidentally depend on globally installed Python packages.

## CI

GitHub Actions runs the same basic formatting, linting, and test checks. A local pass and a CI pass are both expected before considering the Phase 1 foundation validated.

## Later phases

Additional prerequisites such as PostgreSQL, DuckDB, Ollama/local inference, Node/React, n8n, or Docker services will be added here only when their corresponding implementation becomes real. Paid external model providers remain optional.
