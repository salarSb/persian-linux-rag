from fastapi import APIRouter

router = APIRouter()

@router.post("/ingest")
def ingest_stub():
    return {"status": "queued", "note": "Ingestion will arrive in Phase 2."}
