# Persian Linux RAG — Backend (LangChain)

A FastAPI backend that answers Linux/Free-Software questions using a RAG pipeline built with **LangChain**, **Cohere** (chat, embeddings, rerank), and **Chroma** (persistent vector store).  
It supports **token streaming via SSE**, **language-aware answers** (English/Persian), and **diagnostic endpoints**.

---

## Features

- **LangChain runnables** pipeline: *retrieve → rerank → generate*
- **ChatCohere** for generation, **CohereEmbeddings** for query embeddings
- **Cohere Rerank** to reorder retrieved chunks
- **Chroma** persistent vector store (local on disk)
- **SSE streaming** endpoint (`/ask/stream`)
- **Language auto-detect**: replies in the same language as the question (EN/FA)
- **Diagnostics**: `/sources` shows collections and counts
- **Rich error JSON** with stack traces for debugging (in dev)

---

## Project structure

```
backend/
├─ persian_linux_rag/
│  ├─ main.py
│  └─ app/
│     ├─ api/
│     │  ├─ health.py
│     │  ├─ ask.py
│     │  ├─ ask_stream.py
│     │  ├─ sources.py
│     │  ├─ feedback.py
│     │  └─ ingest.py
│     ├─ core/
│     │  ├─ config.py
│     │  └─ deps.py
│     ├─ adapters/
│     │  ├─ embeddings_lc.py
│     │  ├─ vectordb.py
│     │  └─ cohere_client.py
│     ├─ graphs/
│     │  └─ query_chain.py
│     └─ models/
│        └─ schemas.py
├─ requirements.txt
├─ constraints.txt
└─ .env.example
```

---

## Requirements

- **Python**: 3.11.x recommended
- **Cohere API key**
- **Chroma** persisted vector store

---

## Quickstart

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -c constraints.txt
cp .env.example .env
uvicorn persian_linux_rag.main:app --reload
```

---

## Configuration (`.env`)

```env
MODE=live
COHERE_API_KEY=xxx
COHERE_CHAT_MODEL=command-r-08-2024
COHERE_EMBED_MODEL=embed-multilingual-v3.0
COHERE_RERANK_MODEL=rerank-multilingual-v3.0
CHROMA_PATH=../collections/llm_corpus
CHROMA_COLLECTION=llm_corpus
RETRIEVE_K=12
FETCH_K=60
RERANK_TOP_N=6
RETRIEVER_IMPL=raw
RETRIEVER_SEARCH_TYPE=mmr
ANONYMIZED_TELEMETRY=false
```

---

## Endpoints

### `GET /health`
Check backend status.

### `POST /ask`
Ask question — returns JSON answer with citations.

### `POST /ask/stream`
SSE streaming version (live tokens).

### `GET /sources`
Show Chroma diagnostics.

---

## Troubleshooting

- **Missing key:** ensure `COHERE_API_KEY` is set.
- **max_seq_id error:** version mismatch in `chromadb`.
- **Telemetry errors:** harmless; disable with `ANONYMIZED_TELEMETRY=false`.

---

## Example usage

```bash
curl -X POST http://127.0.0.1:8000/ask   -H 'Content-Type: application/json'   -d '{"question":"What is Linux?","top_k":6}'
```

**Streaming:**

```bash
curl -N -X POST http://127.0.0.1:8000/ask/stream   -H 'Content-Type: application/json'   -d '{"question":"What is Linux?","top_k":6}'
```

---

© 2025 Persian Linux RAG — Backend Phase 1.1
