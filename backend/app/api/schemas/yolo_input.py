from pydantic import BaseModel, Field, field_validator

class YoloInput(BaseModel):
    suspicion_score: int = Field(..., description="0–100")

    @field_validator("suspicion_score", mode="before")
    @classmethod
    def _coerce_int(cls, v):
        return int(v)