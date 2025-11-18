from pydantic import BaseModel, Field
from datetime import datetime

class VideoMetadata(BaseModel):
    """
    Defines the data model for a video's metadata.
    This is used for API responses.
    """
    video_id: str = Field(..., description="The unique object name in MinIO (e.g., <uuid>.mp4)")
    title: str
    description: str | None = None
    location: str | None = None
    camera_id: str
    capture_timestamp: datetime | None = None
    upload_timestamp: datetime = Field(..., description="Timestamp of when the file was uploaded to MinIO")
    content_type: str
    size_mb: float = Field(..., description="File size in megabytes")

    class Config:
        # Pydantic v2 config
        from_attributes = True 
        # Pydantic v1 config
        # orm_mode = True 

class VideoDetailsResponse(VideoMetadata):
    """
    The response for a single video, including a download URL.
    """
    download_url: str = Field(..., description="A 1-hour presigned URL to download the video")

class UploadSuccessResponse(BaseModel):
    """
    The response model for a successful upload.
    """
    status: str = "success"
    video_id: str
    metadata: VideoMetadata