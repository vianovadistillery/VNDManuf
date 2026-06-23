"""NU Training Hub API — searchable articles and LLM corpus export."""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import TrainingArticle, TrainingCategory
from app.services.openai_config import public_openai_config, save_openai_config
from app.training.llm_search import ask_training_question, llm_status
from app.training.service import (
    article_to_dict,
    build_corpus_export,
    build_llm_context,
    build_search_blob,
    category_path,
    slugify,
)

router = APIRouter(prefix="/training", tags=["training"])

MEDIA_ROOT = Path(__file__).resolve().parents[2] / "generated" / "training_media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

_ALLOWED_MEDIA = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "video/mp4",
    "video/webm",
    "video/quicktime",
}
_MAX_MEDIA_BYTES = 80 * 1024 * 1024


class StepItem(BaseModel):
    title: str = ""
    body: str = ""


class RiskItem(BaseModel):
    issue: str = ""
    prevention: str = ""


class RelatedLink(BaseModel):
    title: str = ""
    url: str = ""
    link_type: str = "reference"


class CategoryCreate(BaseModel):
    slug: Optional[str] = None
    code: Optional[str] = None
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class CategoryUpdate(BaseModel):
    slug: Optional[str] = None
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ArticleCreate(BaseModel):
    slug: Optional[str] = None
    title: str
    category_id: Optional[str] = None
    content_type: str = "sop"
    status: str = "draft"
    summary: Optional[str] = None
    purpose: Optional[str] = None
    prerequisites: Optional[str] = None
    safety_notes: Optional[str] = None
    steps: List[StepItem] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    troubleshooting: Optional[str] = None
    related_links: List[RelatedLink] = Field(default_factory=list)
    body_markdown: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    systems: List[str] = Field(default_factory=list)
    loom_url: Optional[str] = None
    sharepoint_url: Optional[str] = None
    video_embed_url: Optional[str] = None
    rich_content_html: Optional[str] = None
    sort_order: int = 0


class ArticleUpdate(BaseModel):
    slug: Optional[str] = None
    title: Optional[str] = None
    category_id: Optional[str] = None
    content_type: Optional[str] = None
    status: Optional[str] = None
    summary: Optional[str] = None
    purpose: Optional[str] = None
    prerequisites: Optional[str] = None
    safety_notes: Optional[str] = None
    steps: Optional[List[StepItem]] = None
    risks: Optional[List[RiskItem]] = None
    troubleshooting: Optional[str] = None
    related_links: Optional[List[RelatedLink]] = None
    body_markdown: Optional[str] = None
    tags: Optional[List[str]] = None
    systems: Optional[List[str]] = None
    loom_url: Optional[str] = None
    sharepoint_url: Optional[str] = None
    video_embed_url: Optional[str] = None
    rich_content_html: Optional[str] = None
    sort_order: Optional[int] = None


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    category_id: Optional[str] = None
    system: Optional[str] = None
    content_type: Optional[str] = None
    status: str = "published"


class LlmConfigUpdate(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None
    enabled: Optional[bool] = None
    max_context_articles: Optional[int] = Field(None, ge=1, le=20)
    max_tokens: Optional[int] = Field(None, ge=256, le=4096)
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    request_timeout_seconds: Optional[int] = Field(None, ge=10, le=180)


def _categories_map(db: Session) -> Dict[str, TrainingCategory]:
    rows = db.execute(select(TrainingCategory)).scalars().all()
    return {str(c.id): c for c in rows}


def _category_label(db: Session, category_id: Optional[str]) -> str:
    if not category_id:
        return ""
    by_id = _categories_map(db)
    cat = by_id.get(str(category_id))
    return category_path(cat, by_id) if cat else ""


def _unique_slug(db: Session, base_slug: str, exclude_id: Optional[str] = None) -> str:
    slug = base_slug or "article"
    candidate = slug
    n = 2
    while True:
        existing = db.execute(
            select(TrainingArticle).where(TrainingArticle.slug == candidate)
        ).scalar_one_or_none()
        if not existing or (exclude_id and str(existing.id) == exclude_id):
            return candidate
        candidate = f"{slug}-{n}"
        n += 1


def _dump_items(items: List[Any]) -> List[Dict[str, Any]]:
    """Normalize Pydantic models or plain dicts for JSON column storage."""
    out: List[Dict[str, Any]] = []
    for item in items:
        if hasattr(item, "model_dump"):
            out.append(item.model_dump())
        elif isinstance(item, dict):
            out.append(item)
        else:
            out.append(dict(item))
    return out


def _apply_article_fields(
    article: TrainingArticle, data: Dict[str, Any], db: Session
) -> None:
    if "title" in data and data["title"] is not None:
        article.title = data["title"]
    if "slug" in data and data["slug"] is not None:
        article.slug = _unique_slug(db, data["slug"], str(article.id))
    if "category_id" in data:
        article.category_id = data["category_id"]
    if "content_type" in data and data["content_type"] is not None:
        article.content_type = data["content_type"]
    if "status" in data and data["status"] is not None:
        article.status = data["status"]
    for field in (
        "summary",
        "purpose",
        "prerequisites",
        "safety_notes",
        "troubleshooting",
        "body_markdown",
        "loom_url",
        "sharepoint_url",
        "video_embed_url",
        "rich_content_html",
    ):
        if field in data:
            setattr(article, field, data[field])
    if "steps" in data and data["steps"] is not None:
        article.steps_json = json.dumps(_dump_items(data["steps"]))
    if "risks" in data and data["risks"] is not None:
        article.risks_json = json.dumps(_dump_items(data["risks"]))
    if "related_links" in data and data["related_links"] is not None:
        article.related_links_json = json.dumps(_dump_items(data["related_links"]))
    if "tags" in data and data["tags"] is not None:
        article.tags = ",".join(data["tags"])
    if "systems" in data and data["systems"] is not None:
        article.systems = ",".join(data["systems"])
    if "sort_order" in data and data["sort_order"] is not None:
        article.sort_order = data["sort_order"]

    label = _category_label(
        db, str(article.category_id) if article.category_id else None
    )
    article.search_blob = build_search_blob(article, label)


@router.get("/categories")
def list_categories(
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
):
    """List all training categories."""
    stmt = select(TrainingCategory).order_by(
        TrainingCategory.sort_order, TrainingCategory.name
    )
    if not include_inactive:
        stmt = stmt.where(TrainingCategory.is_active.is_(True))
    rows = db.execute(stmt).scalars().all()
    return [
        {
            "id": str(c.id),
            "slug": c.slug,
            "code": c.code,
            "name": c.name,
            "description": c.description,
            "parent_id": str(c.parent_id) if c.parent_id else None,
            "sort_order": c.sort_order,
            "is_active": c.is_active,
        }
        for c in rows
    ]


@router.post("/categories", status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    slug = payload.slug or slugify(payload.name)
    existing = db.execute(
        select(TrainingCategory).where(TrainingCategory.slug == slug)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=409, detail=f"Category slug '{slug}' already exists"
        )

    cat = TrainingCategory(
        slug=slug,
        code=payload.code,
        name=payload.name,
        description=payload.description,
        parent_id=payload.parent_id,
        sort_order=payload.sort_order,
        is_active=payload.is_active,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return {"id": str(cat.id), "slug": cat.slug, "name": cat.name}


def _query_articles(
    db: Session,
    *,
    q: Optional[str] = None,
    category_id: Optional[str] = None,
    system: Optional[str] = None,
    tag: Optional[str] = None,
    content_type: Optional[str] = None,
    status_filter: Optional[str] = "published",
    include_archived: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> List[dict]:
    """Core article query used by list and search endpoints."""
    stmt = select(TrainingArticle).where(TrainingArticle.deleted_at.is_(None))

    if status_filter and status_filter != "all":
        stmt = stmt.where(TrainingArticle.status == status_filter)
    elif not include_archived:
        stmt = stmt.where(TrainingArticle.status != "archived")

    if category_id:
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
    if tag:
        pattern = f"%{tag.lower()}%"
        stmt = stmt.where(
            or_(
                TrainingArticle.tags.ilike(pattern),
                TrainingArticle.search_blob.ilike(pattern),
            )
        )
    if q:
        pattern = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                TrainingArticle.search_blob.ilike(pattern),
                TrainingArticle.title.ilike(pattern),
                TrainingArticle.summary.ilike(pattern),
            )
        )

    stmt = (
        stmt.order_by(TrainingArticle.sort_order, TrainingArticle.title)
        .offset(offset)
        .limit(limit)
    )
    rows = db.execute(stmt).scalars().all()
    by_id = _categories_map(db)

    return [
        article_to_dict(
            a,
            category_path(by_id.get(str(a.category_id)), by_id)
            if a.category_id and by_id.get(str(a.category_id))
            else "",
        )
        for a in rows
    ]


@router.get("/articles")
def list_articles(
    q: Optional[str] = Query(None, description="Full-text search query"),
    category_id: Optional[str] = Query(None),
    system: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query("published", alias="status"),
    include_archived: bool = Query(False),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Search and list training articles."""
    return _query_articles(
        db,
        q=q,
        category_id=category_id,
        system=system,
        tag=tag,
        content_type=content_type,
        status_filter=status_filter,
        include_archived=include_archived,
        limit=limit,
        offset=offset,
    )


@router.get("/articles/{article_ref}")
def get_article(
    article_ref: str,
    include_llm: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Get article by ID or slug."""
    article = _get_article_or_404(db, article_ref)
    label = _category_label(
        db, str(article.category_id) if article.category_id else None
    )
    return article_to_dict(article, label, include_llm=include_llm)


@router.post("/articles", status_code=status.HTTP_201_CREATED)
def create_article(payload: ArticleCreate, db: Session = Depends(get_db)):
    base_slug = payload.slug or slugify(payload.title)
    slug = _unique_slug(db, base_slug)
    article = TrainingArticle(slug=slug, title=payload.title)
    _apply_article_fields(article, payload.model_dump(), db)
    db.add(article)
    db.commit()
    db.refresh(article)
    label = _category_label(
        db, str(article.category_id) if article.category_id else None
    )
    return article_to_dict(article, label, include_llm=True)


@router.put("/articles/{article_ref}")
def update_article(
    article_ref: str, payload: ArticleUpdate, db: Session = Depends(get_db)
):
    article = _get_article_or_404(db, article_ref)
    data = payload.model_dump(exclude_unset=True)
    if "title" in data and data["title"] and not data.get("slug"):
        data["slug"] = slugify(data["title"])
    _apply_article_fields(article, data, db)
    db.commit()
    db.refresh(article)
    label = _category_label(
        db, str(article.category_id) if article.category_id else None
    )
    return article_to_dict(article, label, include_llm=True)


@router.delete("/articles/{article_ref}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_ref: str, db: Session = Depends(get_db)):
    article = _get_article_or_404(db, article_ref)
    article.status = "archived"
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/search")
def search_training(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query("published", alias="status"),
    db: Session = Depends(get_db),
):
    """Dedicated search endpoint optimised for UI and LLM tool calls."""
    return _query_articles(
        db,
        q=q,
        status_filter=status_filter,
        limit=limit,
        offset=0,
    )


@router.get("/corpus")
def export_corpus(
    status_filter: str = Query("published", alias="status"),
    format: str = Query("json", pattern="^(json|markdown)$"),
    db: Session = Depends(get_db),
):
    """
    Export full training corpus for in-house LLM indexing / RAG pipelines.

    Use ?format=markdown for a single concatenated document.
    """
    stmt = select(TrainingArticle).where(TrainingArticle.deleted_at.is_(None))
    if status_filter != "all":
        stmt = stmt.where(TrainingArticle.status == status_filter)
    stmt = stmt.order_by(TrainingArticle.sort_order, TrainingArticle.title)
    articles = db.execute(stmt).scalars().all()
    by_id = _categories_map(db)
    result = build_corpus_export(articles, by_id, fmt=format)

    if format == "markdown":
        return Response(content=result, media_type="text/markdown; charset=utf-8")
    return result


@router.get("/corpus/{article_ref}")
def export_single_corpus_chunk(article_ref: str, db: Session = Depends(get_db)):
    """Export a single article as an LLM-ready text chunk."""
    article = _get_article_or_404(db, article_ref)
    label = _category_label(
        db, str(article.category_id) if article.category_id else None
    )
    return {
        "slug": article.slug,
        "title": article.title,
        "category_path": label,
        "llm_context": build_llm_context(article, label),
        "structured": article_to_dict(article, label, include_llm=False),
    }


def _get_article_or_404(db: Session, ref: str) -> TrainingArticle:
    stmt = select(TrainingArticle).where(
        TrainingArticle.deleted_at.is_(None),
        or_(TrainingArticle.id == ref, TrainingArticle.slug == ref),
    )
    article = db.execute(stmt).scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Training article not found")
    return article


@router.get("/ask/status")
def training_ask_status():
    """Report whether LLM ask is configured (no secrets)."""
    return llm_status()


@router.get("/llm-config")
def get_llm_config():
    """Return masked Nova University LLM settings (config/openai.json)."""
    return public_openai_config()


@router.put("/llm-config")
def update_llm_config(payload: LlmConfigUpdate):
    """Save Nova University LLM settings to config/openai.json."""
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No settings provided")
    return save_openai_config(data)


@router.post("/ask")
def training_ask(payload: AskRequest, db: Session = Depends(get_db)):
    """
    Natural-language Q&A over published training articles (RAG + OpenAI).

    Requires OPENAI_API_KEY in environment / .env.
    """
    try:
        return ask_training_question(
            db,
            payload.question,
            category_id=payload.category_id,
            system=payload.system,
            content_type=payload.content_type,
            status_filter=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/media/upload", status_code=status.HTTP_201_CREATED)
async def upload_training_media(file: UploadFile = File(...)):
    """Upload image or video for embedding in rich training content."""
    content_type = (file.content_type or "").lower()
    if content_type not in _ALLOWED_MEDIA:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type or 'unknown'}",
        )
    raw = await file.read()
    if len(raw) > _MAX_MEDIA_BYTES:
        raise HTTPException(status_code=400, detail="File exceeds 80 MB limit")

    ext = Path(file.filename or "file").suffix.lower()
    if not ext:
        ext_map = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "video/mp4": ".mp4",
            "video/webm": ".webm",
            "video/quicktime": ".mov",
        }
        ext = ext_map.get(content_type, "")
    safe_name = re.sub(r"[^\w.\-]", "_", Path(file.filename or "upload").stem)[:80]
    filename = f"{uuid.uuid4().hex}_{safe_name}{ext}"
    dest = MEDIA_ROOT / filename
    dest.write_bytes(raw)

    url = f"/api/v1/training/media/{filename}"
    return {
        "url": url,
        "filename": filename,
        "content_type": content_type,
        "kind": "video" if content_type.startswith("video/") else "image",
    }


@router.get("/media/{filename}")
def serve_training_media(filename: str):
    """Serve uploaded training media."""
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    path = MEDIA_ROOT / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Media not found")
    return FileResponse(path)
