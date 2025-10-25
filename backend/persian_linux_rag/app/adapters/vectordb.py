from typing import List
from langchain_core.documents import Document
from ..core.deps import get_chroma_client
from ..core.config import settings

def retrieve_by_embedding(query_embedding: List[float], k: int) -> list[Document]:
    client = get_chroma_client()
    if not client:
        raise RuntimeError("Chroma client not available. Check CHROMA_PATH.")
    try:
        collection = client.get_or_create_collection(settings.CHROMA_COLLECTION)
    except Exception as e:
        raise RuntimeError(f"Failed to open Chroma collection '{settings.CHROMA_COLLECTION}': {e}")
    out = collection.query(query_embeddings=[query_embedding], n_results=k)
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
