"""CRM summary PDF — consolidate table rows into multi-line single cells."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def _multiline_cell(values: List[str], blank: str = "—") -> str:
    """Join values with newlines for a single table cell."""
    lines = [str(v).strip() if v and str(v).strip() else blank for v in values]
    return "\n".join(lines) if lines else blank


def build_crm_table_blocks(
    order_rows: Optional[List[dict]],
    sku_rows: Optional[List[dict]],
    timeline_rows: Optional[List[dict]],
    staff_rows: Optional[List[dict]],
    scheduled_rows: Optional[List[dict]],
) -> Dict[str, Dict[str, Any]]:
    """Consolidate CRM export lists into single-row table blocks for the PDF template."""
    orders = order_rows or []
    skus = sku_rows or []
    timeline = timeline_rows or []
    staff = staff_rows or []
    scheduled = scheduled_rows or []

    def _unit_ex(row: dict) -> str:
        if row.get("unit_ex"):
            return str(row["unit_ex"])
        if row.get("ex"):
            return str(row["ex"])
        qty = float(row.get("total_qty") or row.get("quantity") or 0)
        if qty:
            return str(round(float(row.get("total_ex_gst") or 0) / qty, 2))
        return ""

    return {
        "orders_block": {
            "dates": _multiline_cell([o.get("order_date") or "" for o in orders]),
            "refs": _multiline_cell([o.get("order_ref") or "" for o in orders]),
            "pos": _multiline_cell([o.get("po_number") or "" for o in orders]),
            "statuses": _multiline_cell([o.get("status") or "" for o in orders]),
            "total_ex": _multiline_cell([o.get("total_ex_gst") or "" for o in orders]),
            "total_inc": _multiline_cell(
                [o.get("total_inc_gst") or "" for o in orders]
            ),
        },
        "sku_block": {
            "sku": _multiline_cell([r.get("sku") or "" for r in skus]),
            "product": _multiline_cell(
                [
                    r.get("name") or r.get("product_name") or r.get("description") or ""
                    for r in skus
                ]
            ),
            "qty": _multiline_cell(
                [r.get("total_qty") or r.get("quantity") or "" for r in skus]
            ),
            "unit_ex": _multiline_cell([_unit_ex(r) for r in skus]),
            "line_inc": _multiline_cell(
                [r.get("total_inc_gst") or r.get("tot_inc") or "" for r in skus]
            ),
        },
        "timeline_block": {
            "when": _multiline_cell([t.get("when") or "" for t in timeline]),
            "type": _multiline_cell([t.get("type") or "" for t in timeline]),
            "title": _multiline_cell([t.get("title") or "" for t in timeline]),
            "source": _multiline_cell([t.get("source") or "" for t in timeline]),
        },
        "staff_block": {
            "name": _multiline_cell([s.get("name") or "" for s in staff]),
            "role": _multiline_cell([s.get("role") or "" for s in staff]),
            "phone": _multiline_cell([s.get("phone") or "" for s in staff]),
            "email": _multiline_cell([s.get("email") or "" for s in staff]),
            "primary": _multiline_cell([s.get("is_primary") or "" for s in staff]),
            "notes": _multiline_cell([s.get("notes") or "" for s in staff]),
        },
        "scheduled_block": {
            "when": _multiline_cell([s.get("when") or "" for s in scheduled]),
            "type": _multiline_cell([s.get("type") or "" for s in scheduled]),
            "title": _multiline_cell([s.get("title") or "" for s in scheduled]),
            "status": _multiline_cell([s.get("status") or "" for s in scheduled]),
            "description": _multiline_cell(
                [s.get("description") or "" for s in scheduled]
            ),
        },
    }
