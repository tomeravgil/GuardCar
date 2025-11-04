from pydantic import BaseModel

class UIThresholds(BaseModel):
    suspicion_score_threshold: int = 70