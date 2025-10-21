from pydantic import BaseModel, Field, field_validator

class UIThresholds(BaseModel):
    suspicion_score_threshold: int = 70

class YoloInput(BaseModel):
    # Accepts either an int or a string "78" and coerces to int
    suspicion_score: int = Field(..., description="0-100")

    @field_validator("suspicion_score", mode="before")
    @classmethod
    def _coerce_int(cls, v):
        return int(v)

class SuspicionResponse(BaseModel):
    message: str
class VideoResponse(BaseModel):
    message: str