from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi import Form
from typing import List
import io
from core.entities.video import VideoMetadata, VideoDetailsResponse, UploadSuccessResponse
from core.services.minio.minio_service import (
    upload_video_to_minio,
    list_videos_from_minio,
    get_video_metadata,
    get_video_download_url
)
from minio.error import S3Error

router = APIRouter(prefix="/api/videos", tags=["videos"])

@router.get("", response_model=List[VideoMetadata])
async def list_videos():
    """
    GET /api/videos
    Returns a list of all videos with their metadata.
    """
    try:
        videos = list_videos_from_minio()
        return videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list videos: {str(e)}")

@router.post("/upload", response_model=UploadSuccessResponse, status_code=201)
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    camera_id: str = Form(...),
    description: str = Form(None),
    location: str = Form(None),
    timestamp: str = Form(None)
):
    """
    POST /api/videos/upload
    Uploads a video file with metadata.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Expected video/*, got {file.content_type}"
        )
    
    try:
        # Read file into memory
        contents = await file.read()
        file_io = io.BytesIO(contents)
        
        # Prepare metadata
        metadata = {
            "title": title,
            "camera_id": camera_id,
            "description": description,
            "location": location,
            "timestamp": timestamp
        }
        
        # Upload to MinIO (blocking operation - FastAPI will run in threadpool)
        video_metadata = upload_video_to_minio(
            file=file_io,
            filename=file.filename,
            content_type=file.content_type,
            metadata=metadata
        )
        
        return UploadSuccessResponse(
            status="success",
            video_id=video_metadata.video_id,
            metadata=video_metadata
        )
        
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/{video_id}", response_model=VideoDetailsResponse)
async def get_video(video_id: str):
    """
    GET /api/videos/{video_id}
    Returns metadata and a presigned download URL for a specific video.
    """
    try:
        # Get metadata
        metadata = get_video_metadata(video_id)
        
        # Generate download URL
        download_url = get_video_download_url(video_id)
        
        return VideoDetailsResponse(
            **metadata.model_dump(),
            download_url=download_url
        )
        
    except S3Error as e:
        if e.code == "NoSuchKey":
            raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found")
        raise HTTPException(status_code=500, detail=f"MinIO error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get video: {str(e)}")