from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import router as auth_router
from src.api.content import router as content_router
from src.api.mcp import router as mcp_router
from src.api.oauth import router as oauth_router
from src.api.pages import router as pages_router
from src.api.preview import router as preview_router
from src.api.public import router as public_router
from src.api.sites import router as sites_router
from src.api.themes import router as themes_router
from src.config import get_settings

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="AI CMS API",
    description="AI-powered Content Management System API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "AI CMS API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(sites_router, prefix="/api/sites", tags=["sites"])
app.include_router(pages_router, prefix="/api/sites", tags=["pages"])
app.include_router(content_router, prefix="/api/sites", tags=["content"])
app.include_router(themes_router, prefix="/api/themes", tags=["themes"])
app.include_router(public_router, prefix="/api/public/sites", tags=["public"])
app.include_router(mcp_router, prefix="/api/mcp", tags=["mcp"])
app.include_router(oauth_router, tags=["oauth"])
app.include_router(preview_router, prefix="/api/preview", tags=["preview"])
