"""Orders sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from apps.vndmanuf_sales.ui.components import date_range_picker, filter_dropdown


def layout():
    return html.Div(
        [
            dcc.Store(id="sales-order-form-lines-store", data=[]),
            dcc.Store(id="sales-customers-store", data=[]),
            dcc.Store(id="sales-products-store", data=[]),
            dcc.Store(id="sales-channels-store", data=[]),
            dcc.Store(id="sales-orders-refresh-signal", data=0),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Refresh Orders",
                            id="sales-orders-refresh",
                            color="secondary",
                            className="mb-3",
                        ),
                        width="auto",
                    ),
                ]
            ),
            _filters_card(),
            _orders_table_card(),
            _order_form_card(),
        ],
        className="sales-orders-tab",
    )


def _filters_card():
    return dbc.Card(
        [
            dbc.CardHeader(html.H6("Filters", className="mb-0")),
            dbc.CardBody(
                [
                    date_range_picker("sales-orders-date-range", "Order Date"),
                    filter_dropdown("sales-orders-channel-filter", "Channel", []),
                    filter_dropdown("sales-orders-customer-filter", "Customer", []),
                    filter_dropdown("sales-orders-status-filter", "Status", []),
                    filter_dropdown(
                        "sales-orders-tag-filter",
                        "Tag",
                        [],
                        multi=True,
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
    )


def _orders_table_card():
    return dbc.Card(
        [
            dbc.CardHeader(html.H6("Orders", className="mb-0")),
            dbc.CardBody(
                [
                    dash_table.DataTable(
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
                        style_table={"overflowX": "auto"},
                        style_cell={"padding": "0.5rem"},
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                        },
                    )
                ]
            ),
        ],
        className="mb-4 shadow-sm",
    )


def _order_form_card():
    line_columns = [
        {"name": "Product", "id": "product_label"},
        {"name": "Qty", "id": "qty"},
        {"name": "Price (ex GST)", "id": "unit_price_ex_gst"},
        {"name": "Discount", "id": "discount_ex_gst"},
        {"name": "Line Total (ex GST)", "id": "line_total_ex_gst"},
        {"name": "Line Total (inc GST)", "id": "line_total_inc_gst"},
    ]

    return dbc.Card(
        [
            dbc.CardHeader(html.H6("New Sales Order", className="mb-0")),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Dropdown(
                                    id="sales-order-form-customer",
                                    placeholder="Select customer...",
                                ),
                                md=4,
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="sales-order-form-site",
                                    placeholder="Select site...",
                                    clearable=True,
                                ),
                                md=4,
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="sales-order-form-channel",
                                    placeholder="Select channel...",
                                ),
                                md=4,
                            ),
                        ],
                        className="g-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.DatePickerSingle(
                                    id="sales-order-form-date",
                                    display_format="YYYY-MM-DD",
                                ),
                                md=4,
                                className="mt-3",
                            ),
                            dbc.Col(
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText("Order Ref"),
                                        dbc.Input(
                                            id="sales-order-form-ref",
                                            placeholder="Optional reference",
                                        ),
                                    ]
                                ),
                                md=4,
                                className="mt-3",
                            ),
                            dbc.Col(
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText("Entered By"),
                                        dbc.Input(
                                            id="sales-order-form-entered-by",
                                            placeholder="Optional user name",
                                        ),
                                    ]
                                ),
                                md=4,
                                className="mt-3",
                            ),
                        ],
                        className="g-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Textarea(
                                    id="sales-order-form-notes",
                                    placeholder="Order notes...",
                                    rows=3,
                                ),
                                md=12,
                                className="mt-3",
                            ),
                        ]
                    ),
                    html.Hr(className="my-4"),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Dropdown(
                                    id="sales-order-form-product",
                                    placeholder="Select product...",
                                ),
                                md=5,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="sales-order-form-qty",
                                    type="number",
                                    min=0,
                                    step=1,
                                    placeholder="Qty",
                                ),
                                md=2,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="sales-order-form-price",
                                    type="number",
                                    min=0,
                                    step=0.01,
                                    placeholder="Unit price ex GST",
                                ),
                                md=2,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="sales-order-form-discount",
                                    type="number",
                                    min=0,
                                    step=0.01,
                                    placeholder="Discount ex GST",
                                ),
                                md=2,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Add Line",
                                    id="sales-order-form-add-line",
                                    color="primary",
                                ),
                                md=1,
                            ),
                        ],
                        className="g-2 align-items-end mt-2",
                    ),
                    dash_table.DataTable(
                        id="sales-order-form-lines-table",
                        columns=line_columns,
                        data=[],
                        style_table={"overflowX": "auto", "marginTop": "1rem"},
                        style_cell={"padding": "0.5rem"},
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                        },
                        row_selectable="single",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    "Remove Selected Line",
                                    id="sales-order-form-remove-line",
                                    color="danger",
                                    outline=True,
                                    className="mt-3",
                                ),
                                md="auto",
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Clear Lines",
                                    id="sales-order-form-clear",
                                    color="secondary",
                                    outline=True,
                                    className="mt-3",
                                ),
                                md="auto",
                            ),
                        ],
                        className="g-2",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    "Submit Order",
                                    id="sales-order-form-submit",
                                    color="success",
                                    className="mt-4",
                                ),
                                md="auto",
                            ),
                        ]
                    ),
                    dbc.Alert(
                        id="sales-order-form-feedback",
                        is_open=False,
                        className="mt-3",
                    ),
                ]
            ),
        ],
        className="shadow-sm",
    )
