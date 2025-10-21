from pydantic import BaseModel

class SuspicionResponse(BaseModel):
    message: str

class VideoResponse(BaseModel):
    message: str
