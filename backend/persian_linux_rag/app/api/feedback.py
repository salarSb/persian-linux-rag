from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()

class FeedbackPayload(BaseModel):
    question: str
    answer: str
    rating: int  # -1, 0, +1
    comment: str | None = None

@router.post("/feedback")
def feedback(payload: FeedbackPayload):
    return {"ok": True, "received": payload.model_dump()}
