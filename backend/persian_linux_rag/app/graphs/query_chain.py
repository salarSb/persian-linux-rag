import re
from typing import List, Dict
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_cohere import ChatCohere
from langchain_chroma import Chroma as LCChroma
from ..core.deps import get_chroma_client
from ..models.schemas import AskResponse, Citation
from ..core.config import settings
from ..adapters.embeddings_lc import get_query_embedder
from ..adapters.vectordb import retrieve_by_embedding
from ..adapters.cohere_client import rerank_with_cohere

SYSTEM_PROMPT = (
    "You are a concise, accurate assistant focused on GNU/Linux and free software. "
    "Ground answers in the provided context when possible. "
    "If unsure, say you’re unsure. Always keep answers clear and cite the most relevant snippets."
)


def _format_context(docs: List[Document]) -> str:
    parts = []
    for i, d in enumerate(docs, start=1):
        parts.append(f"[{i}] {d.page_content}")
    return "\n\n".join(parts)


def _detect_lang(text: str) -> str:
    """Return 'fa' if Persian/Arabic script is present, else 'en'."""
    return "fa" if re.search(r"[\u0600-\u06FF]", text) else "en"


def mock_answer(question: str, top_k: int) -> AskResponse:
    demo_citations = [
        Citation(
            source="mock:justforfun",
            snippet="نمونه‌ای از متن برای تست ساختار پاسخ.",
            url=None,
        ),
        Citation(
            source="mock:stallman", snippet="نمونهٔ دیگری برای ارجاع و نمایش.", url=None
        ),
    ]
    return AskResponse(
        answer="(حالت ساختگی) این یک پاسخ نمونه است تا اطمینان بگیریم سرویس فعال است.",
        citations=demo_citations[:top_k],
        used_k=min(top_k, len(demo_citations)),
        mode="mock",
        notes="Set MODE=live + COHERE_API_KEY + Chroma to enable the real pipeline.",
    )


def _make_lc_retriever():
    """Return an LC retriever (MMR or similarity) over the existing persisted store."""
    client = get_chroma_client()
    if not client:
        raise RuntimeError(f"Chroma client not available. CHROMA_PATH={settings.CHROMA_PATH!r}")
    embedder = get_query_embedder()
    vectordb = LCChroma(
        client=client,
        collection_name=settings.CHROMA_COLLECTION,
        embedding_function=embedder,
    )
    # MMR params: k=final results, fetch_k=initial pool, lambda_mult: trade-off (0→diversity, 1→relevance)
    search_kwargs = {
        "k": settings.RETRIEVE_K,
        "fetch_k": settings.FETCH_K,
        "lambda_mult": 0.7,  # good starting point; tune 0.5–0.8
    }
    retriever = vectordb.as_retriever(
        search_type=settings.RETRIEVER_SEARCH_TYPE,  # "mmr" or "similarity"
        search_kwargs=search_kwargs,
    )
    return retriever


def _rerank_runner(inputs: Dict):
    question = inputs["question"]
    docs: List[Document] = inputs["retrieved_docs"]
    if not docs:
        return {"question": question, "ranked_docs": []}
    texts = [d.page_content for d in docs]
    resp = rerank_with_cohere(question, texts, settings.RERANK_TOP_N)
    ranked_docs: List[Document] = []
    for item in resp.results:
        idx = item.index
        ranked_docs.append(docs[idx])
    return {"question": question, "ranked_docs": ranked_docs}


def _prepare_prompt_inputs(inputs: Dict):
    question = inputs["question"]
    ranked_docs: List[Document] = inputs["ranked_docs"]
    context = _format_context(ranked_docs)
    lang_directive = "Answer in English." if _detect_lang(question) == "en" else "به فارسی پاسخ بده."
    return {"question": question, "context": context, "ranked_docs": ranked_docs, "lang_directive": lang_directive}


def build_chain():
    lc_retriever = _make_lc_retriever()
    retrieve_stage = RunnableParallel(
        question=RunnablePassthrough(),
        retrieved_docs=lc_retriever,
    )
    reranker = RunnableLambda(_rerank_runner)
    prep = RunnableLambda(_prepare_prompt_inputs)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                "{lang_directive}\n\nQuestion:\n{question}\n\nContext:\n{context}",
            ),
        ]
    )

    llm = ChatCohere(model=settings.COHERE_CHAT_MODEL, temperature=0.2,
                     cohere_api_key=settings.COHERE_API_KEY)
    parser = StrOutputParser()

    pipeline = (
        retrieve_stage
        | reranker
        | prep
    )

    answer_chain = (
        pipeline
        | (lambda x: {"question": x["question"], "context": x["context"], "lang_directive": x["lang_directive"]})
        | prompt
        | llm
        | parser
    )

    final = RunnableParallel(
        answer=answer_chain,
        ranked_docs=pipeline | RunnableLambda(lambda x: x["ranked_docs"]),
    )
    return final


def answer_question_lc(question: str, top_k: int) -> AskResponse:
    chain = build_chain()
    out = chain.invoke(question)
    docs: List[Document] = out["ranked_docs"][:top_k] if out.get("ranked_docs") else []
    citations = []
    for d in docs:
        meta = d.metadata or {}
        citations.append(
            Citation(
                source=meta.get("source")
                or meta.get("doc_id")
                or meta.get("id")
                or "unknown",
                snippet=d.page_content[:220],
                url=meta.get("url"),
            )
        )
    return AskResponse(
        answer=out["answer"],
        citations=citations,
        used_k=len(docs),
        mode="live",
        notes=None,
    )
