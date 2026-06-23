"""Dash callbacks for the CRM sub-tab."""

from __future__ import annotations

import base64
import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

import dash
import dash_bootstrap_components as dbc
import requests
from dash import ALL, Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate

from apps.vndmanuf_sales.ui.crm_calendar import (
    build_three_month_calendars,
    shift_month,
    three_month_date_range,
    three_month_title,
)
from apps.vndmanuf_sales.ui.period_filters import register_period_preset_callbacks


def _fmt_money(value: Any) -> str:
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return "—"


def _now_local_datetime() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M")


def _format_activity_at(value: Any) -> str:
    if not value:
        return "—"
    text = str(value).replace("Z", "")
    return text[:16].replace("T", " ")


def _parse_activity_at(value: Any) -> str | None:
    if not value:
        return None
    return str(value).strip()


def _truncate_notes(value: Any, limit: int = 80) -> str:
    if not value:
        return "—"
    text = str(value).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _future_local_datetime(days_ahead: int = 7) -> str:
    return (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%dT%H:%M")


def _parse_api_error(response: Any) -> str | None:
    if not isinstance(response, dict) or not response.get("error"):
        return None
    err = response["error"]
    try:
        parsed = json.loads(err)
        if isinstance(parsed, dict):
            detail = parsed.get("detail") or parsed.get("message")
            if isinstance(detail, list) and detail:
                return str(detail[0])
            if detail:
                return str(detail)
    except (json.JSONDecodeError, TypeError):
        pass
    return str(err)


def _activity_editable(item: Dict[str, Any]) -> bool:
    return item.get("source") == "activity" and bool(item.get("id"))


def _activity_action_buttons(activity_id: str) -> html.Div:
    return html.Div(
        [
            dbc.Button(
                "Edit",
                id={"type": "crm-act-edit", "index": activity_id},
                size="sm",
                color="secondary",
                className="me-1",
            ),
            dbc.Button(
                "Delete",
                id={"type": "crm-act-delete", "index": activity_id},
                size="sm",
                color="danger",
                outline=True,
            ),
        ],
        className="crm-activity-actions",
    )


def _activity_display_title(item: Dict[str, Any]) -> str:
    return item.get("body") or item.get("subject") or item.get("title") or "—"


def _activity_badge(item: Dict[str, Any]) -> tuple[str, str]:
    source = item.get("source", "activity")
    color = {
        "order": "primary",
        "scheduled": "warning",
        "activity": "info",
    }.get(source, "secondary")
    label = item.get("activity_type") or item.get("type") or source
    return str(label), color


def _build_activity_list_item(item: Dict[str, Any]) -> dbc.ListGroupItem:
    when = _format_activity_at(item.get("activity_at") or item.get("start"))
    label, badge_color = _activity_badge(item)
    rep = item.get("sales_rep_name") or item.get("rep_name")
    children: List[Any] = [
        html.Div(
            [
                dbc.Badge(label, color=badge_color, className="me-2"),
                html.Small(when, className="text-muted"),
                html.Span(f" · {rep}", className="text-muted small") if rep else None,
            ],
            className="mb-1",
        ),
        html.Div(_activity_display_title(item)),
    ]
    if item.get("note_category"):
        children.append(
            html.Small(item["note_category"], className="text-muted d-block")
        )
    if _activity_editable(item):
        children.append(_activity_action_buttons(str(item["id"])))
    return dbc.ListGroupItem(children)


def _build_activity_feed_card(item: Dict[str, Any]) -> dbc.Card:
    when = _format_activity_at(item.get("activity_at") or item.get("start"))
    label, badge_color = _activity_badge(item)
    rep = item.get("sales_rep_name") or item.get("rep_name")
    body_children: List[Any] = [
        html.Div(
            [
                dbc.Badge(label, color=badge_color, className="me-2"),
                html.Small(when, className="text-muted"),
                html.Span(f" · {rep}", className="text-muted small") if rep else None,
            ],
            className="mb-1",
        ),
        html.Strong(_activity_display_title(item)),
    ]
    if item.get("note_category"):
        body_children.append(
            html.P(item["note_category"], className="mb-0 small text-muted")
        )
    if _activity_editable(item):
        body_children.append(_activity_action_buttons(str(item["id"])))
    return dbc.Card(dbc.CardBody(body_children), className="mb-2 shadow-sm")


def _suggestion_alert(data: Dict[str, Any]) -> Any:
    if not data or data.get("error"):
        return no_update
    urgency = data.get("urgency", "ok")
    color = {"overdue": "danger", "due": "warning", "ok": "success"}.get(
        urgency, "info"
    )
    return dbc.Alert(
        [
            html.Strong(data.get("message", "")),
            html.Br(),
            html.Small(data.get("last_contact_label", ""), className="text-muted"),
        ],
        color=color,
        className="mb-0",
    )


def _upload_note_photos(
    api_base_url: str,
    customer_id: str,
    activity_id: str,
    rep_id: str | None,
    uploads: List[Dict[str, Any]] | None,
) -> str | None:
    if not uploads:
        return None
    for item in uploads:
        raw = item.get("contents") or ""
        if "," in raw:
            raw = raw.split(",", 1)[1]
        try:
            data = base64.b64decode(raw)
        except Exception:
            continue
        filename = item.get("filename") or "photo.jpg"
        mime = item.get("type") or "image/jpeg"
        form: Dict[str, str] = {"activity_id": activity_id}
        if rep_id:
            form["sales_rep_id"] = rep_id
        try:
            resp = requests.post(
                f"{api_base_url}/api/v1/crm/customers/{customer_id}/attachments",
                files={"file": (filename, data, mime)},
                data=form,
                timeout=30,
            )
            if resp.status_code >= 400:
                return f"Photo upload failed: {resp.text[:120]}"
        except Exception as exc:
            return f"Photo upload error: {exc}"
    return None


def _format_day_heading(date_str: str) -> str:
    try:
        d = date.fromisoformat(date_str)
        return d.strftime("%A, %d %B %Y")
    except ValueError:
        return date_str


def _events_for_day(
    events: List[Dict[str, Any]], date_str: str
) -> List[Dict[str, Any]]:
    return [e for e in events if str(e.get("start") or "")[:10] == date_str]


def _build_day_events_body(day_events: List[Dict[str, Any]]) -> Any:
    if not day_events:
        return dbc.Alert("No events on this day.", color="light")
    items = [
        _build_activity_list_item(ev)
        for ev in sorted(
            day_events, key=lambda e: e.get("start") or e.get("activity_at") or ""
        )
    ]
    return dbc.ListGroup(items, flush=True)


def _find_activity_row(
    customer_id: str, activity_id: str, make_api_request
) -> Dict[str, Any] | None:
    rows = make_api_request("GET", f"/crm/customers/{customer_id}/activities")
    if not isinstance(rows, list):
        return None
    return next((r for r in rows if str(r.get("id")) == str(activity_id)), None)


def register_crm_callbacks(
    app, make_api_request, api_base_url: str = "http://127.0.0.1:8000"
):
    """Register CRM workspace callbacks."""

    register_period_preset_callbacks(app, prefix="crm-customer")
    register_period_preset_callbacks(app, prefix="crm-rep")

    @app.callback(
        [
            Output("crm-reps-store", "data"),
            Output("crm-rep-select", "options"),
            Output("crm-rep-select", "value"),
            Output("crm-buying-groups-store", "data"),
            Output("crm-profile-buying-group", "options"),
            Output("crm-assign-rep", "options"),
        ],
        Input("main-tabs", "active_tab"),
        State("crm-rep-select", "value"),
        prevent_initial_call=False,
    )
    def hydrate_crm_lookups(active_tab, current_rep):
        if active_tab != "crm":
            return (no_update,) * 6
        reps = make_api_request("GET", "/sales-reps/", {"is_active": True})
        groups = make_api_request("GET", "/buying-groups/", {"is_active": True})
        reps_list = reps if isinstance(reps, list) else []
        groups_list = groups if isinstance(groups, list) else []
        rep_options = [
            {"label": f"{r.get('name', '')} ({r.get('code', '')})", "value": r["id"]}
            for r in reps_list
        ]
        group_options = [
            {"label": g.get("name", ""), "value": g["id"]} for g in groups_list
        ]
        if current_rep and current_rep in {o["value"] for o in rep_options}:
            rep_value = no_update
        elif rep_options:
            rep_value = rep_options[0]["value"]
        else:
            rep_value = None
        return (
            reps_list,
            rep_options,
            rep_value,
            groups_list,
            group_options,
            rep_options,
        )

    @app.callback(
        Output("crm-customer-select", "options"),
        [
            Input("main-tabs", "active_tab"),
            Input("crm-account-scope", "value"),
            Input("crm-refresh-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_customer_options(active_tab, scope, _refresh):
        if active_tab != "crm":
            return no_update
        params: Dict[str, Any] = {"scope": scope or "all"}
        response = make_api_request("GET", "/crm/customers/search", params)
        customers = response if isinstance(response, list) else []
        options = []
        for c in customers:
            label = f"{c.get('name', '')} ({c.get('code', '')})"
            if c.get("buying_group_name"):
                label += f" · {c['buying_group_name']}"
            options.append({"label": label, "value": c["id"]})
        return options

    @app.callback(
        [
            Output("crm-empty-state", "style"),
            Output("crm-workspace", "style"),
            Output("crm-customer-header", "children"),
            Output("crm-kpi-orders", "children"),
            Output("crm-kpi-revenue", "children"),
            Output("crm-kpi-units", "children"),
            Output("crm-kpi-skus", "children"),
            Output("crm-orders-table", "data"),
            Output("crm-sku-table", "data"),
            Output("crm-profile-buying-group", "value"),
            Output("crm-profile-relationship-status", "value"),
            Output("crm-profile-visit-days", "value"),
            Output("crm-profile-contact-method", "value"),
            Output("crm-rep-assignments", "children"),
            Output("crm-context-rep-id", "data"),
        ],
        [
            Input("crm-customer-select", "value"),
            Input("crm-customer-date-range", "start_date"),
            Input("crm-customer-date-range", "end_date"),
            Input("crm-refresh-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_customer_dashboard(customer_id, start_date, end_date, _refresh):
        if not customer_id:
            return (
                {"display": "block"},
                {"display": "none"},
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                [],
                [],
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                None,
            )
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        dashboard = make_api_request(
            "GET", f"/crm/customers/{customer_id}/dashboard", params
        )
        if isinstance(dashboard, dict) and dashboard.get("error"):
            return (
                {"display": "none"},
                {"display": "block"},
                dbc.Alert(dashboard["error"], color="danger"),
                "—",
                "—",
                "—",
                "—",
                [],
                [],
                None,
                None,
                None,
                None,
                "",
                None,
            )
        profile = dashboard.get("profile", {})
        sales = dashboard.get("sales_summary", {})
        header = dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4(profile.get("name", "Customer"), className="mb-1"),
                        html.P(
                            [
                                html.Span(
                                    profile.get("code", ""),
                                    className="text-muted me-2",
                                ),
                                html.Span(
                                    profile.get("buying_group_name")
                                    or "No buying group",
                                    className="badge bg-secondary me-2",
                                ),
                                html.Span(
                                    profile.get("customer_type") or "",
                                    className="badge bg-light text-dark",
                                ),
                            ],
                            className="mb-0",
                        ),
                    ],
                    md=8,
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.Small("Primary rep: ", className="text-muted"),
                            html.Strong(
                                (profile.get("primary_rep") or {}).get(
                                    "sales_rep_name", "—"
                                )
                            ),
                        ],
                        className="text-end",
                    ),
                    md=4,
                ),
            ],
            className="align-items-center",
        )
        orders_data = []
        for row in sales.get("orders", []):
            orders_data.append(
                {
                    **row,
                    "total_inc_gst": _fmt_money(row.get("total_inc_gst")),
                }
            )
        sku_data = []
        for row in sales.get("rows", []):
            sku_data.append(
                {
                    **row,
                    "total_qty": f"{float(row.get('total_qty', 0)):,.0f}",
                    "total_inc_gst": _fmt_money(row.get("total_inc_gst")),
                }
            )
        reps_resp = make_api_request("GET", f"/crm/customers/{customer_id}/reps")
        reps_rows = reps_resp if isinstance(reps_resp, list) else []
        rep_list = html.Ul(
            [
                html.Li(
                    f"{r.get('sales_rep_name', '—')} ({r.get('role', '')})",
                    className="small",
                )
                for r in reps_rows
            ]
            or [html.Li("No reps assigned", className="small text-muted")]
        )
        return (
            {"display": "none"},
            {"display": "block"},
            header,
            str(sales.get("order_count", 0)),
            _fmt_money(sales.get("total_inc_gst")),
            f"{float(sales.get('total_qty', 0)):,.0f}",
            str(len(sales.get("rows", []))),
            orders_data,
            sku_data,
            profile.get("buying_group_id"),
            profile.get("relationship_status") or "active",
            profile.get("visit_frequency_target_days"),
            profile.get("preferred_contact_method"),
            rep_list,
            (profile.get("primary_rep") or {}).get("sales_rep_id"),
        )

    @app.callback(
        Output("crm-timeline-list", "children"),
        [
            Input("crm-customer-select", "value"),
            Input("crm-customer-date-range", "start_date"),
            Input("crm-customer-date-range", "end_date"),
            Input("crm-refresh-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_timeline(customer_id, start_date, end_date, _refresh):
        if not customer_id:
            return []
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        response = make_api_request(
            "GET", f"/crm/customers/{customer_id}/timeline", params
        )
        if isinstance(response, dict) and response.get("error"):
            return dbc.Alert(response["error"], color="danger")
        items = response.get("items", []) if isinstance(response, dict) else []
        if not items:
            return dbc.Alert("No activity in this period.", color="light")
        return [_build_activity_feed_card(item) for item in items]

    @app.callback(
        Output("crm-note-datetime", "value"),
        Input("crm-customer-select", "value"),
        prevent_initial_call=False,
    )
    def default_note_datetime(customer_id):
        if not customer_id:
            return no_update
        return _now_local_datetime()

    @app.callback(
        [
            Output("crm-staff-edit-btn", "disabled"),
            Output("crm-staff-delete-btn", "disabled"),
        ],
        Input("crm-staff-table", "selected_rows"),
    )
    def toggle_staff_actions(selected_rows):
        disabled = not selected_rows
        return disabled, disabled

    @app.callback(
        [
            Output("crm-note-feedback", "children"),
            Output("crm-note-body", "value"),
            Output("crm-note-datetime", "value", allow_duplicate=True),
            Output("crm-note-photos", "contents"),
            Output("crm-note-photos-preview", "children"),
            Output("crm-refresh-store", "data", allow_duplicate=True),
        ],
        Input("crm-note-save", "n_clicks"),
        [
            State("crm-customer-select", "value"),
            State("crm-context-rep-id", "value"),
            State("crm-note-type", "value"),
            State("crm-note-category", "value"),
            State("crm-note-datetime", "value"),
            State("crm-note-body", "value"),
            State("crm-note-photos", "contents"),
            State("crm-refresh-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_note(
        n_clicks,
        customer_id,
        rep_id,
        note_type,
        category,
        note_datetime,
        body,
        photos,
        refresh,
    ):
        if not n_clicks:
            raise PreventUpdate
        if not customer_id:
            return (
                "Select a customer first.",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        text = (body or "").strip()
        if not text and not photos:
            return (
                "Enter note text or add photos.",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        payload: Dict[str, Any] = {
            "activity_type": note_type or "note",
            "note_category": category,
            "body": text or "(photo note)",
            "sales_rep_id": rep_id,
        }
        parsed = _parse_activity_at(note_datetime)
        if parsed:
            payload["activity_at"] = parsed
        response = make_api_request(
            "POST", f"/crm/customers/{customer_id}/activities", payload
        )
        if isinstance(response, dict) and response.get("error"):
            return (
                response["error"],
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        activity_id = response.get("id") if isinstance(response, dict) else None
        msg = "Note saved."
        if activity_id and photos:
            upload_err = _upload_note_photos(
                api_base_url, customer_id, activity_id, rep_id, photos
            )
            if upload_err:
                msg = f"Note saved. {upload_err}"
        return (
            msg,
            "",
            _now_local_datetime(),
            None,
            "",
            (refresh or 0) + 1,
        )

    @app.callback(
        [
            Output("crm-note-edit-modal", "is_open"),
            Output("crm-note-modal-title", "children"),
            Output("crm-note-edit-id", "data"),
            Output("crm-note-edit-type", "value"),
            Output("crm-note-edit-category", "value"),
            Output("crm-note-edit-datetime", "value"),
            Output("crm-note-edit-body", "value"),
        ],
        [
            Input({"type": "crm-act-edit", "index": ALL}, "n_clicks"),
            Input("crm-note-modal-cancel", "n_clicks"),
        ],
        [
            State({"type": "crm-act-edit", "index": ALL}, "id"),
            State("crm-customer-select", "value"),
        ],
        prevent_initial_call=True,
    )
    def open_activity_edit(edit_clicks, cancel_clicks, edit_ids, customer_id):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == "crm-note-modal-cancel":
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        if not customer_id or not edit_clicks or not edit_ids:
            raise PreventUpdate
        idx = next(
            (i for i, n in enumerate(edit_clicks) if n),
            None,
        )
        if idx is None:
            raise PreventUpdate
        activity_id = edit_ids[idx]["index"]
        row = _find_activity_row(customer_id, activity_id, make_api_request)
        if not row:
            raise PreventUpdate
        raw_when = row.get("activity_at", "")
        dt_val = (
            _parse_activity_at(
                str(raw_when).replace("Z", "")[:16].replace(" ", "T")
                if raw_when and "T" not in str(raw_when)
                else str(raw_when).replace("Z", "")[:16]
            )
            or _now_local_datetime()
        )
        return (
            True,
            "Edit activity",
            row.get("id"),
            row.get("activity_type") or "note",
            row.get("note_category") or "general",
            dt_val,
            row.get("body") or "",
        )

    @app.callback(
        [
            Output("crm-note-edit-modal", "is_open", allow_duplicate=True),
            Output("crm-note-feedback", "children", allow_duplicate=True),
            Output("crm-refresh-store", "data", allow_duplicate=True),
        ],
        Input("crm-note-modal-save", "n_clicks"),
        [
            State("crm-note-edit-id", "data"),
            State("crm-note-edit-type", "value"),
            State("crm-note-edit-category", "value"),
            State("crm-note-edit-datetime", "value"),
            State("crm-note-edit-body", "value"),
            State("crm-refresh-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_note_edit(
        n_clicks, note_id, note_type, category, note_datetime, body, refresh
    ):
        if not n_clicks or not note_id:
            raise PreventUpdate
        text = (body or "").strip()
        if not text:
            return True, "Enter note text.", no_update
        payload: Dict[str, Any] = {
            "activity_type": note_type or "note",
            "note_category": category,
            "body": text,
        }
        parsed = _parse_activity_at(note_datetime)
        if parsed:
            payload["activity_at"] = parsed
        response = make_api_request("PUT", f"/crm/activities/{note_id}", payload)
        if isinstance(response, dict) and response.get("error"):
            return True, response["error"], no_update
        return False, "Note updated.", (refresh or 0) + 1

    @app.callback(
        [
            Output("crm-note-feedback", "children", allow_duplicate=True),
            Output("crm-refresh-store", "data", allow_duplicate=True),
            Output("crm-cal-day-modal", "is_open", allow_duplicate=True),
        ],
        Input({"type": "crm-act-delete", "index": ALL}, "n_clicks"),
        [
            State({"type": "crm-act-delete", "index": ALL}, "id"),
            State("crm-refresh-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def delete_activity(delete_clicks, delete_ids, refresh):
        if not delete_clicks or not delete_ids:
            raise PreventUpdate
        idx = next((i for i, n in enumerate(delete_clicks) if n), None)
        if idx is None:
            raise PreventUpdate
        activity_id = delete_ids[idx]["index"]
        response = make_api_request("DELETE", f"/crm/activities/{activity_id}")
        err = _parse_api_error(response)
        if err:
            return err, no_update, no_update
        return "Activity deleted.", (refresh or 0) + 1, False

    @app.callback(
        [
            Output("crm-profile-feedback", "children"),
            Output("crm-refresh-store", "data", allow_duplicate=True),
        ],
        Input("crm-profile-save", "n_clicks"),
        [
            State("crm-customer-select", "value"),
            State("crm-profile-buying-group", "value"),
            State("crm-profile-relationship-status", "value"),
            State("crm-profile-visit-days", "value"),
            State("crm-profile-contact-method", "value"),
            State("crm-refresh-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_profile(
        n_clicks,
        customer_id,
        buying_group,
        relationship_status,
        visit_days,
        contact_method,
        refresh,
    ):
        if not n_clicks or not customer_id:
            raise PreventUpdate
        payload = {
            "buying_group_id": buying_group,
            "relationship_status": relationship_status or "active",
            "visit_frequency_target_days": visit_days,
            "preferred_contact_method": contact_method,
        }
        response = make_api_request(
            "PATCH", f"/crm/customers/{customer_id}/profile", payload
        )
        if isinstance(response, dict) and response.get("error"):
            return response["error"], no_update
        return "Profile saved.", (refresh or 0) + 1

    @app.callback(
        [
            Output("crm-profile-feedback", "children", allow_duplicate=True),
            Output("crm-refresh-store", "data", allow_duplicate=True),
        ],
        Input("crm-assign-submit", "n_clicks"),
        [
            State("crm-customer-select", "value"),
            State("crm-assign-rep", "value"),
            State("crm-assign-role", "value"),
            State("crm-refresh-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def assign_rep(n_clicks, customer_id, rep_id, role, refresh):
        if not n_clicks or not customer_id or not rep_id:
            raise PreventUpdate
        response = make_api_request(
            "POST",
            f"/crm/customers/{customer_id}/reps",
            {"sales_rep_id": rep_id, "role": role or "primary"},
        )
        if isinstance(response, dict) and response.get("error"):
            return response["error"], no_update
        return "Rep assigned.", (refresh or 0) + 1

    @app.callback(
        Output("crm-sites-table", "data"),
        [
            Input("crm-customer-select", "value"),
            Input("crm-refresh-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_sites(customer_id, _refresh):
        if not customer_id:
            return []
        response = make_api_request(
            "GET", "/sales/customer-sites", {"customer_id": customer_id}
        )
        sites = response if isinstance(response, list) else []
        return [
            {
                "site": s.get("site_name", ""),
                "state": s.get("state", ""),
                "suburb": s.get("suburb") or "—",
                "postcode": s.get("postcode") or "—",
            }
            for s in sites
        ]

    @app.callback(
        [
            Output("crm-add-site-feedback", "children"),
            Output("crm-add-site-name", "value"),
            Output("crm-add-site-state", "value"),
            Output("crm-add-site-suburb", "value"),
            Output("crm-add-site-postcode", "value"),
            Output("crm-refresh-store", "data", allow_duplicate=True),
        ],
        Input("crm-add-site-submit", "n_clicks"),
        [
            State("crm-customer-select", "value"),
            State("crm-add-site-name", "value"),
            State("crm-add-site-state", "value"),
            State("crm-add-site-suburb", "value"),
            State("crm-add-site-postcode", "value"),
            State("crm-refresh-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def add_site(n_clicks, customer_id, name, state, suburb, postcode, refresh):
        if not n_clicks:
            raise PreventUpdate
        if not customer_id:
            return (
                "Select a customer.",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        if not (name or "").strip():
            return (
                "Enter site name.",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        if not (state or "").strip():
            return "Enter state.", no_update, no_update, no_update, no_update, no_update
        payload = {
            "customer_id": customer_id,
            "site_name": name.strip(),
            "state": state.strip()[:8],
            "suburb": (suburb or "").strip() or None,
            "postcode": (postcode or "").strip() or None,
        }
        response = make_api_request("POST", "/sales/customer-sites", payload)
        if isinstance(response, dict) and response.get("error"):
            return (
                response["error"],
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        return "Site added.", "", "", "", "", (refresh or 0) + 1

    @app.callback(
        Output("crm-staff-table", "data"),
        [
            Input("crm-customer-select", "value"),
            Input("crm-refresh-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_staff(customer_id, _refresh):
        if not customer_id:
            return []
        response = make_api_request("GET", f"/crm/customers/{customer_id}/staff")
        staff = response if isinstance(response, list) else []
        return [
            {
                "id": s.get("id"),
                "name": s.get("name", ""),
                "role": s.get("role") or "—",
                "phone": s.get("phone") or "—",
                "email": s.get("email") or "—",
                "notes": _truncate_notes(s.get("notes")),
                "notes_raw": s.get("notes") or "",
                "is_primary": "Yes" if s.get("is_primary") else "",
            }
            for s in staff
        ]

    @app.callback(
        [
            Output("crm-staff-edit-modal", "is_open"),
            Output("crm-staff-edit-id", "data"),
            Output("crm-staff-edit-name", "value"),
            Output("crm-staff-edit-role", "value"),
            Output("crm-staff-edit-phone", "value"),
            Output("crm-staff-edit-email", "value"),
            Output("crm-staff-edit-primary", "value"),
            Output("crm-staff-edit-notes", "value"),
        ],
        [
            Input("crm-staff-edit-btn", "n_clicks"),
            Input("crm-staff-modal-cancel", "n_clicks"),
        ],
        [
            State("crm-staff-table", "selected_rows"),
            State("crm-staff-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def open_staff_modal(edit_clicks, cancel_clicks, selected_rows, data):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == "crm-staff-modal-cancel":
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        if trigger == "crm-staff-edit-btn" and selected_rows and data:
            row = data[selected_rows[0]]
            return (
                True,
                row.get("id"),
                row.get("name", ""),
                row.get("role") if row.get("role") != "—" else "",
                row.get("phone") if row.get("phone") != "—" else "",
                row.get("email") if row.get("email") != "—" else "",
                row.get("is_primary") == "Yes",
                row.get("notes_raw") or "",
            )
        raise PreventUpdate

    @app.callback(
        [
            Output("crm-staff-edit-modal", "is_open", allow_duplicate=True),
            Output("crm-add-staff-feedback", "children", allow_duplicate=True),
            Output("crm-refresh-store", "data", allow_duplicate=True),
        ],
        Input("crm-staff-modal-save", "n_clicks"),
        [
            State("crm-staff-edit-id", "data"),
            State("crm-staff-edit-name", "value"),
            State("crm-staff-edit-role", "value"),
            State("crm-staff-edit-phone", "value"),
            State("crm-staff-edit-email", "value"),
            State("crm-staff-edit-primary", "value"),
            State("crm-staff-edit-notes", "value"),
            State("crm-refresh-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_staff_edit(
        n_clicks, staff_id, name, role, phone, email, is_primary, notes, refresh
    ):
        if not n_clicks or not staff_id:
            raise PreventUpdate
        if not (name or "").strip():
            return True, "Name is required.", no_update
        payload = {
            "name": name.strip(),
            "role": (role or "").strip() or None,
            "phone": (phone or "").strip() or None,
            "email": (email or "").strip() or None,
            "notes": (notes or "").strip() or None,
            "is_primary": bool(is_primary),
        }
        response = make_api_request("PUT", f"/crm/staff/{staff_id}", payload)
        if isinstance(response, dict) and response.get("error"):
            return True, response["error"], no_update
        return False, "Staff updated.", (refresh or 0) + 1

    @app.callback(
        [
            Output("crm-add-staff-feedback", "children", allow_duplicate=True),
            Output("crm-refresh-store", "data", allow_duplicate=True),
        ],
        Input("crm-staff-delete-btn", "n_clicks"),
        [
            State("crm-staff-table", "selected_rows"),
            State("crm-staff-table", "data"),
            State("crm-refresh-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def delete_staff_member(n_clicks, selected_rows, data, refresh):
        if not n_clicks or not selected_rows or not data:
            raise PreventUpdate
        staff_id = data[selected_rows[0]].get("id")
        response = make_api_request("DELETE", f"/crm/staff/{staff_id}")
        if isinstance(response, dict) and response.get("error"):
            return response["error"], no_update
        return "Staff deleted.", (refresh or 0) + 1

    @app.callback(
        [
            Output("crm-add-staff-feedback", "children"),
            Output("crm-add-staff-name", "value"),
            Output("crm-add-staff-role", "value"),
            Output("crm-add-staff-phone", "value"),
            Output("crm-add-staff-email", "value"),
            Output("crm-add-staff-primary", "value"),
            Output("crm-add-staff-notes", "value"),
            Output("crm-refresh-store", "data", allow_duplicate=True),
        ],
        Input("crm-add-staff-submit", "n_clicks"),
        [
            State("crm-customer-select", "value"),
            State("crm-add-staff-name", "value"),
            State("crm-add-staff-role", "value"),
            State("crm-add-staff-phone", "value"),
            State("crm-add-staff-email", "value"),
            State("crm-add-staff-primary", "value"),
            State("crm-add-staff-notes", "value"),
            State("crm-refresh-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def add_staff(
        n_clicks, customer_id, name, role, phone, email, is_primary, notes, refresh
    ):
        if not n_clicks:
            raise PreventUpdate
        if not customer_id:
            return (
                "Select a customer.",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        if not (name or "").strip():
            return (
                "Enter name.",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        payload = {
            "name": name.strip(),
            "role": (role or "").strip() or None,
            "phone": (phone or "").strip() or None,
            "email": (email or "").strip() or None,
            "notes": (notes or "").strip() or None,
            "is_primary": bool(is_primary),
        }
        response = make_api_request(
            "POST", f"/crm/customers/{customer_id}/staff", payload
        )
        if isinstance(response, dict) and response.get("error"):
            return (
                response["error"],
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        return "Staff added.", "", "", "", "", False, "", (refresh or 0) + 1

    @app.callback(
        Output("crm-note-photos-preview", "children", allow_duplicate=True),
        Input("crm-note-photos", "contents"),
        prevent_initial_call=True,
    )
    def preview_note_photos(contents):
        if not contents:
            return ""
        names = [c.get("filename", "photo") for c in contents]
        return html.Span(
            f"{len(names)} photo(s): " + ", ".join(names),
            className="text-muted",
        )

    @app.callback(
        Output("crm-schedule-datetime", "value"),
        Input("crm-customer-select", "value"),
        prevent_initial_call=False,
    )
    def default_schedule_datetime(customer_id):
        if not customer_id:
            return no_update
        return _future_local_datetime(7)

    @app.callback(
        [
            Output("crm-schedule-feedback", "children"),
            Output("crm-schedule-title", "value"),
            Output("crm-schedule-body", "value"),
            Output("crm-schedule-datetime", "value", allow_duplicate=True),
            Output("crm-refresh-store", "data", allow_duplicate=True),
        ],
        Input("crm-schedule-save", "n_clicks"),
        [
            State("crm-customer-select", "value"),
            State("crm-context-rep-id", "value"),
            State("crm-schedule-type", "value"),
            State("crm-schedule-title", "value"),
            State("crm-schedule-datetime", "value"),
            State("crm-schedule-body", "value"),
            State("crm-refresh-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_scheduled(
        n_clicks,
        customer_id,
        rep_id,
        sched_type,
        title,
        sched_datetime,
        body,
        refresh,
    ):
        if not n_clicks:
            raise PreventUpdate
        if not customer_id:
            return "Select a customer.", no_update, no_update, no_update, no_update
        if not rep_id:
            return (
                "Assign a primary sales rep to this customer (Profile tab) "
                "or select a rep on the Sales Rep tab.",
                no_update,
                no_update,
                no_update,
                no_update,
            )
        title_text = (title or "").strip()
        if not title_text:
            return "Enter a title.", no_update, no_update, no_update, no_update
        when = _parse_activity_at(sched_datetime)
        if not when:
            return "Enter date and time.", no_update, no_update, no_update, no_update
        payload = {
            "activity_type": sched_type or "visit",
            "title": title_text,
            "description": (body or "").strip() or None,
            "scheduled_at": when,
            "sales_rep_id": rep_id,
        }
        response = make_api_request(
            "POST", f"/crm/customers/{customer_id}/scheduled", payload
        )
        if isinstance(response, dict) and response.get("error"):
            return response["error"], no_update, no_update, no_update, no_update
        return (
            "Follow-up scheduled.",
            "",
            "",
            _future_local_datetime(7),
            (refresh or 0) + 1,
        )

    @app.callback(
        Output("crm-scheduled-list", "children"),
        [
            Input("crm-customer-select", "value"),
            Input("crm-refresh-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_scheduled_list(customer_id, _refresh):
        if not customer_id:
            return dbc.Alert("Select a customer.", color="light")
        rows = make_api_request("GET", f"/crm/customers/{customer_id}/scheduled")
        items = rows if isinstance(rows, list) else []
        if not items:
            return dbc.Alert("No upcoming scheduled activities.", color="light")
        cards = []
        for row in items:
            when = _format_activity_at(row.get("scheduled_at"))
            cards.append(
                dbc.ListGroupItem(
                    [
                        html.Div(
                            [
                                dbc.Badge(
                                    row.get("activity_type", ""), className="me-2"
                                ),
                                html.Strong(row.get("title", "")),
                            ]
                        ),
                        html.Small(
                            f"{when} · {row.get('status', '')}", className="text-muted"
                        ),
                        html.P(row.get("description") or "", className="mb-0 small"),
                    ]
                )
            )
        return dbc.ListGroup(cards, flush=True)

    @app.callback(
        [
            Output("crm-suggestions-panel", "children"),
            Output("crm-profile-suggestions", "children"),
        ],
        [
            Input("crm-customer-select", "value"),
            Input("crm-refresh-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_suggestions(customer_id, _refresh):
        if not customer_id:
            return "", ""
        data = make_api_request("GET", f"/crm/customers/{customer_id}/suggestions")
        alert = _suggestion_alert(data if isinstance(data, dict) else {})
        if alert is no_update:
            return "", ""
        return alert, alert

    @app.callback(
        Output("crm-calendar-month", "data"),
        [
            Input("crm-customer-select", "value"),
            Input("crm-cal-prev", "n_clicks"),
            Input("crm-cal-next", "n_clicks"),
        ],
        State("crm-calendar-month", "data"),
        prevent_initial_call=False,
    )
    def navigate_calendar(customer_id, prev_clicks, next_clicks, month_key):
        ctx = dash.callback_context
        if not month_key:
            month_key = date.today().strftime("%Y-%m")
        if not ctx.triggered:
            return month_key
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == "crm-customer-select":
            return date.today().strftime("%Y-%m")
        if trigger == "crm-cal-prev":
            return shift_month(month_key, -1)
        if trigger == "crm-cal-next":
            return shift_month(month_key, 1)
        return month_key

    @app.callback(
        [
            Output("crm-cal-title", "children"),
            Output("crm-calendar-grid", "children"),
            Output("crm-cal-events-store", "data"),
        ],
        [
            Input("crm-customer-select", "value"),
            Input("crm-calendar-month", "data"),
            Input("crm-refresh-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_calendar(customer_id, month_key, _refresh):
        if not customer_id:
            return "—", dbc.Alert("Select a customer.", color="light"), []
        month_key = month_key or date.today().strftime("%Y-%m")
        start, end = three_month_date_range(month_key)
        events = make_api_request(
            "GET",
            f"/crm/customers/{customer_id}/calendar-events",
            {"start_date": start, "end_date": end},
        )
        event_list = events if isinstance(events, list) else []
        return (
            three_month_title(month_key),
            build_three_month_calendars(month_key, event_list),
            event_list,
        )

    @app.callback(
        [
            Output("crm-cal-day-modal", "is_open"),
            Output("crm-cal-day-modal-title", "children"),
            Output("crm-cal-day-modal-body", "children"),
        ],
        [
            Input("crm-cal-selected-day", "data"),
            Input("crm-cal-day-modal-close", "n_clicks"),
            Input("crm-refresh-store", "data"),
        ],
        [
            State("crm-cal-events-store", "data"),
            State("crm-cal-day-modal", "is_open"),
            State("crm-cal-selected-day", "data"),
        ],
        prevent_initial_call=True,
    )
    def show_day_events_modal(
        selected, close_clicks, _refresh, events, is_open, selected_day
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == "crm-cal-day-modal-close":
            return False, no_update, no_update
        date_str = None
        day_pick = selected if trigger == "crm-cal-selected-day" else selected_day
        if day_pick and isinstance(day_pick, dict):
            date_str = day_pick.get("date")
        if not date_str:
            raise PreventUpdate
        event_list = events if isinstance(events, list) else []
        day_events = _events_for_day(event_list, date_str)
        open_modal = trigger == "crm-cal-selected-day" or (
            trigger == "crm-refresh-store" and is_open
        )
        if trigger == "crm-refresh-store" and not is_open:
            raise PreventUpdate
        return (
            open_modal,
            _format_day_heading(date_str),
            _build_day_events_body(day_events),
        )

    @app.callback(
        [
            Output("crm-export-download", "data"),
            Output("crm-export-feedback", "children"),
        ],
        Input("crm-export-btn", "n_clicks"),
        [
            State("crm-customer-select", "value"),
            State("crm-export-sections", "value"),
            State("crm-customer-date-range", "start_date"),
            State("crm-customer-date-range", "end_date"),
        ],
        prevent_initial_call=True,
    )
    def export_crm_pdf(n_clicks, customer_id, sections, start_date, end_date):
        if not n_clicks:
            raise PreventUpdate
        if not customer_id:
            return no_update, dbc.Alert(
                "Select a customer before exporting.",
                color="warning",
                className="mb-0 py-1",
            )
        section_list = sections or ["all"]
        if "all" in section_list:
            section_list = ["all"]
        payload = {
            "sections": section_list,
            "start_date": start_date,
            "end_date": end_date,
        }
        gen = make_api_request(
            "POST", f"/crm/customers/{customer_id}/export-pdf", payload
        )
        err = _parse_api_error(gen)
        if err:
            return no_update, dbc.Alert(
                f"Export failed: {err}",
                color="danger",
                className="mb-0 py-1",
            )
        doc_id = gen.get("document_id") if isinstance(gen, dict) else None
        if not doc_id:
            return no_update, dbc.Alert(
                "Export failed: no document returned.",
                color="danger",
                className="mb-0 py-1",
            )
        try:
            resp = requests.get(
                f"{api_base_url}/api/v1/documents/{doc_id}/download", timeout=60
            )
            if resp.status_code == 200:
                filename = f"crm_summary_{customer_id[:8]}.pdf"
                return (
                    dict(
                        content=base64.b64encode(resp.content).decode(),
                        filename=filename,
                        base64=True,
                    ),
                    dbc.Alert(
                        [
                            "PDF downloaded. A copy is saved in ",
                            html.Code("generated/"),
                            f" on the server (e.g. {filename}).",
                        ],
                        color="success",
                        className="mb-0 py-1",
                    ),
                )
            return no_update, dbc.Alert(
                f"Download failed (HTTP {resp.status_code}). "
                "Check API logs — the PDF may still be in generated/.",
                color="danger",
                className="mb-0 py-1",
            )
        except Exception as exc:
            return no_update, dbc.Alert(
                f"Download error: {exc}",
                color="danger",
                className="mb-0 py-1",
            )

    @app.callback(
        [
            Output("crm-rep-empty-state", "style"),
            Output("crm-rep-workspace", "style"),
            Output("crm-rep-header", "children"),
            Output("crm-rep-kpi-customers", "children"),
            Output("crm-rep-kpi-orders", "children"),
            Output("crm-rep-kpi-revenue", "children"),
            Output("crm-rep-kpi-units", "children"),
            Output("crm-rep-customers-table", "data"),
            Output("crm-rep-orders-table", "data"),
        ],
        [
            Input("crm-rep-select", "value"),
            Input("crm-rep-date-range", "start_date"),
            Input("crm-rep-date-range", "end_date"),
            Input("crm-refresh-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_rep_dashboard(rep_id, start_date, end_date, _refresh):
        if not rep_id:
            return (
                {"display": "block"},
                {"display": "none"},
                no_update,
                "—",
                "—",
                "—",
                "—",
                [],
                [],
            )
        params: Dict[str, Any] = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        data = make_api_request("GET", f"/crm/reps/{rep_id}/dashboard", params)
        if isinstance(data, dict) and data.get("error"):
            return (
                {"display": "none"},
                {"display": "block"},
                dbc.Alert(data["error"], color="danger"),
                "—",
                "—",
                "—",
                "—",
                [],
                [],
            )
        header = html.Div(
            [
                html.H4(data.get("rep_name", "Sales rep"), className="mb-1"),
                html.P(
                    f"Code: {data.get('rep_code', '—')}",
                    className="text-muted mb-0",
                ),
            ]
        )
        customers = []
        for row in data.get("customers", []):
            customers.append(
                {
                    **row,
                    "total_inc_gst": _fmt_money(row.get("total_inc_gst")),
                }
            )
        orders = []
        for row in data.get("orders", []):
            orders.append(
                {
                    **row,
                    "total_inc_gst": _fmt_money(row.get("total_inc_gst")),
                }
            )
        return (
            {"display": "none"},
            {"display": "block"},
            header,
            str(data.get("customer_count", 0)),
            str(data.get("order_count", 0)),
            _fmt_money(data.get("total_revenue_inc_gst")),
            f"{float(data.get('total_units', 0)):,.0f}",
            customers,
            orders,
        )

    @app.callback(
        Output("crm-rep-calendar-month", "data"),
        [
            Input("crm-rep-select", "value"),
            Input("crm-rep-date-range", "start_date"),
            Input("crm-rep-cal-prev", "n_clicks"),
            Input("crm-rep-cal-next", "n_clicks"),
        ],
        State("crm-rep-calendar-month", "data"),
        prevent_initial_call=False,
    )
    def navigate_rep_calendar(rep_id, start_date, _prev, _next, month_key):
        ctx = dash.callback_context
        if not month_key:
            month_key = date.today().strftime("%Y-%m")
        if not ctx.triggered:
            if start_date and len(start_date) >= 7:
                return start_date[:7]
            return month_key
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == "crm-rep-select":
            if start_date and len(start_date) >= 7:
                return start_date[:7]
            return date.today().strftime("%Y-%m")
        if trigger == "crm-rep-date-range":
            if start_date and len(start_date) >= 7:
                return start_date[:7]
            return month_key
        if trigger == "crm-rep-cal-prev":
            return shift_month(month_key, -1)
        if trigger == "crm-rep-cal-next":
            return shift_month(month_key, 1)
        return month_key

    @app.callback(
        [
            Output("crm-rep-cal-title", "children"),
            Output("crm-rep-calendar-grid", "children"),
            Output("crm-rep-cal-events-store", "data"),
        ],
        [
            Input("crm-rep-select", "value"),
            Input("crm-rep-date-range", "start_date"),
            Input("crm-rep-date-range", "end_date"),
            Input("crm-rep-calendar-month", "data"),
            Input("crm-refresh-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_rep_calendar(rep_id, start_date, end_date, month_key, _refresh):
        if not rep_id:
            return "—", dbc.Alert("Select a sales rep.", color="light"), []
        month_key = month_key or date.today().strftime("%Y-%m")
        cal_start, cal_end = three_month_date_range(month_key)
        range_start = start_date or cal_start
        range_end = end_date or cal_end
        if range_start > cal_start:
            cal_start = range_start
        if range_end < cal_end:
            cal_end = range_end
        events = make_api_request(
            "GET",
            f"/crm/reps/{rep_id}/calendar-events",
            {"start_date": cal_start, "end_date": cal_end},
        )
        event_list = events if isinstance(events, list) else []
        return (
            three_month_title(month_key),
            build_three_month_calendars(month_key, event_list),
            event_list,
        )
