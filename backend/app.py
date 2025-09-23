from fastapi import FastAPI
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Literal
from datetime import datetime, timezone

# ------------------------------------------------------------
# Shared small types
# ------------------------------------------------------------
class Failure(BaseModel):
    code: str
    message: str
    detail: Dict[str, str] = {}

class WindowMeta(BaseModel):
    window_start: datetime
    window_end: datetime
    source: Optional[str] = None     # camera/stream id
    fps: Optional[float] = None
    frame_count: Optional[int] = None

    @validator("window_end")
    def _end_after_start(cls, v, values):
        if "window_start" in values and v <= values["window_start"]:
            raise ValueError("window_end must be after window_start")
        return v

# ------------------------------------------------------------
# INPUT: interpreted (post-analytics) payload
#  - Keep this minimal and flexible so upstream can evolve.
# ------------------------------------------------------------
class Reason(BaseModel):
    # Structured reasons the UI can render nicely
    # (frontend can show message; optional code/meta for tooltips)
    message: str
    code: Optional[str] = None
    meta: Dict[str, str] = Field(default_factory=dict)

class EvidenceItem(BaseModel):
    # Optional evidence the UI may show (e.g., thumbnails, heatmaps)
    # Not required—safe to ignore on the frontend if not used.
    kind: Literal["thumbnail", "crop", "heatmap", "link", "text"] = "text"
    title: Optional[str] = None
    url: Optional[str] = None        # image/link
    text: Optional[str] = None       # for "text" kind
    meta: Dict[str, str] = Field(default_factory=dict)

class InterpretedInput(BaseModel):
    """
    Upstream sends a single, already-interpreted snapshot/result for a window.
    """
    # Required
    score: float                      # normalized 0..1 from upstream
    reasons: List[Reason] = Field(default_factory=list)

    # Optional UI helpers
    tags: List[str] = Field(default_factory=list)   # quick badges for the UI ("knife", "crowd", etc.)
    evidence: List[EvidenceItem] = Field(default_factory=list)

    # Optional time/context
    imagetimestamp: Optional[datetime] = None       # last frame ts (if useful to show)
    meta: Optional[WindowMeta] = None

    failures: List[Failure] = Field(default_factory=list)

    @validator("score")
    def _clamp_score(cls, v):
        if v is None:
            return 0.0
        return max(0.0, min(1.0, v))

# ------------------------------------------------------------
# OUTPUT: UI-first SuspicionResponse
#  - Adds level & acceptance decision; echoes context for the UI.
# ------------------------------------------------------------
class SuspicionResponse(BaseModel):
    accepted: bool                          # pass/fail for downstream actions
    score: float                             # 0..1 (clamped)
    level: Literal["low", "medium", "high"]  # for color/badge mapping in UI
    reasons: List[Reason] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    # Echo useful context for the UI
    imagetimestamp: Optional[datetime] = None
    meta: Optional[WindowMeta] = None
    evidence: List[EvidenceItem] = Field(default_factory=list)

    # Diagnostics
    failures: List[Failure] = Field(default_factory=list)
    received_at: datetime

# ------------------------------------------------------------
# Runtime config (simple + transparent)
# ------------------------------------------------------------
class UIThresholds(BaseModel):
    # One number decides "accepted" (e.g., trigger banner/alert).
    accept_threshold: float = Field(0.6, ge=0.0, le=1.0)

    # Buckets to decorate the score with a UI level.
    # low:   [0, medium_min)
    # med:   [medium_min, high_min)
    # high:  [high_min, 1]
    medium_min: float = Field(0.33, ge=0.0, le=1.0)
    high_min: float = Field(0.67, ge=0.0, le=1.0)

    @validator("high_min")
    def _ordered_thresholds(cls, v, values):
        mm = values.get("medium_min", 0.33)
        if v <= mm:
            raise ValueError("high_min must be greater than medium_min")
        return v

app = FastAPI(title="Suspicion Result API (UI-first)")

ui_thresholds = UIThresholds()

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def level_from_score(score: float, cfg: UIThresholds) -> str:
    if score >= cfg.high_min:
        return "high"
    if score >= cfg.medium_min:
        return "medium"
    return "low"

def decide_accept(score: float, cfg: UIThresholds) -> bool:
    return score >= cfg.accept_threshold

# ------------------------------------------------------------
# Routes
# ------------------------------------------------------------
@app.get("/")
def root():
    return {"API": "UI-first Suspicion Result", "server_time": datetime.now().astimezone().isoformat(sep=" ")}

@app.get("/api/config/ui-thresholds", response_model=UIThresholds)
def get_ui_thresholds():
    return ui_thresholds

@app.post("/api/config/ui-thresholds", response_model=UIThresholds)
def set_ui_thresholds(cfg: UIThresholds):
    # validate ordering via pydantic; assign if good
    global ui_thresholds
    ui_thresholds = cfg
    return ui_thresholds

# Backwards-compatible path name if your frontend already calls it:
@app.post("/api/suspicionResult", response_model=SuspicionResponse)
def suspicion_result(payload: InterpretedInput):
    s = max(0.0, min(1.0, payload.score))
    level = level_from_score(s, ui_thresholds)
    accepted = decide_accept(s, ui_thresholds)

    # De-duplicate tags (preserve order)
    seen = set()
    tags = []
    for t in payload.tags:
        if t not in seen:
            seen.add(t)
            tags.append(t)

    return SuspicionResponse(
        accepted=accepted,
        score=s,
        level=level,
        reasons=payload.reasons,
        tags=tags,
        imagetimestamp=payload.imagetimestamp,
        meta=payload.meta,
        evidence=payload.evidence,
        failures=payload.failures,
        received_at=datetime.now(timezone.utc),
    )

# Simple health for k8s/compose
@app.get("/healthz")
def health():
    return {"ok": True}
