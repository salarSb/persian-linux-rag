# Persian LLM RAG – Linus & Stallman Corpus

A full-power **RAG** pipeline (**LangChain + Cohere + Chroma**) over:
- **`justforfun_persian.pdf`** (Linus Torvalds’ book — Persian translation)
- **linuxbook.ir** (Jadi’s *Linux & Life* — loaded via `WebBaseLoader`)
- **Wikipedia** pages (FA/EN)
- **stallman.org** internal HTML pages (pre-scraped)

The notebook builds embeddings, persists a Chroma vector store, and exposes an `ask(question)` function that returns a **rich answer** plus **top sources**.

---

## Quickstart

```bash
# 1) Python 3.11 venv and deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) API key
export COHERE_API_KEY=YOUR_KEY
# (or put it in a .env; this file is gitignored)

# 3) Open the notebook
jupyter notebook librechat.ipynb
```

> The index is persisted under `./collections/llm_corpus` (gitignored). Rebuild locally if missing.

---

## Data Sources & Local Layout

This repo **does not** ship data files. Please fetch/place them locally as follows.

**External sources**

- **PDF:** «فقط برای تفریح - داستان یک انقلاب اتفاقی»  
  Author(s): Linus Torvalds, David Diamond — Persian translation by Jadi  
  Link: https://jadi.net/

- **Web (book):** “Linux & Life” by Jadi  
  Link: https://linuxbook.ir/all.html

- **Wikipedia (FA/EN) pages:**  
  ریچارد استالمن · لینوس توروالدز · لینوکس · پروژه گنو · نرم‌افزار آزاد · بنیاد نرم‌افزار آزاد

- **HTML snapshots:** Internal links of https://stallman.org gathered via web scraping.

**Expected local directory layout**

```
data/
├─ justforfun_persian.pdf
└─ html/
   ├─ index.html
   ├─ <other-pages>.html
   └─ ...
```

> `data/` is **gitignored**. Do not commit private data or large binaries.  
> If redistribution is not permitted, keep `data/` empty and point users to the links above.

---

## Fetching Stallman HTML (polite scraper)

A ready-to-use script is provided:

```bash
python scripts/stallman_scrape.py   --base-url https://stallman.org   --out-dir data/html   --max-pages 500
```

Notes:
- Respects `robots.txt`
- Browser-like User-Agent
- Exponential backoff + jitter
- Saves only **internal** `.html` pages

---

## Usage (Notebook)

Inside `librechat.ipynb`, after building the index you get:

```python
res = ask("How did Linux originate and how did it differ from GNU?")
print(res["answer"])
for i, s in enumerate(res["sources"], 1):
    print(f"[{i}] {s['source']}")
```

The `ask()` pipeline uses:
- **Retriever:** Chroma (MMR, `k=6`, `fetch_k=24`)
- **LLM:** Cohere `command-r-08-2024` (temperature ~0.2)
- **Prompting:** Persian system prompt + compact context (chunk trimming)

---

## Repository Structure

```
.
├─ librechat.ipynb            # end-to-end pipeline (ingest → index → RAG ask())
├─ scripts/
│  └─ stallman_scrape.py      # polite scraper for stallman.org → data/html
├─ requirements.txt
├─ .gitignore                 # ignores data/, collections/, envs, etc.
├─ .gitattributes             # (optional) LFS rules if you choose to track large files
├─ README.md                  # this file
└─ data/                      # (local only; not committed)
   ├─ justforfun_persian.pdf
   └─ html/
```

---

## Reproducibility & Ops Tips

- **Vector store:** persisted via `chromadb.PersistentClient` under `./collections/llm_corpus` (gitignored).  
- **Rate limiting:** indexer uses batch + delay + exponential backoff for Cohere embeddings.  
- **Preprocessing:** robust Unicode normalization/cleanup for Persian PDF text (PyPDFium2 extraction quirks).  
- **Extensibility:** swap vector DB (e.g., Pinecone/Qdrant) or embeddings (e.g., multilingual alternatives) with minimal code changes.

---

## Git LFS (optional)

If you decide to track large files (e.g., sample data) with LFS:

```bash
git lfs install
git add .gitattributes
git commit -m "Enable LFS for data/"
```

---

## Legal / Licensing

- **Wikipedia**: CC BY-SA — include attribution if you redistribute text.  
- **linuxbook.ir** and **stallman.org**: check their site terms before redistribution.  
- **`justforfun_persian.pdf`**: may be copyrighted; prefer linking or providing a download script/instructions rather than committing the file.

---

## Env & Security

- Set `COHERE_API_KEY` via environment or `.env` (gitignored).  
- Do **not** commit secrets, API keys, or generated vector stores.

---

## Topics

`langchain` · `rag` · `chromadb` · `cohere` · `nlp` · `persian` · `farsi` · `linux` · `gnu` · `wikipedia` · `information-retrieval` · `vector-search` · `pdf-parsing`
