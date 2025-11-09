"""Dash callbacks powering the Sales Orders sub-tab."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate

STATUS_OPTIONS = [
    {"label": "Draft", "value": "draft"},
    {"label": "Confirmed", "value": "confirmed"},
    {"label": "Fulfilled", "value": "fulfilled"},
    {"label": "Cancelled", "value": "cancelled"},
]


def register_sales_orders_callbacks(app, make_api_request):
    """Register all callbacks for the Sales Orders sub-tab."""

    # ------------------------------------------------------------------ #
    # Data loading
    # ------------------------------------------------------------------ #
    @app.callback(
        [
            Output("sales-order-form-customer", "options"),
            Output("sales-order-form-customer", "value"),
            Output("sales-orders-customer-filter", "options"),
            Output("sales-order-form-channel", "options"),
            Output("sales-order-form-channel", "value"),
            Output("sales-orders-channel-filter", "options"),
            Output("sales-orders-status-filter", "options"),
            Output("sales-order-form-product", "options"),
            Output("sales-order-form-product", "value"),
            Output("sales-order-form-date", "date"),
            Output("sales-customers-store", "data"),
            Output("sales-products-store", "data"),
            Output("sales-channels-store", "data"),
        ],
        Input("sales-subtabs", "value"),
        prevent_initial_call=False,
    )
    def hydrate_form(subtab_value):
        if subtab_value != "sales-orders":
            raise PreventUpdate

        customers_response = make_api_request(
            "GET", "/contacts/", {"is_customer": True, "limit": 1000}
        )
        products_response = make_api_request(
            "GET", "/products/", {"is_sell": True, "limit": 1000}
        )
        channels_response = make_api_request("GET", "/sales/channels")

        customers = customers_response if isinstance(customers_response, list) else []
        products = products_response if isinstance(products_response, list) else []
        channels = channels_response if isinstance(channels_response, list) else []

        customer_options = [
            {"label": customer["name"], "value": customer["id"]}
            for customer in customers
            if customer.get("is_active", True)
        ]
        channel_options = [
            {"label": channel["name"], "value": channel["id"]} for channel in channels
        ]
        product_options = [
            {
                "label": f"{product.get('sku', '')} – {product.get('name', '')}".strip(
                    " –"
                ),
                "value": product["id"],
            }
            for product in products
        ]

        today = datetime.utcnow().date().isoformat()

        return (
            customer_options,
            None,
            customer_options,
            channel_options,
            (channel_options[0]["value"] if channel_options else None),
            channel_options,
            STATUS_OPTIONS,
            product_options,
            None,
            today,
            customers,
            products,
            channels,
        )

    @app.callback(
        [
            Output("sales-order-form-site", "options", allow_duplicate=True),
            Output("sales-order-form-site", "value", allow_duplicate=True),
        ],
        Input("sales-order-form-customer", "value"),
        State("sales-order-form-site", "value"),
        prevent_initial_call=True,
    )
    def load_customer_sites(customer_id, current_site):
        if not customer_id:
            return [], None
        response = make_api_request(
            "GET", "/sales/customer-sites", {"customer_id": customer_id}
        )
        sites = response if isinstance(response, list) else []
        options = [
            {
                "label": f"{site['site_name']} ({site.get('state', '')})".strip(" ()"),
                "value": site["id"],
            }
            for site in sites
        ]
        if current_site in {opt["value"] for opt in options}:
            return options, current_site
        return options, None

    # ------------------------------------------------------------------ #
    # Orders table
    # ------------------------------------------------------------------ #
    @app.callback(
        Output("sales-orders-table", "data"),
        [
            Input("sales-subtabs", "value"),
            Input("sales-orders-refresh", "n_clicks"),
            Input("sales-orders-refresh-signal", "data"),
        ],
        [
            State("sales-orders-customer-filter", "value"),
            State("sales-orders-channel-filter", "value"),
            State("sales-orders-status-filter", "value"),
            State("sales-orders-date-range", "start_date"),
            State("sales-orders-date-range", "end_date"),
            State("sales-customers-store", "data"),
            State("sales-channels-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def refresh_orders(
        subtab_value,
        _refresh_clicks,
        _refresh_signal,
        customer_filter,
        channel_filter,
        status_filter,
        start_date,
        end_date,
        customers,
        channels,
    ):
        if subtab_value != "sales-orders":
            raise PreventUpdate

        params: Dict[str, Any] = {}
        if customer_filter:
            params["customer_id"] = customer_filter
        if channel_filter:
            params["channel_id"] = channel_filter
        if status_filter:
            params["status_filter"] = status_filter
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = make_api_request("GET", "/sales/orders", params or None)
        orders = response if isinstance(response, list) else []

        customer_map = {
            customer["id"]: customer["name"] for customer in (customers or [])
        }
        channel_map = {channel["id"]: channel["name"] for channel in (channels or [])}

        rows = []
        for order in orders:
            rows.append(
                {
                    "order_date": order.get("order_date", "")[:10],
                    "order_ref": order.get("order_ref") or "—",
                    "customer": customer_map.get(order.get("customer_id"), "Unknown"),
                    "channel": channel_map.get(order.get("channel_id"), "—"),
                    "status": order.get("status", "").title(),
                    "total_ex_gst": _format_currency(order.get("total_ex_gst")),
                    "total_inc_gst": _format_currency(order.get("total_inc_gst")),
                }
            )
        return rows

    # ------------------------------------------------------------------ #
    # Order lines management
    # ------------------------------------------------------------------ #
    @app.callback(
        [
            Output("sales-order-form-lines-store", "data", allow_duplicate=True),
            Output("sales-order-form-lines-table", "data", allow_duplicate=True),
            Output("sales-order-form-product", "value", allow_duplicate=True),
            Output("sales-order-form-qty", "value", allow_duplicate=True),
            Output("sales-order-form-price", "value", allow_duplicate=True),
            Output("sales-order-form-discount", "value", allow_duplicate=True),
            Output("sales-order-form-feedback", "children", allow_duplicate=True),
            Output("sales-order-form-feedback", "color", allow_duplicate=True),
            Output("sales-order-form-feedback", "is_open", allow_duplicate=True),
        ],
        Input("sales-order-form-add-line", "n_clicks"),
        [
            State("sales-order-form-product", "value"),
            State("sales-order-form-qty", "value"),
            State("sales-order-form-price", "value"),
            State("sales-order-form-discount", "value"),
            State("sales-order-form-lines-store", "data"),
            State("sales-products-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def add_line(
        n_clicks,
        product_id,
        qty,
        unit_price,
        discount,
        lines,
        products,
    ):
        if not n_clicks:
            raise PreventUpdate
        if not product_id or not qty:
            return (
                lines,
                lines or [],
                product_id,
                qty,
                unit_price,
                discount,
                "Select product and quantity before adding a line.",
                "danger",
                True,
            )

        product_lookup = {product["id"]: product for product in (products or [])}
        product = product_lookup.get(product_id)
        label = (
            f"{product.get('sku', '')} – {product.get('name', '')}".strip(" –")
            if product
            else product_id
        )

        qty_decimal = Decimal(str(qty))
        unit_price_ex = (
            Decimal(str(unit_price))
            if unit_price is not None
            else Decimal(str(product.get("retail_price_ex_gst", "0")))
            if product
            else Decimal("0")
        )
        discount_ex = Decimal(str(discount)) if discount else Decimal("0")
        effective_price_ex = max(Decimal("0"), unit_price_ex - discount_ex)
        unit_price_inc = (
            Decimal(str(product.get("retail_price_inc_gst", "0")))
            if product and product.get("retail_price_inc_gst") is not None
            else effective_price_ex * Decimal("1.1")
        )

        line_total_ex = (effective_price_ex * qty_decimal).quantize(Decimal("0.01"))
        line_total_inc = (unit_price_inc * qty_decimal).quantize(Decimal("0.01"))

        new_line = {
            "product_id": product_id,
            "product_label": label,
            "qty": float(qty_decimal),
            "unit_price_ex_gst": float(unit_price_ex.quantize(Decimal("0.01"))),
            "unit_price_inc_gst": float(unit_price_inc.quantize(Decimal("0.01"))),
            "discount_ex_gst": float(discount_ex.quantize(Decimal("0.01"))),
            "line_total_ex_gst": float(line_total_ex),
            "line_total_inc_gst": float(line_total_inc),
        }

        updated_lines = list(lines or [])
        updated_lines.append(new_line)

        return (
            updated_lines,
            updated_lines,
            None,
            None,
            None,
            None,
            "Line added.",
            "success",
            True,
        )

    @app.callback(
        [
            Output("sales-order-form-lines-store", "data", allow_duplicate=True),
            Output("sales-order-form-lines-table", "data", allow_duplicate=True),
        ],
        Input("sales-order-form-remove-line", "n_clicks"),
        [
            State("sales-order-form-lines-store", "data"),
            State("sales-order-form-lines-table", "selected_rows"),
        ],
        prevent_initial_call=True,
    )
    def remove_line(n_clicks, lines, selected_rows):
        if not n_clicks:
            raise PreventUpdate
        if not selected_rows:
            raise PreventUpdate
        idx = selected_rows[0]
        updated = list(lines or [])
        if 0 <= idx < len(updated):
            updated.pop(idx)
        return updated, updated

    @app.callback(
        [
            Output("sales-order-form-lines-store", "data", allow_duplicate=True),
            Output("sales-order-form-lines-table", "data", allow_duplicate=True),
        ],
        Input("sales-order-form-clear", "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_lines(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return [], []

    # ------------------------------------------------------------------ #
    # Submit order
    # ------------------------------------------------------------------ #
    @app.callback(
        [
            Output("sales-order-form-feedback", "children", allow_duplicate=True),
            Output("sales-order-form-feedback", "color", allow_duplicate=True),
            Output("sales-order-form-feedback", "is_open", allow_duplicate=True),
            Output("sales-order-form-lines-store", "data", allow_duplicate=True),
            Output("sales-order-form-lines-table", "data", allow_duplicate=True),
            Output("sales-order-form-customer", "value", allow_duplicate=True),
            Output("sales-order-form-site", "options", allow_duplicate=True),
            Output("sales-order-form-site", "value", allow_duplicate=True),
            Output("sales-order-form-channel", "value", allow_duplicate=True),
            Output("sales-order-form-date", "date", allow_duplicate=True),
            Output("sales-order-form-ref", "value", allow_duplicate=True),
            Output("sales-order-form-entered-by", "value", allow_duplicate=True),
            Output("sales-order-form-notes", "value", allow_duplicate=True),
            Output("sales-orders-refresh-signal", "data"),
        ],
        Input("sales-order-form-submit", "n_clicks"),
        [
            State("sales-order-form-customer", "value"),
            State("sales-order-form-site", "value"),
            State("sales-order-form-channel", "value"),
            State("sales-order-form-date", "date"),
            State("sales-order-form-ref", "value"),
            State("sales-order-form-entered-by", "value"),
            State("sales-order-form-notes", "value"),
            State("sales-order-form-lines-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def submit_order(
        n_clicks,
        customer_id,
        site_id,
        channel_id,
        order_date,
        order_ref,
        entered_by,
        notes,
        lines,
    ):
        if not n_clicks:
            raise PreventUpdate
        if not customer_id:
            return _submission_error("Select a customer before submitting.")
        if not channel_id:
            return _submission_error("Select a channel before submitting.")
        if not lines:
            return _submission_error("Add at least one line before submitting.")

        payload = {
            "customer_id": customer_id,
            "customer_site_id": site_id,
            "channel_id": channel_id,
            "order_date": order_date or datetime.utcnow().date().isoformat(),
            "order_ref": order_ref,
            "entered_by": entered_by,
            "notes": notes,
            "lines": [
                {
                    "product_id": line["product_id"],
                    "qty": float(line["qty"]),
                    "unit_price_ex_gst": float(line["unit_price_ex_gst"]),
                    "unit_price_inc_gst": float(line["unit_price_inc_gst"]),
                    "discount_ex_gst": float(line["discount_ex_gst"]),
                }
                for line in lines
            ],
        }

        response = make_api_request("POST", "/sales/orders", payload)
        if isinstance(response, dict) and "error" in response:
            return _submission_error(response["error"])

        today = datetime.utcnow().date().isoformat()
        return (
            "Order created successfully.",
            "success",
            True,
            [],
            [],
            None,
            [],
            None,
            channel_id,
            today,
            None,
            None,
            None,
            datetime.utcnow().timestamp(),
        )


def _format_currency(value: Any) -> str:
    try:
        return f"${Decimal(str(value)).quantize(Decimal('0.01')):,}"
    except Exception:
        return "$0.00"


def _submission_error(message: str):
    return (
        message,
        "danger",
        True,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
    )
