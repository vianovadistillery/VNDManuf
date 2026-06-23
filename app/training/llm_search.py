"""Nova University — retrieve training articles and answer via OpenAI."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.adapters.db.models import TrainingArticle, TrainingCategory
from app.services.openai_config import get_llm_runtime, public_openai_config
from app.training.service import build_llm_context, category_path

_SYSTEM_PROMPT = """You are the Nova University assistant for Via Nova Distillery.

You answer staff questions using ONLY the training articles provided below.
Be practical, clear, and safety-conscious. When steps exist in the sources, summarise them in order.
Cite article titles inline when referencing specific procedures (e.g. "per **Botanical Handling**").
If the articles do not contain enough information, say what is missing and suggest which manual section to check.
Do not invent procedures, URLs, or system behaviour not supported by the sources.
Keep answers concise but insightful — aim for operators and office staff, not developers."""


def _tokenize(text: str) -> List[str]:
    return [t for t in re.findall(r"[a-z0-9][a-z0-9\-]{2,}", text.lower()) if t]


def _score_article(question_tokens: List[str], article: TrainingArticle) -> int:
    if not question_tokens:
        return 0
    title = (article.title or "").lower()
    summary = (article.summary or "").lower()
    blob = (article.search_blob or "").lower()
    score = 0
    for token in question_tokens:
        if token in title:
            score += 6
        if token in summary:
            score += 3
        if token in blob:
            score += 1
    return score


def retrieve_relevant_articles(
    db: Session,
    question: str,
    *,
    category_id: Optional[str] = None,
    system: Optional[str] = None,
    content_type: Optional[str] = None,
    status_filter: str = "published",
    limit: Optional[int] = None,
) -> List[Tuple[TrainingArticle, str, int]]:
    """Return (article, category_label, relevance_score) sorted by score."""
    max_articles = limit or get_llm_runtime()["max_context_articles"]
    question_tokens = _tokenize(question)

    stmt = select(TrainingArticle).where(TrainingArticle.deleted_at.is_(None))
    if status_filter and status_filter != "all":
        stmt = stmt.where(TrainingArticle.status == status_filter)
    else:
        stmt = stmt.where(TrainingArticle.status != "archived")

    if category_id and category_id != "all":
        stmt = stmt.where(TrainingArticle.category_id == category_id)
    if content_type:
        stmt = stmt.where(TrainingArticle.content_type == content_type)
    if system:
        pattern = f"%{system.lower()}%"
        stmt = stmt.where(
            or_(
                TrainingArticle.systems.ilike(pattern),
                TrainingArticle.search_blob.ilike(pattern),
            )
        )

    # Broad keyword pre-filter when the corpus is large
    if question_tokens:
        clauses = []
        for token in question_tokens[:12]:
            pattern = f"%{token}%"
            clauses.extend(
                [
                    TrainingArticle.search_blob.ilike(pattern),
                    TrainingArticle.title.ilike(pattern),
                    TrainingArticle.summary.ilike(pattern),
                ]
            )
        stmt = stmt.where(or_(*clauses))

    rows = db.execute(stmt).scalars().all()
    if not rows and question_tokens:
        # Fallback: score entire published corpus
        fallback = select(TrainingArticle).where(TrainingArticle.deleted_at.is_(None))
        if status_filter and status_filter != "all":
            fallback = fallback.where(TrainingArticle.status == status_filter)
        else:
            fallback = fallback.where(TrainingArticle.status != "archived")
        if category_id and category_id != "all":
            fallback = fallback.where(TrainingArticle.category_id == category_id)
        rows = db.execute(fallback).scalars().all()

    categories = {
        str(c.id): c for c in db.execute(select(TrainingCategory)).scalars().all()
    }

    scored: List[Tuple[TrainingArticle, str, int]] = []
    for article in rows:
        cat = categories.get(str(article.category_id)) if article.category_id else None
        label = category_path(cat, categories) if cat else ""
        score = _score_article(question_tokens, article)
        if score > 0 or len(rows) <= max_articles:
            scored.append((article, label, score))

    scored.sort(key=lambda item: (-item[2], item[0].sort_order, item[0].title or ""))
    if not scored:
        return []
    return scored[:max_articles]


def _truncate_context(text: str, max_chars: int = 4500) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def build_rag_context(articles: List[Tuple[TrainingArticle, str, int]]) -> str:
    """Concatenate article LLM contexts for the prompt."""
    chunks: List[str] = []
    for idx, (article, label, score) in enumerate(articles, start=1):
        body = build_llm_context(article, label, include_metadata=True)
        chunks.append(
            f"### Source {idx}: {article.title} (relevance {score})\n"
            + _truncate_context(body)
        )
    return "\n\n---\n\n".join(chunks)


def _call_openai(question: str, context: str) -> str:
    cfg = get_llm_runtime()
    if not cfg["api_key"]:
        raise ValueError(
            "OpenAI API key is not configured. "
            "Add your key in Nova University → AI Settings (saved to config/openai.json)."
        )

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Question:\n{question.strip()}\n\nTraining articles:\n\n{context}"
            ),
        },
    ]

    with httpx.Client(timeout=cfg["request_timeout_seconds"]) as client:
        resp = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": cfg["model"],
                "messages": messages,
                "temperature": cfg["temperature"],
                "max_tokens": cfg["max_tokens"],
            },
        )

    if resp.status_code != 200:
        detail = resp.text
        try:
            detail = resp.json().get("error", {}).get("message", detail)
        except Exception:
            pass
        raise RuntimeError(f"OpenAI API error ({resp.status_code}): {detail}")

    data = resp.json()
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("OpenAI returned no choices")
    return (choices[0].get("message") or {}).get("content") or ""


def ask_training_question(
    db: Session,
    question: str,
    *,
    category_id: Optional[str] = None,
    system: Optional[str] = None,
    content_type: Optional[str] = None,
    status_filter: str = "published",
) -> Dict[str, Any]:
    """Retrieve relevant articles and produce a natural-language answer."""
    question = (question or "").strip()
    if not question:
        raise ValueError("Question is required")
    if len(question) > 2000:
        raise ValueError("Question is too long (max 2000 characters)")

    cfg = get_llm_runtime()
    if not cfg["enabled"]:
        raise ValueError("LLM search is disabled in config/openai.json")
    if not cfg["api_key"]:
        raise ValueError(
            "OpenAI API key is not configured. "
            "Use Nova University → AI Settings or copy config/openai.json.example "
            "to config/openai.json."
        )

    ranked = retrieve_relevant_articles(
        db,
        question,
        category_id=category_id,
        system=system,
        content_type=content_type,
        status_filter=status_filter,
    )

    if not ranked:
        return {
            "question": question,
            "answer": (
                "I could not find any published training articles matching that question. "
                "Try browsing manual sections or rephrase your question."
            ),
            "sources": [],
            "articles_used": 0,
            "model": cfg["model"],
        }

    context = build_rag_context(ranked)
    answer = _call_openai(question, context)

    sources = [
        {
            "id": str(article.id),
            "slug": article.slug,
            "title": article.title,
            "category_path": label,
            "content_type": article.content_type,
            "summary": article.summary,
            "relevance_score": score,
        }
        for article, label, score in ranked
    ]

    return {
        "question": question,
        "answer": answer.strip(),
        "sources": sources,
        "articles_used": len(sources),
        "model": cfg["model"],
    }


def llm_status() -> Dict[str, Any]:
    """Non-secret status for UI."""
    return public_openai_config()
