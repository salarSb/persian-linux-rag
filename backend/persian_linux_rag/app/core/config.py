from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    APP_NAME: str = "persian-linux-rag-lc"
    MODE: str = Field(default="mock", description="mock or live")

    # Cohere
    COHERE_API_KEY: str | None = None
    COHERE_CHAT_MODEL: str = "command-r-08-2024"
    COHERE_EMBED_MODEL: str = "embed-multilingual-v3.0"
    COHERE_RERANK_MODEL: str = "rerank-multilingual-v3.0"

    # Chroma
    CHROMA_PATH: str = "./collections/llm_corpus"
    CHROMA_COLLECTION: str = "llm_corpus"

    # RAG knobs
    RETRIEVE_K: int = 12
    FETCH_K: int = 30
    RERANK_TOP_N: int = 6

settings = Settings()
