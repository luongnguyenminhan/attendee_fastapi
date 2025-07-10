from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.database import create_tables
from app.exceptions.handlers import setup_exception_handlers
from app.middlewares.cors_middleware import setup_cors_middleware
from app.middlewares.logging_middleware import setup_logging_middleware
from app.modules.bots.routes.v1.admin_bot_routes import router as admin_bot_router
from app.modules.bots.routes.v1.bot_routes import router as bot_router
from app.modules.jobs.routes.v1.job_routes import router as job_router
from app.modules.organizations.routes.v1.admin_organization_routes import (
    router as admin_organization_router,
)
from app.modules.organizations.routes.v1.organization_routes import (
    router as organization_router,
)
from app.modules.projects.routes.v1.admin_project_routes import (
    router as admin_project_router,
)
from app.modules.projects.routes.v1.project_routes import router as project_router
from app.modules.system.routes.v1.admin_system_routes import (
    router as admin_system_router,
)
from app.modules.users.routes.v1.admin_user_routes import router as admin_user_router
from app.modules.users.routes.v1.auth_routes import router as auth_router
from app.modules.users.routes.v1.user_routes import router as user_router
from app.modules.websocket.websocket_routes import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await create_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("Server will continue without database...")
    yield
    # Shutdown


app = FastAPI(
    title="Attendee API",
    description="API for managing meeting bots and integrations with Clean Architecture",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup middlewares
setup_cors_middleware(app)
setup_logging_middleware(app)
# setup_auth_middleware(app, settings.SECRET_KEY)  # Uncomment when ready

# Setup exception handlers
setup_exception_handlers(app)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Attendee FastAPI is running",
        "version": "0.1.0",
    }


# Import and include routes with clean architecture

# Include routers with Clean Architecture
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(organization_router, prefix="/api/v1/organizations", tags=["Organizations"])
app.include_router(project_router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(bot_router, prefix="/api/v1/bots", tags=["Bots"])
app.include_router(job_router, prefix="/api/v1/jobs", tags=["Jobs"])

# Admin API endpoints - distributed across modules
app.include_router(admin_system_router, prefix="/api/v1", tags=["Admin - System"])
app.include_router(admin_user_router, prefix="/api/v1", tags=["Admin - Users"])
app.include_router(admin_bot_router, prefix="/api/v1", tags=["Admin - Bots"])
app.include_router(admin_organization_router, prefix="/api/v1", tags=["Admin - Organizations"])
app.include_router(admin_project_router, prefix="/api/v1", tags=["Admin - Projects"])

# WebSocket router
app.include_router(websocket_router, prefix="/api/v1/websocket", tags=["WebSocket"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Attendee FastAPI - Meeting Bot Management System"}
