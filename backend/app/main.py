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

import os 
from datetime import datetime, timedelta 

import jwt 
from dotenv import load_dotenv

# loading the environmental variables and secrets 
load_dotenv()

# get the secrets and keys for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-fallback-change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

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

    # if theres a correct login, return the JWT with username as subject 
    access_token_expiration = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username},expires_in=access_token_expiration)
    return {"access_token": access_token, "token_type": "Bearer"}


# get current user from a token 
def get_user_from_token(token: str):
    try: 
        decodedUser = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = decodedUser.get("sub")
        if username is None:
            return None

        # return fake user object, connect database here 
        return {
            "username": username,
            "role": "admin",
        }

    except jwt.ExpiredSignature:
        return None 
    except jwt.PyJWTError:
        return None 


# Extracts the bearer token from the authorization, 
# then validates that the token matches the one at our login endpoint
async def get_current_user(token: str = Security(oauth2_scheme)):
    user = get_user_from_token(token)
    # Validates the bearer token and then validates the current fake token
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # eventually return the real user information, but currently returning dummy user 
    return user


# Check if the current user has a valid token then return the dictionary
# corrersponding to the current user 
@app.get("/api/me")
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user


@app.on_event("shutdown")
async def on_shutdown():
    shutdown_event.set()


def create_access_token(data: dict, expires_in: timedelta | None = None):
    # copy the data to encode it 
    data_copy = data.copy() 

    # update the expiration date if the secret exists 
    if expires_in is not None:
        expire = datetime.utcnow() + expires_in
    else: 
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # update it in the copy 
    data_copy.update({"exp": expire})

    encoded_JWT = jwt.encode(data_copy, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_JWT


# declare this after functions to be able to use get_current_user as a dependi
app.include_router(suspicion.router)
app.include_router(sse.router)
# GET /api/videos requires current user token / bearer 
app.include_router(videos.router, dependencies=[Depends(get_current_user)])
app.include_router(cloud_config.router)
app.include_router(suspicion_config.router)
app.include_router(video_stream.router)