from typing import List, Dict
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_cohere import ChatCohere
from ..models.schemas import AskResponse, Citation
from ..core.config import settings
from ..adapters.embeddings_lc import get_query_embedder
from ..adapters.vectordb import retrieve_by_embedding
from ..adapters.cohere_client import rerank_with_cohere

SYSTEM_PROMPT = (
    "تو یک دستیار دانای فارسی‌زبان دربارهٔ لینوکس و نرم‌افزار آزاد هستی. "
    "تا حد امکان کوتاه و دقیق پاسخ بده و اگر مطمئن نیستی، صادقانه بگو. "
    "منابع را در نظر داشته باش و با داده‌های بازیابی‌شده سازگار بمان."
)

def _format_context(docs: List[Document]) -> str:
    parts = []
    for i, d in enumerate(docs, start=1):
        parts.append(f"[{i}] {d.page_content}")
    return "\n\n".join(parts)

def mock_answer(question: str, top_k: int) -> AskResponse:
    demo_citations = [
        Citation(source="mock:justforfun", snippet="نمونه‌ای از متن برای تست ساختار پاسخ.", url=None),
        Citation(source="mock:stallman", snippet="نمونهٔ دیگری برای ارجاع و نمایش.", url=None),
    ]
    return AskResponse(
        answer="(حالت ساختگی) این یک پاسخ نمونه است تا اطمینان بگیریم سرویس فعال است.",
        citations=demo_citations[:top_k],
        used_k=min(top_k, len(demo_citations)),
        mode="mock",
        notes="Set MODE=live + COHERE_API_KEY + Chroma to enable the real pipeline.",
    )

def _retrieve_runner(inputs: Dict):
    question = inputs["question"]
    embedder = get_query_embedder()
    q_emb = embedder.embed_query(question)
    docs = retrieve_by_embedding(q_emb, k=settings.RETRIEVE_K)
    return {"question": question, "retrieved_docs": docs}

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
    return {"question": question, "context": context, "ranked_docs": ranked_docs}

def build_chain():
    retriever = RunnableLambda(_retrieve_runner)
    reranker = RunnableLambda(_rerank_runner)
    prep = RunnableLambda(_prepare_prompt_inputs)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "پرسش:\n{question}\n\nمتون کمکی:\n{context}")
    ])
    llm = ChatCohere(model=settings.COHERE_CHAT_MODEL, temperature=0.2)
    parser = StrOutputParser()

    chain = (
        RunnableParallel(question=RunnablePassthrough())
        | retriever
        | reranker
        | prep
    )

    answer_chain = (lambda x: {"question": x["question"], "context": x["context"]}) | prompt | llm | parser

    final = RunnableParallel(
        answer=answer_chain,
        ranked_docs=RunnableLambda(lambda x: x["ranked_docs"]),
    )
    return final

def answer_question_lc(question: str, top_k: int) -> AskResponse:
    chain = build_chain()
    out = chain.invoke(question)
    docs: List[Document] = out["ranked_docs"][:top_k] if out.get("ranked_docs") else []
    citations = []
    for d in docs:
        meta = d.metadata or {}
        citations.append(Citation(
            source=meta.get("source") or meta.get("doc_id") or meta.get("id") or "unknown",
            snippet=d.page_content[:220],
            url=meta.get("url"),
        ))
    return AskResponse(
        answer=out["answer"],
        citations=citations,
        used_k=len(docs),
        mode="live",
        notes=None,
    )
