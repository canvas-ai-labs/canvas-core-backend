from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from backend.api.routes import router
from backend.services.scheduler_service import initialize_scheduler, scheduler_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Canvas AI Labs Backend...")
    
    # Initialize background scheduler
    scheduler = initialize_scheduler()
    print("⏰ Background scheduler initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Canvas AI Labs Backend...")
    if scheduler_service:
        scheduler_service.shutdown()
    print("✅ Shutdown complete")


app = FastAPI(
    title="Canvas AI Labs Backend",
    description="Intelligent Canvas assistant with AI-powered insights and automation",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Canvas AI Labs Backend is running!"}

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve the dashboard at the root
@app.get("/")
def serve_dashboard():
    dashboard_path = os.path.join(static_dir, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"message": "Dashboard not found"}

app.include_router(router, prefix="/api")
