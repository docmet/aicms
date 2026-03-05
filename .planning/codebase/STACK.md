# Tech Stack

## Languages & Runtime
- **Frontend**: TypeScript 5.7, Node.js 22.0+
- **Backend**: Python 3.13+
- **MCP Server**: Python 3.13+
- **Runtime**: Node.js (frontend), Python (backend, MCP)

## Frameworks
- **Frontend**: Next.js 15 (App Router), React 19
- **Backend**: FastAPI 0.115+, Uvicorn
- **MCP Server**: FastAPI 0.104+, MCP Protocol 1.0+
- **Database ORM**: SQLAlchemy 2.0+ (async)

## Key Dependencies

### Frontend
- **UI**: React 19, TailwindCSS 3.4, shadcn/ui, Radix UI
- **Animation**: Framer Motion 12.34, TailwindCSS Animate
- **HTTP Client**: axios 1.13
- **Type System**: TypeScript 5.7
- **Quality**: ESLint 8.57, Prettier 3.4, Vitest 2.1
- **Utilities**: clsx, class-variance-authority, tailwind-merge

### Backend
- **HTTP**: httpx 0.28+ (async)
- **Auth**: python-jose 3.3+ (JWT), passlib 1.7+ (bcrypt), bcrypt<4.1
- **Validation**: Pydantic 2.10+, pydantic-settings 2.6+
- **DB Driver**: asyncpg 0.30+
- **Migrations**: Alembic 1.14+
- **Testing**: pytest 8.3+, pytest-asyncio 0.24+, pytest-cov 6.0+
- **Quality**: black 24.10+, ruff 0.8+, isort 5.13+, mypy 1.13+
- **Forms**: python-multipart 0.0.12
- **Env**: python-dotenv 1.0+

### MCP Server
- **Protocol**: mcp 1.0+
- **HTTP**: httpx 0.27+ (async)
- **Data**: Pydantic 2.0+, SQLAlchemy async, asyncpg
- **Auth**: python-jose 3.3+
- **Web**: FastAPI 0.104+, Uvicorn

## Configuration
- **Build**: Hatchling (Python), Next.js (frontend)
- **Env**: `.env.example` documents all required variables
- **Format**:
  - Frontend: Prettier (`prettier.config.json`)
  - Backend: Black (88-char), isort profile=black
- **Lint**:
  - Frontend: ESLint (`.eslintrc.json`)
  - Backend: Ruff (E, F, I, N, W, UP rules)
- **Typecheck**: mypy (Python), `tsc --noEmit` (TypeScript)
- **Migrations**: Alembic, timestamp format `YYYYMMDD_HHMM_slug`

## Package Management
- **Frontend**: pnpm — locked via `pnpm-lock.yaml`, Node >=22.0.0
- **Backend/MCP**: uv — `pyproject.toml` PEP 621 format, Python >=3.13

## Build & Deployment
- **Containerization**: Docker multi-stage builds
  - Frontend: `node:22-slim` (dev) → `node:22-alpine` (prod)
  - Backend: `python:3.13-slim`
  - MCP Server: `python:3.13-slim`
  - Nginx: `nginx:alpine`
  - Database: `postgres:16-alpine`
- **Orchestration**: Docker Compose
  - `docker-compose.dev.yml` — hot-reload volumes
  - `docker-compose.prod.yml` — production builds
- **Production startup**: `backend/start.sh` runs `alembic upgrade head` then uvicorn

## CLI
- `./cli.sh` — single source of truth for all dev commands
  - `lint`, `typecheck`, `test`, `start`, `deploy:prod`, etc.
  - ALWAYS use cli.sh, never raw npx/pnpm/uv
- lefthook: pre-commit hooks run lint → typecheck → test
