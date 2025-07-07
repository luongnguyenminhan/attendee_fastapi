from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import create_db_and_tables
from app.exceptions.handlers import setup_exception_handlers
from app.middlewares.cors_middleware import setup_cors_middleware
from app.middlewares.logging_middleware import setup_logging_middleware
from app.modules.users.routes.v1.user_routes import router as user_router
from app.modules.users.routes.v1.auth_routes import router as auth_router
from app.modules.organizations.routes.v1.organization_routes import (
    router as organization_router,
)
from app.modules.projects.routes.v1.project_routes import router as project_router
from app.modules.bots.routes.v1.bot_routes import router as bot_router
from app.modules.jobs.routes.v1.job_routes import router as job_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_db_and_tables()
    yield
    # Shutdown


app = FastAPI(
    title="Attendee API",
    description="API for managing meeting bots and integrations with Clean Architecture",
    version="0.1.0",
    lifespan=lifespan,
)

# Setup middlewares
setup_cors_middleware(app)
setup_logging_middleware(app)
# setup_auth_middleware(app, settings.SECRET_KEY)  # Uncomment when ready

# Setup exception handlers
setup_exception_handlers(app)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "FastAPI application is running with Clean Architecture",
    }


# Import and include routes with clean architecture

# Include routers with Clean Architecture
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(
    organization_router, prefix="/api/v1/organizations", tags=["Organizations"]
)
app.include_router(project_router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(bot_router, prefix="/api/v1/bots", tags=["Bots"])
app.include_router(job_router, prefix="/api/v1/jobs", tags=["Jobs"])


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Attendee API with Clean Architecture",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
