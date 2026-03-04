from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
async def root():
    """Root endpoint."""
    return {
        "message": "AI CMS API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers (will be added later)
# from src.api import auth, users, sites, pages, content
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
# app.include_router(sites.router, prefix="/api/v1/sites", tags=["sites"])
# app.include_router(pages.router, prefix="/api/v1/pages", tags=["pages"])
# app.include_router(content.router, prefix="/api/v1/content", tags=["content"])
