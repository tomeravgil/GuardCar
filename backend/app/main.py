import asyncio

from fastapi.middleware.cors import CORSMiddleware

from backend.app.dependencies import init_dependencies
from backend.app.core.services.minio.minio_service import init_minio_bucket
from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime
from backend.app.api.routers import suspicion, video_stream
from backend.app.api.routers import sse
from backend.app.api.routers import videos
from backend.app.api.routers import cloud_config
from backend.app.api.routers import suspicion_config


app = FastAPI(title="GuardCar API")

# creating the OAuth2 Scheme object 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # <-- ALLOW OPTIONS HERE
    allow_headers=["*"],
)


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

# creating a POST Endpoint for login at /api/token 
@app.post("/api/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()): # extracting the username and password of the request 
    # test information for auth 
    if form_data.username != "test" or form_data.password != "password":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            # header when authentification fails 
            headers={"WWW-Authenticate": "Bearer"},
        )

    # if theres a correct login, return token for login, currently temp 
    return {"access_token": "Access-Token-Success", "token_type": "Bearer"}

# Extracts the bearer token from the authorization, 
# then validates that the token matches the one at our login endpoint
async def get_current_user(token: str = Security(oauth2_scheme)):
    # Validates the bearer token and then validates the current fake token
    if token != "Access-Token-Success":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # eventually return the real user information, but currently returning dummy user 
    return {"user-name": "test"}

@app.on_event("shutdown")
async def on_shutdown():
    shutdown_event.set()

# declare this after functions to be able to use get_current_user as a dependi
app.include_router(suspicion.router)
app.include_router(sse.router)
# GET /api/videos requires current user token / bearer 
app.include_router(videos.router, dependencies=[Depends(get_current_user)])
app.include_router(cloud_config.router)
app.include_router(suspicion_config.router)
app.include_router(video_stream.router)