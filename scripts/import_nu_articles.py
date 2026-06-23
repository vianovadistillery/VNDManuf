#!/usr/bin/env python3
"""Import Nova U training articles from JSON (create or update by slug)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.adapters.db.models import TrainingArticle, TrainingCategory
from app.adapters.db.session import get_session
from app.training.service import build_search_blob, category_path


def _apply_payload(article: TrainingArticle, data: dict, cat_label: str) -> None:
    article.title = data["title"]
    article.content_type = data.get("content_type", "sop")
    article.status = data.get("status", "published")
    article.summary = data.get("summary")
    article.purpose = data.get("purpose")
    article.prerequisites = data.get("prerequisites")
    article.safety_notes = data.get("safety_notes")
    article.troubleshooting = data.get("troubleshooting")
    if data.get("steps") is not None:
        article.steps_json = json.dumps(data["steps"])
    if data.get("risks") is not None:
        article.risks_json = json.dumps(data["risks"])
    systems = data.get("systems")
    article.systems = ",".join(systems) if systems else ""
    tags = data.get("tags")
    article.tags = ",".join(tags) if tags else ""
    article.search_blob = build_search_blob(article, cat_label)


def _load_articles(payload: Any) -> list:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("articles"), list):
        return payload["articles"]
    raise SystemExit("JSON root must be an array of articles or {articles: [...]}")


def import_articles(json_path: Path, dry_run: bool = False) -> None:
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    items = _load_articles(payload)

    session = get_session()
    try:
        cats_by_slug = {
            c.slug: c for c in session.execute(select(TrainingCategory)).scalars().all()
        }
        cats_by_id = {str(c.id): c for c in cats_by_slug.values()}

        created = updated = skipped = 0
        for item in items:
            slug = item.get("slug")
            if not slug:
                print(f"skip (no slug): {item.get('title', '?')}")
                skipped += 1
                continue

            cat_slug = item.get("category_slug")
            cat = cats_by_slug.get(cat_slug) if cat_slug else None
            if cat_slug and not cat:
                print(f"skip (unknown category '{cat_slug}'): {slug}")
                skipped += 1
                continue

            cat_id = str(cat.id) if cat else None
            cat_label = category_path(cat, cats_by_id) if cat else ""

            article = session.execute(
                select(TrainingArticle).where(TrainingArticle.slug == slug)
            ).scalar_one_or_none()

            if article:
                article.category_id = cat_id
                _apply_payload(article, item, cat_label)
                updated += 1
                print(f"~ updated: {item['title']} ({slug})")
            else:
                article = TrainingArticle(
                    slug=slug,
                    title=item["title"],
                    category_id=cat_id,
                )
                _apply_payload(article, item, cat_label)
                session.add(article)
                created += 1
                print(f"+ created: {item['title']} ({slug})")

        if dry_run:
            session.rollback()
            print(
                f"Dry run — {created} would create, {updated} would update, {skipped} skipped."
            )
        else:
            session.commit()
            print(f"Done — {created} created, {updated} updated, {skipped} skipped.")
    finally:
        session.close()


if __name__ == "__main__":
    path = ROOT / "data" / "nu" / "articles_welcome_ops.json"
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        path = Path(sys.argv[1])
    import_articles(path, dry_run="--dry-run" in sys.argv)
