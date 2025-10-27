from fastapi import APIRouter, HTTPException
from ..core.deps import get_chroma_client
from ..core.config import settings

router = APIRouter()


@router.get("/sources")
def sources():
    client = get_chroma_client()
    if not client:
        raise HTTPException(
            status_code=500,
            detail=f"Chroma client not available. CHROMA_PATH={settings.CHROMA_PATH!r}",
        )
    try:
        cols = client.list_collections()
        items = []
        for c in cols:
            try:
                col = client.get_collection(c.name)
                cnt = col.count()
            except Exception as e:
                cnt = f"<count error: {e}>"
            items.append({"name": c.name, "count": cnt})
        try:
            focus = client.get_collection(settings.CHROMA_COLLECTION)
            focus_count = focus.count()
        except Exception as e:
            focus_count = f"<count error: {e}>"
        return {
            "path": settings.CHROMA_PATH,
            "collection": settings.CHROMA_COLLECTION,
            "available": items,
            "focus_count": focus_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sources: {e}")
