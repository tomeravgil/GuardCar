import asyncio
from app.dependencies import init_dependencies
from app.core.services.sse.server_side_events import ServerSideEventsService
from app.core.services.minio.minio_service import init_minio_bucket
from fastapi import FastAPI
from datetime import datetime
from app.api.routers import suspicion
from app.api.routers import sse
from app.api.schemas.thresholds import UIThresholds
from app.api.routers import videos

app = FastAPI(title="GuardCar API")

app.include_router(suspicion.router)
app.include_router(sse.router)
app.include_router(videos.router)
                   
shutdown_event = asyncio.Event()
init_dependencies(shutdown_event)

@app.on_event("startup")  
async def startup_event():
    """Initialize MinIO bucket on startup"""
    init_minio_bucket()

@app.get("/")
def root():
    return {
        "API": "GuardCar Suspicion Result",
        "server_time": datetime.now().astimezone().isoformat(sep=" "),
    }

@app.get("/healthz")
def health():
    return {"ok": True}

@app.on_event("shutdown")
async def on_shutdown():
    shutdown_event.set()