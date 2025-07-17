from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(router, prefix="/api")
