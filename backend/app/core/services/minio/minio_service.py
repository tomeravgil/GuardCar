from minio import Minio
from minio.error import S3Error
from .config import settings
from .logging_config import log
from app.core.entities.video import VideoMetadata
from datetime import datetime, timedelta
import uuid
import io

# 1. --- MinIO Client Initialization ---
try:
    minio_client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False  # Set to True if using HTTPS
    )
    log.info("MinIO client initialized.")
except Exception as e:
    log.error(f"Failed to initialize MinIO client: {e}")
    minio_client = None

def init_minio_bucket():
    """
    Ensures the target bucket exists on application startup.
    This is called from main.py.
    """
    if not minio_client:
        log.error("MinIO client not available. Cannot initialize bucket.")
        return
        
    try:
        if not minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
            minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
            log.info(f"Successfully created bucket: {settings.MINIO_BUCKET_NAME}")
        else:
            log.info(f"Bucket '{settings.MINIO_BUCKET_NAME}' already exists.")
    except S3Error as e:
        log.error(f"Error checking/creating MinIO bucket: {e}")
        raise

# 2. --- Metadata Helper Functions ---
def _to_user_metadata(data: dict) -> dict:
    """
    Converts a flat dict to MinIO's required 'X-Amz-Meta-' format.
    We also ensure all values are strings, as required by MinIO.
    """
    return {f"X-Amz-Meta-{k.lower()}": str(v) for k, v in data.items() if v is not None}

def _from_stat_object(stat, video_id: str) -> VideoMetadata:
    """
    Converts a MinIO 'stat' object into our Pydantic VideoMetadata model.
    """
    metadata = stat.metadata
    prefix = 'x-amz-meta-'
    
    # Parse user metadata
    user_meta = {k[len(prefix):]: v for k, v in metadata.items() if k.startswith(prefix)}
    
    # Handle potential missing keys gracefully
    capture_ts = user_meta.get('capture_timestamp')

    return VideoMetadata(
        video_id=video_id,
        title=user_meta.get('title', 'Unknown Title'),
        description=user_meta.get('description'),
        location=user_meta.get('location'),
        camera_id=user_meta.get('camera_id', 'Unknown Camera'),
        capture_timestamp=datetime.fromisoformat(capture_ts) if capture_ts else None,
        upload_timestamp=stat.last_modified,
        content_type=stat.content_type,
        size_mb=round(stat.size / (1024 * 1024), 2)
    )

# 3. --- Core Service Functions (Blocking) ---
# These functions are synchronous and will be run in a threadpool by FastAPI
# This prevents them from blocking the main application loop.

def upload_video_to_minio(
    file: io.BytesIO,
    filename: str,
    content_type: str,
    metadata: dict
) -> VideoMetadata:
    """
    Uploads a video file and its metadata to MinIO.
    """
    if not minio_client:
        raise ConnectionError("MinIO client is not initialized.")

    try:
        # Generate a unique ID and filename
        file_extension = filename.split('.')[-1]
        video_id = f"{uuid.uuid4()}.{file_extension}"
        
        # Get file size
        file.seek(0, io.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        # Store metadata to be uploaded
        upload_metadata = {
            "title": metadata.get("title"),
            "camera_id": metadata.get("camera_id"),
            "description": metadata.get("description"),
            "location": metadata.get("location"),
            "capture_timestamp": metadata.get("timestamp"),
        }
        user_metadata = _to_user_metadata(upload_metadata)

        log.info(f"Uploading file '{filename}' as '{video_id}' to MinIO...")
        
        # Upload the object
        minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=video_id,
            data=file,
            length=file_length,
            content_type=content_type,
            metadata=user_metadata
        )
        
        log.info(f"Successfully uploaded {video_id} ({file_length} bytes).")
        
        # After upload, fetch the 'stat' to get the definitive metadata
        return get_video_metadata(video_id)

    except S3Error as e:
        log.error(f"MinIO upload error for {filename}: {e}")
        raise
    except Exception as e:
        log.error(f"An unexpected error occurred during upload: {e}")
        raise

def list_videos_from_minio() -> list[VideoMetadata]:
    """
    Lists all videos in the bucket and retrieves their metadata.
    
    WARNING: This is an N+1 operation (1 list + N stat calls).
    It will be SLOW on buckets with many files.
    This is a trade-off for not having a separate database.
    """
    if not minio_client:
        raise ConnectionError("MinIO client is not initialized.")
    
    videos = []
    try:
        objects = minio_client.list_objects(settings.MINIO_BUCKET_NAME, recursive=True)
        for obj in objects:
            try:
                # This is the N+1 call
                metadata = get_video_metadata(obj.object_name)
                videos.append(metadata)
            except S3Error as e:
                log.warning(f"Could not stat object {obj.object_name}: {e}")
        
        log.info(f"Found {len(videos)} videos in bucket.")
        return videos
        
    except S3Error as e:
        log.error(f"MinIO list_objects error: {e}")
        raise

def get_video_metadata(video_id: str) -> VideoMetadata:
    """
    Retrieves the stat object for a single video and parses it.
    """
    if not minio_client:
        raise ConnectionError("MinIO client is not initialized.")
        
    try:
        stat = minio_client.stat_object(settings.MINIO_BUCKET_NAME, video_id)
        return _from_stat_object(stat, video_id)
    except S3Error as e:
        log.warning(f"MinIO stat_object error for {video_id}: {e}")
        # Re-raise to be handled by the endpoint
        raise

def get_video_download_url(video_id: str) -> str:
    """
    Generates a 1-hour presigned URL for a video.
    """
    if not minio_client:
        raise ConnectionError("MinIO client is not initialized.")
        
    try:
        url = minio_client.get_presigned_url(
            "GET",
            settings.MINIO_BUCKET_NAME,
            video_id,
            expires=timedelta(hours=1) # URL is valid for 1 hour
        )
        return url
    except S3Error as e:
        log.error(f"MinIO get_presigned_url error for {video_id}: {e}")
        raise