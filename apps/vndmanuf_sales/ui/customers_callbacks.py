"""Dash callbacks for Sales Customers sub-tab."""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from dash import Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _format_currency(value: Any) -> str:
    try:
        return f"${Decimal(str(value)).quantize(Decimal('0.01')):,}"
    except Exception:
        return "$0.00"


def _format_customer_type(value: Optional[str]) -> str:
    if not value:
        return "—"
    return value.replace("_", " ").title()


def _format_last_order(
    last_order_date: Optional[str], days_since: Optional[int]
) -> str:
    if not last_order_date:
        return "—"
    try:
        dt = datetime.fromisoformat(last_order_date)
        label = dt.strftime("%d %b %Y")
    except (TypeError, ValueError):
        label = str(last_order_date)
    if days_since is not None:
        day_word = "day" if days_since == 1 else "days"
        return f"{label} ({days_since} {day_word} ago)"
    return label


def _format_pricing_level(value: Optional[str]) -> str:
    if not value:
        return "—"
    return value.replace("_", " ").title()


def _resolve_display_name(*candidates: Optional[str]) -> str:
    for candidate in candidates:
        if not candidate:
            continue
        label = str(candidate).strip()
        if label and not _UUID_RE.match(label):
            return label
    return "Customer"


def _customer_modal_title(*name_candidates: Optional[str]) -> str:
    return f"Customer — {_resolve_display_name(*name_candidates)}"


def _special_price_rows(items: list, *, include_meta: bool = False) -> list:
    rows = []
    for item in items or []:
        end = item.get("expiry_date")
        end_raw = None
        if end and isinstance(end, str) and len(end) >= 10:
            end_raw = end[:10]
            end = end_raw
        elif end and hasattr(end, "strftime"):
            end_raw = end.strftime("%Y-%m-%d")
            end = end_raw
        else:
            end = "Ongoing" if not end else str(end)
        start = item.get("effective_date")
        start_raw = None
        if start and isinstance(start, str) and len(start) >= 10:
            start_raw = start[:10]
            start = start_raw
        elif start and hasattr(start, "strftime"):
            start_raw = start.strftime("%Y-%m-%d")
            start = start_raw
        else:
            start = "—"
        sku = item.get("product_sku") or ""
        name = item.get("product_name") or ""
        product_label = f"{sku} – {name}".strip(" –") or item.get("product_id", "")
        row = {
            "customer": item.get("customer_name") or "—",
            "product": product_label,
            "price_ex": _format_currency(item.get("unit_price_ex_gst")),
            "start_date": start,
            "end_date": end,
            "active": "Yes" if item.get("is_active") else "—",
            "notes": item.get("notes") or "—",
        }
        if include_meta:
            row["special_price_id"] = item.get("id")
            row["product_id"] = item.get("product_id")
            row["unit_price_ex_raw"] = item.get("unit_price_ex_gst")
            row["start_date_raw"] = start_raw
            row["end_date_raw"] = end_raw
        rows.append(row)
    return rows


def _tier_price_cell(tier_value: Any, special_value: Any) -> str:
    tier = _format_currency(tier_value)
    if special_value is None:
        return tier
    return f"{tier} **{_format_currency(special_value)}**"


def _sites_table_rows(sites: list) -> list:
    return [
        {
            "site_id": s.get("id"),
            "site": s.get("site_name", ""),
            "state": s.get("state", ""),
            "suburb": s.get("suburb") or "—",
            "postcode": s.get("postcode") or "—",
        }
        for s in sites
    ]


def register_sales_customers_callbacks(app, make_api_request):
    """Register callbacks for Customers: KPIs, table, customer modal, global offers."""

    @app.callback(
        [
            Output("sales-customers-total", "children"),
            Output("sales-customers-new", "children"),
            Output("sales-customers-lifetime", "children"),
            Output("sales-customers-last-order", "children"),
            Output("sales-customers-table", "data"),
        ],
        [
            Input("sales-subtabs", "value"),
            Input("sales-customers-dashboard-refresh", "data"),
            Input("sales-customer-pricing-refresh", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_customers_dashboard(subtab_value, _dash_refresh, _pricing_refresh):
        if subtab_value != "sales-customers":
            return (no_update,) * 5

        dashboard = make_api_request("GET", "/sales/customers/dashboard")
        if isinstance(dashboard, dict) and dashboard.get("error"):
            return ("—", "—", "—", "—", [])

        summary = dashboard.get("summary", {}) if isinstance(dashboard, dict) else {}
        customers = (
            dashboard.get("customers", []) if isinstance(dashboard, dict) else []
        )

        active = summary.get("active_customers", 0)
        new_month = summary.get("new_this_month", 0)
        avg_ltv = _format_currency(summary.get("avg_lifetime_value", 0))

        days_since = summary.get("days_since_last_order")
        if days_since is None:
            last_order_kpi = "—"
        elif days_since == 0:
            last_order_kpi = "Today"
        elif days_since == 1:
            last_order_kpi = "1 day"
        else:
            last_order_kpi = f"{days_since} days"

        customers_table_data = [
            {
                "customer_id": c.get("id"),
                "customer": c.get("name", ""),
                "type": _format_customer_type(c.get("customer_type")),
                "pricing_level": _format_pricing_level(c.get("default_pricing_level")),
                "active_specials": int(c.get("active_special_prices") or 0),
                "email": c.get("email") or "—",
                "phone": c.get("phone") or "—",
                "orders": c.get("order_count", 0),
                "revenue": _format_currency(c.get("revenue_inc_gst", 0)),
                "last_order": _format_last_order(
                    c.get("last_order_date"), c.get("days_since_last_order")
                ),
            }
            for c in customers
        ]

        return (
            str(active),
            str(new_month),
            avg_ltv,
            last_order_kpi,
            customers_table_data,
        )

    @app.callback(
        [
            Output("sales-open-customer-id", "data"),
            Output("sales-open-customer-name", "data"),
            Output("sales-customer-detail-modal", "is_open"),
        ],
        Input("sales-customers-open-selected", "n_clicks"),
        [
            State("sales-customers-table", "data"),
            State("sales-customers-table", "selected_rows"),
        ],
        prevent_initial_call=True,
    )
    def open_customer_modal(open_clicks, table_data, selected_rows):
        if not open_clicks or not table_data or not selected_rows:
            raise PreventUpdate
        idx = selected_rows[0]
        if 0 <= idx < len(table_data) and table_data[idx].get("customer_id"):
            row = table_data[idx]
            return row["customer_id"], row.get("customer"), True
        raise PreventUpdate

    @app.callback(
        [
            Output("sales-customer-detail-modal", "is_open", allow_duplicate=True),
            Output("sales-open-customer-id", "data", allow_duplicate=True),
            Output("sales-open-customer-name", "data", allow_duplicate=True),
        ],
        Input("sales-customer-detail-close", "n_clicks"),
        prevent_initial_call=True,
    )
    def close_customer_modal(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return False, None, None

    @app.callback(
        [
            Output("sales-customer-detail-title", "children"),
            Output("sales-pricing-level", "value"),
            Output("sales-customer-special-prices-table", "data"),
            Output("sales-customer-sites-table", "data"),
            Output("sales-customer-site-name", "value"),
            Output("sales-customer-site-state", "value"),
            Output("sales-customer-site-suburb", "value"),
            Output("sales-customer-site-postcode", "value"),
            Output("sales-customer-site-edit-id", "data"),
            Output("sales-customer-sites-table", "selected_rows"),
            Output("sales-special-price-product", "value", allow_duplicate=True),
            Output("sales-special-price-amount", "value", allow_duplicate=True),
            Output("sales-special-price-basis", "value", allow_duplicate=True),
            Output("sales-special-price-start", "date", allow_duplicate=True),
            Output("sales-special-price-end", "date", allow_duplicate=True),
            Output("sales-special-price-notes", "value", allow_duplicate=True),
            Output("sales-special-price-edit-id", "data", allow_duplicate=True),
            Output(
                "sales-customer-special-prices-table",
                "selected_rows",
                allow_duplicate=True,
            ),
        ],
        [
            Input("sales-open-customer-id", "data"),
            Input("sales-customer-pricing-refresh", "data"),
        ],
        State("sales-open-customer-name", "data"),
        prevent_initial_call="initial_duplicate",
    )
    def load_customer_modal(customer_id, _refresh, stored_name):
        empty_site = ("", "", "", "", None, [])
        empty_special = (None, None, "ex", None, None, "", None, [])
        if not customer_id:
            return (
                _customer_modal_title(stored_name),
                None,
                [],
                [],
                *empty_site,
                *empty_special,
            )

        pricing = make_api_request("GET", f"/sales/customers/{customer_id}/pricing")
        sites = make_api_request(
            "GET", "/sales/customer-sites", {"customer_id": customer_id}
        )
        if isinstance(pricing, dict) and pricing.get("error"):
            return (
                _customer_modal_title(stored_name, customer_id),
                None,
                [],
                [],
                *empty_site,
                *empty_special,
            )

        title = _customer_modal_title(pricing.get("customer_name"), stored_name)
        price_rows = _special_price_rows(
            pricing.get("special_prices") or [], include_meta=True
        )
        for r in price_rows:
            r.pop("customer", None)
        site_rows = _sites_table_rows(sites if isinstance(sites, list) else [])

        return (
            title,
            pricing.get("default_pricing_level"),
            price_rows,
            site_rows,
            "",
            "",
            "",
            "",
            None,
            [],
            None,
            None,
            "ex",
            None,
            None,
            "",
            None,
            [],
        )

    @app.callback(
        [
            Output("sales-special-price-product", "options"),
            Output("sales-global-special-product-filter", "options"),
        ],
        Input("sales-subtabs", "value"),
        prevent_initial_call=False,
    )
    def load_pricing_product_options(subtab_value):
        if subtab_value != "sales-customers":
            raise PreventUpdate
        products_response = make_api_request(
            "GET", "/products/", {"is_sell": True, "limit": 1000}
        )
        products = products_response if isinstance(products_response, list) else []
        options = [
            {
                "label": f"{p.get('sku', '')} – {p.get('name', '')}".strip(" –"),
                "value": p["id"],
            }
            for p in products
        ]
        return options, options

    @app.callback(
        [
            Output("sales-customer-tier-prices-section", "style"),
            Output("sales-customer-tier-prices-heading", "children"),
            Output("sales-customer-tier-prices-table", "data"),
        ],
        [
            Input("sales-pricing-level", "value"),
            Input("sales-open-customer-id", "data"),
            Input("sales-customer-pricing-refresh", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_tier_prices_table(pricing_level, customer_id, _refresh):
        if not customer_id or not pricing_level:
            return {"display": "none"}, "", []

        level_label = _format_pricing_level(pricing_level)
        heading = f"{level_label} tier prices"
        params = {"pricing_level": pricing_level, "customer_id": customer_id}
        catalog = make_api_request("GET", "/sales/pricing/tier-catalog", params)
        if isinstance(catalog, dict) and catalog.get("error"):
            return {"display": "block"}, heading, []

        rows = []
        for item in catalog if isinstance(catalog, list) else []:
            tier_ex = item.get("unit_price_ex_gst")
            tier_inc = item.get("unit_price_inc_gst")
            special_ex = item.get("special_price_ex_gst")
            special_inc = item.get("special_price_inc_gst")
            if item.get("has_active_special"):
                price_ex = _tier_price_cell(tier_ex, special_ex)
                price_inc = _tier_price_cell(tier_inc, special_inc)
            else:
                price_ex = _format_currency(tier_ex)
                price_inc = _format_currency(tier_inc)
            rows.append(
                {
                    "product": item.get("product") or "—",
                    "price_ex": price_ex,
                    "price_inc": price_inc,
                }
            )
        return {"display": "block"}, heading, rows

    @app.callback(
        Output("sales-special-price-amount", "placeholder"),
        Input("sales-special-price-basis", "value"),
        prevent_initial_call=False,
    )
    def special_price_amount_placeholder(basis):
        return "Unit inc GST" if basis == "inc" else "Unit ex GST"

    @app.callback(
        [
            Output("sales-pricing-level-feedback", "children", allow_duplicate=True),
            Output("sales-customer-pricing-refresh", "data", allow_duplicate=True),
            Output("sales-customers-dashboard-refresh", "data", allow_duplicate=True),
        ],
        Input("sales-pricing-level-save", "n_clicks"),
        [
            State("sales-open-customer-id", "data"),
            State("sales-pricing-level", "value"),
            State("sales-customer-pricing-refresh", "data"),
            State("sales-customers-dashboard-refresh", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_pricing_level(n_clicks, customer_id, level, refresh, dash_refresh):
        if not n_clicks:
            raise PreventUpdate
        if not customer_id:
            return "No customer selected.", no_update, no_update
        response = make_api_request(
            "PUT",
            f"/sales/customers/{customer_id}/pricing-level",
            {"default_pricing_level": level},
        )
        if isinstance(response, dict) and response.get("error"):
            return response["error"], no_update, no_update
        return (
            "Pricing level saved.",
            (refresh or 0) + 1,
            (dash_refresh or 0) + 1,
        )

    @app.callback(
        [
            Output("sales-special-price-feedback", "children", allow_duplicate=True),
            Output("sales-customer-pricing-refresh", "data", allow_duplicate=True),
        ],
        [
            Input("sales-special-price-save", "n_clicks"),
            Input("sales-special-price-delete", "n_clicks"),
        ],
        [
            State("sales-open-customer-id", "data"),
            State("sales-special-price-edit-id", "data"),
            State("sales-special-price-product", "value"),
            State("sales-special-price-basis", "value"),
            State("sales-special-price-amount", "value"),
            State("sales-special-price-start", "date"),
            State("sales-special-price-end", "date"),
            State("sales-special-price-notes", "value"),
            State("sales-customer-special-prices-table", "data"),
            State("sales-customer-special-prices-table", "selected_rows"),
            State("sales-customer-pricing-refresh", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_or_delete_special_price(
        save_clicks,
        delete_clicks,
        customer_id,
        edit_id,
        product_id,
        price_basis,
        price_amount,
        start_date,
        end_date,
        notes,
        table_data,
        selected_rows,
        refresh,
    ):
        if not callback_context.triggered or not customer_id:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"]
        new_refresh = (refresh or 0) + 1

        if "sales-special-price-delete" in trigger:
            if not (delete_clicks or 0) >= 1:
                raise PreventUpdate
            price_id = edit_id
            if not price_id and selected_rows and table_data:
                idx = selected_rows[0]
                if 0 <= idx < len(table_data):
                    price_id = table_data[idx].get("special_price_id")
            if not price_id:
                return "Select a special price to delete.", no_update
            response = make_api_request(
                "DELETE",
                f"/sales/customers/{customer_id}/special-prices/{price_id}",
            )
            if isinstance(response, dict) and response.get("error"):
                return response["error"], no_update
            return "Special price deleted.", new_refresh

        if not (save_clicks or 0) >= 1:
            raise PreventUpdate
        if not product_id or price_amount is None or not start_date:
            return "Product, unit price, and start date are required.", no_update

        price_field = (
            "unit_price_inc_gst"
            if (price_basis or "ex") == "inc"
            else "unit_price_ex_gst"
        )
        payload = {
            price_field: float(price_amount),
            "effective_date": f"{start_date}T00:00:00",
            "notes": (notes or "").strip() or None,
        }
        if end_date:
            payload["expiry_date"] = f"{end_date}T23:59:59"
        elif edit_id:
            payload["expiry_date"] = None

        if edit_id:
            response = make_api_request(
                "PUT",
                f"/sales/customers/{customer_id}/special-prices/{edit_id}",
                payload,
            )
            msg = "Special price updated."
        else:
            payload["product_id"] = product_id
            response = make_api_request(
                "POST",
                f"/sales/customers/{customer_id}/special-prices",
                payload,
            )
            msg = "Special price added."
        if isinstance(response, dict) and response.get("error"):
            return response["error"], no_update
        return msg, new_refresh

    @app.callback(
        [
            Output("sales-special-price-product", "value", allow_duplicate=True),
            Output("sales-special-price-amount", "value", allow_duplicate=True),
            Output("sales-special-price-basis", "value", allow_duplicate=True),
            Output("sales-special-price-start", "date", allow_duplicate=True),
            Output("sales-special-price-end", "date", allow_duplicate=True),
            Output("sales-special-price-notes", "value", allow_duplicate=True),
            Output("sales-special-price-edit-id", "data", allow_duplicate=True),
            Output(
                "sales-customer-special-prices-table",
                "selected_rows",
                allow_duplicate=True,
            ),
        ],
        Input("sales-special-price-new", "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_special_price_form(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return None, None, "ex", None, None, "", None, []

    @app.callback(
        [
            Output("sales-special-price-product", "value", allow_duplicate=True),
            Output("sales-special-price-amount", "value", allow_duplicate=True),
            Output("sales-special-price-basis", "value", allow_duplicate=True),
            Output("sales-special-price-start", "date", allow_duplicate=True),
            Output("sales-special-price-end", "date", allow_duplicate=True),
            Output("sales-special-price-notes", "value", allow_duplicate=True),
            Output("sales-special-price-edit-id", "data", allow_duplicate=True),
        ],
        Input("sales-customer-special-prices-table", "selected_rows"),
        State("sales-customer-special-prices-table", "data"),
        prevent_initial_call=True,
    )
    def load_special_price_into_form(selected_rows, table_data):
        if not selected_rows or not table_data:
            raise PreventUpdate
        idx = selected_rows[0]
        if idx < 0 or idx >= len(table_data):
            raise PreventUpdate
        row = table_data[idx]
        end_raw = row.get("end_date_raw")
        return (
            row.get("product_id"),
            row.get("unit_price_ex_raw"),
            "ex",
            row.get("start_date_raw"),
            end_raw,
            "" if (row.get("notes") or "—") == "—" else row.get("notes"),
            row.get("special_price_id"),
        )

    @app.callback(
        Output("sales-special-price-product", "disabled"),
        Input("sales-special-price-edit-id", "data"),
        prevent_initial_call=False,
    )
    def lock_special_price_product_on_edit(edit_id):
        return bool(edit_id)

    @app.callback(
        Output("sales-global-special-prices-table", "data"),
        [
            Input("sales-subtabs", "value"),
            Input("sales-global-special-refresh", "n_clicks"),
            Input("sales-global-special-product-filter", "value"),
            Input("sales-global-special-active-only", "value"),
            Input("sales-customer-pricing-refresh", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_global_special_prices(
        subtab_value, _refresh_btn, product_filter, active_only, _pricing_refresh
    ):
        if subtab_value != "sales-customers":
            raise PreventUpdate
        params = {}
        if product_filter:
            params["product_id"] = product_filter
        if active_only and "active" in active_only:
            params["active_only"] = True
        response = make_api_request("GET", "/sales/special-prices", params or None)
        if not isinstance(response, list):
            return []
        return _special_price_rows(response)

    @app.callback(
        [
            Output("sales-customer-site-name", "value", allow_duplicate=True),
            Output("sales-customer-site-state", "value", allow_duplicate=True),
            Output("sales-customer-site-suburb", "value", allow_duplicate=True),
            Output("sales-customer-site-postcode", "value", allow_duplicate=True),
            Output("sales-customer-site-edit-id", "data", allow_duplicate=True),
            Output("sales-customer-sites-table", "selected_rows", allow_duplicate=True),
        ],
        Input("sales-customer-site-new", "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_site_form(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return "", "", "", "", None, []

    @app.callback(
        [
            Output("sales-customer-site-name", "value", allow_duplicate=True),
            Output("sales-customer-site-state", "value", allow_duplicate=True),
            Output("sales-customer-site-suburb", "value", allow_duplicate=True),
            Output("sales-customer-site-postcode", "value", allow_duplicate=True),
            Output("sales-customer-site-edit-id", "data", allow_duplicate=True),
        ],
        Input("sales-customer-sites-table", "selected_rows"),
        State("sales-customer-sites-table", "data"),
        prevent_initial_call=True,
    )
    def load_site_into_form(selected_rows, table_data):
        if not selected_rows or not table_data:
            return "", "", "", "", None
        idx = selected_rows[0]
        if idx < 0 or idx >= len(table_data):
            raise PreventUpdate
        row = table_data[idx]
        suburb = row.get("suburb")
        if suburb == "—":
            suburb = ""
        postcode = row.get("postcode")
        if postcode == "—":
            postcode = ""
        return (
            row.get("site") or "",
            row.get("state") or "",
            suburb,
            postcode,
            row.get("site_id"),
        )

    @app.callback(
        [
            Output("sales-customer-site-feedback", "children", allow_duplicate=True),
            Output("sales-customer-pricing-refresh", "data", allow_duplicate=True),
        ],
        [
            Input("sales-customer-site-save", "n_clicks"),
            Input("sales-customer-site-delete", "n_clicks"),
        ],
        [
            State("sales-open-customer-id", "data"),
            State("sales-customer-site-edit-id", "data"),
            State("sales-customer-site-name", "value"),
            State("sales-customer-site-state", "value"),
            State("sales-customer-site-suburb", "value"),
            State("sales-customer-site-postcode", "value"),
            State("sales-customer-sites-table", "data"),
            State("sales-customer-sites-table", "selected_rows"),
            State("sales-customer-pricing-refresh", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_or_delete_site(
        save_clicks,
        delete_clicks,
        customer_id,
        site_edit_id,
        site_name,
        state,
        suburb,
        postcode,
        sites_data,
        selected_rows,
        refresh,
    ):
        if not callback_context.triggered or not customer_id:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"]
        new_refresh = (refresh or 0) + 1

        if "sales-customer-site-delete" in trigger:
            if not (delete_clicks or 0) >= 1:
                raise PreventUpdate
            site_id = site_edit_id
            if not site_id and selected_rows and sites_data:
                idx = selected_rows[0]
                if 0 <= idx < len(sites_data):
                    site_id = sites_data[idx].get("site_id")
            if not site_id:
                return "Select a site to delete.", no_update
            response = make_api_request("DELETE", f"/sales/customer-sites/{site_id}")
            if isinstance(response, dict) and response.get("error"):
                return response["error"], no_update
            return "Site deleted.", new_refresh

        if not (save_clicks or 0) >= 1:
            raise PreventUpdate
        if not (site_name or "").strip():
            return "Enter a site name.", no_update
        if not (state or "").strip():
            return "Enter state (e.g. VIC, NSW).", no_update
        payload = {
            "site_name": (site_name or "").strip(),
            "state": (state or "").strip()[:8],
            "suburb": (suburb or "").strip() or None,
            "postcode": (postcode or "").strip() or None,
        }
        if site_edit_id:
            response = make_api_request(
                "PUT", f"/sales/customer-sites/{site_edit_id}", payload
            )
            msg = "Site updated."
        else:
            response = make_api_request(
                "POST",
                "/sales/customer-sites",
                {"customer_id": customer_id, **payload},
            )
            msg = "Site added."
        if isinstance(response, dict) and response.get("error"):
            return response["error"], no_update
        return msg, new_refresh
