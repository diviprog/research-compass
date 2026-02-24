"""
Research Assistant API - Main FastAPI application.
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db import init_db

import uvicorn
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Initialize database
    print("🚀 Starting up Research Assistant API...")
    init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Research Assistant API...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered research opportunity discovery platform",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "Research Assistant API",
        "status": "running",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "research-assistant-api",
        "version": settings.VERSION
    }


# Import and include API routers
from app.api.auth import router as auth_router
from app.api.opportunities import router as opportunities_router
from app.api.profile import router as profile_router
from app.api.embeddings import router as embeddings_router
from app.api.search import router as search_router
from app.api.outreach import router as outreach_router
from app.api.scrape import router as scrape_router

app.include_router(auth_router, prefix="/api")
app.include_router(opportunities_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(embeddings_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(outreach_router, prefix="/api")
app.include_router(scrape_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

