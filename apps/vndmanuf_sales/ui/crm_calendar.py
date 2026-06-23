"""Month calendar grid for CRM timeline."""

from calendar import month_name, monthcalendar
from datetime import date, timedelta
from typing import Any, Dict, List

import dash_bootstrap_components as dbc
from dash import html

_SUMMARY_MAX_LEN = 22
_MAX_SUMMARIES_PER_DAY = 2


def shift_month(month_key: str, delta: int) -> str:
    year, month = map(int, month_key.split("-"))
    month += delta
    while month < 1:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    return f"{year:04d}-{month:02d}"


def month_range_bounds(month_key: str) -> tuple[date, date]:
    year, month = map(int, month_key.split("-"))
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start, end


def three_month_date_range(center_month_key: str) -> tuple[str, str]:
    prev_start, _ = month_range_bounds(shift_month(center_month_key, -1))
    _, next_end = month_range_bounds(shift_month(center_month_key, 1))
    return prev_start.isoformat(), next_end.isoformat()


def events_by_day(events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for ev in events:
        start = str(ev.get("start") or "")[:10]
        if not start:
            continue
        grouped.setdefault(start, []).append(ev)
    return grouped


def _event_summary(text: str, max_len: int = _SUMMARY_MAX_LEN) -> str:
    text = (text or "").strip()
    if not text:
        return "—"
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def _day_event_summaries(day_events: List[Dict[str, Any]]) -> list:
    items = []
    for ev in day_events[:_MAX_SUMMARIES_PER_DAY]:
        color = ev.get("color") or "#6c757d"
        summary = _event_summary(ev.get("title") or ev.get("type") or "Event")
        items.append(
            html.Div(
                summary,
                className="crm-cal-event-summary",
                style={"borderLeftColor": color},
                title=ev.get("title", ""),
            )
        )
    if len(day_events) > _MAX_SUMMARIES_PER_DAY:
        extra = len(day_events) - _MAX_SUMMARIES_PER_DAY
        items.append(html.Small(f"+{extra}", className="crm-cal-more text-muted"))
    return items


def build_month_calendar(
    month_key: str,
    events: List[Dict[str, Any]],
    *,
    compact: bool = False,
) -> html.Div:
    """Render one month grid; compact mode for 3-across layout."""
    _start, _end = month_range_bounds(month_key)
    year, month = map(int, month_key.split("-"))
    by_day = events_by_day(events)
    weeks = monthcalendar(year, month)
    weekday_headers = (
        ["M", "T", "W", "T", "F", "S", "S"]
        if compact
        else ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    )

    header_row = html.Tr(
        [html.Th(d, className="crm-cal-weekday") for d in weekday_headers]
    )
    body_rows = []
    for week in weeks:
        cells = []
        for day in week:
            if day == 0:
                cells.append(html.Td("", className="crm-cal-day crm-cal-empty"))
                continue
            day_key = date(year, month, day).isoformat()
            day_events = by_day.get(day_key, [])
            is_today = day_key == date.today().isoformat()
            summaries = _day_event_summaries(day_events)
            cells.append(
                html.Td(
                    html.Div(
                        [
                            html.Div(str(day), className="crm-cal-day-num"),
                            html.Div(summaries, className="crm-cal-events"),
                        ],
                        id=f"crm-cal-day-{day_key}",
                        className="crm-cal-day-inner",
                    ),
                    className=(
                        "crm-cal-day crm-cal-day-clickable crm-cal-today"
                        if is_today
                        else "crm-cal-day crm-cal-day-clickable"
                    ),
                )
            )
        body_rows.append(html.Tr(cells))

    table = html.Table(
        [html.Thead(header_row), html.Tbody(body_rows)],
        className=(
            "table table-bordered crm-cal-table crm-cal-compact mb-0"
            if compact
            else "table table-bordered crm-cal-table mb-0"
        ),
    )
    extras = []
    if not compact:
        extras.extend(
            [
                html.Div(_legend(events), className="small text-muted mt-2"),
                html.Small(
                    "Double-click a day to view all events.",
                    className="text-muted d-block mt-1",
                ),
            ]
        )
    return html.Div([table, *extras], className="crm-calendar-wrap")


def build_three_month_calendars(
    center_month_key: str, events: List[Dict[str, Any]]
) -> html.Div:
    """Three months side by side: previous, current, next."""
    months = [
        shift_month(center_month_key, -1),
        center_month_key,
        shift_month(center_month_key, 1),
    ]
    cols = []
    for mk in months:
        month_events = [e for e in events if str(e.get("start") or "")[:7] == mk]
        cols.append(
            dbc.Col(
                [
                    html.H6(
                        month_title(mk),
                        className="text-center crm-cal-month-label mb-1",
                    ),
                    build_month_calendar(mk, month_events, compact=True),
                ],
                md=4,
                xs=12,
                className="crm-cal-month-col",
            )
        )
    return html.Div(
        [
            dbc.Row(cols, className="g-2"),
            html.Div(_legend(events), className="small text-muted mt-2"),
            html.Small(
                "Double-click a day to view or edit events.",
                className="text-muted d-block mt-1",
            ),
        ]
    )


def _legend(events: List[Dict[str, Any]]) -> html.Div:
    seen = {}
    for ev in events:
        src = ev.get("source", "activity")
        if src not in seen:
            seen[src] = ev.get("color", "#6c757d")
    if not seen:
        return html.Span("No events in this period.")
    items = []
    labels = {
        "activity": "Notes & visits",
        "order": "Orders",
        "scheduled": "Scheduled",
    }
    for src, color in seen.items():
        items.append(
            html.Span(
                [
                    html.Span(
                        className="crm-cal-legend-swatch d-inline-block me-1",
                        style={"backgroundColor": color},
                    ),
                    labels.get(src, src),
                ],
                className="me-3",
            )
        )
    return html.Div(items)


def month_title(month_key: str) -> str:
    year, month = map(int, month_key.split("-"))
    return f"{month_name[month]} {year}"


def three_month_title(center_month_key: str) -> str:
    left = shift_month(center_month_key, -1)
    right = shift_month(center_month_key, 1)
    ly, lm = map(int, left.split("-"))
    ry, rm = map(int, right.split("-"))
    if ly == ry:
        return f"{month_name[lm]} – {month_name[rm]} {ry}"
    return f"{month_name[lm]} {ly} – {month_name[rm]} {ry}"
