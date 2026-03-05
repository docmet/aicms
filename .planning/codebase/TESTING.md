# Testing

## Framework

### Frontend
- **Framework**: Vitest 2.1
- **Run**: `./cli.sh test` → `vitest run`
- **Config**: defined in `frontend/package.json`

### Backend
- **Framework**: pytest 8.3+ with pytest-asyncio 0.24+
- **Coverage**: pytest-cov 6.0+
- **Run**: `./cli.sh test` → `pytest`
- **Config**: `backend/pyproject.toml` `[tool.pytest.ini_options]`

## Test Structure

### Backend
```
backend/src/tests/
├── conftest.py              # Fixtures: DB setup, AsyncClient, auth helpers
├── unit/                    # Unit tests (models, schemas, utils)
└── integration/             # Full API flow tests (HTTP requests → DB)
```

### Frontend
```
frontend/src/test/           # Vitest test files
```
- Frontend test coverage is minimal currently — Vitest is configured but few tests written

## Running Tests
```bash
./cli.sh test                # Run all tests (frontend + backend)
./cli.sh test:backend        # Backend only (pytest)
./cli.sh test:frontend       # Frontend only (vitest run)
```

## Backend Testing Patterns

### conftest.py fixtures
```python
@pytest.fixture
async def db():
    # SQLite in-memory for isolation
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
async def client(db):
    app.dependency_overrides[get_db] = lambda: db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_headers(client):
    # Register + login → return Bearer headers
```

### Async test pattern
```python
@pytest.mark.asyncio
async def test_create_site(client, auth_headers):
    response = await client.post("/api/sites", json={
        "name": "Test Site",
        "slug": "test-site"
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["slug"] == "test-site"
```

### Coverage areas (backend)
- Auth: register, login, token validation
- Site CRUD: create, list, update, delete, plan limits
- Page CRUD
- Content: upsert by type, publish flow
- Public API: published-only content, no auth
- Themes: list, apply
- MCP client: registration, token auth

## Frontend Testing Patterns
- Vitest configured but test files sparse
- Test pattern: standard React Testing Library + Vitest
- No snapshot tests currently

## Mocking
### Backend
- DB: SQLite in-memory (via `app.dependency_overrides[get_db]`)
- External HTTP: `httpx.MockTransport` or monkeypatching `httpx.AsyncClient`
- Auth: dependency override for `get_current_user`

### Frontend
- API calls: mock via `vi.mock('@/lib/api')`
- No MSW setup currently

## Test Data
- **Seed script**: `backend/seeds/seed.py` — creates users + demo sites
- **Demo content**: `backend/seeds/demo_data.py` — rich section content
- **Test credentials**:
  - Admin: `norbi@docmet.com` / `password123`
  - Client: `client@docmet.com` / `password123`
- **Manual seed**: `./cli.sh seed` or `./cli.sh seed:demo`

## Coverage Gaps
- Frontend components largely untested
- MCP server tools have no automated tests
- OAuth flow not tested end-to-end
- No load / performance tests
- No E2E tests (Playwright/Cypress not set up)
- Admin impersonation flow untested
