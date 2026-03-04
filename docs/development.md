# Development Guide

This guide covers the development setup, workflows, and best practices for AI CMS.

## 🛠️ Development Environment Setup

### Prerequisites

Install the following tools:

```bash
# Docker & Docker Compose
brew install docker docker-compose

# Node.js 22+
brew install node@22

# pnpm
npm install -g pnpm

# Python 3.13+
brew install python@3.13

# uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# GitHub CLI
brew install gh
```

### Initial Setup

1. Clone the repository:
```bash
git clone git@github.com:docmet/aicms.git
cd aicms
```

2. Initialize the environment:
```bash
./cli.sh init
```

This will:
- Create `.env` from `env.example`
- Configure git hooks
- Install frontend dependencies (pnpm)
- Install backend dependencies (uv)
- Start Docker services
- Run database migrations
- Seed the database

3. Start the development stack:
```bash
./cli.sh start
```

## 📋 Development Workflow

### Daily Development

```bash
# Start services
./cli.sh start

# Make changes to code

# Run tests
./cli.sh test

# Run linters
./cli.sh lint

# Format code
./cli.sh format

# Type check
./cli.sh typecheck

# Commit (pre-commit hooks will run automatically)
git add .
git commit -m "feat(frontend): add new feature"
```

### Database Operations

```bash
# Run migrations
./cli.sh db:migrate

# Seed database
./cli.sh db:seed

# Reset database (drop, create, migrate, seed)
./cli.sh db:reset

# Clean database volume only
./cli.sh clean-db
```

### Service Management

```bash
# Start all services
./cli.sh start

# Stop all services
./cli.sh stop

# Restart all services
./cli.sh restart

# Restart frontend only
./cli.sh restart-frontend

# Restart backend only
./cli.sh restart-backend

# View logs
./cli.sh logs
```

## 🎨 Frontend Development

### Technology Stack

- **Next.js 15+** with App Router
- **TypeScript** with strict mode
- **TailwindCSS** for styling
- **shadcn/ui** for UI components
- **Vitest** for testing

### Project Structure

```
frontend/
├── src/
│   ├── app/              # App Router pages
│   │   ├── (public)/     # Public pages
│   │   ├── (dashboard)/  # Protected admin pages
│   │   └── [site_slug]/  # Public site routing
│   ├── components/       # React components
│   │   ├── ui/          # shadcn/ui components
│   │   └── admin/       # Admin-specific components
│   ├── lib/             # Utilities and helpers
│   └── styles/          # Global styles and theme config
├── package.json
├── pnpm-lock.yaml
├── tailwind.config.ts
└── next.config.ts
```

### Adding New Components

```bash
cd frontend

# Add shadcn/ui component
pnpm dlx shadcn@latest add button

# Create custom component
mkdir -p src/components/admin
touch src/components/admin/MyComponent.tsx
```

### Running Tests

```bash
cd frontend
pnpm test
```

### Code Style

- Use TypeScript strict mode
- Follow React best practices
- Use functional components with hooks
- Prefer composition over inheritance
- Use TailwindCSS for styling

## 🔧 Backend Development

### Technology Stack

- **Python 3.13+**
- **FastAPI** for API
- **SQLAlchemy** (async) for ORM
- **PostgreSQL** for database
- **Alembic** for migrations
- **Pytest** for testing

### Project Structure

```
backend/
├── src/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration settings
│   ├── database.py      # Database setup
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── api/             # API routes
│   ├── services/        # Business logic
│   └── tests/           # Tests
├── pyproject.toml
├── Dockerfile
└── seeds/
    └── seed.py          # Database seeding
```

### Adding New API Endpoints

1. Create Pydantic schemas in `src/schemas/`
2. Create API routes in `src/api/`
3. Add business logic in `src/services/`
4. Register routes in `src/main.py`

Example:

```python
# src/schemas/item.py
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class ItemCreate(BaseModel):
    name: str
    description: str

class ItemResponse(BaseModel):
    id: UUID
    name: str
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# src/api/items.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.item import ItemCreate, ItemResponse
from src.services.item import ItemService

router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=ItemResponse)
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_db)
):
    return await ItemService.create_item(db, item)

# src/main.py
from src.api.items import router as items_router

app.include_router(items_router)
```

### Database Migrations

```bash
cd backend

# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migration
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

### Running Tests

```bash
cd backend

# Unit tests
uv run pytest tests/unit -v

# Integration tests
uv run pytest tests/integration -v

# All tests
uv run pytest tests/ -v
```

### Code Style

- Follow PEP 8 style guide
- Use type hints everywhere
- Use async/await for database operations
- Write docstrings for all functions
- Keep functions small and focused

## 🐳 Docker Development

### Development Compose

The `docker-compose.dev.yml` includes:
- Volume mounts for hot reload
- Debug configuration
- Development database

### Production Compose

The `docker-compose.yml` includes:
- Optimized builds
- No volume mounts
- Production database
- Health checks

### Common Commands

```bash
# Start development stack
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop stack
docker-compose -f docker-compose.dev.yml down

# Rebuild services
docker-compose -f docker-compose.dev.yml build --no-cache

# Execute command in container
docker-compose -f docker-compose.dev.yml exec backend uv run python -m pytest
```

## 🧪 Testing

### Frontend Tests

```bash
cd frontend
pnpm test
```

### Backend Tests

```bash
cd backend
uv run pytest tests/ -v
```

### Integration Tests

Integration tests require the database to be running:

```bash
# Start database
./cli.sh start

# Run integration tests
cd backend
uv run pytest tests/integration -v
```

## 🤖 MCP Development

### MCP Server Architecture

The MCP server provides AI tool integration via HTTP+SSE transport:

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Claude    │──────▶│   MCP Proxy │──────▶│   MCP Server│
│   Desktop   │  OAuth│   (Nginx)   │  HTTP │   (FastAPI) │
└─────────────┘      └─────────────┘      └──────┬──────┘
                                                  │
                                                  ▼
                                            ┌─────────────┐
                                            │   Backend   │
                                            └─────────────┘
```

### Testing MCP Tools Locally

1. Start all services:
   ```bash
   ./cli.sh start
   ```

2. Get your JWT token by logging in:
   ```bash
   curl -X POST http://localhost/api/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=your@email.com&password=yourpassword"
   ```

3. Register an MCP client:
   ```bash
   curl -X POST http://localhost/api/mcp/register \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "Claude Test", "tool_type": "claude"}'
   ```
   Response: `{"id": "uuid", "token": "mcp-token"}`

4. Test tools/list via curl:
   ```bash
   curl -X POST http://localhost/sse/YOUR-CLIENT-ID \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer MCP-TOKEN" \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
   ```

5. Test creating a site:
   ```bash
   curl -X POST http://localhost/sse/YOUR-CLIENT-ID \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer MCP-TOKEN" \
     -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"create_site","arguments":{"name":"Test Site","slug":"test"}}}'
   ```

### MCP Server Logs

```bash
# View MCP server logs
./cli.sh logs:mcp-server

# Or via docker
docker-compose -f docker-compose.dev.yml logs mcp_server -f
```

### Adding New MCP Tools

1. Add tool definition in `mcp_server/src/main.py`:
   ```python
   {"name": "my_tool", "description": "...", "inputSchema": {...}}
   ```

2. Add handler in tools/call section:
   ```python
   elif tool_name == "my_tool":
       response = await client.get(...)
       content_text = process_response(response)
   ```

3. Test via curl before testing with Claude

## 📝 Commit Convention

We use conventional commits with scopes:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test changes
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### Scopes

- `frontend`: Frontend changes
- `backend`: Backend changes
- `api`: API changes
- `infra`: Infrastructure changes
- `docs`: Documentation changes
- `test`: Test changes
- `mcp`: MCP server changes (future)
- `deploy`: Deployment changes

### Examples

```
feat(frontend): add login page

Implement login page with email/password form.
Add validation and error handling.

Closes #123
```

```
fix(backend): resolve auth token issue

Fix JWT token expiration validation.
Add proper error messages for expired tokens.

Fixes #456
```

```
refactor(backend): simplify theme service

Extract theme loading logic into separate function.
Improve code readability and testability.
```

## 🔒 Security Best Practices

### Authentication

- Use JWT tokens with short expiration
- Implement refresh token rotation
- Store passwords using bcrypt
- Use HTTPS in production

### Data Validation

- Validate all inputs with Pydantic
- Sanitize user inputs to prevent XSS
- Use parameterized queries (SQLAlchemy handles this)
- Implement rate limiting

### Multi-Tenancy

- Always scope queries to authenticated user
- Validate ownership on all operations
- Never expose internal IDs in URLs
- Implement proper authorization checks

## 🚀 Deployment

### Staging Deployment

Deployment is automated via GitHub Actions:

1. Push to `main` branch
2. CI/CD runs tests
3. Coolify webhook triggers deployment
4. Application deploys to staging

### Manual Deployment

```bash
# Build production images
./cli.sh build

# Deploy to Coolify (via CLI or web UI)
# See docs/deployment.md for details
```

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com/)

## 🆘 Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.dev.yml ps postgres

# Restart database
./cli.sh restart-backend

# Reset database
./cli.sh db:reset
```

### Frontend Build Issues

```bash
# Clear Next.js cache
cd frontend
rm -rf .next

# Reinstall dependencies
rm -rf node_modules
pnpm install
```

### Backend Import Issues

```bash
# Reinstall dependencies
cd backend
uv sync --dev

# Check Python version
python3 --version  # Should be 3.13+
```

### Git Hook Issues

```bash
# Skip hooks (not recommended)
git commit --no-verify -m "message"

# Reconfigure hooks
git config core.hooksPath .githooks
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Commit with conventional commits
6. Push to your fork
7. Create a pull request
