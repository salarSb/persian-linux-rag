from .config import settings

_cohere_client = None
_chroma_client = None

def get_mode() -> str:
    return (settings.MODE or "mock").lower()

def get_cohere_client():
    global _cohere_client
    if _cohere_client is not None:
        return _cohere_client
    if not settings.COHERE_API_KEY:
        return None
    try:
        import cohere
        _cohere_client = cohere.ClientV2(api_key=settings.COHERE_API_KEY)
        return _cohere_client
    except Exception:
        return None

def get_chroma_client():
    global _chroma_client
    if _chroma_client is not None:
        return _chroma_client
    try:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        return _chroma_client
    except Exception:
        return None
