from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minio-secret-password"
    MINIO_BUCKET_NAME: str = "videos"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()