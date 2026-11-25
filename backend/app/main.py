"""FastAPI Application entrypoint with lifespan janitor, CORS, and routers."""
import asyncio
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
)
from app.storage.session_manager import SessionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("preprocessing_backend")


async def periodic_session_cleanup():
    """Background loop that periodically prunes expired session files."""
    interval_seconds = settings.SESSION_CLEANUP_INTERVAL_MINUTES * 60
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            purged = SessionManager.cleanup_expired_sessions()
            if purged > 0:
                logger.info("Janitor cleaned up %d expired sessions.", purged)
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.warning("Error during session janitor run: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager to run background maintenance."""
    logger.info("Initializing Data Preprocessing Backend...")
    # Initial quick cleanup of any stale sessions on startup
    purged_start = SessionManager.cleanup_expired_sessions()
    logger.info("Startup cleanup removed %d old sessions.", purged_start)
    
    # Launch background janitor task
    cleanup_task = asyncio.create_task(periodic_session_cleanup())
    yield
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    logger.info("Backend shut down cleanly.")


def create_application() -> FastAPI:
    """Factory creating and configuring the FastAPI app."""
    app = FastAPI(
        title="Data Preprocessing & Cleaning API",
        version="0.1.0",
        description="Stateless REST API for automated dataset ingestion, profiling, and preprocessing.",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom Exception Handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Include API Routers
    app.include_router(api_v1_router, prefix="/api")

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": "0.1.0",
            "environment": settings.ENVIRONMENT,
            "max_upload_size_mb": settings.MAX_UPLOAD_SIZE_MB
        }

    return app


app = create_application()

