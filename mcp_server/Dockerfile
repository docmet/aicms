FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy pyproject.toml
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv venv
RUN uv pip install --system mcp httpx pydantic fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg python-jose[cryptography]

# Copy source code
COPY src/ ./src/

# Copy README
COPY README.md ./

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
