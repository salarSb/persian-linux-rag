from pydantic import BaseModel, Field
from typing import List, Optional

class Citation(BaseModel):
    source: str = Field(..., description="Short source name or id")
    snippet: str = Field(..., description="Short excerpt that supports the answer")
    url: Optional[str] = Field(default=None, description="Optional URL to the source")

class AskRequest(BaseModel):
    question: str
    top_k: int = 8

class AskResponse(BaseModel):
    answer: str
    citations: List[Citation] = []
    used_k: int = 0
    mode: str = "mock"
    notes: Optional[str] = None
