from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str = "videos"
    
    class Config:
        env_file = str(Path(__file__).parent / ".env")
        case_sensitive = True

settings = Settings()