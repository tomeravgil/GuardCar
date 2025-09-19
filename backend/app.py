from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, timezone, timedelta
from typing import List
class Failure(BaseModel):
    code: str
    message: str
    detail: Dict[str, str] = {}

class SuspicionSubmit(BaseModel):
    suspicionscore: Optional[float] = None
    from pydantic import Field
    failures: List[Failure] = Field(default_factory=list)
    imagetimestamp: datetime




    

app = FastAPI()

@app.get("/")
def root():
    cur_date = datetime.now().astimezone()
    cur_date.tzinfo = True
    cur_date = cur_date.isoformat(sep=" ")
    return {"API running at": cur_date}

@app.post("/api/suspicionResult")
def suspcicionResult():
    return 
