from ..core.deps import get_cohere_client
from ..core.config import settings

def rerank_with_cohere(query: str, docs: list[str], top_n: int):
    co = get_cohere_client()
    if not co:
        raise RuntimeError("Cohere client not configured. Set COHERE_API_KEY and MODE=live.")
    resp = co.rerank(
        model=settings.COHERE_RERANK_MODEL,
        query=query,
        documents=docs,
        top_n=min(top_n, len(docs)),
    )
    return resp
