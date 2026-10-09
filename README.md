# TaskFlow API

A compact educational REST API for task management using Python, FastAPI, SQLAlchemy and SQLite.

## Features

- Task CRUD: create, list, retrieve, partially update and delete
- Status (`todo`, `in_progress`, `done`), priority (`low`, `medium`, `high`), due dates
- Filtering, case-insensitive title search, sorting, pagination
- Task statistics, request validation, interactive OpenAPI docs
- Isolated Pytest integration tests and GitHub Actions CI

## Requirements

Python 3.11 or newer.

## Run locally

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Visit http://127.0.0.1:8000/docs . On Linux/macOS use `.venv/bin/python` instead.

## Example

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tasks/ -H "Content-Type: application/json" -d '{"title":"Write tests","priority":"high"}'
curl http://127.0.0.1:8000/api/v1/tasks/?status=todo
```

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Liveness |
| GET | `/api/v1/tasks/` | List/filter/search/sort/paginate |
| POST | `/api/v1/tasks/` | Create |
| GET | `/api/v1/tasks/{task_id}` | Retrieve |
| PATCH | `/api/v1/tasks/{task_id}` | Partial update |
| DELETE | `/api/v1/tasks/{task_id}` | Delete |
| GET | `/api/v1/stats/` | Counts by status |

## Tests

```bash
python -m pytest -v
ruff check .
```

## Docker

```bash
docker build -t taskflow-api .
docker run --rm -p 8000:8000 taskflow-api
```

For persistent data, mount a writable volume and set `DATABASE_URL` accordingly.

## Architecture

- `app/api/routes`: HTTP endpoints and status codes
- `app/schemas`: Pydantic validation and response contracts
- `app/services`: database operations and business logic
- `app/models`: SQLAlchemy ORM table definitions
- `app/db`: engine and request-scoped database sessions
- `tests`: API integration tests against isolated in-memory SQLite

## Scope and limitations

This is a **single-user local demo**. No authentication or authorization is implemented. **Do not expose it publicly with write access**. SQLite `create_all()` is for initial schema creation, not migrations. SQLite stores UTC timestamps without timezone metadata; treat stored values as UTC. `GET /health` is a liveness check, not a database readiness check. Version constraints are not a lockfile. Tests and linting must pass in your own environment before publishing a release.
