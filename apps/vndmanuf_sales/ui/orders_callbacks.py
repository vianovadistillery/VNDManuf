"""Dash callbacks powering the Sales Orders sub-tab."""

from __future__ import annotations

import base64
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

import dash_bootstrap_components as dbc
import requests
from dash import Input, Output, State, callback_context, dash_table, html, no_update
from dash.exceptions import PreventUpdate

STATUS_OPTIONS = [
    {"label": "Draft", "value": "draft"},
    {"label": "Confirmed", "value": "confirmed"},
    {"label": "Fulfilled", "value": "fulfilled"},
    {"label": "Cancelled", "value": "cancelled"},
]


def register_sales_orders_callbacks(
    app, make_api_request, api_base_url: str = "http://127.0.0.1:8000"
):
    """Register all callbacks for the Sales Orders sub-tab. api_base_url is used for document download (no /api/v1 suffix)."""

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

        customers_response = make_api_request("GET", "/sales/customers")
        products_response = make_api_request(
            "GET", "/products/", {"is_sell": True, "limit": 1000}
        )
        channels_response = make_api_request("GET", "/sales/channels")

        customers = customers_response if isinstance(customers_response, list) else []
        products = products_response if isinstance(products_response, list) else []
        channels = channels_response if isinstance(channels_response, list) else []

        customer_options = [
            {"label": f"{c.get('name', '')} ({c.get('code', '')})", "value": c["id"]}
            for c in customers
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
            Input("sales-orders-include-inactive", "value"),
            Input("sales-customers-store", "data"),
            Input("sales-orders-customer-filter", "value"),
            Input("sales-orders-channel-filter", "value"),
            Input("sales-orders-status-filter", "value"),
        ],
        [
            State("sales-orders-type-filter", "value"),
            State("sales-orders-date-range", "start_date"),
            State("sales-orders-date-range", "end_date"),
            State("sales-channels-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def refresh_orders(
        subtab_value,
        _refresh_clicks,
        _refresh_signal,
        include_inactive_filter,
        customers,
        customer_filter,
        channel_filter,
        status_filter,
        type_filter,
        start_date,
        end_date,
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
        if type_filter:
            if "has_delivery" in type_filter:
                params["has_delivery"] = True
            if "has_invoice" in type_filter:
                params["has_invoice"] = True
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if include_inactive_filter and "include_inactive" in include_inactive_filter:
            params["include_deleted"] = True

        response = make_api_request("GET", "/sales/orders", params or None)
        orders = response if isinstance(response, list) else []

        customer_map = {
            customer["id"]: customer["name"] for customer in (customers or [])
        }
        channel_map = {channel["id"]: channel["name"] for channel in (channels or [])}

        rows = []
        for order in orders:
            order_date = order.get("order_date") or ""
            if isinstance(order_date, str) and len(order_date) >= 10:
                order_date = order_date[:10]
            elif hasattr(order_date, "strftime"):
                order_date = order_date.strftime("%Y-%m-%d")
            delivery_date = order.get("delivery_date")
            if delivery_date and hasattr(delivery_date, "strftime"):
                delivery_date = delivery_date.strftime("%Y-%m-%d")
            elif isinstance(delivery_date, str):
                delivery_date = (
                    delivery_date[:10] if len(delivery_date) >= 10 else delivery_date
                )
            is_active = not order.get("deleted_at")
            rows.append(
                {
                    "order_id": order.get("id"),
                    "order_date": order_date,
                    "order_ref": order.get("order_ref") or "—",
                    "po_number": order.get("po_number") or "—",
                    "customer": customer_map.get(order.get("customer_id"), "Unknown"),
                    "channel": channel_map.get(order.get("channel_id"), "—"),
                    "status": (order.get("status") or "").title(),
                    "active": "Yes" if is_active else "No",
                    "delivery_docket_number": order.get("delivery_docket_number")
                    or "—",
                    "delivery_date": delivery_date or "—",
                    "docket_file": "Yes"
                    if order.get("delivery_docket_document")
                    else "—",
                    "invoice_number": order.get("invoice_number") or "—",
                    "invoice_file": "Yes" if order.get("invoice_document") else "—",
                    "paid": "Yes" if order.get("paid") else "—",
                    "lal": _format_lal(order.get("total_alcohol_volume_litres")),
                    "total_ex_gst": _format_currency(order.get("total_ex_gst")),
                    "total_inc_gst": _format_currency(order.get("total_inc_gst")),
                }
            )
        return rows

    # ------------------------------------------------------------------ #
    # Open order detail modal
    # ------------------------------------------------------------------ #
    @app.callback(
        [
            Output("sales-open-order-id", "data"),
            Output("sales-order-detail-modal", "is_open"),
        ],
        [
            Input("sales-orders-open-selected", "n_clicks"),
            Input("sales-order-detail-close", "n_clicks"),
        ],
        [
            State("sales-orders-table", "data"),
            State("sales-orders-table", "selected_rows"),
            State("sales-order-detail-modal", "is_open"),
        ],
        prevent_initial_call=True,
    )
    def open_or_close_order_modal(
        open_clicks, close_clicks, table_data, selected_rows, modal_is_open
    ):
        if not callback_context.triggered:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"]
        if "sales-order-detail-close" in trigger:
            return None, False
        if "sales-orders-open-selected" in trigger and table_data and selected_rows:
            idx = selected_rows[0]
            if 0 <= idx < len(table_data) and table_data[idx].get("order_id"):
                return table_data[idx]["order_id"], True
        raise PreventUpdate

    @app.callback(
        Output("sales-new-order-modal", "is_open"),
        [
            Input("sales-orders-new-order-btn", "n_clicks"),
            Input("sales-new-order-close", "n_clicks"),
            Input("sales-new-order-header-close", "n_clicks"),
        ],
        State("sales-new-order-modal", "is_open"),
        prevent_initial_call=True,
    )
    def open_close_new_order_modal(
        open_clicks, close_clicks, header_close_clicks, is_open
    ):
        if not callback_context.triggered:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"]
        if "sales-orders-new-order-btn" in trigger:
            return True
        if (
            "sales-new-order-close" in trigger
            or "sales-new-order-header-close" in trigger
        ):
            return False
        return no_update

    @app.callback(
        [
            Output("sales-order-detail-title", "children"),
            Output("sales-order-detail-body", "children"),
            Output("sales-order-detail-footer", "children"),
        ],
        Input("sales-open-order-id", "data"),
        Input("sales-order-detail-refresh", "data"),
        State("sales-customers-store", "data"),
        prevent_initial_call=False,
    )
    def load_order_detail(order_id, _refresh, customers_store):
        if not order_id:
            return (
                "Order",
                html.Div("Select an order and click Open.", className="text-muted"),
                [dbc.Button("Close", id="sales-order-detail-close", color="secondary")],
            )
        response = make_api_request("GET", f"/sales/orders/{order_id}")
        if isinstance(response, dict) and response.get("error"):
            return (
                f"Order {order_id[:8]}…",
                html.Div(f"Error: {response['error']}", className="text-danger"),
                [dbc.Button("Close", id="sales-order-detail-close", color="secondary")],
            )
        order_ref = response.get("order_ref") or response.get("id", "")[:8]
        title = f"Order {order_ref}"
        cid = response.get("customer_id")
        customer_name = next(
            (c.get("name", cid) for c in (customers_store or []) if c.get("id") == cid),
            cid or "—",
        )
        lines = response.get("lines") or []
        delivery_date = response.get("delivery_date")
        if delivery_date and hasattr(delivery_date, "strftime"):
            delivery_date = delivery_date.strftime("%Y-%m-%d")
        elif isinstance(delivery_date, str) and len(delivery_date) >= 10:
            delivery_date = delivery_date[:10]
        else:
            delivery_date = delivery_date or "—"

        # Line table with GST column; GST per line = inc - ex; format currency for display
        def _dec(v):
            if v is None:
                return 0
            return float(v) if not isinstance(v, (int, float)) else v

        def _qty_display(val):
            if val is None:
                return ""
            n = float(val)
            return int(n) if n == int(n) else n

        table_data = []
        for order_line in lines:
            ex = _dec(order_line.get("line_total_ex_gst"))
            inc = _dec(order_line.get("line_total_inc_gst"))
            gst = inc - ex
            product_code = (
                order_line.get("product_sku")
                or order_line.get("product_name")
                or (
                    str(order_line.get("product_id"))
                    if order_line.get("product_id")
                    else "—"
                )
            )
            description = order_line.get("product_name") or ""
            table_data.append(
                {
                    "line_id": order_line.get("id"),
                    "product_id": order_line.get("product_id"),
                    "qty": _qty_display(order_line.get("qty")),
                    "product_code": product_code,
                    "description": description,
                    "unit_price_ex_gst": _format_currency(
                        _dec(order_line.get("unit_price_ex_gst"))
                    ),
                    "unit_price_ex_gst_raw": _dec(order_line.get("unit_price_ex_gst")),
                    "gst": _format_currency(gst),
                    "line_total_ex_gst": _format_currency(ex),
                    "line_total_inc_gst": _format_currency(inc),
                }
            )
        total_ex = _dec(response.get("total_ex_gst"))
        total_inc = _dec(response.get("total_inc_gst"))
        total_gst = total_inc - total_ex

        # Totals: label in second-right column (Line total ex), value in right column (Line total inc)
        table_data.append(
            {
                "line_id": "",
                "product_id": "_total_ex",
                "qty": "",
                "product_code": "",
                "description": "",
                "unit_price_ex_gst": "",
                "gst": "",
                "line_total_ex_gst": "Total ex GST",
                "line_total_inc_gst": _format_currency(total_ex),
            }
        )
        table_data.append(
            {
                "line_id": "",
                "product_id": "_total_gst",
                "qty": "",
                "product_code": "",
                "description": "",
                "unit_price_ex_gst": "",
                "gst": "",
                "line_total_ex_gst": "Total GST",
                "line_total_inc_gst": _format_currency(total_gst),
            }
        )
        table_data.append(
            {
                "line_id": "",
                "product_id": "_total_inc",
                "qty": "",
                "product_code": "",
                "description": "",
                "unit_price_ex_gst": "",
                "gst": "",
                "line_total_ex_gst": "Total inc GST",
                "line_total_inc_gst": _format_currency(total_inc),
            }
        )

        delivery_doc = response.get("delivery_docket_document")
        invoice_doc = response.get("invoice_document")
        picking_doc = response.get("picking_slip_document")
        delivery_number = response.get("delivery_docket_number") or "—"
        invoice_number = response.get("invoice_number") or "—"

        def _doc_link(label: str, doc: dict):
            if not doc:
                return label
            url = f"{api_base_url}/api/v1/documents/{doc['id']}/download"
            return html.A(
                label,
                href=url,
                target="_blank",
                rel="noopener noreferrer",
                className="btn btn-primary btn-sm",
            )

        # Left: order info only (Delivery # and Invoice # are buttons that open file when doc exists)
        left_col = html.Div(
            [
                html.P([html.Strong("Customer: "), customer_name]),
                html.P(
                    [
                        html.Strong("Order date: "),
                        (response.get("order_date") or "")[:10],
                    ]
                ),
                html.P([html.Strong("PO: "), response.get("po_number") or "—"]),
                html.P(
                    [
                        html.Strong("Delivery #: "),
                        _doc_link(delivery_number, delivery_doc)
                        if delivery_doc
                        else delivery_number,
                    ]
                ),
                html.P([html.Strong("Delivery date: "), delivery_date]),
                html.P(
                    [
                        html.Strong("Invoice #: "),
                        _doc_link(invoice_number, invoice_doc)
                        if invoice_doc
                        else invoice_number,
                    ]
                ),
                html.P([html.Strong("Paid: "), "Yes" if response.get("paid") else "—"]),
                html.P(
                    [
                        html.Strong("Order discount (ex): "),
                        _format_currency(response.get("order_discount_ex_gst")),
                    ]
                ),
                html.P(
                    [
                        html.Strong("Total alcohol (L): "),
                        str(response.get("total_alcohol_volume_litres") or "—"),
                    ]
                ),
            ],
            style={"overflowY": "auto", "maxHeight": "70vh"},
        )
        # Right: line items — Qty first, then Product code; totals in right columns
        is_converted = bool(response.get("delivery_docket_id"))
        # DataTable editable must be boolean; only "qty" column is editable when order not converted
        line_items_table = dash_table.DataTable(
            id="sales-order-detail-table",
            data=table_data,
            columns=[
                {"name": "Qty", "id": "qty", "editable": not is_converted},
                {"name": "Product", "id": "product_code", "editable": False},
                {"name": "Description", "id": "description", "editable": False},
                {"name": "Unit (ex)", "id": "unit_price_ex_gst", "editable": False},
                {"name": "GST", "id": "gst", "editable": False},
                {
                    "name": "Line total (ex)",
                    "id": "line_total_ex_gst",
                    "editable": False,
                },
                {
                    "name": "Line total (inc)",
                    "id": "line_total_inc_gst",
                    "editable": False,
                },
            ],
            page_size=100,
            page_action="none",
            style_cell={"padding": "0.3rem"},
            style_data_conditional=[
                {
                    "if": {"filter_query": '{product_id} contains "_total"'},
                    "fontWeight": "bold",
                    "backgroundColor": "rgba(248, 249, 250, 0.9)",
                },
            ],
            editable=not is_converted,
        )
        right_col = html.Div(
            [
                html.Div(
                    "Line items (qty, product code)", className="small text-muted mb-1"
                ),
                line_items_table,
            ],
            className="h-100",
            style={"minHeight": "200px", "overflowY": "auto", "maxHeight": "70vh"},
        )

        body = [
            dbc.Row(
                [
                    dbc.Col(left_col, width=4, className="pe-2"),
                    dbc.Col(right_col, width=8, className="ps-2 border-start"),
                ],
                className="g-2",
            ),
        ]

        # Footer: Create delivery docket / Create invoice (disabled when doc exists); no Open buttons
        footer = []
        if delivery_doc:
            footer.append(
                dbc.Button(
                    "Create delivery docket",
                    id="sales-order-print-delivery",
                    color="secondary",
                    size="sm",
                    disabled=True,
                )
            )
        else:
            footer.append(
                dbc.Button(
                    "Create delivery docket",
                    id="sales-order-print-delivery",
                    color="secondary",
                    size="sm",
                )
            )
        if picking_doc:
            footer.append(
                dbc.Button(
                    "Create picking slip",
                    id="sales-order-print-picking",
                    color="secondary",
                    size="sm",
                    disabled=True,
                )
            )
        else:
            footer.append(
                dbc.Button(
                    "Create picking slip",
                    id="sales-order-print-picking",
                    color="secondary",
                    size="sm",
                )
            )
        footer.append(
            dbc.Button(
                "Convert to delivery",
                id="sales-order-convert-delivery",
                color="info",
                size="sm",
                title="Create a delivery docket from this order and lock the order from further edits. You can then set delivery quantities and generate the docket PDF.",
            )
        )
        footer.append(
            dbc.Button(
                "Convert to invoice",
                id="sales-order-convert-invoice",
                color="info",
                size="sm",
            )
        )
        if invoice_doc:
            footer.append(
                dbc.Button(
                    "Create invoice",
                    id="sales-order-print-invoice",
                    color="secondary",
                    size="sm",
                    disabled=True,
                )
            )
        else:
            footer.append(
                dbc.Button(
                    "Create invoice",
                    id="sales-order-print-invoice",
                    color="secondary",
                    size="sm",
                )
            )
        footer.append(
            dbc.Button(
                "Mark paid", id="sales-order-mark-paid", color="success", size="sm"
            )
        )
        footer.append(
            dbc.Button(
                "Delete order", id="sales-order-delete-btn", color="danger", size="sm"
            )
        )
        footer.append(
            dbc.Button("Close", id="sales-order-detail-close", color="secondary")
        )
        if not is_converted:
            footer.insert(
                -1,
                dbc.Button(
                    "Save", id="sales-order-detail-save", color="primary", size="sm"
                ),
            )
            footer.insert(
                -1,
                dbc.Button(
                    "Cancel",
                    id="sales-order-detail-cancel",
                    color="secondary",
                    size="sm",
                ),
            )
        return title, body, footer

    @app.callback(
        Output("sales-order-detail-table", "data"),
        Input("sales-order-detail-table", "data"),
        prevent_initial_call=False,
    )
    def order_detail_table_recalc(data):
        """When qty (or any cell) changes in the order detail table, recalc line totals and order totals."""
        if not data:
            return no_update
        data_rows = [
            r
            for r in data
            if r.get("line_id")
            and str(r.get("product_id", "") or "").strip()
            and not str(r.get("product_id", "")).startswith("_")
        ]
        total_rows = [
            r for r in data if str(r.get("product_id", "") or "").startswith("_total")
        ]
        if not data_rows or len(total_rows) != 3:
            return no_update
        total_ex = Decimal("0")
        total_gst = Decimal("0")
        total_inc = Decimal("0")
        out_rows = []
        for r in data_rows:
            try:
                qty = Decimal(str(r.get("qty") or 0))
            except Exception:
                qty = Decimal("0")
            up_raw = r.get("unit_price_ex_gst_raw")
            if up_raw is None:
                up_raw = 0
            try:
                unit_ex = Decimal(str(up_raw))
            except Exception:
                unit_ex = Decimal("0")
            line_ex = (qty * unit_ex).quantize(Decimal("0.01"))
            line_inc = (line_ex * Decimal("1.1")).quantize(Decimal("0.01"))
            gst_line = line_inc - line_ex
            total_ex += line_ex
            total_inc += line_inc
            total_gst += gst_line
            out_rows.append(
                {
                    **r,
                    "line_total_ex_gst": _format_currency(line_ex),
                    "line_total_inc_gst": _format_currency(line_inc),
                    "gst": _format_currency(gst_line),
                }
            )
        # total_inc already includes gst; total_gst = total_inc - total_ex
        total_gst = total_inc - total_ex
        value_by_id = {
            "_total_ex": total_ex,
            "_total_gst": total_gst,
            "_total_inc": total_inc,
        }
        for r in total_rows:
            pid = r.get("product_id")
            out_rows.append(
                {**r, "line_total_inc_gst": _format_currency(value_by_id.get(pid, 0))}
            )
        return out_rows

    @app.callback(
        Output("sales-order-detail-refresh", "data", allow_duplicate=True),
        Input("sales-order-detail-cancel", "n_clicks"),
        prevent_initial_call=True,
    )
    def order_detail_cancel(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return datetime.utcnow().timestamp()

    @app.callback(
        Output("sales-order-detail-refresh", "data", allow_duplicate=True),
        Input("sales-order-detail-save", "n_clicks"),
        [
            State("sales-open-order-id", "data"),
            State("sales-order-detail-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def order_detail_save(n_clicks, order_id, table_data):
        if not n_clicks or not order_id or not table_data:
            raise PreventUpdate
        data_rows = [
            r
            for r in table_data
            if r.get("line_id")
            and str(r.get("product_id", "") or "").strip()
            and not str(r.get("product_id", "")).startswith("_")
        ]
        if not data_rows:
            raise PreventUpdate
        lines_payload = []
        for r in data_rows:
            try:
                qty = float(r.get("qty") or 0)
            except (TypeError, ValueError):
                qty = 0
            up = r.get("unit_price_ex_gst_raw")
            if up is None:
                up = 0
            try:
                up = float(up)
            except (TypeError, ValueError):
                up = 0
            lines_payload.append(
                {
                    "product_id": str(r.get("product_id")),
                    "qty": qty,
                    "unit_price_ex_gst": up,
                    "uom": "unit",
                }
            )
        r = make_api_request(
            "PUT", f"/sales/orders/{order_id}", {"lines": lines_payload}
        )
        if isinstance(r, dict) and r.get("error"):
            raise PreventUpdate
        return datetime.utcnow().timestamp()

    @app.callback(
        [
            Output("sales-orders-refresh-signal", "data", allow_duplicate=True),
            Output("sales-order-detail-modal", "is_open", allow_duplicate=True),
        ],
        [
            Input("sales-order-convert-delivery", "n_clicks"),
            Input("sales-order-convert-invoice", "n_clicks"),
            Input("sales-order-mark-paid", "n_clicks"),
        ],
        [State("sales-open-order-id", "data")],
        prevent_initial_call=True,
    )
    def order_detail_actions(conv_delivery, conv_invoice, mark_paid, order_id):
        if not order_id or not callback_context.triggered:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"]
        if "sales-order-convert-delivery" in trigger:
            r = make_api_request(
                "POST", f"/sales/orders/{order_id}/convert-to-delivery", {}
            )
            if isinstance(r, dict) and r.get("error"):
                return no_update, no_update
            return (datetime.utcnow().timestamp(), False)
        if "sales-order-convert-invoice" in trigger:
            r = make_api_request(
                "POST", f"/sales/orders/{order_id}/convert-to-invoice", {}
            )
            if isinstance(r, dict) and r.get("error"):
                return no_update, no_update
            return (datetime.utcnow().timestamp(), False)
        if "sales-order-mark-paid" in trigger:
            response = make_api_request("GET", f"/sales/orders/{order_id}")
            inv_id = (
                (response or {}).get("invoice_id")
                if isinstance(response, dict)
                else None
            )
            if inv_id:
                make_api_request("PATCH", f"/sales/invoices/{inv_id}/paid")
            return (datetime.utcnow().timestamp(), False)
        raise PreventUpdate

    # Open delete-confirm modal when "Delete order" is clicked; cancel/confirm in same callback
    @app.callback(
        [
            Output("sales-order-delete-confirm-modal", "is_open"),
            Output("sales-order-pending-delete", "data"),
            Output("sales-orders-refresh-signal", "data", allow_duplicate=True),
            Output("sales-order-detail-modal", "is_open", allow_duplicate=True),
            Output("sales-open-order-id", "data", allow_duplicate=True),
        ],
        [
            Input("sales-order-delete-btn", "n_clicks"),
            Input("sales-order-delete-cancel", "n_clicks"),
            Input("sales-order-delete-confirm", "n_clicks"),
        ],
        [
            State("sales-open-order-id", "data"),
            State("sales-order-delete-confirm-modal", "is_open"),
            State("sales-order-pending-delete", "data"),
        ],
        prevent_initial_call=True,
    )
    def order_delete_confirm_flow(
        delete_btn_clicks,
        cancel_clicks,
        confirm_clicks,
        open_order_id,
        confirm_modal_open,
        pending_delete_id,
    ):
        if not callback_context.triggered:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"]
        # Only open modal on actual click (n_clicks >= 1); footer re-render can fire with n_clicks=0
        if (
            "sales-order-delete-btn" in trigger
            and open_order_id
            and (delete_btn_clicks or 0) >= 1
        ):
            return True, open_order_id, no_update, no_update, no_update
        if "sales-order-delete-cancel" in trigger:
            return False, None, no_update, no_update, no_update
        if "sales-order-delete-confirm" in trigger and pending_delete_id:
            r = make_api_request("DELETE", f"/sales/orders/{pending_delete_id}")
            if isinstance(r, dict) and r.get("error"):
                return no_update, no_update, no_update, no_update, no_update
            return (
                False,
                None,
                datetime.utcnow().timestamp(),
                False,
                None,
            )
        raise PreventUpdate

    # ------------------------------------------------------------------ #
    # Delivery quantities modal + generate delivery docket
    # ------------------------------------------------------------------ #
    @app.callback(
        [
            Output("sales-delivery-quantities-modal", "is_open"),
            Output("sales-delivery-docket-id-modal", "data"),
        ],
        Input("sales-order-print-delivery", "n_clicks"),
        State("sales-open-order-id", "data"),
        prevent_initial_call=True,
    )
    def open_delivery_quantities_modal(n_clicks, order_id):
        if not n_clicks or not order_id:
            raise PreventUpdate
        order = make_api_request("GET", f"/sales/orders/{order_id}")
        if not isinstance(order, dict) or order.get("error"):
            raise PreventUpdate
        delivery_docket_id = order.get("delivery_docket_id")
        if not delivery_docket_id:
            r = make_api_request(
                "POST", f"/sales/orders/{order_id}/convert-to-delivery", {}
            )
            if isinstance(r, dict) and r.get("error"):
                err = str(r.get("error", ""))
                if "409" in err or "already has a delivery docket" in err.lower():
                    order = make_api_request("GET", f"/sales/orders/{order_id}")
                    if isinstance(order, dict) and not order.get("error"):
                        delivery_docket_id = order.get("delivery_docket_id")
                if not delivery_docket_id:
                    return no_update, no_update
            else:
                delivery_docket_id = (r if isinstance(r, dict) else {}).get(
                    "delivery_docket_id"
                )
                if not delivery_docket_id:
                    order = make_api_request("GET", f"/sales/orders/{order_id}")
                    if isinstance(order, dict):
                        delivery_docket_id = order.get("delivery_docket_id")
        if not delivery_docket_id:
            return no_update, no_update
        return True, {"docket_id": delivery_docket_id, "order_id": order_id}

    @app.callback(
        [
            Output("sales-delivery-quantities-table", "data"),
            Output("sales-delivery-quantities-total", "children"),
        ],
        Input("sales-delivery-quantities-modal", "is_open"),
        State("sales-delivery-docket-id-modal", "data"),
        prevent_initial_call=False,
    )
    def load_delivery_quantities_modal(is_open, store):
        if not is_open or not store or not store.get("docket_id"):
            return [], ""
        docket = make_api_request(
            "GET", f"/sales/delivery-dockets/{store['docket_id']}"
        )
        if not isinstance(docket, dict) or docket.get("error"):
            return [], ""
        lines = docket.get("lines") or []
        total_delivered = 0
        table_data = []
        for ln in lines:
            oq = float(ln.get("ordered_quantity") or 0)
            qty = float(ln.get("quantity") or 0)
            total_delivered += qty
            table_data.append(
                {
                    "line_id": ln.get("id"),
                    "product_id": ln.get("product_id"),
                    "product_sku": ln.get("product_sku")
                    or ln.get("product_name")
                    or "—",
                    "ordered_quantity": int(oq) if oq == int(oq) else oq,
                    "quantity": int(qty) if qty == int(qty) else qty,
                }
            )
        total_str = f"Total delivered: {int(total_delivered) if total_delivered == int(total_delivered) else total_delivered}"
        return table_data, total_str

    @app.callback(
        Output("sales-delivery-quantities-total", "children", allow_duplicate=True),
        Input("sales-delivery-quantities-table", "data"),
        prevent_initial_call=True,
    )
    def update_delivery_total_from_table(table_data):
        if not table_data:
            return ""
        total = sum(float(r.get("quantity") or 0) for r in table_data)
        return f"Total delivered: {int(total) if total == int(total) else total}"

    @app.callback(
        [
            Output("sales-delivery-quantities-modal", "is_open", allow_duplicate=True),
            Output("sales-order-docket-download", "data"),
            Output("sales-order-detail-refresh", "data", allow_duplicate=True),
            Output("sales-backorder-pending", "data"),
            Output("sales-backorder-modal", "is_open"),
        ],
        Input("sales-delivery-quantities-confirm", "n_clicks"),
        [
            State("sales-delivery-docket-id-modal", "data"),
            State("sales-delivery-quantities-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def confirm_delivery_docket_and_generate(n_clicks, store, table_data):
        if not n_clicks or not store or not table_data:
            raise PreventUpdate
        docket_id = store.get("docket_id")
        order_id = store.get("order_id")
        if not docket_id:
            raise PreventUpdate
        from decimal import Decimal as D

        lines_patch = []
        backorder_lines = []
        for row in table_data:
            oqty = float(row.get("ordered_quantity") or 0)
            dqty = float(row.get("quantity") or 0)
            if dqty > oqty:
                dqty = oqty
            lines_patch.append(
                {"line_id": row.get("line_id"), "quantity": D(str(dqty))}
            )
            if oqty > dqty and order_id and row.get("product_id"):
                backorder_lines.append(
                    {"product_id": row["product_id"], "backorder_qty": oqty - dqty}
                )
        if not lines_patch:
            raise PreventUpdate
        r = make_api_request(
            "PATCH",
            f"/sales/delivery-dockets/{docket_id}/lines",
            {"lines": lines_patch},
        )
        if isinstance(r, dict) and r.get("error"):
            raise PreventUpdate
        gen = make_api_request(
            "POST",
            "/documents/generate",
            {
                "template_name": "Delivery_Docket.docx",
                "doc_type": "delivery_docket",
                "delivery_docket_id": docket_id,
            },
        )
        if not isinstance(gen, dict) or gen.get("error"):
            return False, no_update, no_update, no_update, no_update
        doc = gen.get("document") or {}
        doc_id = doc.get("id")
        download_data = no_update
        if doc_id:
            try:
                resp = requests.get(
                    f"{api_base_url}/api/v1/documents/{doc_id}/download", timeout=30
                )
                if resp.status_code == 200:
                    fn = (
                        (gen.get("pdf_path") or "delivery_docket.pdf")
                        .split("/")[-1]
                        .split("\\")[-1]
                    )
                    download_data = dict(
                        content=base64.b64encode(resp.content).decode(),
                        filename=fn,
                        base64=True,
                    )
            except Exception:
                pass
        refresh = datetime.utcnow().timestamp()
        backorder_pending = (
            {"order_id": order_id, "lines": backorder_lines}
            if backorder_lines and order_id
            else None
        )
        backorder_modal_open = bool(backorder_pending)
        return False, download_data, refresh, backorder_pending, backorder_modal_open

    @app.callback(
        [
            Output("sales-delivery-quantities-modal", "is_open", allow_duplicate=True),
            Output("sales-delivery-docket-id-modal", "data", allow_duplicate=True),
        ],
        Input("sales-delivery-quantities-cancel", "n_clicks"),
        prevent_initial_call=True,
    )
    def cancel_delivery_quantities_modal(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return False, None

    @app.callback(
        [
            Output("sales-order-detail-refresh", "data", allow_duplicate=True),
            Output("sales-backorder-modal", "is_open", allow_duplicate=True),
            Output("sales-backorder-pending", "data", allow_duplicate=True),
        ],
        Input("sales-backorder-confirm", "n_clicks"),
        State("sales-backorder-pending", "data"),
        prevent_initial_call=True,
    )
    def confirm_backorder(n_clicks, pending):
        if not n_clicks or not pending:
            raise PreventUpdate
        order_id = pending.get("order_id")
        lines = pending.get("lines") or []
        if not order_id or not lines:
            return no_update, False, None
        r = make_api_request(
            "POST", f"/sales/orders/{order_id}/backorder", {"lines": lines}
        )
        if isinstance(r, dict) and r.get("error"):
            return no_update, no_update, no_update
        return datetime.utcnow().timestamp(), False, None

    @app.callback(
        [
            Output("sales-backorder-modal", "is_open", allow_duplicate=True),
            Output("sales-backorder-pending", "data", allow_duplicate=True),
        ],
        Input("sales-backorder-cancel", "n_clicks"),
        prevent_initial_call=True,
    )
    def cancel_backorder(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return False, None

    # ------------------------------------------------------------------ #
    # New order: populate Price ex when product selected
    # ------------------------------------------------------------------ #
    @app.callback(
        Output("sales-order-form-price", "value", allow_duplicate=True),
        Input("sales-order-form-product", "value"),
        [
            State("sales-order-form-customer", "value"),
            State("sales-customers-store", "data"),
            State("sales-products-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def new_order_product_select_populate_price(
        product_id, customer_id, customers, products
    ):
        if not product_id or not products:
            return no_update
        product_lookup = {p["id"]: p for p in products}
        product = product_lookup.get(product_id)
        if not product:
            return no_update
        price_level_to_key = {
            "retail": "retail_price_ex_gst",
            "wholesale": "wholesale_price_ex_gst",
            "distributor": "distributor_price_ex_gst",
            "counter": "counter_price_ex_gst",
            "trade": "trade_price_ex_gst",
            "contract": "contract_price_ex_gst",
            "industrial": "industrial_price_ex_gst",
        }
        default_price_key = "retail_price_ex_gst"
        if customer_id and customers:
            for c in customers:
                if c.get("id") == customer_id:
                    level = (c.get("default_pricing_level") or "").strip().lower()
                    if level and level in price_level_to_key:
                        default_price_key = price_level_to_key[level]
                    break
        price = product.get(default_price_key) or product.get("retail_price_ex_gst")
        if price is not None:
            try:
                return float(Decimal(str(price)).quantize(Decimal("0.01")))
            except Exception:
                pass
        return no_update

    # ------------------------------------------------------------------ #
    # New order live totals
    # ------------------------------------------------------------------ #
    @app.callback(
        Output("sales-new-order-totals", "children"),
        Input("sales-order-form-lines-store", "data"),
        prevent_initial_call=False,
    )
    def new_order_live_totals(lines):
        if not lines:
            return html.Div(
                [
                    html.Div(
                        [
                            "Number of items: 0",
                            html.Span("Total ex: $0.00", className="float-end"),
                        ],
                        className="d-flex justify-content-between",
                    ),
                    html.Div(
                        [
                            "Order volume: 0",
                            html.Span("GST: $0.00", className="float-end"),
                        ],
                        className="d-flex justify-content-between",
                    ),
                    html.Div(
                        [
                            "Alcohol volume: —",
                            html.Span("Total inc: $0.00", className="float-end"),
                        ],
                        className="d-flex justify-content-between",
                    ),
                ],
                className="d-flex flex-column gap-1",
            )
        total_ex = sum(float(r.get("line_total_ex_gst") or 0) for r in lines)
        total_inc = sum(float(r.get("line_total_inc_gst") or 0) for r in lines)
        total_gst = total_inc - total_ex
        num_items = len(lines)
        order_volume = sum(float(r.get("qty") or 0) for r in lines)
        try:
            alcohol_vol = sum(float(r.get("alcohol_volume_litres") or 0) for r in lines)
            alcohol_str = f"{alcohol_vol:.2f} L" if alcohol_vol else "—"
        except Exception:
            alcohol_str = "—"
        return html.Div(
            [
                html.Div(
                    [
                        f"Number of items: {num_items}",
                        html.Span(
                            f"Total ex: {_format_currency(total_ex)}",
                            className="float-end",
                        ),
                    ],
                    className="d-flex justify-content-between",
                ),
                html.Div(
                    [
                        f"Order volume: {order_volume:.0f}",
                        html.Span(
                            f"GST: {_format_currency(total_gst)}", className="float-end"
                        ),
                    ],
                    className="d-flex justify-content-between",
                ),
                html.Div(
                    [
                        f"Alcohol volume: {alcohol_str}",
                        html.Span(
                            f"Total inc: {_format_currency(total_inc)}",
                            className="float-end",
                        ),
                    ],
                    className="d-flex justify-content-between",
                ),
            ],
            className="d-flex flex-column gap-1",
        )

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
            State("sales-order-form-customer", "value"),
            State("sales-customers-store", "data"),
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
        customer_id,
        customers,
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

        # Default price: use customer's default_pricing_level if no price entered
        price_level_to_key = {
            "retail": "retail_price_ex_gst",
            "wholesale": "wholesale_price_ex_gst",
            "distributor": "distributor_price_ex_gst",
            "counter": "counter_price_ex_gst",
            "trade": "trade_price_ex_gst",
            "contract": "contract_price_ex_gst",
            "industrial": "industrial_price_ex_gst",
        }
        default_price_key = "retail_price_ex_gst"
        if customer_id and customers:
            for c in customers:
                if c.get("id") == customer_id:
                    level = (c.get("default_pricing_level") or "").strip().lower()
                    if level and level in price_level_to_key:
                        default_price_key = price_level_to_key[level]
                    break

        qty_decimal = Decimal(str(qty))
        unit_price_ex = (
            Decimal(str(unit_price))
            if unit_price is not None
            else Decimal(
                str(
                    product.get(
                        default_price_key, product.get("retail_price_ex_gst", "0")
                    )
                )
            )
            if product
            else Decimal("0")
        )
        discount_ex = Decimal(str(discount)) if discount else Decimal("0")
        effective_price_ex = max(Decimal("0"), unit_price_ex - discount_ex)
        # Always derive inc GST from the entered (effective) ex GST price so totals are correct
        unit_price_inc = (effective_price_ex * Decimal("1.1")).quantize(Decimal("0.01"))

        line_total_ex = (effective_price_ex * qty_decimal).quantize(Decimal("0.01"))
        line_total_inc = (unit_price_inc * qty_decimal).quantize(Decimal("0.01"))

        product_description = (product.get("name") or "") if product else ""
        code = (product.get("sku") or "") if product else str(product_id)
        new_line = {
            "product_id": product_id,
            "code": code,
            "product_label": label,
            "product_description": product_description,
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

    # ------------------------------------------------------------------ #
    # New order: edit line modal open + fill
    # ------------------------------------------------------------------ #
    @app.callback(
        [
            Output("sales-new-order-edit-line-modal", "is_open"),
            Output("sales-new-order-edit-line-index", "data"),
            Output("sales-new-order-edit-code", "value"),
            Output("sales-new-order-edit-qty", "value"),
            Output("sales-new-order-edit-price", "value"),
            Output("sales-new-order-edit-discount", "value"),
        ],
        [
            Input("sales-order-form-edit-line", "n_clicks"),
            Input("sales-new-order-edit-line-cancel", "n_clicks"),
            Input("sales-new-order-edit-line-save", "n_clicks"),
        ],
        [
            State("sales-new-order-edit-line-modal", "is_open"),
            State("sales-new-order-edit-line-index", "data"),
            State("sales-order-form-lines-store", "data"),
            State("sales-order-form-lines-table", "selected_rows"),
        ],
        prevent_initial_call=True,
    )
    def new_order_edit_line_modal_open(
        edit_clicks,
        cancel_clicks,
        save_clicks,
        is_open,
        edit_index,
        lines,
        selected_rows,
    ):
        if not callback_context.triggered:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"]
        if (
            "sales-new-order-edit-line-cancel" in trigger
            or "sales-new-order-edit-line-save" in trigger
        ):
            return False, None, no_update, no_update, no_update, no_update
        if (
            "sales-order-form-edit-line" in trigger
            and selected_rows
            and lines
            and 0 <= selected_rows[0] < len(lines)
        ):
            row = lines[selected_rows[0]]
            return (
                True,
                selected_rows[0],
                row.get("code", ""),
                row.get("qty"),
                row.get("unit_price_ex_gst"),
                row.get("discount_ex_gst"),
            )
        return no_update, no_update, no_update, no_update, no_update, no_update

    @app.callback(
        [
            Output("sales-order-form-lines-store", "data", allow_duplicate=True),
            Output("sales-order-form-lines-table", "data", allow_duplicate=True),
            Output("sales-new-order-edit-line-modal", "is_open", allow_duplicate=True),
            Output("sales-new-order-edit-line-index", "data", allow_duplicate=True),
        ],
        Input("sales-new-order-edit-line-save", "n_clicks"),
        [
            State("sales-new-order-edit-line-index", "data"),
            State("sales-order-form-lines-store", "data"),
            State("sales-new-order-edit-qty", "value"),
            State("sales-new-order-edit-price", "value"),
            State("sales-new-order-edit-discount", "value"),
        ],
        prevent_initial_call=True,
    )
    def new_order_edit_line_save(n_clicks, edit_index, lines, qty, price, discount):
        if (
            not n_clicks
            or edit_index is None
            or not lines
            or edit_index < 0
            or edit_index >= len(lines)
        ):
            raise PreventUpdate
        try:
            qty_val = float(Decimal(str(qty or 0)))
            price_val = float(Decimal(str(price or 0)))
            discount_val = float(Decimal(str(discount or 0)))
        except Exception:
            raise PreventUpdate
        effective_ex = max(0, price_val - discount_val)
        line_inc = (Decimal(str(effective_ex)) * Decimal("1.1")).quantize(
            Decimal("0.01")
        )
        line_ex = (Decimal(str(effective_ex)) * Decimal(str(qty_val))).quantize(
            Decimal("0.01")
        )
        line_inc_total = (line_inc * Decimal(str(qty_val))).quantize(Decimal("0.01"))
        updated = list(lines)
        row = dict(updated[edit_index])
        row["qty"] = qty_val
        row["unit_price_ex_gst"] = price_val
        row["unit_price_inc_gst"] = float(line_inc)
        row["discount_ex_gst"] = discount_val
        row["line_total_ex_gst"] = float(line_ex)
        row["line_total_inc_gst"] = float(line_inc_total)
        updated[edit_index] = row
        return updated, updated, False, None

    # ------------------------------------------------------------------ #
    # New order: recalc line totals when table data changes (e.g. qty edited in table)
    # ------------------------------------------------------------------ #
    @app.callback(
        [
            Output("sales-order-form-lines-store", "data", allow_duplicate=True),
            Output("sales-order-form-lines-table", "data", allow_duplicate=True),
        ],
        Input("sales-order-form-lines-table", "data"),
        prevent_initial_call=True,
    )
    def new_order_table_recalc(data):
        if not data:
            return no_update, no_update
        updated = []
        changed = False
        for r in data:
            try:
                qty = float(Decimal(str(r.get("qty") or 0)))
                up = float(Decimal(str(r.get("unit_price_ex_gst") or 0)))
                disc = float(Decimal(str(r.get("discount_ex_gst") or 0)))
            except Exception:
                updated.append(r)
                continue
            effective_ex = max(Decimal("0"), Decimal(str(up)) - Decimal(str(disc)))
            line_ex = (effective_ex * Decimal(str(qty))).quantize(Decimal("0.01"))
            line_inc = (effective_ex * Decimal("1.1") * Decimal(str(qty))).quantize(
                Decimal("0.01")
            )
            new_ex = float(line_ex)
            new_inc = float(line_inc)
            if (
                abs(new_ex - float(r.get("line_total_ex_gst") or 0)) > 0.001
                or abs(new_inc - float(r.get("line_total_inc_gst") or 0)) > 0.001
            ):
                changed = True
            updated.append(
                {
                    **r,
                    "line_total_ex_gst": new_ex,
                    "line_total_inc_gst": new_inc,
                }
            )
        if not changed:
            return no_update, no_update
        return updated, updated

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
            Output("sales-orders-refresh-signal", "data", allow_duplicate=True),
            Output("sales-new-order-modal", "is_open", allow_duplicate=True),
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
            "customer_id": str(customer_id),
            "customer_site_id": str(site_id) if site_id else None,
            "channel_id": str(channel_id),
            "order_date": order_date or datetime.utcnow().date().isoformat(),
            "order_ref": order_ref or None,
            "entered_by": entered_by or None,
            "notes": notes or None,
            "lines": [
                {
                    "product_id": str(line["product_id"]),
                    "qty": float(line["qty"]),
                    "unit_price_ex_gst": float(line["unit_price_ex_gst"]),
                    "unit_price_inc_gst": float(line["unit_price_inc_gst"]),
                    "discount_ex_gst": float(line.get("discount_ex_gst", 0) or 0),
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
            False,  # close new order modal
        )

    # ------------------------------------------------------------------ #
    # Orders table totals
    # ------------------------------------------------------------------ #
    @app.callback(
        Output("sales-orders-table-totals", "children"),
        Input("sales-orders-table", "data"),
        prevent_initial_call=False,
    )
    def update_orders_totals(data):
        if not data:
            return ""
        total_ex = sum(_parse_currency(r.get("total_ex_gst")) for r in data)
        total_inc = sum(_parse_currency(r.get("total_inc_gst")) for r in data)
        total_lal = 0.0
        for r in data:
            lal = r.get("lal", "—")
            if lal and lal != "—":
                try:
                    total_lal += float(lal)
                except Exception:
                    pass
        lal_str = f"{total_lal:.3f}" if total_lal else "—"
        return html.Div(
            [
                html.Span(f"LAL: {lal_str}", className="me-4"),
                html.Span(
                    f"Total (Ex): {_format_currency(total_ex)}", className="me-4"
                ),
                html.Span(f"Total (Inc): {_format_currency(total_inc)}"),
            ],
        )


def _format_currency(value: Any) -> str:
    try:
        return f"${Decimal(str(value)).quantize(Decimal('0.01')):,}"
    except Exception:
        return "$0.00"


def _format_lal(value: Any) -> str:
    if value is None:
        return "—"
    try:
        v = float(Decimal(str(value)))
        return f"{v:.3f}" if v else "—"
    except Exception:
        return "—"


def _parse_currency(s: Any) -> float:
    try:
        return float(str(s).replace("$", "").replace(",", ""))
    except Exception:
        return 0.0


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
        no_update,  # keep modal open on error
    )
