"""NU training hub — search indexing and LLM corpus helpers."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.adapters.db.models import TrainingArticle, TrainingCategory


def slugify(text: str) -> str:
    """Convert title to URL-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug[:140].strip("-")


def _parse_json_list(raw: Optional[str]) -> List[Any]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def _split_csv(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def category_path(
    category: Optional[TrainingCategory], by_id: Dict[str, TrainingCategory]
) -> str:
    """Build breadcrumb path for a category."""
    if not category:
        return "Uncategorised"
    parts: List[str] = []
    current: Optional[TrainingCategory] = category
    seen: set[str] = set()
    while current and current.id not in seen:
        seen.add(str(current.id))
        parts.append(current.name)
        parent_id = current.parent_id
        current = by_id.get(str(parent_id)) if parent_id else None
    return " > ".join(reversed(parts))


def _strip_html(html: Optional[str]) -> str:
    if not html:
        return ""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def video_embed_url(url: Optional[str]) -> Optional[str]:
    """Convert share/watch URLs to embeddable iframe src."""
    if not url:
        return None
    u = url.strip()
    loom = re.match(r"https?://(?:www\.)?loom\.com/share/([a-zA-Z0-9]+)", u)
    if loom:
        return f"https://www.loom.com/embed/{loom.group(1)}"
    yt = re.match(
        r"https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{6,})",
        u,
    )
    if yt:
        return f"https://www.youtube.com/embed/{yt.group(1)}"
    vimeo = re.match(r"https?://(?:www\.)?vimeo\.com/(\d+)", u)
    if vimeo:
        return f"https://player.vimeo.com/video/{vimeo.group(1)}"
    if "/embed/" in u:
        return u
    return u


def build_search_blob(article: TrainingArticle, category_name: str = "") -> str:
    """Denormalised text for full-text search."""
    steps = _parse_json_list(article.steps_json)
    risks = _parse_json_list(article.risks_json)
    step_text = " ".join(
        f"{s.get('title', '')} {s.get('body', '')}"
        for s in steps
        if isinstance(s, dict)
    )
    risk_text = " ".join(
        f"{r.get('issue', '')} {r.get('prevention', '')}"
        for r in risks
        if isinstance(r, dict)
    )
    parts = [
        article.title or "",
        article.slug or "",
        article.summary or "",
        article.purpose or "",
        article.prerequisites or "",
        article.safety_notes or "",
        step_text,
        risk_text,
        article.troubleshooting or "",
        article.body_markdown or "",
        _strip_html(getattr(article, "rich_content_html", None)),
        article.tags or "",
        article.systems or "",
        category_name,
        article.content_type or "",
        getattr(article, "video_embed_url", None) or "",
    ]
    return "\n".join(p for p in parts if p).lower()


def build_llm_context(
    article: TrainingArticle,
    category_label: str = "",
    include_metadata: bool = True,
) -> str:
    """Format article as a single text block for RAG / in-house LLM ingestion."""
    lines: List[str] = [f"# ν SOP – {article.title}"]
    if include_metadata:
        lines.extend(
            [
                f"slug: {article.slug}",
                f"category: {category_label or 'Uncategorised'}",
                f"content_type: {article.content_type}",
                f"status: {article.status}",
                f"systems: {article.systems or ''}",
                f"tags: {article.tags or ''}",
            ]
        )
        if article.loom_url:
            lines.append(f"loom: {article.loom_url}")
        if article.sharepoint_url:
            lines.append(f"sharepoint: {article.sharepoint_url}")
        if getattr(article, "video_embed_url", None):
            lines.append(f"video: {article.video_embed_url}")
        lines.append("")

    if article.summary:
        lines.extend(["## Summary", article.summary, ""])
    if article.purpose:
        lines.extend(["## Purpose", article.purpose, ""])
    if article.prerequisites:
        lines.extend(["## Prerequisites", article.prerequisites, ""])
    if article.safety_notes:
        lines.extend(["## Safety Notes", article.safety_notes, ""])

    steps = _parse_json_list(article.steps_json)
    if steps:
        lines.append("## Steps")
        for idx, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                continue
            title = step.get("title") or f"Step {idx}"
            body = step.get("body") or ""
            lines.append(f"{idx}. **{title}**")
            if body:
                lines.append(body)
        lines.append("")

    risks = _parse_json_list(article.risks_json)
    if risks:
        lines.append("## Risks & Common Errors")
        for risk in risks:
            if not isinstance(risk, dict):
                continue
            issue = risk.get("issue") or ""
            prevention = risk.get("prevention") or ""
            if issue:
                lines.append(f"- **Issue:** {issue}")
            if prevention:
                lines.append(f"  **Prevention:** {prevention}")
        lines.append("")

    if article.troubleshooting:
        lines.extend(["## Troubleshooting", article.troubleshooting, ""])

    related = _parse_json_list(article.related_links_json)
    if related:
        lines.append("## Related Content")
        for link in related:
            if not isinstance(link, dict):
                continue
            title = link.get("title") or link.get("url") or "Link"
            url = link.get("url") or ""
            lines.append(f"- [{title}]({url})" if url else f"- {title}")
        lines.append("")

    if article.body_markdown:
        lines.extend(["## Additional Notes", article.body_markdown, ""])

    rich = getattr(article, "rich_content_html", None)
    if rich:
        lines.extend(["## Training Content", _strip_html(rich), ""])

    return "\n".join(lines).strip()


def article_to_dict(
    article: TrainingArticle,
    category_label: str = "",
    include_llm: bool = False,
) -> Dict[str, Any]:
    """Serialise article for API responses."""
    data: Dict[str, Any] = {
        "id": str(article.id),
        "slug": article.slug,
        "title": article.title,
        "category_id": str(article.category_id) if article.category_id else None,
        "category_path": category_label or None,
        "content_type": article.content_type,
        "status": article.status,
        "summary": article.summary,
        "purpose": article.purpose,
        "prerequisites": article.prerequisites,
        "safety_notes": article.safety_notes,
        "steps": _parse_json_list(article.steps_json),
        "risks": _parse_json_list(article.risks_json),
        "troubleshooting": article.troubleshooting,
        "related_links": _parse_json_list(article.related_links_json),
        "body_markdown": article.body_markdown,
        "tags": _split_csv(article.tags),
        "systems": _split_csv(article.systems),
        "loom_url": article.loom_url,
        "sharepoint_url": article.sharepoint_url,
        "video_embed_url": getattr(article, "video_embed_url", None),
        "rich_content_html": getattr(article, "rich_content_html", None),
        "sort_order": article.sort_order,
        "created_at": article.created_at.isoformat() if article.created_at else None,
        "updated_at": article.updated_at.isoformat() if article.updated_at else None,
    }
    if include_llm:
        data["llm_context"] = build_llm_context(article, category_label)
    return data


def build_corpus_export(
    articles: List[TrainingArticle],
    categories_by_id: Dict[str, TrainingCategory],
    fmt: str = "json",
) -> Any:
    """Export published articles for in-house LLM indexing."""
    items = []
    for article in articles:
        cat = (
            categories_by_id.get(str(article.category_id))
            if article.category_id
            else None
        )
        label = category_path(cat, categories_by_id) if cat else ""
        items.append(
            {
                **article_to_dict(article, label, include_llm=True),
                "indexed_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    if fmt == "markdown":
        chunks = [item["llm_context"] for item in items]
        header = (
            "# NU | Nova University — Training Corpus\n\n"
            f"Generated: {datetime.now(timezone.utc).isoformat()}\n"
            f"Articles: {len(items)}\n\n---\n\n"
        )
        return header + "\n\n---\n\n".join(chunks)

    return {
        "corpus_version": "1.0",
        "source": "NU | Nova University",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "article_count": len(items),
        "articles": items,
    }
