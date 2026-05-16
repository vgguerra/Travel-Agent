---
name: writing-python-tests
description: "Team pattern for writing Python tests with pytest in team projects (async FastAPI + in-memory fakes). Use this when adding tests to a Python project or debugging existing tests."
---

# Writing Python Tests — A&M standard

Guide for adding tests in team Python projects. Based on the pattern already used in Cortex (FastAPI async + pytest + in-memory fakes), generalizable to other projects.

---

## Standard stack

```toml
# pyproject.toml
[dependency-groups]
dev = [
    "pytest>=9.0.3",
    "pytest-asyncio>=1.3.0",
    "pytest-cov>=7.1.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
filterwarnings = ["ignore::DeprecationWarning"]

[tool.coverage.run]
source = ["src"]

[tool.coverage.report]
show_missing = true
fail_under = 70
```

- `asyncio_mode = "auto"` — every `async def test_*` runs without a marker
- `fail_under = 70` — coverage threshold (adjust per project)

---

## Recommended structure

```
backend/
├── pyproject.toml
├── src/
│   └── <modules>
└── tests/
    ├── __init__.py
    ├── conftest.py          # Shared fixtures
    ├── test_<module1>.py
    ├── test_<module2>.py
    └── test_<routeX>.py
```

Always run with `PYTHONPATH=src`:

```bash
PYTHONPATH=src python -m pytest tests/ -q --tb=line
# or with uv
uv run pytest tests/ -q --tb=line
```

---

## conftest.py — the core

`conftest.py` centralizes **shared fixtures** and **global mocks** (database, external services). Pattern:

```python
"""Shared test fixtures — mocked database, auth, and services."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# In-memory state (reset between tests)
_tables: dict[str, list[dict]] = {}


@pytest.fixture(autouse=True)
def clean_db():
    """Reset in-memory DB before each test."""
    _tables.clear()
    yield
    _tables.clear()


@asynccontextmanager
async def fake_get_db():
    # Yield a fake connection + cursor backed by _tables
    ...


@pytest.fixture()
def app():
    """FastAPI app with mocked database and external services."""
    with (
        patch("config.database.db.get_db", side_effect=fake_get_db),
        patch("config.database.db.initialize_database", new_callable=AsyncMock),
        patch("services.external_client.send", return_value=True),
    ):
        from app import app as fastapi_app
        yield fastapi_app


@pytest.fixture()
async def client(app):
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture()
def auth_headers():
    from utils.security import create_access_token
    token = create_access_token({"user_id": 1, "role": "consultant"})
    return {"Authorization": f"Bearer {token}"}
```

**Principles**:
1. **No hits on real external services** — mock DB, email, external APIs, blob storage
2. **State reset between tests** — `autouse=True` fixture that resets
3. **Auth-specific fixtures** — one per role (auth_headers, admin_headers, owner_headers)
4. **Factory helpers** — `make_user()`, `make_plugin_zip()`, etc — don't recreate in each test

---

## Test file structure

One file per code module; classes group related endpoints or units:

```python
"""Tests for auth routes."""

import pytest


class TestLogin:
    """POST /api/v1/auth/login"""

    async def test_login_success(self, client, auth_headers):
        res = await client.post("/api/v1/auth/login", data={...})
        assert res.status_code == 200
        assert "access_token" in res.json()

    async def test_login_invalid_credentials(self, client):
        res = await client.post(
            "/api/v1/auth/login",
            data={"username": "nobody", "password": "wrong"},
        )
        assert res.status_code == 401


class TestMe:
    """GET /api/v1/auth/me"""

    async def test_me_no_token(self, client):
        res = await client.get("/api/v1/auth/me")
        # HTTPBearer returns 401 or 403 depending on config
        assert res.status_code in (401, 403)
```

**Conventions**:
- Class: `TestXxx` with docstring naming the endpoint/module
- Method: `test_<specific_scenario>` in snake_case
- `async def` when the test hits an async route
- Auth-missing status accepts `in (401, 403)` — varies per config

---

## What to test

In priority order:

1. **Auth routes** — login, invalid token, permissions, admin endpoints without admin return 403
2. **Input validation** — missing fields, invalid format, size limits
3. **Critical business logic** — rules the code promises to uphold
4. **Pure functions** — helpers that transform data (parsing, calculations)
5. **Error cases** — 404, 409, 500 must not leak sensitive data

**Do not test**:
- Trivial getters/setters
- Framework config (FastAPI already has its own tests)
- External dependencies (aiomysql already has its own tests)

---

## Practical tips

### Testing input validation (Pydantic)
```python
async def test_register_short_password(self, client):
    res = await client.post("/api/v1/auth/register", json={
        "username": "test", "email": "t@x.com", "password": "123",
    })
    assert res.status_code == 422  # Pydantic ValidationError
```

### Testing 4xx/5xx responses
```python
async def test_duplicate_email(self, client):
    # ... create a user with an email
    res = await client.post(..., json={"email": "same@x.com", ...})
    assert res.status_code == 409
    assert "already registered" in res.json()["detail"].lower()
```

### Testing upload (multipart)
```python
import io

async def test_upload_zip(self, client, admin_headers):
    zip_bytes = b"..."
    res = await client.post(
        "/api/v1/plugins/upload",
        files={"file": ("test.zip", io.BytesIO(zip_bytes), "application/zip")},
        headers=admin_headers,
    )
```

### Pure functions
Whenever possible, keep complex logic in pure (I/O-free) functions — they're trivially testable without mocks:

```python
def test_slugify():
    from utils.text import slugify
    assert slugify("Hello World") == "hello-world"
    assert slugify("  a  ") == "a"
    assert slugify("") == ""
```

---

## Coverage

```bash
uv run pytest tests/ --cov=src --cov-report=term-missing
```

Rule of thumb:
- New routes: coverage > 80%
- Pure helpers: 100%
- External services (mocked): cover happy path + 1-2 errors

`fail_under = 70` in pyproject.toml turns CI red if overall coverage drops below.

---

## CI integration

```yaml
# .github/workflows/deploy.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --dev
        working-directory: ./backend
      - run: uv run pytest tests/ -v --tb=short
        working-directory: ./backend
        env:
          PYTHONPATH: src

  deploy:
    needs: test  # block deploy if tests fail
    ...
```

---

## Pre-commit hook

Recommended to run tests in `.husky/pre-commit` (or equivalent) when the diff has `.py`:

```bash
staged_py=$(git diff --cached --name-only --diff-filter=ACM -- '*.py')
if [ -n "$staged_py" ]; then
  PYTHONPATH=src python3 -m pytest tests/ -q --tb=line || exit 1
fi
```

---

## Antipatterns

- Tests hitting a real external service (flaky, slow)
- Order-dependent tests (state leaking between tests — use `autouse` reset fixture)
- Mocking everything: if the only real code tested is a single `return`, the test covers nothing
- Asserting exact error messages ("exactly this string") — makes the suite brittle
- Forgetting `async def` in an async test (test silently passes without testing)

---

## References

- Pytest docs: https://docs.pytest.org/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- httpx async testing: https://www.python-httpx.org/async/
- Real example in Cortex: [../../../Cortex/backend/tests/](../../../Cortex/backend/tests/)
