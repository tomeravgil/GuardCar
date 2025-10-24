from fastapi import FastAPI
from datetime import datetime
from api.routers import suspicion
from api.routers import sse
from api.schemas.thresholds import UIThresholds

app = FastAPI(title="GuardCar API")

app.include_router(suspicion.router)
app.include_router(sse.router)

@app.get("/")
def root():
    return {
        "API": "GuardCar Suspicion Result",
        "server_time": datetime.now().astimezone().isoformat(sep=" "),
    }

@app.get("/healthz")
def health():
    return {"ok": True}
