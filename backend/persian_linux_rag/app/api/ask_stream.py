import json
from typing import Iterator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_cohere import ChatCohere
from langchain_core.messages import BaseMessage
from ..core.config import settings
from ..graphs.query_chain import prepare_prompt_bundle

router = APIRouter()


def _sse(data: str, event: str | None = None) -> str:
    if event:
        return f"event: {event}\ndata: {data}\n\n"
    return f"data: {data}\n\n"


@router.post("/ask/stream")
def ask_stream(payload: dict):
    question = payload.get("question")
    top_k = int(payload.get("top_k", 8))
    if not isinstance(question, str) or not question.strip():
        raise HTTPException(
            status_code=400, detail="'question' must be a non-empty string"
        )

    try:
        bundle = prepare_prompt_bundle(question)
        messages: list[BaseMessage] = bundle["messages"]
        citations = bundle["citations"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to prepare context: {e}")

    llm = ChatCohere(
        model=settings.COHERE_CHAT_MODEL,
        temperature=0.2,
        streaming=True,
        cohere_api_key=settings.COHERE_API_KEY,
    )

    def token_stream() -> Iterator[str]:
        try:
            for chunk in llm.stream(messages):
                try:
                    txt = (
                        getattr(chunk, "text", None)
                        or getattr(chunk, "content", None)
                        or str(chunk)
                    )
                except Exception:
                    txt = str(chunk)
                if txt:
                    yield _sse(txt, event="token")
            meta = {
                "citations": [c.model_dump() for c in citations[:top_k]],
                "used_k": min(top_k, len(citations)),
                "mode": "live",
            }
            yield _sse(json.dumps(meta), event="meta")
            yield _sse("done", event="done")
        except Exception as e:
            err = {"error": str(e)}
            yield _sse(json.dumps(err), event="error")

    return StreamingResponse(token_stream(), media_type="text/event-stream")
