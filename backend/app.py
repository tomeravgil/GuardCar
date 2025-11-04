# from fastapi import FastAPI, Body
# from datetime import datetime
# from .datatypes import *

# # ------------------------------------------------------------
# # Global config
# # ------------------------------------------------------------
# app = FastAPI()
# ui_thresholds = UIThresholds(suspicion_score_threshold=70)

 
# # ------------------------------------------------------------
# # Routes
# # ------------------------------------------------------------
# @app.get("/")
# def root():
#     return {"API": "UI-first Suspicion Result", "server_time": datetime.now().astimezone().isoformat(sep=" ")}

# @app.get("/api/config/ui-thresholds", response_model=UIThresholds)
# def get_ui_thresholds():
#     return ui_thresholds

# @app.post("/api/config/ui-thresholds", response_model=UIThresholds)
# def set_ui_thresholds(cfg: UIThresholds):
#     # validate ordering via pydantic; assign if good
#     global ui_thresholds
#     ui_thresholds = cfg
#     return ui_thresholds

# # Backwards-compatible path name if your frontend already calls it:
# @app.post("/api/suspicionResult", response_model=SuspicionResponse)
# def suspicion_result(payload: YoloInput = Body(..., embed=False)):
    
#     if payload.suspicion_score >= ui_thresholds.suspicion_score_threshold:
#         # either of these is fine:
#         return SuspicionResponse(message="your car is in danger")
#         # return {"message": "your car is in danger"}
#     else:
#         return SuspicionResponse(message="you're in the clear, buddy")
#         # return {"message": "you're in the clear, buddy"}


# @app.post("/api/videoResult", response_model=VideoResponse)
# def video_result(payload: YoloInput = Body(..., embed=False)):
#     return VideoResponse("This is a Video")
# # Simple health for k8s/compose
# @app.get("/healthz")
# def health():
#     return {"ok": True}
