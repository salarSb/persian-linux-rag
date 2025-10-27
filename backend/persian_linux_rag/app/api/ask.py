from fastapi import APIRouter, HTTPException
from ..models.schemas import AskRequest, AskResponse
from ..core.deps import get_mode
from ..graphs.query_chain import answer_question_lc, mock_answer
import traceback, sys

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    mode = get_mode()
    try:
        if mode == "mock":
            return mock_answer(payload.question, payload.top_k)
        return answer_question_lc(question=payload.question, top_k=payload.top_k)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail={"type": type(e).__name__, "message": str(e), "trace": tb},
        )
