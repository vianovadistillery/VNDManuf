#!/usr/bin/env python3
"""Seed NU training categories and checklist articles."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.adapters.db.models import TrainingArticle, TrainingCategory
from app.adapters.db.session import get_session
from app.training.service import build_search_blob, slugify

# NU SharePoint taxonomy + checklist topics
CATEGORIES = [
    {
        "code": "01",
        "slug": "company-induction",
        "name": "Company Induction",
        "sort": 10,
    },
    {
        "code": "01.01",
        "slug": "welcome",
        "name": "Welcome",
        "parent": "company-induction",
        "sort": 11,
    },
    {
        "code": "01.02",
        "slug": "safety-hr",
        "name": "Safety & HR",
        "parent": "company-induction",
        "sort": 12,
    },
    {
        "code": "01.03",
        "slug": "code-of-conduct",
        "name": "Code of Conduct",
        "parent": "company-induction",
        "sort": 13,
    },
    {
        "code": "02",
        "slug": "distillery-operations",
        "name": "Distillery Operations",
        "sort": 20,
    },
    {
        "code": "02.01",
        "slug": "distillation",
        "name": "Distillation",
        "parent": "distillery-operations",
        "sort": 21,
    },
    {
        "code": "02.02",
        "slug": "vndaq-training",
        "name": "VND-DAQ System Training",
        "parent": "distillery-operations",
        "sort": 22,
    },
    {
        "code": "02.03",
        "slug": "trip-logic-safety",
        "name": "Trip Logic & Safety",
        "parent": "distillery-operations",
        "sort": 23,
    },
    {
        "code": "02.04",
        "slug": "cleaning-sanitising",
        "name": "Cleaning & Sanitising",
        "parent": "distillery-operations",
        "sort": 24,
    },
    {
        "code": "02.05",
        "slug": "packaging-bottling",
        "name": "Packaging & Bottling",
        "parent": "distillery-operations",
        "sort": 25,
    },
    {"code": "03", "slug": "finance-xero", "name": "Finance & Xero", "sort": 30},
    {
        "code": "03.01",
        "slug": "daily-tasks",
        "name": "Daily Tasks",
        "parent": "finance-xero",
        "sort": 31,
    },
    {
        "code": "03.02",
        "slug": "bank-reconciliation",
        "name": "Bank Reconciliation",
        "parent": "finance-xero",
        "sort": 32,
    },
    {
        "code": "03.03",
        "slug": "inventory-excise",
        "name": "Inventory & Excise",
        "parent": "finance-xero",
        "sort": 33,
    },
    {
        "code": "03.04",
        "slug": "reporting",
        "name": "Reporting",
        "parent": "finance-xero",
        "sort": 34,
    },
    {
        "code": "04",
        "slug": "sales-distribution",
        "name": "Sales & Distribution",
        "sort": 40,
    },
    {
        "code": "04.01",
        "slug": "price-lists-policies",
        "name": "Price Lists & Policies",
        "parent": "sales-distribution",
        "sort": 41,
    },
    {
        "code": "04.02",
        "slug": "retailer-setup",
        "name": "Retailer Setup",
        "parent": "sales-distribution",
        "sort": 42,
    },
    {
        "code": "04.03",
        "slug": "shopify-local-delivery",
        "name": "Shopify & Local Delivery",
        "parent": "sales-distribution",
        "sort": 43,
    },
    {
        "code": "05",
        "slug": "product-knowledge",
        "name": "Product Knowledge",
        "sort": 50,
    },
    {
        "code": "06",
        "slug": "quality-compliance",
        "name": "Quality & Compliance",
        "sort": 60,
    },
    {"code": "07", "slug": "systems-tools", "name": "Systems & Tools", "sort": 70},
    {
        "code": "07.01",
        "slug": "loom-library",
        "name": "Loom Library",
        "parent": "systems-tools",
        "sort": 71,
    },
    {
        "code": "07.02",
        "slug": "vndaq",
        "name": "VND-DAQ",
        "parent": "systems-tools",
        "sort": 72,
    },
    {
        "code": "07.03",
        "slug": "vndmanuf",
        "name": "VNDManuf",
        "parent": "systems-tools",
        "sort": 73,
    },
    {
        "code": "07.04",
        "slug": "shopify",
        "name": "Shopify",
        "parent": "systems-tools",
        "sort": 74,
    },
    {
        "code": "07.05",
        "slug": "sharepoint-guides",
        "name": "SharePoint Guides",
        "parent": "systems-tools",
        "sort": 75,
    },
]

# (title, category_slug, systems, content_type)
ARTICLES = [
    # VNDManuf
    ("How to log raw materials", "vndmanuf", "vndmanuf", "sop"),
    ("How to create a production order", "vndmanuf", "vndmanuf", "sop"),
    ("How to record WIP", "vndmanuf", "vndmanuf", "sop"),
    ("How to complete a production batch", "vndmanuf", "vndmanuf", "sop"),
    ("How to conduct a stocktake", "vndmanuf", "vndmanuf", "sop"),
    ("How to manage recipes and costings", "vndmanuf", "vndmanuf", "sop"),
    ("How to track packaging inventory", "vndmanuf", "vndmanuf", "sop"),
    # VND-DAQ
    ("How to start and stop the DAQ system", "vndaq", "vndaq", "sop"),
    ("How to navigate the Live tab", "vndaq", "vndaq", "sop"),
    ("How to read alarms", "vndaq", "vndaq", "sop"),
    ("How to acknowledge and reset trips", "vndaq", "vndaq", "sop"),
    ("How to use permissives and interlocks", "vndaq", "vndaq", "sop"),
    ("How to configure channels and scales", "vndaq", "vndaq", "sop"),
    ("How to operate the PID controller", "vndaq", "vndaq", "sop"),
    # Production
    ("How to mix feedstock", "packaging-bottling", "vndmanuf,vndaq", "sop"),
    ("How to dilute Gin60 to Gin42", "distillation", "vndmanuf,vndaq", "sop"),
    ("How to bottle product", "packaging-bottling", "vndmanuf", "sop"),
    ("How to apply shrink seals", "packaging-bottling", "vndmanuf", "sop"),
    ("How to label bottles", "packaging-bottling", "vndmanuf", "sop"),
    # Sales
    ("How to set up a new customer", "retailer-setup", "vndmanuf", "sop"),
    (
        "How to deliver product and complete ID checks",
        "retailer-setup",
        "vndmanuf",
        "sop",
    ),
    ("How to record the sale", "retailer-setup", "vndmanuf,shopify,xero", "sop"),
    # Xero
    ("Daily bank reconciliation", "bank-reconciliation", "xero", "sop"),
    ("Creating and sending invoices", "daily-tasks", "xero,vndmanuf", "sop"),
    ("How to prepare EX46 excise return", "inventory-excise", "xero", "sop"),
    # Shopify
    ("How to receive a Shopify order", "shopify", "shopify", "sop"),
    ("How to mark an order as fulfilled", "shopify", "shopify", "sop"),
    # Onboarding
    ("Full site walkthrough", "welcome", "", "guide"),
    ("Safety briefing", "safety-hr", "", "guide"),
    ("How to navigate NU training directory", "welcome", "sharepoint", "guide"),
]


def seed(dry_run: bool = False) -> None:
    session = get_session()
    try:
        slug_to_id: dict[str, str] = {}
        existing_cats = {
            c.slug: c for c in session.execute(select(TrainingCategory)).scalars().all()
        }

        for cat_def in CATEGORIES:
            if cat_def["slug"] in existing_cats:
                slug_to_id[cat_def["slug"]] = str(existing_cats[cat_def["slug"]].id)
                continue
            parent_slug = cat_def.get("parent")
            cat = TrainingCategory(
                slug=cat_def["slug"],
                code=cat_def.get("code"),
                name=cat_def["name"],
                parent_id=slug_to_id.get(parent_slug) if parent_slug else None,
                sort_order=cat_def.get("sort", 0),
                is_active=True,
            )
            session.add(cat)
            session.flush()
            slug_to_id[cat_def["slug"]] = str(cat.id)
            print(f"+ category: {cat.name}")

        existing_slugs = {
            a.slug for a in session.execute(select(TrainingArticle)).scalars().all()
        }

        for title, cat_slug, systems, ctype in ARTICLES:
            slug = slugify(title)
            if slug in existing_slugs:
                continue
            cat_id = slug_to_id.get(cat_slug)
            cat_name = next(
                (c["name"] for c in CATEGORIES if c["slug"] == cat_slug), ""
            )
            article = TrainingArticle(
                slug=slug,
                title=title,
                category_id=cat_id,
                content_type=ctype,
                status="draft",
                summary=f"Training article: {title}. Content to be captured via Loom/SOP.",
                purpose=f"Document the standard procedure for: {title}.",
                systems=systems,
                steps_json=json.dumps(
                    [
                        {
                            "title": "To be documented",
                            "body": "Record Loom walkthrough and steps here.",
                        }
                    ]
                ),
            )
            article.search_blob = build_search_blob(article, cat_name)
            session.add(article)
            print(f"+ article: {title}")

        if dry_run:
            session.rollback()
            print("Dry run — no changes committed.")
        else:
            session.commit()
            print("Seed complete.")
    finally:
        session.close()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    seed(dry_run=dry)
