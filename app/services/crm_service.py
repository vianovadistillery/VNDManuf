"""CRM business logic: calendar events, visit suggestions, export data."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.adapters.db.models import (
    CrmActivity,
    CrmScheduledActivity,
    Customer,
    CustomerRepAssignment,
    SalesOrder,
    SalesOrderLine,
    SalesRep,
)

VISIT_TYPES = frozenset({"visit", "phone", "email"})


def _event_color(event_type: str, source: str = "activity") -> str:
    if source == "order":
        return "#0d6efd"
    if source == "scheduled":
        return "#fd7e14"
    return {
        "visit": "#198754",
        "phone": "#6f42c1",
        "email": "#0dcaf0",
        "note": "#6c757d",
        "photo": "#d63384",
    }.get(event_type, "#6c757d")


def gather_calendar_events(
    db: Session,
    customer_id: str,
    start: Optional[date] = None,
    end: Optional[date] = None,
) -> List[Dict[str, Any]]:
    """Merge activities, orders, and scheduled items for calendar display."""
    events: List[Dict[str, Any]] = []

    act_stmt = (
        select(CrmActivity)
        .where(
            CrmActivity.customer_id == customer_id,
            CrmActivity.deleted_at.is_(None),
        )
        .options(joinedload(CrmActivity.sales_rep))
    )
    if start:
        act_stmt = act_stmt.where(
            CrmActivity.activity_at >= datetime.combine(start, datetime.min.time())
        )
    if end:
        act_stmt = act_stmt.where(
            CrmActivity.activity_at <= datetime.combine(end, datetime.max.time())
        )
    for act in db.execute(act_stmt).scalars().all():
        when = act.activity_at
        subject = (act.subject or "").strip()
        body = (act.body or "").strip()
        type_label = (act.activity_type or "activity").replace("_", " ").title()
        if subject:
            title = subject[:80]
        elif act.activity_type in ("note", "photo", "file") and body:
            title = type_label
        elif body:
            title = body[:80]
        else:
            title = type_label
        comment_parts: List[str] = []
        if act.sales_rep and act.sales_rep.name:
            comment_parts.append(f"Rep: {act.sales_rep.name}")
        if body:
            comment_parts.append(body)
        elif subject:
            comment_parts.append(subject)
        events.append(
            {
                "id": str(act.id),
                "title": title,
                "start": when.isoformat() if when else "",
                "type": act.activity_type,
                "source": "activity",
                "color": _event_color(act.activity_type, "activity"),
                "rep_name": act.sales_rep.name if act.sales_rep else None,
                "comment": "\n".join(comment_parts),
            }
        )

    orders = (
        db.execute(
            select(SalesOrder).where(
                SalesOrder.customer_id == customer_id,
                SalesOrder.deleted_at.is_(None),
            )
        )
        .scalars()
        .all()
    )
    for order in orders:
        od = order.order_date
        if not od:
            continue
        od_date = od.date() if hasattr(od, "date") else od
        if start and od_date < start:
            continue
        if end and od_date > end:
            continue
        events.append(
            {
                "id": f"order-{order.id}",
                "title": f"Order {order.order_ref or order.id}",
                "start": od.isoformat() if hasattr(od, "isoformat") else str(od),
                "type": "order",
                "source": "order",
                "color": _event_color("order", "order"),
                "rep_name": None,
                "comment": (order.notes or "").strip(),
            }
        )

    sched_stmt = select(CrmScheduledActivity).where(
        CrmScheduledActivity.customer_id == customer_id,
        CrmScheduledActivity.deleted_at.is_(None),
        CrmScheduledActivity.status.in_(("scheduled", "overdue")),
    )
    if start:
        sched_stmt = sched_stmt.where(
            CrmScheduledActivity.scheduled_at
            >= datetime.combine(start, datetime.min.time())
        )
    if end:
        sched_stmt = sched_stmt.where(
            CrmScheduledActivity.scheduled_at
            <= datetime.combine(end, datetime.max.time())
        )
    for item in db.execute(sched_stmt).scalars().all():
        events.append(
            {
                "id": str(item.id),
                "title": item.title,
                "start": item.scheduled_at.isoformat(),
                "type": item.activity_type,
                "source": "scheduled",
                "color": _event_color(item.activity_type, "scheduled"),
                "rep_name": None,
                "comment": (item.description or "").strip(),
            }
        )

    events.sort(key=lambda e: e.get("start") or "")
    return events


def compute_visit_suggestions(db: Session, customer: Customer) -> Dict[str, Any]:
    """Suggest next call/visit from profile target and last interaction."""
    target_days = customer.visit_frequency_target_days or 30
    method = customer.preferred_contact_method or "visit"

    last_visit = db.execute(
        select(CrmActivity)
        .where(
            CrmActivity.customer_id == str(customer.id),
            CrmActivity.deleted_at.is_(None),
            CrmActivity.activity_type.in_(tuple(VISIT_TYPES)),
        )
        .order_by(CrmActivity.activity_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    last_order = db.execute(
        select(SalesOrder)
        .where(
            SalesOrder.customer_id == str(customer.id),
            SalesOrder.deleted_at.is_(None),
        )
        .order_by(SalesOrder.order_date.desc())
        .limit(1)
    ).scalar_one_or_none()

    now = datetime.utcnow()
    last_contact_at: Optional[datetime] = None
    last_contact_label = "No recorded contact"

    if last_visit and last_visit.activity_at:
        last_contact_at = last_visit.activity_at
        last_contact_label = (
            f"Last {last_visit.activity_type}: "
            f"{last_visit.activity_at.strftime('%Y-%m-%d')}"
        )
    elif last_order and last_order.order_date:
        last_contact_at = last_order.order_date
        last_contact_label = f"Last order: {last_order.order_date.strftime('%Y-%m-%d')}"

    suggested_at: Optional[datetime] = None
    days_overdue = 0
    if last_contact_at:
        suggested_at = last_contact_at + timedelta(days=target_days)
        days_overdue = (now.date() - suggested_at.date()).days
    else:
        suggested_at = now
        days_overdue = target_days

    urgency = "ok"
    if days_overdue > 7:
        urgency = "overdue"
    elif days_overdue >= 0:
        urgency = "due"

    suggested_type = method if method in VISIT_TYPES else "visit"
    if suggested_type == "in_person":
        suggested_type = "visit"

    return {
        "visit_frequency_target_days": target_days,
        "preferred_contact_method": method,
        "last_contact_at": last_contact_at.isoformat() if last_contact_at else None,
        "last_contact_label": last_contact_label,
        "suggested_at": suggested_at.isoformat() if suggested_at else None,
        "suggested_type": suggested_type,
        "days_overdue": max(days_overdue, 0) if days_overdue > 0 else 0,
        "urgency": urgency,
        "message": _suggestion_message(
            suggested_at, suggested_type, urgency, target_days, days_overdue
        ),
    }


def _suggestion_message(
    suggested_at: Optional[datetime],
    suggested_type: str,
    urgency: str,
    target_days: int,
    days_overdue: int,
) -> str:
    if not suggested_at:
        return f"Set a visit target in Profile; default cycle is {target_days} days."
    date_str = suggested_at.strftime("%d %b %Y")
    action = {"visit": "visit", "phone": "phone call", "email": "email"}.get(
        suggested_type, "contact"
    )
    if urgency == "overdue":
        return (
            f"Overdue for a {action} — target was {date_str} "
            f"({days_overdue} day(s) ago)."
        )
    if urgency == "due":
        return f"Due for a {action} around {date_str} (every {target_days} days)."
    return f"Next {action} suggested around {date_str}."


def rep_customer_assignments(db: Session, rep_id: str) -> List[CustomerRepAssignment]:
    return list(
        db.execute(
            select(CustomerRepAssignment)
            .where(
                CustomerRepAssignment.sales_rep_id == rep_id,
                CustomerRepAssignment.deleted_at.is_(None),
            )
            .options(
                joinedload(CustomerRepAssignment.customer).joinedload(
                    Customer.buying_group
                )
            )
        )
        .scalars()
        .unique()
        .all()
    )


def _activity_event(
    act: CrmActivity,
    *,
    customer_name: Optional[str] = None,
) -> Dict[str, Any]:
    when = act.activity_at
    subject = (act.subject or "").strip()
    body = (act.body or "").strip()
    type_label = (act.activity_type or "activity").replace("_", " ").title()
    if subject:
        title = subject[:80]
    elif act.activity_type in ("note", "photo", "file") and body:
        title = type_label
    elif body:
        title = body[:80]
    else:
        title = type_label
    if customer_name:
        title = f"{customer_name}: {title}"
    comment_parts: List[str] = []
    if act.sales_rep and act.sales_rep.name:
        comment_parts.append(f"Rep: {act.sales_rep.name}")
    if body:
        comment_parts.append(body)
    elif subject:
        comment_parts.append(subject)
    return {
        "id": str(act.id),
        "title": title,
        "start": when.isoformat() if when else "",
        "type": act.activity_type,
        "source": "activity",
        "color": _event_color(act.activity_type, "activity"),
        "rep_name": act.sales_rep.name if act.sales_rep else None,
        "comment": "\n".join(comment_parts),
        "customer_id": str(act.customer_id),
        "customer_name": customer_name,
    }


def gather_rep_calendar_events(
    db: Session,
    rep_id: str,
    start: Optional[date] = None,
    end: Optional[date] = None,
) -> List[Dict[str, Any]]:
    """Calendar events for a rep across their assigned customers."""
    assignments = rep_customer_assignments(db, rep_id)
    customer_ids = [str(a.customer_id) for a in assignments]
    customer_names = {
        str(a.customer_id): (a.customer.name if a.customer else "Customer")
        for a in assignments
    }
    events: List[Dict[str, Any]] = []

    act_filters = [CrmActivity.deleted_at.is_(None)]
    rep_filters = [CrmActivity.sales_rep_id == rep_id]
    if customer_ids:
        rep_filters.append(CrmActivity.customer_id.in_(customer_ids))
    act_filters.append(or_(*rep_filters))
    act_stmt = (
        select(CrmActivity)
        .where(*act_filters)
        .options(joinedload(CrmActivity.sales_rep))
    )
    if start:
        act_stmt = act_stmt.where(
            CrmActivity.activity_at >= datetime.combine(start, datetime.min.time())
        )
    if end:
        act_stmt = act_stmt.where(
            CrmActivity.activity_at <= datetime.combine(end, datetime.max.time())
        )
    for act in db.execute(act_stmt).scalars().all():
        cid = str(act.customer_id)
        events.append(_activity_event(act, customer_name=customer_names.get(cid)))

    if customer_ids:
        order_stmt = select(SalesOrder).where(
            SalesOrder.customer_id.in_(customer_ids),
            SalesOrder.deleted_at.is_(None),
        )
        if start:
            order_stmt = order_stmt.where(
                SalesOrder.order_date >= datetime.combine(start, datetime.min.time())
            )
        if end:
            order_stmt = order_stmt.where(
                SalesOrder.order_date <= datetime.combine(end, datetime.max.time())
            )
        for order in db.execute(order_stmt).scalars().all():
            od = order.order_date
            if not od:
                continue
            cname = customer_names.get(str(order.customer_id), "Customer")
            events.append(
                {
                    "id": f"order-{order.id}",
                    "title": f"{cname}: Order {order.order_ref or order.id}",
                    "start": od.isoformat() if hasattr(od, "isoformat") else str(od),
                    "type": "order",
                    "source": "order",
                    "color": _event_color("order", "order"),
                    "rep_name": None,
                    "comment": (order.notes or "").strip(),
                    "customer_id": str(order.customer_id),
                    "customer_name": cname,
                }
            )

    sched_stmt = select(CrmScheduledActivity).where(
        CrmScheduledActivity.sales_rep_id == rep_id,
        CrmScheduledActivity.deleted_at.is_(None),
        CrmScheduledActivity.status.in_(("scheduled", "overdue")),
    )
    if start:
        sched_stmt = sched_stmt.where(
            CrmScheduledActivity.scheduled_at
            >= datetime.combine(start, datetime.min.time())
        )
    if end:
        sched_stmt = sched_stmt.where(
            CrmScheduledActivity.scheduled_at
            <= datetime.combine(end, datetime.max.time())
        )
    for item in db.execute(sched_stmt).scalars().all():
        cname = customer_names.get(str(item.customer_id), "Customer")
        events.append(
            {
                "id": str(item.id),
                "title": f"{cname}: {item.title}",
                "start": item.scheduled_at.isoformat(),
                "type": item.activity_type,
                "source": "scheduled",
                "color": _event_color(item.activity_type, "scheduled"),
                "rep_name": None,
                "comment": (item.description or "").strip(),
                "customer_id": str(item.customer_id),
                "customer_name": cname,
            }
        )

    events.sort(key=lambda e: e.get("start") or "")
    return events


def build_rep_portfolio_dashboard(
    db: Session,
    rep_id: str,
    start: Optional[date] = None,
    end: Optional[date] = None,
) -> Dict[str, Any]:
    rep = db.get(SalesRep, rep_id)
    if not rep or rep.deleted_at is not None:
        raise ValueError("Sales rep not found")

    assignments = rep_customer_assignments(db, rep_id)
    customer_ids = [str(a.customer_id) for a in assignments]
    customer_rows: List[Dict[str, Any]] = []
    total_orders = 0
    total_inc = 0.0
    total_units = 0.0
    portfolio_orders: List[Dict[str, Any]] = []

    for assignment in assignments:
        customer = assignment.customer
        if not customer or customer.deleted_at is not None:
            continue
        cid = str(customer.id)
        order_stmt = select(SalesOrder).where(
            SalesOrder.customer_id == cid,
            SalesOrder.deleted_at.is_(None),
        )
        if start:
            order_stmt = order_stmt.where(
                SalesOrder.order_date >= datetime.combine(start, datetime.min.time())
            )
        if end:
            order_stmt = order_stmt.where(
                SalesOrder.order_date <= datetime.combine(end, datetime.max.time())
            )
        orders = (
            db.execute(order_stmt.order_by(SalesOrder.order_date.desc()))
            .scalars()
            .all()
        )
        order_count = len(orders)
        cust_inc = sum(float(o.total_inc_gst or 0) for o in orders)
        last_order = orders[0].order_date if orders else None
        last_order_str = None
        if last_order:
            last_order_str = (
                last_order.date().isoformat()
                if hasattr(last_order, "date")
                else str(last_order)[:10]
            )
        customer_rows.append(
            {
                "customer_id": cid,
                "code": customer.code,
                "name": customer.name,
                "buying_group_name": (
                    customer.buying_group.name if customer.buying_group else None
                ),
                "assignment_role": assignment.role,
                "order_count": order_count,
                "total_inc_gst": cust_inc,
                "last_order_date": last_order_str,
            }
        )
        total_orders += order_count
        total_inc += cust_inc
        for order in orders[:5]:
            od = order.order_date
            od_str = (
                od.date().isoformat()
                if od and hasattr(od, "date")
                else str(od or "")[:10]
            )
            portfolio_orders.append(
                {
                    "order_date": od_str,
                    "order_ref": order.order_ref or "—",
                    "customer_name": customer.name,
                    "status": (order.status or "").title(),
                    "total_inc_gst": float(order.total_inc_gst or 0),
                }
            )

    if customer_ids:
        line_stmt = (
            select(func.coalesce(func.sum(SalesOrderLine.qty), 0))
            .join(SalesOrder, SalesOrder.id == SalesOrderLine.order_id)
            .where(
                SalesOrder.customer_id.in_(customer_ids),
                SalesOrder.deleted_at.is_(None),
                SalesOrderLine.deleted_at.is_(None),
            )
        )
        if start:
            line_stmt = line_stmt.where(
                SalesOrder.order_date >= datetime.combine(start, datetime.min.time())
            )
        if end:
            line_stmt = line_stmt.where(
                SalesOrder.order_date <= datetime.combine(end, datetime.max.time())
            )
        total_units = float(db.execute(line_stmt).scalar() or 0)

    customer_rows.sort(key=lambda r: r["total_inc_gst"], reverse=True)
    portfolio_orders.sort(key=lambda r: r["order_date"], reverse=True)

    return {
        "rep_id": str(rep.id),
        "rep_name": rep.name,
        "rep_code": rep.code,
        "customer_count": len(customer_rows),
        "order_count": total_orders,
        "total_revenue_inc_gst": total_inc,
        "total_units": total_units,
        "customers": customer_rows,
        "orders": portfolio_orders[:50],
    }
