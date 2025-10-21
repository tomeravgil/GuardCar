from fastapi import FastAPI
from datetime import datetime
from app.api.routers import suspicion
from app.api.schemas.thresholds import UIThresholds

app = FastAPI(title="GuardCar API")

app.include_router(suspicion.router)

@app.get("/")
def root():
    return {
        "API": "GuardCar Suspicion Result",
        "server_time": datetime.now().astimezone().isoformat(sep=" "),
    }

@app.get("/healthz")
def health():
    return {"ok": True}
