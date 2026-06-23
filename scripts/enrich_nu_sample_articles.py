#!/usr/bin/env python3
"""Enrich selected Nova U articles with realistic sample content for demos."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.adapters.db.models import TrainingArticle, TrainingCategory
from app.adapters.db.session import get_session
from app.training.service import build_search_blob, category_path

# slug -> enrichment payload
ENRICHMENTS: dict[str, dict] = {
    "how-to-log-raw-materials": {
        "status": "published",
        "summary": "Receive a delivery of raw materials into VNDManuf and keep supplier, lot, and cost data accurate.",
        "purpose": "Ensure every inbound raw material is recorded before it is used in production or excise reporting.",
        "prerequisites": "Delivery docket or supplier invoice; product SKU already set up in Products; supplier contact in Contacts.",
        "safety_notes": "Check SDS for spirit bases and chemicals. Wear gloves and eye protection when handling undiluted ethanol.",
        "steps": [
            {
                "title": "Open Products",
                "body": "Manufacturing → Products. Filter to RAW or search by SKU.",
            },
            {
                "title": "Select material",
                "body": "Open the product and go to the inventory / movements section.",
            },
            {
                "title": "Record receipt",
                "body": "Enter quantity in purchase units, lot/batch reference, supplier invoice number, and unit cost ex-GST.",
            },
            {
                "title": "Verify stock",
                "body": "Confirm on-hand quantity updated. Attach docket scan to SharePoint if required.",
            },
        ],
        "risks": [
            {
                "issue": "Wrong SKU selected",
                "prevention": "Match supplier product code to internal SKU before posting.",
            },
            {
                "issue": "Cost not entered",
                "prevention": "FIFO costing depends on receipt cost — always enter invoice unit price.",
            },
        ],
        "systems": ["vndmanuf"],
        "tags": ["raw-materials", "inventory", "receiving"],
        "body_markdown": "Related: Contacts (suppliers), Purchase formats, Excise records.",
    },
    "how-to-create-a-production-order": {
        "status": "published",
        "summary": "Raise a work order in VNDManuf to plan distillation, blending, or packaging.",
        "purpose": "Convert a formula and batch plan into a traceable production job with planned quantities.",
        "prerequisites": "Approved formula exists; raw materials in stock; work area configured if applicable.",
        "steps": [
            {
                "title": "Work Orders tab",
                "body": "Manufacturing → Work Orders → New work order.",
            },
            {
                "title": "Choose product",
                "body": "Select finished or WIP product and planned output quantity.",
            },
            {
                "title": "Link formula",
                "body": "Pick the active formula revision. Review component list and yield.",
            },
            {
                "title": "Release",
                "body": "Save as planned, then Release when ready for the still or packaging line.",
            },
        ],
        "risks": [
            {
                "issue": "Insufficient stock",
                "prevention": "Check RM availability on the WO detail screen before release.",
            },
        ],
        "systems": ["vndmanuf"],
        "tags": ["work-orders", "production"],
    },
    "how-to-conduct-a-stocktake": {
        "status": "published",
        "summary": "Run a physical stocktake in VNDManuf and post variances.",
        "purpose": "Reconcile system inventory with physical counts for excise, insurance, and production planning.",
        "prerequisites": "Count sheets prepared; access to Stocktake page; movements frozen where possible.",
        "steps": [
            {"title": "Open Stocktake", "body": "Manufacturing → Stocktake."},
            {
                "title": "Enter counts",
                "body": "Search products and enter counted quantity per location or pack unit.",
            },
            {
                "title": "Review variances",
                "body": "Compare system vs counted. Investigate large deltas before posting.",
            },
            {
                "title": "Post",
                "body": "Submit stocktake to create adjustment movements with audit trail.",
            },
        ],
        "systems": ["vndmanuf"],
        "tags": ["stocktake", "inventory"],
    },
    "how-to-start-and-stop-the-daq-system": {
        "status": "published",
        "summary": "Safely start and shut down the VND-DAQ distillation control system.",
        "purpose": "Prevent uncontrolled heating, pump run-dry, or trip conditions during startup and shutdown.",
        "prerequisites": "Operator induction complete; hardware permissives green; no active maintenance locks.",
        "safety_notes": "Never bypass interlocks. Confirm condenser flow before enabling boiler heat.",
        "steps": [
            {
                "title": "Pre-checks",
                "body": "Verify cooling water, condensate path, and vessel levels on Live tab.",
            },
            {
                "title": "Enable permissives",
                "body": "Acknowledge any advisory alarms. Wait for trip logic to show READY.",
            },
            {
                "title": "Start sequence",
                "body": "Follow site SOP order: pumps → condenser → heat ramp per recipe.",
            },
            {
                "title": "Shutdown",
                "body": "Ramp down heat, stop feed, flush lines per cleaning SOP before full power off.",
            },
        ],
        "systems": ["vndaq"],
        "tags": ["daq", "startup", "safety"],
    },
    "daily-bank-reconciliation": {
        "status": "published",
        "summary": "Match bank feed lines in Xero to payments and receipts for Via Nova.",
        "purpose": "Keep cash records accurate for BAS, excise, and management reporting.",
        "prerequisites": "Bank feed imported; previous day reconciled; invoices entered in Xero or via VNDManuf sales export.",
        "steps": [
            {
                "title": "Open reconcile",
                "body": "Xero → Accounting → Bank accounts → Reconcile.",
            },
            {
                "title": "Match known items",
                "body": "Auto-match customer receipts and supplier payments where possible.",
            },
            {
                "title": "Code exceptions",
                "body": "Create spend/receive money for unmatched items with correct account codes.",
            },
            {
                "title": "Balance",
                "body": "Confirm statement balance equals Xero balance. Finish reconciliation.",
            },
        ],
        "systems": ["xero"],
        "tags": ["finance", "reconciliation"],
    },
    "full-site-walkthrough": {
        "status": "published",
        "summary": "Orientation tour of Via Nova Distillery — production, lab, warehouse, and office systems.",
        "purpose": "Give new staff a mental map of the site and where each NU training topic applies.",
        "steps": [
            {
                "title": "Receival & raw store",
                "body": "Where spirit, botanicals, and packaging arrive. SDS folder location.",
            },
            {
                "title": "Still & DAQ",
                "body": "VND-DAQ screens, emergency stops, and cleaning station.",
            },
            {
                "title": "Blending & packaging",
                "body": "Dilution, filtering, bottling, labelling, and shrink seal.",
            },
            {
                "title": "Finished goods",
                "body": "Bond store, excise records, dispatch staging.",
            },
            {
                "title": "Office systems",
                "body": "VNDManuf, Xero, Shopify, SharePoint NU library.",
            },
        ],
        "systems": [],
        "tags": ["induction", "site-tour"],
        "content_type": "guide",
    },
    "how-to-set-up-a-new-customer": {
        "status": "published",
        "summary": "Create a retailer or wholesale customer in VNDManuf Sales and link to Contacts.",
        "purpose": "Ensure orders, delivery dockets, and invoices use correct pricing, excise, and delivery details.",
        "steps": [
            {
                "title": "Contacts",
                "body": "Contacts tab → New contact. Enter legal name, ABN, delivery address.",
            },
            {
                "title": "Sales customer",
                "body": "Sales → Customers → link to contact; set channel, payment terms, price list.",
            },
            {
                "title": "Verify",
                "body": "Place a test order and confirm delivery address and pricing on order PDF.",
            },
        ],
        "systems": ["vndmanuf", "xero"],
        "tags": ["sales", "customers"],
    },
}


def enrich(dry_run: bool = False) -> None:
    session = get_session()
    try:
        by_id = {
            str(c.id): c
            for c in session.execute(select(TrainingCategory)).scalars().all()
        }
        updated = 0
        for slug, data in ENRICHMENTS.items():
            article = session.execute(
                select(TrainingArticle).where(TrainingArticle.slug == slug)
            ).scalar_one_or_none()
            if not article:
                print(f"skip (missing): {slug}")
                continue

            article.status = data.get("status", article.status)
            article.summary = data.get("summary", article.summary)
            article.purpose = data.get("purpose", article.purpose)
            article.prerequisites = data.get("prerequisites", article.prerequisites)
            article.safety_notes = data.get("safety_notes", article.safety_notes)
            article.troubleshooting = data.get(
                "troubleshooting", article.troubleshooting
            )
            article.body_markdown = data.get("body_markdown", article.body_markdown)
            if data.get("systems") is not None:
                article.systems = ",".join(data["systems"])
            if data.get("tags"):
                article.tags = ",".join(data["tags"])
            if data.get("content_type"):
                article.content_type = data["content_type"]
            if data.get("steps"):
                article.steps_json = json.dumps(data["steps"])
            if data.get("risks"):
                article.risks_json = json.dumps(data["risks"])

            cat = by_id.get(str(article.category_id)) if article.category_id else None
            label = category_path(cat, by_id) if cat else ""
            article.search_blob = build_search_blob(article, label)
            updated += 1
            print(f"~ enriched: {article.title}")

        if dry_run:
            session.rollback()
            print("Dry run — no changes committed.")
        else:
            session.commit()
            print(f"Enriched {updated} articles.")
    finally:
        session.close()


if __name__ == "__main__":
    enrich(dry_run="--dry-run" in sys.argv)
