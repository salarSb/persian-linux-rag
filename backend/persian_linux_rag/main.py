from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from .app.core.config import settings
from .app.api.health import router as health_router
from .app.api.ask import router as ask_router
from .app.api.ask_stream import router as ask_stream_router
from .app.api.sources import router as sources_router
from .app.api.ingest import router as ingest_router
from .app.api.feedback import router as feedback_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Persian Linux RAG – Backend (LangChain)",
        default_response_class=ORJSONResponse,
        version="0.1.1",
    )
    app.include_router(health_router, prefix="")
    app.include_router(ask_router, prefix="")
    app.include_router(ask_stream_router, prefix="")
    app.include_router(sources_router, prefix="")
    app.include_router(ingest_router, prefix="")
    app.include_router(feedback_router, prefix="")
    return app


app = create_app()
