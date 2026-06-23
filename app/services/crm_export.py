"""Gather CRM data and build PDF export context."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.api.sales import _get_filtered_orders
from app.documents.context_builder import build_context_from_crm_summary
from app.documents.contracts import DocumentContext
from app.services.crm_service import compute_visit_suggestions, gather_calendar_events


def _parse_sections(section_list: List[str]) -> dict[str, bool]:
    all_flag = "all" in section_list
    keys = ("sales", "timeline", "profile", "people", "scheduled")
    return {k: all_flag or k in section_list for k in keys}


def build_crm_export_context(
    db: Session,
    customer_id: str,
    sections_list: List[str],
    start_date: Optional[date],
    end_date: Optional[date],
) -> DocumentContext:
    from app.api.crm import _build_product_summary, _get_customer, _profile_response

    sections = _parse_sections(sections_list)
    customer = _get_customer(db, customer_id)
    profile = _profile_response(db, customer)
    suggestions = compute_visit_suggestions(db, customer)

    sales_rows = None
    sales_orders = None
    order_count = 0
    total_ex = Decimal("0")
    total_inc = Decimal("0")
    total_qty = Decimal("0")

    if sections.get("sales"):
        orders = _get_filtered_orders(
            db,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
        )
        summary = _build_product_summary(db, orders)
        sales_rows = [r.model_dump() for r in summary.rows]
        sales_orders = [o.model_dump() for o in summary.orders]
        order_count = summary.order_count
        total_ex = Decimal(str(summary.total_ex_gst))
        total_inc = Decimal(str(summary.total_inc_gst))
        total_qty = Decimal(str(summary.total_qty))

    timeline_items: List[dict] = []
    if sections.get("timeline"):
        events = gather_calendar_events(db, customer_id, start_date, end_date)
        timeline_items = [
            {
                "when": (e.get("start") or "")[:16].replace("T", " "),
                "type": e.get("type", ""),
                "title": e.get("title", ""),
                "source": e.get("source", ""),
                "comment": e.get("comment") or "",
            }
            for e in events
        ]

    staff_items: List[dict] = []
    if sections.get("people"):
        from sqlalchemy import select

        from app.adapters.db.models import CrmCustomerStaff

        rows = (
            db.execute(
                select(CrmCustomerStaff).where(
                    CrmCustomerStaff.customer_id == customer_id,
                    CrmCustomerStaff.deleted_at.is_(None),
                )
            )
            .scalars()
            .all()
        )
        staff_items = [
            {
                "name": s.name,
                "role": s.role or "",
                "phone": s.phone or "",
                "email": s.email or "",
                "notes": s.notes or "",
                "is_primary": "Yes" if s.is_primary else "",
            }
            for s in rows
        ]

    scheduled_items: List[dict] = []
    if sections.get("scheduled"):
        from sqlalchemy import select

        from app.adapters.db.models import CrmScheduledActivity

        rows = (
            db.execute(
                select(CrmScheduledActivity).where(
                    CrmScheduledActivity.customer_id == customer_id,
                    CrmScheduledActivity.deleted_at.is_(None),
                )
            )
            .scalars()
            .all()
        )
        scheduled_items = [
            {
                "when": s.scheduled_at.strftime("%Y-%m-%d %H:%M"),
                "type": s.activity_type,
                "title": s.title,
                "description": s.description or "",
                "status": s.status,
            }
            for s in rows
        ]

    profile_extra: Dict[str, Any] = {}
    if sections.get("profile"):
        profile_extra = {
            "buying_group": profile.buying_group_name or "—",
            "visit_target_days": str(profile.visit_frequency_target_days or "—"),
            "preferred_contact": profile.preferred_contact_method or "—",
            "primary_rep": (
                profile.primary_rep.sales_rep_name if profile.primary_rep else "—"
            ),
            "customer_type": profile.customer_type or "—",
            "email": profile.email or "—",
            "phone": profile.phone or "—",
        }

    return build_context_from_crm_summary(
        db,
        customer_id=customer_id,
        sections=sections,
        period_start=start_date,
        period_end=end_date,
        sales_rows=sales_rows,
        sales_orders=sales_orders,
        sales_order_count=order_count,
        sales_total_ex_gst=total_ex,
        sales_total_inc_gst=total_inc,
        sales_total_qty=total_qty,
        timeline_items=timeline_items,
        staff_items=staff_items,
        scheduled_items=scheduled_items,
        profile_extra=profile_extra,
        suggestions=suggestions if sections.get("profile") else None,
    )
