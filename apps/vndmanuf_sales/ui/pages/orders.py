"""Orders sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, html

from apps.vndmanuf_sales.ui.components import date_range_picker, filter_dropdown


def layout():
    filters = dbc.Card(
        [
            dbc.CardHeader(html.H6("Filters", className="mb-0")),
            dbc.CardBody(
                [
                    date_range_picker("sales-orders-date-range", "Order Date"),
                    filter_dropdown(
                        "sales-orders-channel-filter",
                        "Channel",
                        [
                            {"label": "Retail", "value": "RETAIL"},
                            {"label": "Venue", "value": "VENUE"},
                            {"label": "Online", "value": "ONLINE"},
                            {"label": "Direct", "value": "DIRECT"},
                        ],
                    ),
                    filter_dropdown(
                        "sales-orders-customer-filter",
                        "Customer",
                        [],
                    ),
                    filter_dropdown(
                        "sales-orders-status-filter",
                        "Status",
                        [
                            {"label": "Draft", "value": "draft"},
                            {"label": "Confirmed", "value": "confirmed"},
                            {"label": "Fulfilled", "value": "fulfilled"},
                            {"label": "Cancelled", "value": "cancelled"},
                        ],
                    ),
                    filter_dropdown(
                        "sales-orders-tag-filter",
                        "Tag",
                        [],
                        multi=True,
                    ),
                ]
            ),
        ],
        className="mb-3 shadow-sm",
    )

    orders_table = dash_table.DataTable(
        id="sales-orders-table",
        columns=[
            {"name": "Order Date", "id": "order_date"},
            {"name": "Order Ref", "id": "order_ref"},
            {"name": "Customer", "id": "customer"},
            {"name": "Channel", "id": "channel"},
            {"name": "Status", "id": "status"},
            {"name": "Total (Ex GST)", "id": "total_ex_gst"},
            {"name": "Total (Inc GST)", "id": "total_inc_gst"},
        ],
        data=[],
        page_size=15,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"padding": "0.5rem"},
        style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
    )

    new_order_button = dbc.Button(
        "New Order",
        id="sales-orders-new-order",
        color="primary",
        className="mb-3",
    )

    modal = dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("New Sales Order")),
            dbc.ModalBody(
                html.Div(
                    [
                        dbc.Alert(
                            "Order wizard coming soon. Import orders via CSV in the Import/Export tab.",
                            color="info",
                        )
                    ]
                )
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="sales-orders-modal-close", className="ms-auto")
            ),
        ],
        id="sales-orders-modal",
        is_open=False,
        centered=True,
    )

    return html.Div(
        [
            filters,
            new_order_button,
            orders_table,
            modal,
        ],
        className="sales-orders-tab",
    )
