from typing import List
from langchain_core.documents import Document
from ..core.deps import get_chroma_client
from ..core.config import settings

def retrieve_by_embedding(query_embedding: List[float], k: int) -> list[Document]:
    client = get_chroma_client()
    if not client:
        raise RuntimeError(f"Chroma client not available. CHROMA_PATH={settings.CHROMA_PATH!r}")

    # List collections for diagnostics
    try:
        available = [c.name for c in client.list_collections()]
    except Exception as e:
        available = [f"<error listing collections: {e}>"]

    # Strict: do NOT create a new collection by accident
    try:
        collection = client.get_collection(settings.CHROMA_COLLECTION)
    except Exception as e:
        raise RuntimeError(
            f"Collection '{settings.CHROMA_COLLECTION}' not found at CHROMA_PATH={settings.CHROMA_PATH!r}. "
            f"Available: {available}. Original error: {e}"
        )

    # Sanity: count first
    try:
        n = collection.count()
    except Exception as e:
        raise RuntimeError(
            f"Failed counting docs in collection '{settings.CHROMA_COLLECTION}'. "
            f"CHROMA_PATH={settings.CHROMA_PATH!r} available={available} error={e}"
        )
    if n == 0:
        # Graceful: empty index
        return []

    try:
        out = collection.query(query_embeddings=[query_embedding], n_results=k)
    except Exception as e:
        raise RuntimeError(
            f"Chroma query failed for collection '{settings.CHROMA_COLLECTION}' at "
            f"CHROMA_PATH={settings.CHROMA_PATH!r}. Available={available}. Original error: {e}"
        )

    docs = out.get("documents", [[]])[0]
    metadatas = out.get("metadatas", [[]])[0]
    ids = out.get("ids", [[]])[0]
    results: list[Document] = []
    for i, text in enumerate(docs):
        meta = metadatas[i] if i < len(metadatas) else {}
        if not isinstance(meta, dict):
            meta = {}
        meta.setdefault("id", ids[i] if i < len(ids) else None)
        results.append(Document(page_content=text, metadata=meta))
    return results
