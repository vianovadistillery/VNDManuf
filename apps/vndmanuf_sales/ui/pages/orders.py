"""Orders sub-tab layout."""

from __future__ import annotations

from datetime import date, timedelta

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from apps.vndmanuf_sales.ui.components import date_range_picker, filter_dropdown


# Default order date range: last 90 days
def _default_order_start_date() -> str:
    return (date.today() - timedelta(days=90)).isoformat()


def _default_order_end_date() -> str:
    return date.today().isoformat()


# Orders table column definitions
ORDER_TABLE_COLUMNS = [
    {"name": "Order Date", "id": "order_date"},
    {"name": "Order Ref", "id": "order_ref"},
    {"name": "PO", "id": "po_number"},
    {"name": "Customer", "id": "customer"},
    {"name": "Channel", "id": "channel"},
    {"name": "Status", "id": "status"},
    {"name": "Active", "id": "active"},
    {"name": "Delivery #", "id": "delivery_docket_number"},
    {"name": "Delivery date", "id": "delivery_date"},
    {"name": "Docket file", "id": "docket_file"},
    {"name": "Invoice #", "id": "invoice_number"},
    {"name": "Invoice file", "id": "invoice_file"},
    {"name": "Paid", "id": "paid"},
    {"name": "LAL", "id": "lal"},
    {"name": "Total (Ex)", "id": "total_ex_gst"},
    {"name": "Total (Inc)", "id": "total_inc_gst"},
    {"name": "Order ID", "id": "order_id"},
]
ORDER_TABLE_ALWAYS_HIDDEN = ["order_id"]


def _shared_stores_and_modal():
    """Stores and delete modal shared by Orders list and New order form."""
    return [
        dcc.Store(id="sales-order-form-lines-store", data=[]),
        dcc.Store(id="sales-customers-store", data=[]),
        dcc.Store(id="sales-products-store", data=[]),
        dcc.Store(id="sales-channels-store", data=[]),
        dcc.Store(id="sales-orders-refresh-signal", data=0),
        dcc.Store(id="sales-open-order-id", data=None),
        dcc.Store(id="sales-order-pending-delete", data=None),
        dcc.Download(id="sales-order-docket-download"),
        dcc.Store(id="sales-order-detail-refresh", data=0),
        dcc.Store(id="sales-delivery-docket-id-modal", data=None),
        dcc.Store(id="sales-backorder-pending", data=None),
        dcc.Store(id="sales-new-order-edit-line-index", data=None),
        _order_delete_confirm_modal(),
        _delivery_quantities_modal(),
        _backorder_confirm_modal(),
    ]


def layout_orders_list():
    """Orders list only (first-tier tab 'Orders'). New order is opened via modal."""
    return html.Div(
        _shared_stores_and_modal() + current_orders_layout(),
        className="sales-orders-tab-wrapper",
    )


def layout_new_order():
    """New order form only (first-tier tab 'New order'). No inner tabs."""
    return html.Div(
        _shared_stores_and_modal() + new_order_layout(),
        className="sales-orders-tab-wrapper",
    )


def layout():
    """Legacy combined layout with inner Orders / New order tabs (if still used)."""
    return html.Div(
        _shared_stores_and_modal()
        + [
            dcc.Tabs(
                id="sales-order-subtabs",
                value="sales-current-orders",
                children=[
                    dcc.Tab(
                        label="Orders",
                        value="sales-current-orders",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        label="New order",
                        value="sales-new-order",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
                className="mb-3",
            ),
            html.Div(
                id="sales-current-orders-panel",
                children=current_orders_layout(),
                className="sales-orders-tab",
            ),
            html.Div(
                id="sales-new-order-panel",
                children=new_order_layout(),
                className="sales-orders-tab",
            ),
        ],
        className="sales-orders-tab-wrapper",
    )


def current_orders_layout():
    """Layout for Current orders sub-tab: filters and table."""
    return [
        _filters_row(),
        _tag_filter_row(),
        _orders_table_card(),
    ]


def new_order_layout():
    """Layout for New order sub-tab: create order form."""
    return [
        # Hidden filter dropdowns so hydrate_form callback can update options when this tab is active
        html.Div(
            [
                dcc.Dropdown(
                    id="sales-orders-customer-filter",
                    options=[],
                    style={"display": "none"},
                ),
                dcc.Dropdown(
                    id="sales-orders-channel-filter",
                    options=[],
                    style={"display": "none"},
                ),
                dcc.Dropdown(
                    id="sales-orders-status-filter",
                    options=[],
                    style={"display": "none"},
                ),
            ],
            style={"display": "none"},
        ),
        _order_form_card(),
    ]


def _filters_row():
    """Single compact row: Order date, Channel, Customer, Status (narrow), then three checkboxes."""
    return dbc.Row(
        [
            dbc.Col(
                date_range_picker(
                    "sales-orders-date-range",
                    "Order Date",
                    start_date=_default_order_start_date(),
                    end_date=_default_order_end_date(),
                ),
                xs=12,
                sm=6,
                md=2,
                className="mb-2 mb-md-0",
            ),
            dbc.Col(
                filter_dropdown("sales-orders-channel-filter", "Channel", []),
                xs=12,
                sm=6,
                md=2,
                className="mb-2 mb-md-0",
            ),
            dbc.Col(
                filter_dropdown("sales-orders-customer-filter", "Customer", []),
                xs=12,
                sm=6,
                md=2,
                className="mb-2 mb-md-0",
            ),
            dbc.Col(
                filter_dropdown("sales-orders-status-filter", "Status", []),
                xs=12,
                sm=6,
                md=2,
                className="mb-2 mb-md-0",
            ),
            dbc.Col(
                [
                    dbc.Label("Type", className="form-label mb-1"),
                    dbc.Checklist(
                        id="sales-orders-type-filter",
                        options=[
                            {"label": " Has delivery", "value": "has_delivery"},
                            {"label": " Has invoice", "value": "has_invoice"},
                        ],
                        value=[],
                        inline=True,
                        className="me-3",
                    ),
                    dbc.Checklist(
                        id="sales-orders-include-inactive",
                        options=[
                            {"label": " Include inactive", "value": "include_inactive"}
                        ],
                        value=[],
                        inline=True,
                        className="mb-0",
                    ),
                ],
                xs=12,
                md="auto",
                className="mb-2 mb-md-0 d-flex flex-wrap align-items-end",
            ),
        ],
        className="mb-2",
    )


def _tag_filter_row():
    """Single row for Tag filter to save vertical space."""
    return dbc.Row(
        [
            dbc.Col(
                filter_dropdown(
                    "sales-orders-tag-filter",
                    "Tag",
                    [],
                    multi=True,
                ),
                xs=12,
                sm=6,
                md=3,
                className="mb-2",
            ),
        ],
    )


def _orders_table_card():
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.H6("Orders", className="mb-0 d-inline-block"),
                    html.Div(
                        [
                            dbc.Button(
                                "New Order",
                                id="sales-orders-new-order-btn",
                                color="primary",
                                size="sm",
                                outline=True,
                                className="me-1",
                            ),
                            dbc.Button(
                                "Open selected",
                                id="sales-orders-open-selected",
                                color="primary",
                                size="sm",
                                className="me-1",
                            ),
                            dbc.Button(
                                "Refresh Orders",
                                id="sales-orders-refresh",
                                color="secondary",
                                size="sm",
                            ),
                        ],
                        className="ms-auto",
                    ),
                ],
                className="d-flex align-items-center",
            ),
            dbc.CardBody(
                [
                    dash_table.DataTable(
                        id="sales-orders-table",
                        columns=ORDER_TABLE_COLUMNS,
                        data=[],
                        page_size=15,
                        sort_action="native",
                        row_selectable="single",
                        selected_rows=[],
                        hidden_columns=["order_id"],
                        style_data_conditional=[
                            {
                                "if": {"filter_query": "{active} = No"},
                                "backgroundColor": "rgba(0,0,0,0.04)",
                            },
                        ],
                        style_table={"overflowX": "auto"},
                        style_cell={"padding": "0.5rem"},
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                        },
                    ),
                    html.Div(
                        id="sales-orders-table-totals",
                        className="mt-2 text-end fw-bold small",
                    ),
                    _order_detail_modal(),
                    _new_order_modal(),
                    _new_order_edit_line_modal(),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
    )


def _order_detail_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle(id="sales-order-detail-title"),
                close_button=True,
            ),
            dbc.ModalBody(id="sales-order-detail-body"),
            dbc.ModalFooter(
                id="sales-order-detail-footer",
                children=[],
                className="d-flex flex-wrap gap-2",
            ),
        ],
        id="sales-order-detail-modal",
        size="xl",
        is_open=False,
        className="sales-order-modal-resizable",
        style={"maxWidth": "98vw", "width": "min(98vw, 1850px)"},
    )


def _new_order_modal():
    """New order as a modal with same two-column layout as order detail: left = customer/channel/PO etc, right = line items."""
    left_col = html.Div(
        [
            html.P(
                [
                    html.Strong("Customer"),
                    html.Br(),
                    dcc.Dropdown(
                        id="sales-order-form-customer", placeholder="Select customer..."
                    ),
                ],
                className="mb-3",
            ),
            html.P(
                [
                    html.Strong("Site"),
                    html.Br(),
                    dcc.Dropdown(
                        id="sales-order-form-site",
                        placeholder="Select site...",
                        clearable=True,
                    ),
                ],
                className="mb-3",
            ),
            html.P(
                [
                    html.Small(
                        "Optional. Select customer first.", className="text-muted"
                    )
                ],
                className="mb-3",
            ),
            html.P(
                [
                    html.Strong("Channel"),
                    html.Br(),
                    dcc.Dropdown(
                        id="sales-order-form-channel", placeholder="Select channel..."
                    ),
                ],
                className="mb-3",
            ),
            html.P(
                [
                    html.Strong("Order date"),
                    html.Br(),
                    dcc.DatePickerSingle(
                        id="sales-order-form-date", display_format="YYYY-MM-DD"
                    ),
                ],
                className="mb-3",
            ),
            html.P(
                [
                    html.Strong("Order Ref / PO"),
                    html.Br(),
                    dbc.Input(
                        id="sales-order-form-ref", placeholder="Optional reference"
                    ),
                ],
                className="mb-3",
            ),
            html.P(
                [
                    html.Strong("Entered by"),
                    html.Br(),
                    dbc.Input(id="sales-order-form-entered-by", placeholder="Optional"),
                ],
                className="mb-3",
            ),
            html.P(
                [
                    html.Strong("Notes"),
                    html.Br(),
                    dbc.Textarea(
                        id="sales-order-form-notes",
                        placeholder="Order notes...",
                        rows=3,
                    ),
                ],
                className="mb-0",
            ),
        ],
        style={"overflowY": "auto", "maxHeight": "70vh"},
    )
    right_col = html.Div(
        [
            html.Div("Line items", className="small text-muted mb-1"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="sales-order-form-product", placeholder="Product"
                        ),
                        md=7,
                        style={"minWidth": "200px"},
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
                            placeholder="Price ex",
                        ),
                        md=2,
                    ),
                    dbc.Col(
                        dbc.Input(
                            id="sales-order-form-discount",
                            type="number",
                            min=0,
                            step=0.01,
                            placeholder="Discount",
                        ),
                        md=2,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Add Line",
                            id="sales-order-form-add-line",
                            color="primary",
                            size="sm",
                        ),
                        md=1,
                    ),
                ],
                className="g-2 align-items-end mb-2",
            ),
            dash_table.DataTable(
                id="sales-order-form-lines-table",
                columns=[
                    {"name": "Code", "id": "code", "editable": False},
                    {
                        "name": "Description",
                        "id": "product_description",
                        "editable": False,
                    },
                    {"name": "Qty", "id": "qty", "editable": True},
                    {
                        "name": "Price (ex GST)",
                        "id": "unit_price_ex_gst",
                        "editable": False,
                    },
                    {"name": "Discount", "id": "discount_ex_gst", "editable": False},
                    {
                        "name": "Line Total (ex GST)",
                        "id": "line_total_ex_gst",
                        "editable": False,
                    },
                    {
                        "name": "Line Total (inc GST)",
                        "id": "line_total_inc_gst",
                        "editable": False,
                    },
                ],
                data=[],
                style_table={"overflowX": "auto"},
                style_cell={"padding": "0.4rem"},
                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
                row_selectable="single",
                editable=True,
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Remove Selected Line",
                            id="sales-order-form-remove-line",
                            color="danger",
                            outline=True,
                            size="sm",
                            className="mt-2",
                        ),
                        md="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Edit Line",
                            id="sales-order-form-edit-line",
                            color="secondary",
                            outline=True,
                            size="sm",
                            className="mt-2",
                        ),
                        md="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Clear Lines",
                            id="sales-order-form-clear",
                            color="secondary",
                            outline=True,
                            size="sm",
                            className="mt-2",
                        ),
                        md="auto",
                    ),
                ],
                className="g-2",
            ),
            html.Div(id="sales-new-order-totals", className="mt-2 mb-2 fw-bold small"),
            dbc.Button(
                "Submit Order",
                id="sales-order-form-submit",
                color="success",
                size="sm",
                className="mt-3",
            ),
            dbc.Alert(id="sales-order-form-feedback", is_open=False, className="mt-3"),
        ],
        className="h-100",
        style={"minHeight": "200px", "overflowY": "auto", "maxHeight": "70vh"},
    )
    body = dbc.Row(
        [
            dbc.Col(left_col, width=4, className="pe-2 border-end"),
            dbc.Col(right_col, width=8, className="ps-2"),
        ],
        className="g-2",
    )
    return dbc.Modal(
        [
            dbc.ModalHeader(
                [
                    dbc.ModalTitle("New Order"),
                    dbc.Button(
                        "×",
                        id="sales-new-order-header-close",
                        className="btn-close",
                        title="Close",
                    ),
                ],
            ),
            dbc.ModalBody(body),
            dbc.ModalFooter(
                dbc.Button(
                    "Cancel", id="sales-new-order-close", color="secondary", size="sm"
                )
            ),
        ],
        id="sales-new-order-modal",
        size="xl",
        is_open=False,
        className="sales-order-modal-resizable",
        style={"maxWidth": "98vw", "width": "min(98vw, 1850px)"},
    )


def _new_order_edit_line_modal():
    """Modal to edit qty, price, discount of the selected line in new order."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Edit line")),
            dbc.ModalBody(
                [
                    dbc.Label("Code"),
                    dbc.Input(
                        id="sales-new-order-edit-code", disabled=True, className="mb-2"
                    ),
                    dbc.Label("Qty"),
                    dbc.Input(
                        id="sales-new-order-edit-qty",
                        type="number",
                        min=0,
                        step=1,
                        className="mb-2",
                    ),
                    dbc.Label("Price (ex GST)"),
                    dbc.Input(
                        id="sales-new-order-edit-price",
                        type="number",
                        min=0,
                        step=0.01,
                        className="mb-2",
                    ),
                    dbc.Label("Discount (ex GST)"),
                    dbc.Input(
                        id="sales-new-order-edit-discount",
                        type="number",
                        min=0,
                        step=0.01,
                        className="mb-2",
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="sales-new-order-edit-line-cancel",
                        color="secondary",
                        size="sm",
                    ),
                    dbc.Button(
                        "Save",
                        id="sales-new-order-edit-line-save",
                        color="primary",
                        size="sm",
                    ),
                ]
            ),
        ],
        id="sales-new-order-edit-line-modal",
        is_open=False,
    )


def _order_delete_confirm_modal():
    """Fixed modal for delete confirmation so it is not recreated when order detail footer updates."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Mark order as inactive?")),
            dbc.ModalBody(
                "The order will be hidden from the list but can be restored later."
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel", id="sales-order-delete-cancel", color="secondary"
                    ),
                    dbc.Button(
                        "Mark inactive", id="sales-order-delete-confirm", color="danger"
                    ),
                ],
                className="d-flex flex-wrap gap-2",
            ),
        ],
        id="sales-order-delete-confirm-modal",
        is_open=False,
    )


def _delivery_quantities_modal():
    """Modal to set delivery quantities (oqty/dqty) before generating delivery docket PDF."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Set delivery quantities")),
            dbc.ModalBody(
                [
                    html.P(
                        "Adjust delivered quantity (dqty) for each line. dqty cannot exceed ordered (oqty).",
                        className="small text-muted",
                    ),
                    dash_table.DataTable(
                        id="sales-delivery-quantities-table",
                        columns=[
                            {"name": "Product", "id": "product_sku"},
                            {"name": "Ordered (oqty)", "id": "ordered_quantity"},
                            {"name": "Deliver (dqty)", "id": "quantity"},
                        ],
                        data=[],
                        page_action="none",
                        style_cell={"padding": "0.3rem"},
                        editable=[False, False, True],
                        hidden_columns=["line_id"],
                    ),
                    html.Div(
                        id="sales-delivery-quantities-total", className="mt-2 fw-bold"
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="sales-delivery-quantities-cancel",
                        color="secondary",
                    ),
                    dbc.Button(
                        "Create delivery docket",
                        id="sales-delivery-quantities-confirm",
                        color="primary",
                    ),
                ],
                className="d-flex flex-wrap gap-2",
            ),
        ],
        id="sales-delivery-quantities-modal",
        size="lg",
        is_open=False,
    )


def _backorder_confirm_modal():
    """Confirm create backorder for remaining (oqty - dqty) items."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Backorder remaining items?")),
            dbc.ModalBody(
                "Some items were not fully delivered. Create a new order for the remaining quantities (same customer, PO and order date)?"
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel", id="sales-backorder-cancel", color="secondary"
                    ),
                    dbc.Button(
                        "Create backorder",
                        id="sales-backorder-confirm",
                        color="primary",
                    ),
                ],
                className="d-flex flex-wrap gap-2",
            ),
        ],
        id="sales-backorder-modal",
        is_open=False,
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
                                [
                                    dcc.Dropdown(
                                        id="sales-order-form-site",
                                        placeholder="Select site...",
                                        clearable=True,
                                    ),
                                    html.Small(
                                        "Optional. Select customer first to see their sites.",
                                        className="text-muted d-block mt-1",
                                    ),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    dcc.Dropdown(
                                        id="sales-order-form-channel",
                                        placeholder="Select channel (ALM, Direct, Shopify)...",
                                    ),
                                    html.Small(
                                        "Run scripts/seed_sales_channels.py if empty.",
                                        className="text-muted d-block mt-1",
                                    ),
                                ],
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
