#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${PROJECT_ROOT}/.env"
ENV_EXAMPLE="${PROJECT_ROOT}/.env.example"
COMPOSE_DEV="${PROJECT_ROOT}/docker-compose.dev.yml"
COMPOSE_PROD="${PROJECT_ROOT}/docker-compose.prod.yml"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"
BACKEND_DIR="${PROJECT_ROOT}/backend"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect docker compose command
compose_cmd() {
  if docker compose version &>/dev/null; then
    echo "docker compose"
  elif command -v docker-compose &>/dev/null; then
    echo "docker-compose"
  else
    log_error "Neither 'docker compose' nor 'docker-compose' found"
    exit 1
  fi
}

usage() {
  cat <<'EOF'
🚀 AI CMS CLI

Usage: ./cli.sh <command>

Commands:
  init                 Initialize the development environment
  start                Start all development services (Docker)
  stop                 Stop all services
  restart              Restart all services
  restart-frontend     Restart frontend container
  restart-backend      Restart backend container
  logs                 Show logs from all services
  logs:frontend        Show frontend logs
  logs:backend         Show backend logs
  logs:postgres        Show postgres logs
  
  lint                 Run all linters
  lint:frontend        Run frontend linter
  lint:backend         Run backend linter
  
  format               Format all code
  format:frontend      Format frontend code
  format:backend       Format backend code
  
  test                 Run all tests
  test:frontend        Run frontend tests
  test:backend         Run backend tests
  test:integration     Run backend integration tests
  
  typecheck            Run type checking
  typecheck:frontend   Run frontend type check
  typecheck:backend    Run backend type check
  
  db:migrate           Run database migrations
  db:seed              Seed the database
  db:reset             Reset database (drop, create, migrate, seed)
  clean-db             Remove database volume only
  
  build                Build Docker images for production
  build:frontend       Build frontend only
  build:backend        Build backend only
  deploy:prod          Build + start production stack (docker-compose.prod.yml)
  
  mcp:install          Install MCP server dependencies
  mcp:run              Run MCP server (requires token)
  
  verify               Verify all required tools are installed
  clean                Remove all containers, volumes, and build artifacts
  help                 Show this help message
EOF
}

configure_hooks_path() {
  if ! command -v git >/dev/null 2>&1; then
    return
  fi

  if ! git -C "${PROJECT_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    return
  fi

  local desired=".githooks"
  local current
  current=$(git -C "${PROJECT_ROOT}" config --get core.hooksPath || true)

  if [[ "${current}" != "${desired}" ]]; then
    git -C "${PROJECT_ROOT}" config core.hooksPath "${desired}"
    log_success "Configured git hooks path to ${desired}"
  fi
}

setup_dependencies() {
  log_info "Installing dependencies..."
  
  if [[ -d "${FRONTEND_DIR}" ]] && command -v pnpm >/dev/null 2>&1; then
    log_info "Installing frontend dependencies with pnpm..."
    (cd "${FRONTEND_DIR}" && pnpm install)
  else
    log_warn "Frontend dependencies skipped (missing directory or pnpm)"
  fi

  if [[ -d "${BACKEND_DIR}" ]] && command -v uv >/dev/null 2>&1; then
    log_info "Synchronizing backend environment with uv..."
    (cd "${BACKEND_DIR}" && uv sync --dev)
  else
    log_warn "Backend dependencies skipped (missing directory or uv)"
  fi
}

init_command() {
  if [[ ! -f "${ENV_EXAMPLE}" ]]; then
    log_error "env.example not found at ${ENV_EXAMPLE}"
    exit 1
  fi

  configure_hooks_path

  if [[ ! -f "${ENV_FILE}" ]]; then
    cp "${ENV_EXAMPLE}" "${ENV_FILE}"
    log_success "Created ${ENV_FILE} from env.example"
    log_warn "Please review and update the secrets before starting the stack"
    setup_dependencies
    log_info "Once configured, run './cli.sh start' to launch the containers"
    return
  fi

  setup_dependencies
  log_info ".env already exists. You can run './cli.sh start' to launch the containers"
}

start_command() {
  if [[ ! -f "${ENV_FILE}" ]]; then
    log_error ".env not found. Run './cli.sh init' to create it first"
    exit 1
  fi

  local compose_cmd
  compose_cmd="$(compose_cmd)"

  log_info "Starting development stack..."
  ${compose_cmd} -f "${COMPOSE_DEV}" up -d
  
  log_info "Waiting for services to be ready..."
  sleep 5
  
  log_success "Development stack started!"
  log_info "Frontend: http://localhost:3000"
  log_info "Backend API: http://localhost:8000"
  log_info "API Docs: http://localhost:8000/docs"
}

stop_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"

  log_info "Stopping development stack..."
  ${compose_cmd} -f "${COMPOSE_DEV}" down
  log_success "Development stack stopped"
}

restart_command() {
  stop_command
  sleep 2
  start_command
}

restart_frontend_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"

  log_info "Restarting frontend..."
  ${compose_cmd} -f "${COMPOSE_DEV}" restart frontend
  log_success "Frontend restarted"
}

restart_backend_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"

  log_info "Restarting backend..."
  ${compose_cmd} -f "${COMPOSE_DEV}" restart backend
  log_success "Backend restarted"
}

logs_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"
  ${compose_cmd} -f "${COMPOSE_DEV}" logs -f
}

logs_frontend_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"
  ${compose_cmd} -f "${COMPOSE_DEV}" logs -f frontend
}

logs_backend_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"
  ${compose_cmd} -f "${COMPOSE_DEV}" logs -f backend
}

logs_postgres_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"
  ${compose_cmd} -f "${COMPOSE_DEV}" logs -f postgres
}

lint_frontend_command() {
  if [[ -d "${FRONTEND_DIR}" ]] && command -v pnpm >/dev/null 2>&1; then
    log_info "Running frontend lint..."
    (cd "${FRONTEND_DIR}" && pnpm run lint)
  else
    log_warn "Frontend lint skipped (missing directory or pnpm)"
  fi
}

lint_backend_command() {
  if [[ -d "${BACKEND_DIR}" ]] && command -v uv >/dev/null 2>&1; then
    log_info "Running backend lint..."
    (cd "${BACKEND_DIR}" && uv run ruff check .)
  else
    log_warn "Backend lint skipped (missing directory or uv)"
  fi
}

lint_command() {
  log_info "Running all linters..."
  lint_frontend_command
  lint_backend_command
  log_success "Linting completed"
}

format_frontend_command() {
  if [[ -d "${FRONTEND_DIR}" ]] && command -v pnpm >/dev/null 2>&1; then
    log_info "Formatting frontend code..."
    (cd "${FRONTEND_DIR}" && pnpm run format)
  else
    log_warn "Frontend formatting skipped (missing directory or pnpm)"
  fi
}

format_backend_command() {
  if [[ -d "${BACKEND_DIR}" ]] && command -v uv >/dev/null 2>&1; then
    log_info "Formatting backend code..."
    (cd "${BACKEND_DIR}" && uv run black . && uv run isort .)
  else
    log_warn "Backend formatting skipped (missing directory or uv)"
  fi
}

format_command() {
  log_info "Formatting all code..."
  format_frontend_command
  format_backend_command
  log_success "Formatting completed"
}

test_frontend_command() {
  if [[ -d "${FRONTEND_DIR}" ]] && command -v pnpm >/dev/null 2>&1; then
    log_info "Running frontend tests..."
    (cd "${FRONTEND_DIR}" && pnpm test)
  else
    log_warn "Frontend tests skipped (missing directory or pnpm)"
  fi
}

test_backend_command() {
  if [[ -d "${BACKEND_DIR}" ]] && command -v uv >/dev/null 2>&1; then
    log_info "Running backend tests..."
    (cd "${BACKEND_DIR}" && uv run pytest src/tests/ -v)
  else
    log_warn "Backend tests skipped (missing directory or uv)"
  fi
}

test_integration_command() {
  if [[ -d "${BACKEND_DIR}" ]] && command -v uv >/dev/null 2>&1; then
    log_info "Running backend integration tests..."
    (cd "${BACKEND_DIR}" && uv run pytest src/tests/integration -v)
  else
    log_warn "Backend integration tests skipped (missing directory or uv)"
  fi
}

test_command() {
  log_info "Running all tests..."
  test_frontend_command
  test_backend_command
  log_success "Tests completed"
}

typecheck_frontend_command() {
  if [[ -d "${FRONTEND_DIR}" ]] && command -v pnpm >/dev/null 2>&1; then
    log_info "Running frontend type check..."
    (cd "${FRONTEND_DIR}" && pnpm run typecheck)
  else
    log_warn "Frontend type check skipped (missing directory or pnpm)"
  fi
}

typecheck_backend_command() {
  if [[ -d "${BACKEND_DIR}" ]] && command -v uv >/dev/null 2>&1; then
    log_info "Running backend type check..."
    (cd "${BACKEND_DIR}" && uv run mypy src/)
  else
    log_warn "Backend type check skipped (missing directory or uv)"
  fi
}

typecheck_command() {
  log_info "Running type checks..."
  typecheck_frontend_command
  typecheck_backend_command
  log_success "Type checks completed"
}

is_backend_running() {
  docker inspect -f '{{.State.Running}}' aicms_backend 2>/dev/null | grep -q true
}

db_migrate_command() {
  log_info "Running database migrations..."
  if is_backend_running; then
    local compose_cmd
    compose_cmd="$(compose_cmd)"
    ${compose_cmd} -f "${COMPOSE_DEV}" exec backend uv run alembic upgrade head
  else
    (cd "${BACKEND_DIR}" && uv run alembic upgrade head)
  fi
  log_success "Migrations completed"
}

db_seed_command() {
  log_info "Seeding database..."
  if is_backend_running; then
    local compose_cmd
    compose_cmd="$(compose_cmd)"
    ${compose_cmd} -f "${COMPOSE_DEV}" exec backend uv run python seeds/seed.py
  else
    (cd "${BACKEND_DIR}" && uv run python seeds/seed.py)
  fi
  log_success "Database seeded"
}

db_reset_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"

  log_warn "This will delete all data. Are you sure? (y/N)"
  read -r response
  if [[ ! "$response" =~ ^[Yy]$ ]]; then
    log_info "Aborted"
    return
  fi

  log_info "Resetting database..."
  ${compose_cmd} -f "${COMPOSE_DEV}" down -v
  ${compose_cmd} -f "${COMPOSE_DEV}" up -d postgres

  log_info "Waiting for postgres to be ready..."
  sleep 5

  # Start backend temporarily for migrations (needs DB connection)
  ${compose_cmd} -f "${COMPOSE_DEV}" up -d backend
  log_info "Waiting for backend to be ready..."
  sleep 3

  db_migrate_command
  db_seed_command

  # Bring up the rest of the stack
  ${compose_cmd} -f "${COMPOSE_DEV}" up -d
  log_success "Database reset completed"
}

clean_db_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"

  log_info "Cleaning database volume..."
  ${compose_cmd} -f "${COMPOSE_DEV}" down -v
  docker volume rm aicms_postgres_data 2>/dev/null || true
  log_success "Database volume cleaned"
}

build_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"

  log_info "Building production images..."
  ${compose_cmd} -f "${COMPOSE_PROD}" build
  log_success "Production images built"
}

build_frontend_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"

  log_info "Building frontend image..."
  ${compose_cmd} -f "${COMPOSE_PROD}" build frontend
  log_success "Frontend image built"
}

build_backend_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"

  log_info "Building backend image..."
  ${compose_cmd} -f "${COMPOSE_PROD}" build backend
  log_success "Backend image built"
}
deploy_prod_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"

  log_info "Building and starting production stack..."
  ${compose_cmd} -f "${COMPOSE_PROD}" up -d --build
  log_success "Production stack deployed"
  log_info "Run './cli.sh db:migrate' to apply migrations"
}

verify_command() {
  log_info "Verifying development environment..."
  echo ""
  
  local all_good=true
  
  # Check Docker
  if command -v docker >/dev/null 2>&1; then
    log_success "Docker installed"
  else
    log_error "Docker NOT FOUND - Install: https://docs.docker.com/get-docker/"
    all_good=false
  fi
  
  # Check Docker Compose
  if docker compose version &>/dev/null || command -v docker-compose >/dev/null 2>&1; then
    log_success "Docker Compose installed"
  else
    log_error "Docker Compose NOT FOUND - Install: https://docs.docker.com/compose/install/"
    all_good=false
  fi
  
  # Check Node.js
  if command -v node >/dev/null 2>&1; then
    log_success "Node.js installed: $(node --version)"
  else
    log_error "Node.js NOT FOUND - Install: brew install node@22"
    all_good=false
  fi
  
  # Check pnpm
  if command -v pnpm >/dev/null 2>&1; then
    log_success "pnpm installed: $(pnpm --version)"
  else
    log_error "pnpm NOT FOUND - Install: npm install -g pnpm"
    all_good=false
  fi
  
  # Check Python
  if command -v python3 >/dev/null 2>&1; then
    log_success "Python installed: $(python3 --version)"
  else
    log_error "Python NOT FOUND - Install: brew install python@3.13"
    all_good=false
  fi
  
  # Check uv
  if command -v uv >/dev/null 2>&1; then
    log_success "uv installed: $(uv --version)"
  else
    log_error "uv NOT FOUND - Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    all_good=false
  fi
  
  # Check Git hooks
  if [ -d "${PROJECT_ROOT}/.git" ]; then
    hooks_path=$(git -C "${PROJECT_ROOT}" config --get core.hooksPath || echo "")
    if [ "$hooks_path" = ".githooks" ]; then
      log_success "Git hooks configured"
    else
      log_warn "Git hooks not configured - Run: git config core.hooksPath .githooks"
    fi
  fi
  
  echo ""
  if $all_good; then
    log_success "All required tools are installed!"
  else
    log_error "Some required tools are missing. See above for installation instructions."
    exit 1
  fi
}

clean_command() {
  local compose_cmd
  compose_cmd="$(compose_cmd)"

  log_warn "This will remove all containers, volumes, and build artifacts. Are you sure? (y/N)"
  read -r response
  if [[ ! "$response" =~ ^[Yy]$ ]]; then
    log_info "Aborted"
    return
  fi

  log_info "Cleaning everything..."
  ${compose_cmd} -f "${COMPOSE_DEV}" down -v --remove-orphans
  ${compose_cmd} -f "${COMPOSE_PROD}" down -v --remove-orphans
  docker system prune -f
  log_success "Cleanup completed"
}

mcp_install_command() {
  log_info "Installing MCP server..."
  (cd "${PROJECT_ROOT}/mcp_server" && {
    if command -v uv &> /dev/null; then
      uv sync
    else
      pip install -e .
    fi
  })
  log_success "MCP server installed"
}

mcp_run_command() {
  local api_url="${2:-http://localhost:8000/api/v1}"
  local token="${3:-}"

  if [[ -z "$token" ]]; then
    log_error "API token required. Usage: ./cli.sh mcp:run [api_url] [token]"
    exit 1
  fi

  log_info "Starting MCP server..."
  (cd "${PROJECT_ROOT}/mcp_server" && {
    if command -v uv &> /dev/null; then
      uv run aicms-mcp --api-url "$api_url" --api-token "$token"
    else
      aicms-mcp --api-url "$api_url" --api-token "$token"
    fi
  })
}

main() {
  # Ensure we're in the project root
  cd "${PROJECT_ROOT}"
  
  # Set up Python path
  export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/backend/src"
  
  if [[ $# -lt 1 ]]; then
    usage
    exit 1
  fi

  case "${1:-}" in
    init)
      init_command
      ;;
    start)
      start_command
      ;;
    stop)
      stop_command
      ;;
    restart)
      restart_command
      ;;
    restart-frontend)
      restart_frontend_command
      ;;
    restart-backend)
      restart_backend_command
      ;;
    logs)
      logs_command
      ;;
    logs:frontend)
      logs_frontend_command
      ;;
    logs:backend)
      logs_backend_command
      ;;
    logs:postgres)
      logs_postgres_command
      ;;
    lint)
      lint_command
      ;;
    lint:frontend)
      lint_frontend_command
      ;;
    lint:backend)
      lint_backend_command
      ;;
    format)
      format_command
      ;;
    format:frontend)
      format_frontend_command
      ;;
    format:backend)
      format_backend_command
      ;;
    test)
      test_command
      ;;
    test:frontend)
      test_frontend_command
      ;;
    test:backend)
      test_backend_command
      ;;
    test:integration)
      test_integration_command
      ;;
    typecheck)
      typecheck_command
      ;;
    typecheck:frontend)
      typecheck_frontend_command
      ;;
    typecheck:backend)
      typecheck_backend_command
      ;;
    db:migrate)
      db_migrate_command
      ;;
    db:seed)
      db_seed_command
      ;;
    db:reset)
      db_reset_command
      ;;
    clean-db)
      clean_db_command
      ;;
    build)
      build_command
      ;;
    build:frontend)
      build_frontend_command
      ;;
    build:backend)
      build_backend_command
      ;;
    deploy:prod)
      deploy_prod_command
      ;;
    verify)
      verify_command
      ;;
    clean)
      clean_command
      ;;
    mcp:install)
      mcp_install_command
      ;;
    mcp:run)
      mcp_run_command
      ;;
    help|-h|--help)
      usage
      ;;
    *)
      log_error "Unknown command: $1"
      usage
      exit 1
      ;;
  esac
}

main "$@"
