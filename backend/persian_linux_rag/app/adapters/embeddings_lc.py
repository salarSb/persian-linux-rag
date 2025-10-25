from langchain_cohere import CohereEmbeddings
from ..core.config import settings

def get_query_embedder() -> CohereEmbeddings:
    # LangChain will call embed_query() for queries (uses cohere embed under the hood).
    return CohereEmbeddings(model=settings.COHERE_EMBED_MODEL)
