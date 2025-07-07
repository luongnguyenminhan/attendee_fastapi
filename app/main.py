from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_db_and_tables()
    yield
    # Shutdown

app = FastAPI(
    title="Attendee API",
    description="API for managing meeting bots and integrations",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "FastAPI application is running"}

from app.modules.users.auth import router as auth_router

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

from app.modules.users.routes import router as users_router
from app.modules.projects.routes import router as projects_router

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(projects_router, prefix="/projects", tags=["Projects"])

from app.modules.bots.routes import router as bots_router

app.include_router(bots_router, prefix="/bots", tags=["Bots"])

from app.modules.jobs.routes import router as jobs_router

app.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])

