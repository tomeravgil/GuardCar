import asyncio

from fastapi.middleware.cors import CORSMiddleware

from backend.app.dependencies import init_dependencies
from backend.app.core.services.minio.minio_service import init_minio_bucket
from fastapi import FastAPI
from datetime import datetime
from backend.app.api.routers import suspicion, video_stream
from backend.app.api.routers import sse
from backend.app.api.routers import videos
from backend.app.api.routers import cloud_config
from backend.app.api.routers import suspicion_config

app = FastAPI(title="GuardCar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # <-- ALLOW OPTIONS HERE
    allow_headers=["*"],
)
app.include_router(suspicion.router)
app.include_router(sse.router)
app.include_router(videos.router)
app.include_router(cloud_config.router)
app.include_router(suspicion_config.router)
app.include_router(video_stream.router)

shutdown_event = asyncio.Event()
@app.on_event("startup")  
async def startup_event():
    """Initialize MinIO bucket on startup"""
    init_minio_bucket()
    init_dependencies(shutdown_event)

@app.get("/")
def root():
    return {
        "API": "GuardCar Backend",
        "server_time": datetime.now().astimezone().isoformat(sep=" "),
    }

@app.get("/healthz")
def health():
    return {"ok": True}

@app.on_event("shutdown")
async def on_shutdown():
    shutdown_event.set()