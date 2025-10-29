import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router
from backend.config import get_settings
from backend.services.scheduler_service import initialize_scheduler, scheduler_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = logging.getLogger("uvicorn.error")
    logger.info("🚀 Starting Canvas AI Labs Backend...")

    # Initialize background scheduler
    try:
        initialize_scheduler()
        logger.info("⏰ Background scheduler initialized")
    except Exception as exc:
        logger.exception("Failed to initialize background scheduler: %s", exc)

    yield

    # Shutdown
    logger.info("🛑 Shutting down Canvas AI Labs Backend...")
    try:
        if scheduler_service:
            scheduler_service.shutdown()
    except Exception as exc:
        logger.exception("Error during scheduler shutdown: %s", exc)
    logger.info("✅ Shutdown complete")


app = FastAPI(
    title="Canvas AI Labs Backend",
    description="Intelligent Canvas assistant with AI-powered insights and automation",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - Strong configuration for localhost:3000
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Canvas AI Labs Backend is running!"}


"""Static files configuration."""
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
static_dir = os.path.join(repo_root, "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Serve the dashboard at the root
@app.get("/")
def serve_dashboard():
    dashboard_path = os.path.join(static_dir, "dashboard.html")
    if os.path.isfile(dashboard_path):
        return FileResponse(dashboard_path)
    return {"message": "Dashboard not found"}


app.include_router(router)
