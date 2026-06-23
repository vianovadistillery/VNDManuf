from pathlib import Path

path = Path("apps/vndmanuf_sales/ui/orders_callbacks.py")
text = path.read_text(encoding="utf-8")

start = text.index(
    '    @app.callback(\n        [\n            Output("sales-order-detail-title", "children"),'
)
end = text.index(
    '    @app.callback(\n        [\n            Output("sales-orders-refresh-signal", "data", allow_duplicate=True),\n            Output("sales-order-detail-modal", "is_open", allow_duplicate=True),\n        ],\n        [\n            Input("sales-order-convert-delivery", "n_clicks"),'
)

new_block = r"""    @app.callback(
        [
            Output("sales-order-detail-title", "children"),
            Output("sales-order-detail-meta", "children"),
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
        empty = ("Order", html.Div("Select an order and click Open.", className="text-muted"), [], False, None, [], False, None, "")
        if not order_id:
            return empty
        response = make_api_request("GET", f"/sales/orders/{order_id}")
        if isinstance(response, dict) and response.get("error"):
            return (
                f"Order {order_id[:8]}…",
                html.Div(f"Error: {response['error']}", className="text-danger"),
                [],
                False,
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
        delivery_date = response.get("delivery_date")
        if delivery_date and hasattr(delivery_date, "strftime"):
            delivery_date = delivery_date.strftime("%Y-%m-%d")
        elif isinstance(delivery_date, str) and len(delivery_date) >= 10:
            delivery_date = delivery_date[:10]
        else:
            delivery_date = delivery_date or "—"

        table_data = _build_order_line_rows(lines)
        freight_ex, freight_gst, freight_inc = _normalize_freight(
            response.get("freight_ex_gst"),
            response.get("freight_gst"),
            response.get("freight_inc_gst"),
        )
        commission = response.get("commission_amount")
        distributor = response.get("distributor")
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

        is_converted = bool(response.get("delivery_docket_id"))
        meta = html.Div(
            [
                html.P([html.Strong("Customer: "), customer_name]),
                html.P([html.Strong("Order date: "), (response.get("order_date") or "")[:10]]),
                html.P([html.Strong("PO: "), response.get("po_number") or "—"]),
                html.P(
                    [
                        html.Strong("Delivery #: "),
                        _doc_link(delivery_number, delivery_doc) if delivery_doc else delivery_number,
                    ]
                ),
                html.P([html.Strong("Delivery date: "), delivery_date]),
                html.P(
                    [
                        html.Strong("Invoice #: "),
                        _doc_link(invoice_number, invoice_doc) if invoice_doc else invoice_number,
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
            ]
        )

        footer_state = {
            "has_delivery_doc": bool(delivery_doc),
            "has_picking_doc": bool(picking_doc),
            "has_invoice_doc": bool(invoice_doc),
            "is_converted": is_converted,
        }

        snapshot = {
            "table": table_data,
            "freight_ex": float(freight_ex),
            "freight_gst": float(freight_gst),
            "freight_inc": float(freight_inc),
            "commission": float(_dec_or_zero(commission)) if commission is not None else None,
            "distributor": distributor,
            "payment_date": _iso_date(response.get("payment_date")),
            "payment_reference": response.get("payment_reference"),
            "invoice_date": _iso_date(response.get("invoice_date")),
        }

        return (
            title,
            meta,
            table_data,
            not is_converted,
            footer_state,
            table_data,
            False,
            snapshot,
            summary,
        )

    @app.callback(
        [
            Output("sales-order-freight-ex", "value"),
            Output("sales-order-freight-gst", "value"),
            Output("sales-order-freight-inc", "value"),
            Output("sales-order-commission", "value"),
            Output("sales-order-distributor", "value"),
            Output("sales-order-payment-date", "date"),
            Output("sales-order-payment-ref", "value"),
            Output("sales-order-invoice-date", "date"),
        ],
        Input("sales-open-order-id", "data"),
        Input("sales-order-detail-refresh", "data"),
        prevent_initial_call=False,
    )
    def hydrate_order_adjustments(order_id, _refresh):
        empty = (None, None, None, None, None, None, None, None)
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
            response.get("distributor"),
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
        data_rows = [r for r in data if r.get("line_id")]
        if not data_rows:
            raise PreventUpdate
        edited_col = (active_cell or {}).get("column_id") if active_cell else None
        out_rows, _, _ = _recalc_product_rows(data_rows, prev_data, edited_col)
        if not _product_rows_changed(data_rows, out_rows):
            raise PreventUpdate
        return out_rows, out_rows, True

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
            Input("sales-order-distributor", "value"),
            Input("sales-order-payment-date", "date"),
            Input("sales-order-payment-ref", "value"),
            Input("sales-order-invoice-date", "date"),
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
        distributor,
        payment_date,
        payment_ref,
        invoice_date,
        table_data,
        snapshot,
    ):
        if not table_data:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"] if callback_context.triggered else ""
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

        data_rows = [r for r in table_data if r.get("line_id")]
        lines_ex, lines_inc = _lines_totals_from_table(data_rows)
        summary = _build_order_summary_html(lines_ex, lines_inc, f_ex, f_inc, commission)
        dirty = _form_is_dirty(
            data_rows,
            f_ex,
            f_gst,
            f_inc,
            commission,
            distributor,
            snapshot,
            payment_date=payment_date,
            payment_reference=payment_ref,
            invoice_date=invoice_date,
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
            State("sales-order-freight-ex", "value"),
            State("sales-order-freight-gst", "value"),
            State("sales-order-freight-inc", "value"),
            State("sales-order-commission", "value"),
            State("sales-order-distributor", "value"),
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
        freight_ex,
        freight_gst,
        freight_inc,
        commission,
        distributor,
        payment_date,
        payment_ref,
        invoice_date,
    ):
        if not callback_context.triggered or not order_id:
            raise PreventUpdate
        trigger = callback_context.triggered[0]["prop_id"]
        if not (confirm_clicks or unsaved_save_clicks):
            raise PreventUpdate
        is_converted = bool((footer_state or {}).get("is_converted"))
        payload = {
            "freight_ex_gst": float(_dec_or_zero(freight_ex)),
            "freight_gst": float(_dec_or_zero(freight_gst)),
            "freight_inc_gst": float(_dec_or_zero(freight_inc)),
            "commission_amount": float(_dec_or_zero(commission))
            if commission is not None and commission != ""
            else None,
            "distributor": distributor or None,
            "payment_reference": (payment_ref or "").strip() or None,
        }
        if payment_date:
            payload["payment_date"] = f"{payment_date}T00:00:00"
        if invoice_date:
            payload["invoice_date"] = f"{invoice_date}T00:00:00"
        if not is_converted and table_data:
            data_rows = [r for r in table_data if r.get("line_id")]
            lines_payload = []
            for r in data_rows:
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
            if lines_payload:
                payload["lines"] = lines_payload
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
            return refresh, False, False, False, None, False, "Order saved.", "success", True
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

"""

path.write_text(text[:start] + new_block + text[end:], encoding="utf-8")
print("patched")
