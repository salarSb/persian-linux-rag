# Persian Linux RAG – Backend (LangChain Edition, Phase 1)

This backend uses **LangChain** for the query pipeline:
- LC **Runnables** for composition
- **ChatCohere** for generation
- **CohereEmbeddings** for query embeddings
- **ChromaDB** (direct client) for vector search, returned as LangChain `Document`s
- **Cohere Rerank** on retrieved chunks
- **FastAPI** for the HTTP API

> Why direct Chroma client? It avoids package conflicts while still returning LC `Document`s.
> We can swap to `langchain-chroma` in Phase 1.2 if your environment allows a compatible set.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -c constraints.txt

# Optional: set env
cp .env.example .env
# then edit .env

uvicorn persian_linux_rag.main:app --reload
```

Open http://127.0.0.1:8000/docs

### Modes
- **mock** (default): `/ask` returns a shaped test response
- **live**: real pipeline (Cohere + Chroma). Requires `COHERE_API_KEY` and an existing Chroma collection.

## Endpoints
- `GET /health`
- `POST /ask` → `{ answer, citations[], used_k, mode }`
- `POST /feedback` (stub)
- `POST /ingest` (stub)

## How it works (live path)
1) **Retriever**: embed query (LC `CohereEmbeddings.embed_query`) → search Chroma by embedding (direct Chroma client)  
2) **Rerank**: Cohere Rerank over retrieved chunks  
3) **Generate**: `ChatCohere` with a Persian system prompt + compact context  
4) **Return**: answer + citations (top ranked chunks)
