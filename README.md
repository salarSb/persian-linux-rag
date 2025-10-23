# Persian LLM RAG – Linus & Stallman Corpus

A full-power RAG pipeline (LangChain + Cohere + Chroma) over:
- **justforfun_persian.pdf** (Linus Torvalds' book – Persian translation)
- **linuxbook.ir** (Jadi's *Linux & Life* – fetched via WebBaseLoader)
- **Wikipedia** pages (FA/EN)
- **stallman.org** HTML snapshots (downloaded beforehand)

## Quickstart

```bash
# 1) Create venv (Python 3.11) and install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) Set your Cohere API key
export COHERE_API_KEY=YOUR_KEY
# or put it in a .env (this file is gitignored)

# 3) Open the notebook
jupyter notebook librechat.ipynb
```

The notebook builds embeddings and a Chroma vector store, then exposes an `ask(question)`
function that returns a rich answer + top sources.

## Data

Put your data under `data/`. See `data/README.md` for notes and licensing.
**Do NOT commit private API keys or generated vector stores (`collections/`).**

## Git LFS

Large files in `data/` are tracked via **Git LFS**. Before your first commit:

```bash
git lfs install
git add .gitattributes
```

## Legal / Licensing

- Wikipedia content is under **CC BY-SA**; include attribution if you redistribute text.
- `linuxbook.ir` content and `stallman.org` pages: check their site terms before redistribution.
- The `justforfun_persian.pdf` file may be copyrighted; if redistribution is not permitted,
  prefer distributing a small sample and a download script/URL instead of the full file.


## Data Sources (external)

- **PDF:** «فقط برای تفریح - داستان یک انقلاب اتفاقی» (لینوس توروالدز / دیوید دیاموند، ترجمهٔ جادی)  
  لینک: https://jadi.net/

- **وب:** کتاب «لینوکس و زندگی» از جادی  
  لینک: https://linuxbook.ir/all.html

- **ویکی‌پدیا (FA/EN):**  
  ریچارد استالمن · لینوس توروالدز · لینوکس · پروژه گنو · نرم‌افزار آزاد · بنیاد نرم‌افزار آزاد

- **HTML snapshots:** لینک‌های داخلی وب‌سایت https://stallman.org که به‌صورت Web Scraping استخراج می‌شوند (کد نمونه در نوت‌بوک/اسکریپت).

