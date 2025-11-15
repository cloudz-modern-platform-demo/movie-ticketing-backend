"""FastAPI application factory and configuration."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from movie_ticketing_backend.db.session import init_db
from movie_ticketing_backend.route.ticket_route import router as ticket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    
    Args:
        app: FastAPI application instance
    """
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: Cleanup if needed
    pass


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Movie Ticketing Backend API",
        description="API for movie ticket issuing and refunding",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(ticket_router)
    
    @app.get("/", tags=["health"])
    async def root():
        """Root endpoint for health check."""
        return {
            "status": "ok",
            "message": "Movie Ticketing Backend API is running",
            "docs": "/docs",
        }
    
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    return app

