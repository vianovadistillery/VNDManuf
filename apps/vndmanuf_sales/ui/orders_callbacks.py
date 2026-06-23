"""Dash callbacks powering the Sales Orders sub-tab."""

from __future__ import annotations

import base64
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

import requests
from dash import (
    Input,
    Output,
    State,
    callback_context,
    html,
    no_update,
)
from dash.exceptions import PreventUpdate

from apps.vndmanuf_sales.ui.period_filters import register_period_preset_callbacks

STATUS_OPTIONS = [
    {"label": "Draft", "value": "draft"},
    {"label": "Confirmed", "value": "confirmed"},
    {"label": "Fulfilled", "value": "fulfilled"},
    {"label": "Cancelled", "value": "cancelled"},
]

GST_MULTIPLIER = Decimal("1.1")


def register_sales_orders_callbacks(
    app, make_api_request, api_base_url: str = "http://127.0.0.1:8000"
):
    """Register all callbacks for the Sales Orders sub-tab. api_base_url is used for document download (no /api/v1 suffix)."""

    register_period_preset_callbacks(app, prefix="sales-orders")

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
            Output("sales-order-detail-channel", "options"),
            Output("sales-order-detail-add-product", "options"),
        ],
        [
            Input("sales-channels-store", "data"),
            Input("sales-products-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def detail_form_dropdown_options(channels, products):
        channel_options = [
            {"label": channel["name"], "value": channel["id"]}
            for channel in (channels or [])
        ]
        product_options = [
            {
                "label": f"{product.get('sku', '')} – {product.get('name', '')}".strip(
                    " –"
                ),
                "value": product["id"],
            }
            for product in (products or [])
        ]
        return channel_options, product_options

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
            Input("sales-orders-type-filter", "value"),
            Input("sales-orders-date-range", "start_date"),
            Input("sales-orders-date-range", "end_date"),
        ],
        [
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

        params = _orders_list_params(
            customer_filter=customer_filter,
            channel_filter=channel_filter,
            status_filter=status_filter,
            type_filter=type_filter,
            start_date=start_date,
            end_date=end_date,
            include_inactive_filter=include_inactive_filter,
        )
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

    @app.callback(
        [
            Output("sales-orders-products-table", "data"),
            Output("sales-orders-products-totals", "children"),
        ],
        [
            Input("sales-subtabs", "value"),
            Input("sales-orders-refresh", "n_clicks"),
            Input("sales-orders-refresh-signal", "data"),
            Input("sales-orders-include-inactive", "value"),
            Input("sales-orders-customer-filter", "value"),
            Input("sales-orders-channel-filter", "value"),
            Input("sales-orders-status-filter", "value"),
            Input("sales-orders-type-filter", "value"),
            Input("sales-orders-date-range", "start_date"),
            Input("sales-orders-date-range", "end_date"),
        ],
        prevent_initial_call=False,
    )
    def refresh_order_products(
        subtab_value,
        _refresh_clicks,
        _refresh_signal,
        include_inactive_filter,
        customer_filter,
        channel_filter,
        status_filter,
        type_filter,
        start_date,
        end_date,
    ):
        if subtab_value != "sales-orders":
            raise PreventUpdate

        params = _orders_list_params(
            customer_filter=customer_filter,
            channel_filter=channel_filter,
            status_filter=status_filter,
            type_filter=type_filter,
            start_date=start_date,
            end_date=end_date,
            include_inactive_filter=include_inactive_filter,
        )
        response = make_api_request(
            "GET", "/sales/orders/product-summary", params or None
        )
        if not isinstance(response, dict):
            return [], ""

        rows = []
        for row in response.get("rows") or []:
            rows.append(
                {
                    "product_id": row.get("product_id"),
                    "sku": row.get("sku") or "—",
                    "name": row.get("name") or "—",
                    "total_qty": _format_qty(row.get("total_qty")),
                    "order_count": row.get("order_count") or 0,
                    "total_ex_gst": _format_currency(row.get("total_ex_gst")),
                    "total_inc_gst": _format_currency(row.get("total_inc_gst")),
                }
            )

        order_count = response.get("order_count") or 0
        totals = html.Div(
            [
                html.Span(f"Orders: {order_count}", className="me-4"),
                html.Span(
                    f"Total qty: {_format_qty(response.get('total_qty'))}",
                    className="me-4",
                ),
                html.Span(
                    f"Total (Ex): {_format_currency(response.get('total_ex_gst'))}",
                    className="me-4",
                ),
                html.Span(
                    f"Total (Inc): {_format_currency(response.get('total_inc_gst'))}"
                ),
            ],
        )
        return rows, totals

    @app.callback(
        Output("sales-orders-products-report-download", "data"),
        Input("sales-orders-print-products-report", "n_clicks"),
        [
            State("sales-orders-customer-filter", "value"),
            State("sales-orders-channel-filter", "value"),
            State("sales-orders-status-filter", "value"),
            State("sales-orders-type-filter", "value"),
            State("sales-orders-date-range", "start_date"),
            State("sales-orders-date-range", "end_date"),
            State("sales-orders-include-inactive", "value"),
        ],
        prevent_initial_call=True,
    )
    def print_products_report(
        n_clicks,
        customer_filter,
        channel_filter,
        status_filter,
        type_filter,
        start_date,
        end_date,
        include_inactive_filter,
    ):
        if not n_clicks:
            raise PreventUpdate

        params = _orders_list_params(
            customer_filter=customer_filter,
            channel_filter=channel_filter,
            status_filter=status_filter,
            type_filter=type_filter,
            start_date=start_date,
            end_date=end_date,
            include_inactive_filter=include_inactive_filter,
        )
        summary = make_api_request(
            "GET", "/sales/orders/product-summary", params or None
        )
        if not isinstance(summary, dict):
            raise PreventUpdate
        if not summary.get("orders") and not summary.get("rows"):
            raise PreventUpdate

        product_rows = []
        for row in summary.get("rows") or []:
            product_rows.append(
                {
                    "product_id": row.get("product_id"),
                    "sku": row.get("sku"),
                    "name": row.get("name"),
                    "total_qty": row.get("total_qty"),
                    "total_ex_gst": row.get("total_ex_gst"),
                    "total_inc_gst": row.get("total_inc_gst"),
                }
            )
        order_rows = [
            {
                "order_date": row.get("order_date"),
                "order_ref": row.get("order_ref"),
                "po_number": row.get("po_number"),
                "status": row.get("status"),
                "total_ex_gst": row.get("total_ex_gst"),
                "total_inc_gst": row.get("total_inc_gst"),
            }
            for row in (summary.get("orders") or [])
        ]

        gen = make_api_request(
            "POST",
            "/documents/generate",
            {
                "template_name": "Customer_Purchase_Report.docx",
                "doc_type": "customer_purchase_report",
                "customer_id": customer_filter,
                "product_summary_rows": product_rows,
                "product_summary_orders": order_rows,
                "product_summary_order_count": summary.get("order_count") or 0,
                "product_summary_period_start": start_date,
                "product_summary_period_end": end_date,
                "product_summary_total_ex_gst": summary.get("total_ex_gst") or 0,
                "product_summary_total_inc_gst": summary.get("total_inc_gst") or 0,
                "product_summary_total_qty": summary.get("total_qty") or 0,
            },
        )
        if not isinstance(gen, dict) or gen.get("error"):
            raise PreventUpdate
        doc = gen.get("document") or {}
        doc_id = doc.get("id")
        if not doc_id:
            raise PreventUpdate
        try:
            resp = requests.get(
                f"{api_base_url}/api/v1/documents/{doc_id}/download", timeout=60
            )
            if resp.status_code == 200:
                fn = (
                    (gen.get("pdf_path") or "customer_purchase_report.pdf")
                    .split("/")[-1]
                    .split("\\")[-1]
                )
                return dict(
                    content=base64.b64encode(resp.content).decode(),
                    filename=fn,
                    base64=True,
                )
        except Exception:
            pass
        raise PreventUpdate

    # ------------------------------------------------------------------ #
    # Open order detail modal
    # ------------------------------------------------------------------ #
    @app.callback(
        [
            Output("sales-open-order-id", "data"),
            Output("sales-order-detail-modal", "is_open"),
        ],
        Input("sales-orders-open-selected", "n_clicks"),
        [
            State("sales-orders-table", "data"),
            State("sales-orders-table", "selected_rows"),
        ],
        prevent_initial_call=True,
    )
    def open_order_modal(open_clicks, table_data, selected_rows):
        if not open_clicks or not table_data or not selected_rows:
            raise PreventUpdate
        idx = selected_rows[0]
        if 0 <= idx < len(table_data) and table_data[idx].get("order_id"):
            return table_data[idx]["order_id"], True
        raise PreventUpdate

    @app.callback(
        [
            Output("sales-order-unsaved-modal", "is_open"),
            Output("sales-order-detail-modal", "is_open", allow_duplicate=True),
            Output("sales-open-order-id", "data", allow_duplicate=True),
            Output("sales-order-detail-dirty", "data", allow_duplicate=True),
        ],
        [
            Input("sales-order-detail-close", "n_clicks"),
            Input("sales-order-unsaved-discard", "n_clicks"),
            Input("sales-order-unsaved-keep", "n_clicks"),
        ],
        State("sales-order-detail-dirty", "data"),
        prevent_initial_call=True,
    )
    def close_order_modal(close_clicks, discard_clicks, keep_clicks, dirty):
        if not callback_context.triggered:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"]
        if "sales-order-unsaved-keep" in trigger:
            if not (keep_clicks or 0) >= 1:
                raise PreventUpdate
            return False, no_update, no_update, no_update
        if "sales-order-unsaved-discard" in trigger:
            if not (discard_clicks or 0) >= 1:
                raise PreventUpdate
            return False, False, None, False
        if "sales-order-detail-close" in trigger:
            if not (close_clicks or 0) >= 1:
                raise PreventUpdate
            if dirty:
                return True, no_update, no_update, no_update
            return False, False, None, False
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
            Output("sales-order-detail-doc-links", "children"),
            Output("sales-order-detail-customer-name", "children"),
            Output("sales-order-detail-customer-id", "data"),
            Output("sales-order-detail-invoice-number", "children"),
            Output("sales-order-detail-table", "data"),
            Output("sales-order-detail-table", "editable"),
            Output("sales-order-detail-footer-state", "data"),
            Output("sales-order-detail-prev-data", "data"),
            Output("sales-order-detail-dirty", "data"),
            Output("sales-order-detail-snapshot", "data"),
            Output("sales-order-detail-summary", "children"),
        ],
        Input("sales-open-order-id", "data"),
        Input("sales-order-detail-refresh", "data"),
        State("sales-customers-store", "data"),
        prevent_initial_call=False,
    )
    def load_order_detail(order_id, _refresh, customers_store):
        empty = (
            "Order",
            "",
            "—",
            None,
            "",
            [],
            True,
            None,
            [],
            False,
            None,
            "",
        )
        if not order_id:
            return empty
        response = make_api_request("GET", f"/sales/orders/{order_id}")
        if isinstance(response, dict) and response.get("error"):
            return (
                f"Order {order_id[:8]}…",
                html.Div(f"Error: {response['error']}", className="text-danger"),
                "—",
                None,
                "",
                [],
                True,
                None,
                [],
                False,
                None,
                "",
            )

        order_ref = response.get("order_ref") or response.get("id", "")[:8]
        title = f"Order {order_ref}"
        cid = response.get("customer_id")
        customer_name = next(
            (c.get("name", cid) for c in (customers_store or []) if c.get("id") == cid),
            cid or "—",
        )
        lines = response.get("lines") or []
        table_data = _build_order_line_rows(lines)
        freight_ex, freight_gst, freight_inc = _normalize_freight(
            response.get("freight_ex_gst"),
            response.get("freight_gst"),
            response.get("freight_inc_gst"),
        )
        commission = response.get("commission_amount")
        lines_ex, lines_inc = _lines_totals_from_table(table_data)
        summary = _build_order_summary_html(
            lines_ex, lines_inc, freight_ex, freight_inc, commission
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

        doc_links = html.Div(
            [
                html.Div(
                    [
                        html.Strong("Delivery #: "),
                        _doc_link(delivery_number, delivery_doc)
                        if delivery_doc
                        else delivery_number,
                    ],
                    className="mb-1",
                ),
                html.Div(
                    [
                        html.Strong("Invoice #: "),
                        _doc_link(invoice_number, invoice_doc)
                        if invoice_doc
                        else invoice_number,
                    ],
                ),
            ]
        )
        invoice_meta = (
            f"Invoice: {invoice_number}"
            if invoice_number and invoice_number != "—"
            else "No invoice linked yet"
        )

        is_converted = bool(response.get("delivery_docket_id"))
        footer_state = {
            "has_delivery_doc": bool(delivery_doc),
            "has_picking_doc": bool(picking_doc),
            "has_invoice_doc": bool(invoice_doc),
            "is_converted": is_converted,
            "invoice_id": response.get("invoice_id"),
            "delivery_docket_id": response.get("delivery_docket_id"),
        }

        snapshot = {
            "table": table_data,
            "freight_ex": float(freight_ex),
            "freight_gst": float(freight_gst),
            "freight_inc": float(freight_inc),
            "commission": float(_dec_or_zero(commission))
            if commission is not None
            else None,
            "payment_date": _iso_date(response.get("payment_date")),
            "payment_reference": response.get("payment_reference"),
            "invoice_date": _iso_date(response.get("invoice_date")),
            "channel_id": response.get("channel_id"),
            "order_ref": response.get("order_ref"),
            "po_number": response.get("po_number"),
            "order_date": _iso_date(response.get("order_date")),
            "delivery_date": _iso_date(response.get("delivery_date")),
            "status": response.get("status"),
            "order_discount_ex_gst": float(
                _dec_or_zero(response.get("order_discount_ex_gst"))
            ),
            "entered_by": response.get("entered_by"),
            "notes": response.get("notes"),
            "paid": bool(response.get("paid")),
        }

        return (
            title,
            doc_links,
            customer_name,
            cid,
            invoice_meta,
            table_data,
            True,
            footer_state,
            table_data,
            False,
            snapshot,
            summary,
        )

    @app.callback(
        [
            Output("sales-order-detail-channel", "value"),
            Output("sales-order-detail-order-ref", "value"),
            Output("sales-order-detail-po", "value"),
            Output("sales-order-detail-order-date", "date"),
            Output("sales-order-detail-delivery-date", "date"),
            Output("sales-order-detail-status", "value"),
            Output("sales-order-detail-discount", "value"),
            Output("sales-order-detail-entered-by", "value"),
            Output("sales-order-detail-notes", "value"),
            Output("sales-order-detail-paid", "value"),
        ],
        Input("sales-open-order-id", "data"),
        Input("sales-order-detail-refresh", "data"),
        prevent_initial_call=False,
    )
    def hydrate_order_header(order_id, _refresh):
        empty = (None, None, None, None, None, None, None, None, None, [])
        if not order_id:
            return empty
        response = make_api_request("GET", f"/sales/orders/{order_id}")
        if isinstance(response, dict) and response.get("error"):
            return empty
        paid_val = ["paid"] if response.get("paid") else []
        discount = response.get("order_discount_ex_gst")
        return (
            response.get("channel_id"),
            response.get("order_ref"),
            response.get("po_number"),
            _iso_date(response.get("order_date")),
            _iso_date(response.get("delivery_date")),
            response.get("status") or "confirmed",
            float(_dec_or_zero(discount)) if discount is not None else None,
            response.get("entered_by"),
            response.get("notes"),
            paid_val,
        )

    @app.callback(
        [
            Output("sales-order-freight-ex", "value"),
            Output("sales-order-freight-gst", "value"),
            Output("sales-order-freight-inc", "value"),
            Output("sales-order-commission", "value"),
            Output("sales-order-payment-date", "date"),
            Output("sales-order-payment-ref", "value"),
            Output("sales-order-invoice-date", "date"),
        ],
        Input("sales-open-order-id", "data"),
        Input("sales-order-detail-refresh", "data"),
        prevent_initial_call=False,
    )
    def hydrate_order_adjustments(order_id, _refresh):
        empty = (None, None, None, None, None, None, None)
        if not order_id:
            return empty
        response = make_api_request("GET", f"/sales/orders/{order_id}")
        if isinstance(response, dict) and response.get("error"):
            return empty
        freight_ex, freight_gst, freight_inc = _normalize_freight(
            response.get("freight_ex_gst"),
            response.get("freight_gst"),
            response.get("freight_inc_gst"),
        )
        commission = response.get("commission_amount")
        return (
            float(freight_ex),
            float(freight_gst),
            float(freight_inc),
            float(_dec_or_zero(commission)) if commission is not None else None,
            _iso_date(response.get("payment_date")),
            response.get("payment_reference"),
            _iso_date(response.get("invoice_date")),
        )

    @app.callback(
        [
            Output("sales-order-print-delivery", "disabled"),
            Output("sales-order-print-picking", "disabled"),
            Output("sales-order-print-invoice", "disabled"),
        ],
        Input("sales-order-detail-footer-state", "data"),
        prevent_initial_call=False,
    )
    def apply_order_detail_footer_state(state):
        if not state:
            return True, True, True
        return (
            bool(state.get("has_delivery_doc")),
            bool(state.get("has_picking_doc")),
            bool(state.get("has_invoice_doc")),
        )

    @app.callback(
        [
            Output("sales-order-detail-table", "data", allow_duplicate=True),
            Output("sales-order-detail-prev-data", "data", allow_duplicate=True),
            Output("sales-order-detail-dirty", "data", allow_duplicate=True),
        ],
        Input("sales-order-detail-table", "data_timestamp"),
        [
            State("sales-order-detail-table", "data"),
            State("sales-order-detail-prev-data", "data"),
            State("sales-order-detail-table", "active_cell"),
            State("sales-open-order-id", "data"),
        ],
        prevent_initial_call=True,
    )
    def order_lines_recalc(_ts, data, prev_data, active_cell, order_id):
        if not order_id or not data:
            raise PreventUpdate
        data_rows = [r for r in data if r.get("product_id")]
        if not data_rows:
            raise PreventUpdate
        edited_col = (active_cell or {}).get("column_id") if active_cell else None
        out_rows, _, _ = _recalc_product_rows(data_rows, prev_data, edited_col)
        if not _product_rows_changed(data_rows, out_rows):
            raise PreventUpdate
        return out_rows, out_rows, True

    @app.callback(
        [
            Output("sales-order-detail-table", "data", allow_duplicate=True),
            Output("sales-order-detail-prev-data", "data", allow_duplicate=True),
            Output("sales-order-detail-dirty", "data", allow_duplicate=True),
            Output("sales-order-detail-summary", "children", allow_duplicate=True),
            Output("sales-order-detail-add-product", "value"),
            Output("sales-order-detail-add-qty", "value"),
            Output("sales-order-detail-add-price", "value"),
            Output(
                "sales-order-detail-line-feedback", "children", allow_duplicate=True
            ),
            Output("sales-order-detail-line-feedback", "color", allow_duplicate=True),
            Output("sales-order-detail-line-feedback", "is_open", allow_duplicate=True),
        ],
        Input("sales-order-detail-add-line", "n_clicks"),
        [
            State("sales-order-detail-add-product", "value"),
            State("sales-order-detail-add-qty", "value"),
            State("sales-order-detail-add-price", "value"),
            State("sales-order-detail-table", "data"),
            State("sales-order-detail-snapshot", "data"),
            State("sales-products-store", "data"),
            State("sales-order-detail-customer-id", "data"),
            State("sales-customers-store", "data"),
            State("sales-order-freight-ex", "value"),
            State("sales-order-freight-inc", "value"),
            State("sales-order-commission", "value"),
        ],
        prevent_initial_call=True,
    )
    def add_detail_line(
        n_clicks,
        product_id,
        qty,
        unit_price,
        table_data,
        snapshot,
        products,
        customer_id,
        customers,
        freight_ex,
        freight_inc,
        commission,
    ):
        if not n_clicks:
            raise PreventUpdate
        if not product_id or not qty:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                product_id,
                qty,
                unit_price,
                "Select a product and quantity.",
                "warning",
                True,
            )
        new_row = _make_new_detail_line_row(
            product_id,
            products,
            qty,
            unit_price,
            customer_id,
            customers,
            make_api_request,
        )
        updated = list(table_data or [])
        updated.append(new_row)
        out_rows, lines_ex, lines_inc = _recalc_product_rows(updated, updated, None)
        f_ex, _, f_inc = _normalize_freight(freight_ex, None, freight_inc)
        summary = _build_order_summary_html(
            lines_ex, lines_inc, f_ex, f_inc, commission
        )
        dirty = _form_is_dirty(
            out_rows, f_ex, Decimal("0"), f_inc, commission, snapshot
        )
        return (
            out_rows,
            out_rows,
            dirty,
            summary,
            None,
            None,
            None,
            "Line added.",
            "success",
            True,
        )

    @app.callback(
        [
            Output("sales-order-detail-table", "data", allow_duplicate=True),
            Output("sales-order-detail-prev-data", "data", allow_duplicate=True),
            Output("sales-order-detail-table", "selected_rows", allow_duplicate=True),
            Output("sales-order-detail-dirty", "data", allow_duplicate=True),
            Output("sales-order-detail-summary", "children", allow_duplicate=True),
            Output(
                "sales-order-detail-line-feedback", "children", allow_duplicate=True
            ),
            Output("sales-order-detail-line-feedback", "color", allow_duplicate=True),
            Output("sales-order-detail-line-feedback", "is_open", allow_duplicate=True),
        ],
        Input("sales-order-detail-remove-line", "n_clicks"),
        [
            State("sales-order-detail-table", "data"),
            State("sales-order-detail-table", "selected_rows"),
            State("sales-order-detail-snapshot", "data"),
            State("sales-order-freight-ex", "value"),
            State("sales-order-freight-inc", "value"),
            State("sales-order-commission", "value"),
        ],
        prevent_initial_call=True,
    )
    def remove_detail_line(
        n_clicks,
        table_data,
        selected_rows,
        snapshot,
        freight_ex,
        freight_inc,
        commission,
    ):
        if not n_clicks or not table_data:
            raise PreventUpdate
        if not selected_rows:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                "Select a line to remove.",
                "warning",
                True,
            )
        idx = selected_rows[0]
        if idx < 0 or idx >= len(table_data):
            raise PreventUpdate
        updated = [r for i, r in enumerate(table_data) if i != idx]
        out_rows, lines_ex, lines_inc = _recalc_product_rows(updated, updated, None)
        f_ex, _, f_inc = _normalize_freight(freight_ex, None, freight_inc)
        summary = _build_order_summary_html(
            lines_ex, lines_inc, f_ex, f_inc, commission
        )
        dirty = _form_is_dirty(
            out_rows, f_ex, Decimal("0"), f_inc, commission, snapshot
        )
        return out_rows, out_rows, [], dirty, summary, "Line removed.", "success", True

    @app.callback(
        [
            Output("sales-order-freight-ex", "value", allow_duplicate=True),
            Output("sales-order-freight-gst", "value", allow_duplicate=True),
            Output("sales-order-freight-inc", "value", allow_duplicate=True),
            Output("sales-order-detail-summary", "children", allow_duplicate=True),
            Output("sales-order-detail-dirty", "data", allow_duplicate=True),
        ],
        [
            Input("sales-order-freight-ex", "value"),
            Input("sales-order-freight-gst", "value"),
            Input("sales-order-freight-inc", "value"),
            Input("sales-order-commission", "value"),
            Input("sales-order-payment-date", "date"),
            Input("sales-order-payment-ref", "value"),
            Input("sales-order-invoice-date", "date"),
            Input("sales-order-detail-channel", "value"),
            Input("sales-order-detail-order-ref", "value"),
            Input("sales-order-detail-po", "value"),
            Input("sales-order-detail-order-date", "date"),
            Input("sales-order-detail-delivery-date", "date"),
            Input("sales-order-detail-status", "value"),
            Input("sales-order-detail-discount", "value"),
            Input("sales-order-detail-entered-by", "value"),
            Input("sales-order-detail-notes", "value"),
            Input("sales-order-detail-paid", "value"),
        ],
        [
            State("sales-order-detail-table", "data"),
            State("sales-order-detail-snapshot", "data"),
        ],
        prevent_initial_call=True,
    )
    def order_adjustments_recalc(
        freight_ex,
        freight_gst,
        freight_inc,
        commission,
        payment_date,
        payment_ref,
        invoice_date,
        channel_id,
        order_ref,
        po_number,
        order_date,
        delivery_date,
        status,
        order_discount,
        entered_by,
        notes,
        paid_values,
        table_data,
        snapshot,
    ):
        if not snapshot:
            raise PreventUpdate
        trigger = (
            callback_context.triggered[0]["prop_id"]
            if callback_context.triggered
            else ""
        )
        f_ex, f_gst, f_inc = _normalize_freight(freight_ex, freight_gst, freight_inc)
        if "sales-order-freight-ex" in trigger and freight_ex not in (None, ""):
            f_ex = _dec_or_zero(freight_ex)
            f_inc = _inc_from_ex(f_ex)
            f_gst = f_inc - f_ex
            freight_out = (float(f_ex), float(f_gst), float(f_inc))
        elif "sales-order-freight-inc" in trigger and freight_inc not in (None, ""):
            f_inc = _dec_or_zero(freight_inc)
            f_ex = _ex_from_inc(f_inc)
            f_gst = f_inc - f_ex
            freight_out = (float(f_ex), float(f_gst), float(f_inc))
        elif "sales-order-freight-gst" in trigger and freight_gst not in (None, ""):
            f_gst = _dec_or_zero(freight_gst)
            f_ex = (f_gst / Decimal("0.1")).quantize(Decimal("0.01"))
            f_inc = f_ex + f_gst
            freight_out = (float(f_ex), float(f_gst), float(f_inc))
        else:
            freight_out = (no_update, no_update, no_update)

        data_rows = [
            r
            for r in (table_data or (snapshot or {}).get("table") or [])
            if r.get("product_id")
        ]
        lines_ex, lines_inc = _lines_totals_from_table(data_rows)
        summary = _build_order_summary_html(
            lines_ex, lines_inc, f_ex, f_inc, commission
        )
        dirty = _form_is_dirty(
            data_rows,
            f_ex,
            f_gst,
            f_inc,
            commission,
            snapshot,
            payment_date=payment_date,
            payment_reference=payment_ref,
            invoice_date=invoice_date,
            channel_id=channel_id,
            order_ref=order_ref,
            po_number=po_number,
            order_date=order_date,
            delivery_date=delivery_date,
            status=status,
            order_discount=order_discount,
            entered_by=entered_by,
            notes=notes,
            paid="paid" in (paid_values or []),
        )
        return (*freight_out, summary, dirty)

    @app.callback(
        Output("sales-order-save-confirm-modal", "is_open"),
        [
            Input("sales-order-detail-save", "n_clicks"),
            Input("sales-order-save-cancel", "n_clicks"),
        ],
        State("sales-order-save-confirm-modal", "is_open"),
        prevent_initial_call=True,
    )
    def order_save_confirm_modal(save_clicks, cancel_clicks, is_open):
        if not callback_context.triggered:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"]
        if "sales-order-detail-save" in trigger and (save_clicks or 0) >= 1:
            return True
        if "sales-order-save-cancel" in trigger:
            return False
        raise PreventUpdate

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
        [
            Output("sales-order-detail-refresh", "data", allow_duplicate=True),
            Output("sales-order-detail-dirty", "data", allow_duplicate=True),
            Output("sales-order-unsaved-modal", "is_open", allow_duplicate=True),
            Output("sales-order-detail-modal", "is_open", allow_duplicate=True),
            Output("sales-open-order-id", "data", allow_duplicate=True),
            Output("sales-order-save-confirm-modal", "is_open", allow_duplicate=True),
            Output("sales-order-detail-feedback", "children", allow_duplicate=True),
            Output("sales-order-detail-feedback", "color", allow_duplicate=True),
            Output("sales-order-detail-feedback", "is_open", allow_duplicate=True),
        ],
        [
            Input("sales-order-save-confirm", "n_clicks"),
            Input("sales-order-unsaved-save", "n_clicks"),
        ],
        [
            State("sales-open-order-id", "data"),
            State("sales-order-detail-table", "data"),
            State("sales-order-detail-footer-state", "data"),
            State("sales-order-detail-channel", "value"),
            State("sales-order-detail-order-ref", "value"),
            State("sales-order-detail-po", "value"),
            State("sales-order-detail-order-date", "date"),
            State("sales-order-detail-delivery-date", "date"),
            State("sales-order-detail-status", "value"),
            State("sales-order-detail-discount", "value"),
            State("sales-order-detail-entered-by", "value"),
            State("sales-order-detail-notes", "value"),
            State("sales-order-detail-paid", "value"),
            State("sales-order-freight-ex", "value"),
            State("sales-order-freight-gst", "value"),
            State("sales-order-freight-inc", "value"),
            State("sales-order-commission", "value"),
            State("sales-order-payment-date", "date"),
            State("sales-order-payment-ref", "value"),
            State("sales-order-invoice-date", "date"),
        ],
        prevent_initial_call=True,
    )
    def order_detail_save(
        confirm_clicks,
        unsaved_save_clicks,
        order_id,
        table_data,
        footer_state,
        channel_id,
        order_ref,
        po_number,
        order_date,
        delivery_date,
        status,
        order_discount,
        entered_by,
        notes,
        paid_values,
        freight_ex,
        freight_gst,
        freight_inc,
        commission,
        payment_date,
        payment_ref,
        invoice_date,
    ):
        if not callback_context.triggered or not order_id:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"]
        if not (confirm_clicks or unsaved_save_clicks):
            raise PreventUpdate
        payload = {
            "channel_id": channel_id or None,
            "order_ref": (order_ref or "").strip() or None,
            "po_number": (po_number or "").strip() or None,
            "order_date": f"{order_date}T00:00:00" if order_date else None,
            "delivery_date": f"{delivery_date}T00:00:00" if delivery_date else None,
            "status": status or "confirmed",
            "order_discount_ex_gst": float(_dec_or_zero(order_discount)),
            "entered_by": (entered_by or "").strip() or None,
            "notes": (notes or "").strip() or None,
            "paid": "paid" in (paid_values or []),
            "freight_ex_gst": float(_dec_or_zero(freight_ex)),
            "freight_gst": float(_dec_or_zero(freight_gst)),
            "freight_inc_gst": float(_dec_or_zero(freight_inc)),
            "commission_amount": float(_dec_or_zero(commission))
            if commission is not None and commission != ""
            else None,
            "payment_reference": (payment_ref or "").strip() or None,
            "payment_date": f"{payment_date}T00:00:00" if payment_date else None,
            "invoice_date": f"{invoice_date}T00:00:00" if invoice_date else None,
        }
        lines_payload = _lines_payload_from_table(table_data)
        if lines_payload:
            payload["lines"] = lines_payload
        elif table_data is not None:
            payload["lines"] = []
        r = make_api_request("PUT", f"/sales/orders/{order_id}", payload)
        if isinstance(r, dict) and r.get("error"):
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                f"Save failed: {r.get('error')}",
                "danger",
                True,
            )
        refresh = datetime.utcnow().timestamp()
        if "sales-order-unsaved-save" in trigger:
            return (
                refresh,
                False,
                False,
                False,
                None,
                False,
                "Order saved.",
                "success",
                True,
            )
        return (
            refresh,
            False,
            no_update,
            no_update,
            no_update,
            False,
            "Order saved.",
            "success",
            True,
        )

    @app.callback(
        [
            Output("sales-convert-invoice-modal", "is_open"),
            Output("sales-convert-invoice-date", "date"),
            Output("sales-convert-invoice-number", "value"),
            Output("sales-convert-invoice-feedback", "children", allow_duplicate=True),
            Output("sales-convert-invoice-feedback", "color", allow_duplicate=True),
            Output("sales-convert-invoice-feedback", "is_open", allow_duplicate=True),
        ],
        Input("sales-order-convert-invoice", "n_clicks"),
        [
            State("sales-open-order-id", "data"),
            State("sales-channels-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def open_convert_invoice_modal(n_clicks, order_id, channels):
        if not (n_clicks or 0) >= 1 or not order_id:
            raise PreventUpdate
        response = make_api_request("GET", f"/sales/orders/{order_id}")
        if isinstance(response, dict) and response.get("error"):
            return (
                True,
                datetime.utcnow().date().isoformat(),
                "",
                f"Could not load order: {response['error']}",
                "danger",
                True,
            )
        if response.get("invoice_id"):
            return (
                True,
                datetime.utcnow().date().isoformat(),
                "",
                "This order already has an invoice.",
                "warning",
                True,
            )
        channel_id = response.get("channel_id")
        channel_code = ""
        for ch in channels or []:
            if ch.get("id") == channel_id:
                channel_code = (ch.get("code") or ch.get("name") or "").upper()
                break
        docket_number = response.get("delivery_docket_number")
        suggested = _suggest_invoice_number(channel_code, docket_number)
        today = datetime.utcnow().date().isoformat()
        return True, today, suggested or "", "", "success", False

    @app.callback(
        [
            Output("sales-convert-invoice-modal", "is_open", allow_duplicate=True),
            Output("sales-orders-refresh-signal", "data", allow_duplicate=True),
            Output("sales-order-detail-refresh", "data", allow_duplicate=True),
            Output("sales-convert-invoice-feedback", "children", allow_duplicate=True),
            Output("sales-convert-invoice-feedback", "color", allow_duplicate=True),
            Output("sales-convert-invoice-feedback", "is_open", allow_duplicate=True),
        ],
        [
            Input("sales-convert-invoice-confirm", "n_clicks"),
            Input("sales-convert-invoice-cancel", "n_clicks"),
        ],
        [
            State("sales-open-order-id", "data"),
            State("sales-convert-invoice-number", "value"),
            State("sales-convert-invoice-date", "date"),
            State("sales-order-detail-footer-state", "data"),
        ],
        prevent_initial_call=True,
    )
    def confirm_convert_invoice_modal(
        confirm_clicks,
        cancel_clicks,
        order_id,
        invoice_number,
        invoice_date,
        footer_state,
    ):
        if not callback_context.triggered:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"]
        if "sales-convert-invoice-cancel" in trigger:
            return False, no_update, no_update, "", "success", False
        if not (confirm_clicks or 0) >= 1 or not order_id:
            raise PreventUpdate
        payload = {}
        if invoice_number and str(invoice_number).strip():
            payload["invoice_number"] = str(invoice_number).strip()
        if invoice_date:
            payload["invoice_date"] = f"{invoice_date}T00:00:00"
        docket_id = (footer_state or {}).get("delivery_docket_id")
        if not docket_id:
            order_resp = make_api_request("GET", f"/sales/orders/{order_id}")
            if isinstance(order_resp, dict):
                docket_id = order_resp.get("delivery_docket_id")
        if docket_id:
            payload["delivery_docket_id"] = docket_id
        r = make_api_request(
            "POST", f"/sales/orders/{order_id}/convert-to-invoice", payload
        )
        if isinstance(r, dict) and r.get("error"):
            return (
                True,
                no_update,
                no_update,
                f"Create invoice failed: {r.get('error')}",
                "danger",
                True,
            )
        ts = datetime.utcnow().timestamp()
        return False, ts, ts, "Invoice created.", "success", True

    @app.callback(
        [
            Output("sales-orders-refresh-signal", "data", allow_duplicate=True),
            Output("sales-order-detail-modal", "is_open", allow_duplicate=True),
        ],
        [
            Input("sales-order-convert-delivery", "n_clicks"),
            Input("sales-order-mark-paid", "n_clicks"),
        ],
        [State("sales-open-order-id", "data")],
        prevent_initial_call=True,
    )
    def order_detail_actions(conv_delivery, mark_paid, order_id):
        if not order_id or not callback_context.triggered:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"]
        if "sales-order-convert-delivery" in trigger:
            if not (conv_delivery or 0) >= 1:
                raise PreventUpdate
            r = make_api_request(
                "POST", f"/sales/orders/{order_id}/convert-to-delivery", {}
            )
            if isinstance(r, dict) and r.get("error"):
                return no_update, no_update
            return (datetime.utcnow().timestamp(), False)
        if "sales-order-mark-paid" in trigger:
            if not (mark_paid or 0) >= 1:
                raise PreventUpdate
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

        qty_decimal = Decimal(str(qty))
        unit_price_ex = None
        if unit_price is not None and unit_price != "":
            unit_price_ex = Decimal(str(unit_price))
        elif customer_id and product_id:
            resolved = make_api_request(
                "GET",
                "/sales/pricing/resolve",
                {"customer_id": customer_id, "product_id": product_id},
            )
            if isinstance(resolved, dict) and not resolved.get("error"):
                unit_price_ex = Decimal(str(resolved.get("unit_price_ex_gst", 0)))
        if unit_price_ex is None:
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
            unit_price_ex = (
                Decimal(
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


def _orders_list_params(
    *,
    customer_filter,
    channel_filter,
    status_filter,
    type_filter,
    start_date,
    end_date,
    include_inactive_filter,
) -> Dict[str, Any]:
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
        if "paid" in type_filter:
            params["paid"] = True
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if include_inactive_filter and "include_inactive" in include_inactive_filter:
        params["include_deleted"] = True
    return params


def _format_qty(value: Any) -> str:
    if value is None:
        return "0"
    try:
        n = float(value)
        return str(int(n)) if n == int(n) else f"{n:g}"
    except Exception:
        return "0"


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


def _make_new_detail_line_row(
    product_id,
    products,
    qty,
    unit_price=None,
    customer_id=None,
    customers=None,
    make_api_request=None,
):
    product_lookup = {product["id"]: product for product in (products or [])}
    product = product_lookup.get(product_id)
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
    unit_ex = None
    if unit_price is not None and unit_price != "":
        unit_ex = Decimal(str(unit_price))
    elif make_api_request and customer_id and product_id:
        resolved = make_api_request(
            "GET",
            "/sales/pricing/resolve",
            {"customer_id": customer_id, "product_id": product_id},
        )
        if isinstance(resolved, dict) and not resolved.get("error"):
            unit_ex = Decimal(str(resolved.get("unit_price_ex_gst", 0)))
            up_inc = resolved.get("unit_price_inc_gst")
            if up_inc is not None:
                unit_inc = Decimal(str(up_inc))
            else:
                unit_inc = _inc_from_ex(unit_ex)
            line_ex = (unit_ex * qty_decimal).quantize(Decimal("0.01"))
            line_inc = (unit_inc * qty_decimal).quantize(Decimal("0.01"))
            product_code = (
                (product.get("sku") or str(product_id)) if product else str(product_id)
            )
            return {
                "line_id": str(uuid.uuid4()),
                "product_id": product_id,
                "qty": _qty_display(qty_decimal),
                "product_code": product_code,
                "description": (product.get("name") or "") if product else "",
                "unit_price_ex_gst": float(unit_ex.quantize(Decimal("0.01"))),
                "unit_price_inc_gst": float(unit_inc.quantize(Decimal("0.01"))),
                "unit_price_ex_gst_raw": float(unit_ex),
                "unit_price_inc_gst_raw": float(unit_inc),
                "gst": _format_currency(line_inc - line_ex),
                "line_total_ex_gst": _format_currency(line_ex),
                "line_total_inc_gst": _format_currency(line_inc),
            }
    if unit_ex is None:
        unit_ex = (
            Decimal(
                str(
                    product.get(
                        default_price_key, product.get("retail_price_ex_gst", "0")
                    )
                )
            )
            if product
            else Decimal("0")
        )
    unit_inc = _inc_from_ex(unit_ex)
    line_ex = (unit_ex * qty_decimal).quantize(Decimal("0.01"))
    line_inc = (unit_inc * qty_decimal).quantize(Decimal("0.01"))
    product_code = (
        (product.get("sku") or str(product_id)) if product else str(product_id)
    )
    return {
        "line_id": str(uuid.uuid4()),
        "product_id": product_id,
        "qty": _qty_display(qty_decimal),
        "product_code": product_code,
        "description": (product.get("name") or "") if product else "",
        "unit_price_ex_gst": float(unit_ex.quantize(Decimal("0.01"))),
        "unit_price_inc_gst": float(unit_inc.quantize(Decimal("0.01"))),
        "unit_price_ex_gst_raw": float(unit_ex),
        "unit_price_inc_gst_raw": float(unit_inc),
        "gst": _format_currency(line_inc - line_ex),
        "line_total_ex_gst": _format_currency(line_ex),
        "line_total_inc_gst": _format_currency(line_inc),
    }


def _lines_payload_from_table(table_data):
    lines_payload = []
    for r in table_data or []:
        if not r.get("product_id"):
            continue
        try:
            qty = float(r.get("qty") or 0)
        except (TypeError, ValueError):
            qty = 0
        up_ex = r.get("unit_price_ex_gst_raw")
        if up_ex is None:
            up_ex = r.get("unit_price_ex_gst")
        up_inc = r.get("unit_price_inc_gst_raw")
        if up_inc is None:
            up_inc = r.get("unit_price_inc_gst")
        try:
            up_ex = float(up_ex or 0)
        except (TypeError, ValueError):
            up_ex = 0
        try:
            up_inc = float(up_inc or 0)
        except (TypeError, ValueError):
            up_inc = 0
        if up_inc == 0 and up_ex > 0:
            up_inc = float(_inc_from_ex(Decimal(str(up_ex))))
        lines_payload.append(
            {
                "product_id": str(r.get("product_id")),
                "qty": qty,
                "unit_price_ex_gst": up_ex,
                "unit_price_inc_gst": up_inc,
                "uom": "unit",
            }
        )
    return lines_payload


def _suggest_invoice_number(channel_code: str, docket_number: str | None) -> str | None:
    """ALM channel: DD260050 → A260050 from delivery docket number."""
    if (channel_code or "").upper() != "ALM" or not docket_number:
        return None
    dn = docket_number.strip().upper()
    if dn.startswith("DD"):
        return "A" + dn[2:]
    return None


def _iso_date(value: Any) -> str | None:
    """Normalize API date/datetime strings for DatePickerSingle."""
    if value is None or value == "":
        return None
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, str) and len(value) >= 10:
        return value[:10]
    return None


def _dec_or_zero(value: Any) -> Decimal:
    if value is None or value == "":
        return Decimal("0")
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")


def _ex_from_inc(inc: Decimal) -> Decimal:
    return (inc / GST_MULTIPLIER).quantize(Decimal("0.01"))


def _inc_from_ex(ex: Decimal) -> Decimal:
    return (ex * GST_MULTIPLIER).quantize(Decimal("0.01"))


def _gst_from_ex(ex: Decimal) -> Decimal:
    return (ex * Decimal("0.1")).quantize(Decimal("0.01"))


def _qty_display(val):
    if val is None:
        return ""
    n = float(val)
    return int(n) if n == int(n) else n


def _unit_display(val):
    if val is None:
        return ""
    return float(_dec_or_zero(val).quantize(Decimal("0.01")))


def _build_order_line_rows(lines):
    rows = []
    for order_line in lines:
        ex = _dec_or_zero(order_line.get("line_total_ex_gst"))
        inc = _dec_or_zero(order_line.get("line_total_inc_gst"))
        gst = inc - ex
        unit_ex = _dec_or_zero(order_line.get("unit_price_ex_gst"))
        unit_inc = _dec_or_zero(order_line.get("unit_price_inc_gst"))
        if unit_inc == 0 and unit_ex > 0:
            unit_inc = _inc_from_ex(unit_ex)
        elif unit_ex == 0 and unit_inc > 0:
            unit_ex = _ex_from_inc(unit_inc)
        product_code = (
            order_line.get("product_sku")
            or order_line.get("product_name")
            or (
                str(order_line.get("product_id"))
                if order_line.get("product_id")
                else "—"
            )
        )
        rows.append(
            {
                "line_id": order_line.get("id"),
                "product_id": order_line.get("product_id"),
                "qty": _qty_display(order_line.get("qty")),
                "product_code": product_code,
                "description": order_line.get("product_name") or "",
                "unit_price_ex_gst": _unit_display(unit_ex),
                "unit_price_inc_gst": _unit_display(unit_inc),
                "unit_price_ex_gst_raw": float(unit_ex),
                "unit_price_inc_gst_raw": float(unit_inc),
                "gst": _format_currency(gst),
                "line_total_ex_gst": _format_currency(ex),
                "line_total_inc_gst": _format_currency(inc),
            }
        )
    return rows


def _normalize_freight(ex_val, gst_val, inc_val):
    f_ex = _dec_or_zero(ex_val)
    f_gst = _dec_or_zero(gst_val)
    f_inc = _dec_or_zero(inc_val)
    if f_inc == 0 and f_ex > 0:
        f_inc = _inc_from_ex(f_ex)
        f_gst = f_inc - f_ex
    elif f_ex == 0 and f_inc > 0:
        f_ex = _ex_from_inc(f_inc)
        f_gst = f_inc - f_ex
    elif f_gst == 0 and f_ex > 0:
        f_gst = f_inc - f_ex if f_inc else _gst_from_ex(f_ex)
    return f_ex, f_gst, f_inc


def _lines_totals_from_table(data_rows):
    total_ex = Decimal("0")
    total_inc = Decimal("0")
    for r in data_rows:
        total_ex += _dec_or_zero(_parse_currency(r.get("line_total_ex_gst")))
        total_inc += _dec_or_zero(_parse_currency(r.get("line_total_inc_gst")))
    return total_ex, total_inc


def _build_order_summary_html(lines_ex, lines_inc, freight_ex, freight_inc, commission):
    comm = _dec_or_zero(commission)
    f_ex = _dec_or_zero(freight_ex)
    f_inc = _dec_or_zero(freight_inc)
    net_ex = lines_ex - f_ex - comm
    net_inc = lines_inc - f_inc - comm
    return html.Div(
        [
            html.H6("Summary", className="mb-2"),
            html.Div(
                [
                    html.Span("Sales total (ex)"),
                    html.Strong(_format_currency(lines_ex)),
                ],
                className="d-flex justify-content-between",
            ),
            html.Div(
                [
                    html.Span("Sales total (inc)"),
                    html.Strong(_format_currency(lines_inc)),
                ],
                className="d-flex justify-content-between",
            ),
            html.Div(
                [
                    html.Span("Freight (ex)"),
                    html.Span(_format_currency(f_ex)),
                ],
                className="d-flex justify-content-between text-muted",
            ),
            html.Div(
                [
                    html.Span("Commission (ex)"),
                    html.Span(_format_currency(comm)),
                ],
                className="d-flex justify-content-between text-muted",
            ),
            html.Hr(className="my-2"),
            html.Div(
                [
                    html.Span("Net revenue to VND (ex)"),
                    html.Strong(_format_currency(net_ex)),
                ],
                className="d-flex justify-content-between fw-bold",
            ),
            html.Div(
                [
                    html.Span("Net revenue to VND (inc)"),
                    html.Strong(_format_currency(net_inc)),
                ],
                className="d-flex justify-content-between",
            ),
        ],
        className="d-flex flex-column gap-1",
    )


def _recalc_product_rows(data_rows, prev_data, edited_col):
    prev_by_id = {r.get("line_id"): r for r in (prev_data or []) if r.get("line_id")}
    out_rows = []
    total_ex = Decimal("0")
    total_inc = Decimal("0")
    for r in data_rows:
        try:
            qty = Decimal(str(r.get("qty") or 0))
        except Exception:
            qty = Decimal("0")
        prev = prev_by_id.get(r.get("line_id"), {})
        unit_ex = _dec_or_zero(r.get("unit_price_ex_gst"))
        unit_inc = _dec_or_zero(r.get("unit_price_inc_gst"))
        prev_ex = _dec_or_zero(
            prev.get("unit_price_ex_gst_raw") or prev.get("unit_price_ex_gst")
        )
        prev_inc = _dec_or_zero(
            prev.get("unit_price_inc_gst_raw") or prev.get("unit_price_inc_gst")
        )
        if edited_col == "unit_price_inc_gst" and unit_inc != prev_inc:
            unit_ex = _ex_from_inc(unit_inc)
        elif edited_col == "unit_price_ex_gst" and unit_ex != prev_ex:
            unit_inc = _inc_from_ex(unit_ex)
        elif unit_inc == 0 and unit_ex > 0:
            unit_inc = _inc_from_ex(unit_ex)
        elif unit_ex == 0 and unit_inc > 0:
            unit_ex = _ex_from_inc(unit_inc)
        line_ex = (qty * unit_ex).quantize(Decimal("0.01"))
        if unit_ex > 0:
            ratio = unit_inc / unit_ex
            line_inc = (line_ex * ratio).quantize(Decimal("0.01"))
        else:
            line_inc = (qty * unit_inc).quantize(Decimal("0.01"))
        gst_line = line_inc - line_ex
        total_ex += line_ex
        total_inc += line_inc
        out_rows.append(
            {
                **r,
                "qty": _qty_display(qty),
                "unit_price_ex_gst": float(unit_ex.quantize(Decimal("0.01"))),
                "unit_price_inc_gst": float(unit_inc.quantize(Decimal("0.01"))),
                "unit_price_ex_gst_raw": float(unit_ex),
                "unit_price_inc_gst_raw": float(unit_inc),
                "line_total_ex_gst": _format_currency(line_ex),
                "line_total_inc_gst": _format_currency(line_inc),
                "gst": _format_currency(gst_line),
            }
        )
    return out_rows, total_ex, total_inc


def _product_rows_changed(before, after):
    if len(before) != len(after):
        return True
    keys = (
        "qty",
        "unit_price_ex_gst",
        "unit_price_inc_gst",
        "line_total_ex_gst",
        "line_total_inc_gst",
    )
    for a, b in zip(before, after):
        for k in keys:
            if str(a.get(k, "")) != str(b.get(k, "")):
                return True
    return False


def _form_is_dirty(
    table_rows,
    freight_ex,
    freight_gst,
    freight_inc,
    commission,
    snapshot,
    *,
    payment_date=None,
    payment_reference=None,
    invoice_date=None,
    channel_id=None,
    order_ref=None,
    po_number=None,
    order_date=None,
    delivery_date=None,
    status=None,
    order_discount=None,
    entered_by=None,
    notes=None,
    paid=None,
):
    if not snapshot:
        return True
    snap_table = snapshot.get("table") or []
    if _product_rows_changed(snap_table, table_rows):
        return True
    f_ex, f_gst, f_inc = _normalize_freight(freight_ex, freight_gst, freight_inc)
    if float(f_ex) != float(snapshot.get("freight_ex") or 0):
        return True
    if float(f_gst) != float(snapshot.get("freight_gst") or 0):
        return True
    if float(f_inc) != float(snapshot.get("freight_inc") or 0):
        return True
    comm = (
        float(_dec_or_zero(commission))
        if commission is not None and commission != ""
        else None
    )
    snap_comm = snapshot.get("commission")
    if comm != snap_comm:
        return True
    if _iso_date(payment_date) != _iso_date(snapshot.get("payment_date")):
        return True
    if (payment_reference or "").strip() != (
        snapshot.get("payment_reference") or ""
    ).strip():
        return True
    if _iso_date(invoice_date) != _iso_date(snapshot.get("invoice_date")):
        return True
    if (channel_id or None) != (snapshot.get("channel_id") or None):
        return True
    if (order_ref or "").strip() != (snapshot.get("order_ref") or "").strip():
        return True
    if (po_number or "").strip() != (snapshot.get("po_number") or "").strip():
        return True
    if _iso_date(order_date) != _iso_date(snapshot.get("order_date")):
        return True
    if _iso_date(delivery_date) != _iso_date(snapshot.get("delivery_date")):
        return True
    if (status or None) != (snapshot.get("status") or None):
        return True
    disc = float(_dec_or_zero(order_discount))
    if disc != float(snapshot.get("order_discount_ex_gst") or 0):
        return True
    if (entered_by or "").strip() != (snapshot.get("entered_by") or "").strip():
        return True
    if (notes or "").strip() != (snapshot.get("notes") or "").strip():
        return True
    if bool(paid) != bool(snapshot.get("paid")):
        return True
    return False


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
