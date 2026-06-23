"""Orders sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from apps.vndmanuf_sales.ui.components import date_range_picker, filter_dropdown
from apps.vndmanuf_sales.ui.period_filters import (
    default_period_iso,
    period_applying_store,
    period_preset_dropdown,
)

_default_start, _default_end = default_period_iso()


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

ORDER_STATUS_OPTIONS = [
    {"label": "Draft", "value": "draft"},
    {"label": "Confirmed", "value": "confirmed"},
    {"label": "Fulfilled", "value": "fulfilled"},
    {"label": "Cancelled", "value": "cancelled"},
]

ORDER_DETAIL_LINE_COLUMNS = [
    {"name": "Qty", "id": "qty", "editable": True, "type": "numeric"},
    {"name": "Product", "id": "product_code", "editable": False},
    {"name": "Description", "id": "description", "editable": False},
    {
        "name": "Unit (ex)",
        "id": "unit_price_ex_gst",
        "editable": True,
        "type": "numeric",
    },
    {
        "name": "Unit (inc)",
        "id": "unit_price_inc_gst",
        "editable": True,
        "type": "numeric",
    },
    {"name": "GST", "id": "gst", "editable": False},
    {"name": "Line total (ex)", "id": "line_total_ex_gst", "editable": False},
    {"name": "Line total (inc)", "id": "line_total_inc_gst", "editable": False},
]


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
        dcc.Download(id="sales-orders-products-report-download"),
        dcc.Store(id="sales-order-detail-refresh", data=0),
        dcc.Store(id="sales-order-detail-prev-data", data=[]),
        dcc.Store(id="sales-order-detail-dirty", data=False),
        dcc.Store(id="sales-order-detail-snapshot", data=None),
        dcc.Store(id="sales-order-detail-footer-state", data=None),
        dcc.Store(id="sales-delivery-docket-id-modal", data=None),
        dcc.Store(id="sales-backorder-pending", data=None),
        dcc.Store(id="sales-new-order-edit-line-index", data=None),
        _order_delete_confirm_modal(),
        _order_unsaved_changes_modal(),
        _order_save_confirm_modal(),
        _convert_invoice_modal(),
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
    """Layout for Current orders sub-tab: filters and summary (orders + products)."""
    return [
        period_applying_store("sales-orders-applying-preset"),
        _filters_row(),
        _tag_filter_row(),
        _summary_card(),
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
    """Single compact row: Period, Order date, Channel, Customer, Status, then checkboxes."""
    return dbc.Row(
        [
            dbc.Col(
                period_preset_dropdown("sales-orders-period-preset"),
                xs=12,
                sm=6,
                md=2,
                className="mb-2 mb-md-0",
            ),
            dbc.Col(
                date_range_picker(
                    "sales-orders-date-range",
                    "Order Date",
                    start_date=_default_start,
                    end_date=_default_end,
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
                    dbc.Label("Presence", className="form-label mb-1"),
                    dbc.Checklist(
                        id="sales-orders-type-filter",
                        options=[
                            {"label": " Delivered", "value": "has_delivery"},
                            {"label": " Invoiced", "value": "has_invoice"},
                            {"label": " Paid", "value": "paid"},
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


ORDER_PRODUCTS_TABLE_COLUMNS = [
    {"name": "Code", "id": "sku"},
    {"name": "Description", "id": "name"},
    {"name": "Total Qty", "id": "total_qty"},
    {"name": "Orders", "id": "order_count"},
    {"name": "Total (Ex)", "id": "total_ex_gst"},
    {"name": "Total (Inc)", "id": "total_inc_gst"},
    {"name": "Product ID", "id": "product_id"},
]
ORDER_PRODUCTS_TABLE_HIDDEN = ["product_id"]


def _summary_card():
    """Single summary card: orders table, then products in filtered orders."""
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.H6("Summary", className="mb-0 d-inline-block"),
                    html.Div(
                        [
                            dbc.Button(
                                "Print report",
                                id="sales-orders-print-products-report",
                                color="primary",
                                size="sm",
                                outline=True,
                                className="me-1",
                            ),
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
                                "Refresh",
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
                    html.H6("Orders", className="mb-2"),
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
                        className="mt-2 mb-4 text-end fw-bold small",
                    ),
                    html.Hr(className="my-3"),
                    html.H6("Products in filtered orders", className="mb-2"),
                    dash_table.DataTable(
                        id="sales-orders-products-table",
                        columns=ORDER_PRODUCTS_TABLE_COLUMNS,
                        data=[],
                        page_size=15,
                        sort_action="native",
                        hidden_columns=ORDER_PRODUCTS_TABLE_HIDDEN,
                        style_table={"overflowX": "auto"},
                        style_cell={"padding": "0.5rem"},
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                        },
                    ),
                    html.Div(
                        id="sales-orders-products-totals",
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


def _order_detail_adjustments_panel():
    """Freight, commission, payment — static IDs below the line items table."""
    return html.Div(
        [
            html.Hr(className="my-3"),
            html.H6("Adjustments", className="mb-2"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Commission (ex GST)", className="mb-1"),
                            dbc.Input(
                                id="sales-order-commission",
                                type="number",
                                min=0,
                                step=0.01,
                                placeholder="0.00",
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="g-2 mb-2",
            ),
            dbc.Label("Freight", className="mb-1"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Small("Ex", className="text-muted"),
                            dbc.Input(
                                id="sales-order-freight-ex",
                                type="number",
                                min=0,
                                step=0.01,
                                placeholder="0.00",
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            html.Small("GST", className="text-muted"),
                            dbc.Input(
                                id="sales-order-freight-gst",
                                type="number",
                                min=0,
                                step=0.01,
                                placeholder="0.00",
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            html.Small("Inc", className="text-muted"),
                            dbc.Input(
                                id="sales-order-freight-inc",
                                type="number",
                                min=0,
                                step=0.01,
                                placeholder="0.00",
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="g-2 mb-2",
            ),
            html.H6("Payment & invoice", className="mb-2 mt-1"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Payment date", className="mb-1"),
                            dcc.DatePickerSingle(
                                id="sales-order-payment-date",
                                display_format="YYYY-MM-DD",
                                placeholder="YYYY-MM-DD",
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Payment reference", className="mb-1"),
                            dbc.Input(
                                id="sales-order-payment-ref",
                                placeholder="e.g. bank ref, remittance",
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Invoice date", className="mb-1"),
                            dcc.DatePickerSingle(
                                id="sales-order-invoice-date",
                                display_format="YYYY-MM-DD",
                                placeholder="YYYY-MM-DD",
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="g-2 mb-2",
            ),
            dbc.Alert(id="sales-order-detail-feedback", is_open=False, duration=4000),
            html.Div(
                id="sales-order-detail-summary",
                className="mt-2 p-2 border rounded bg-light small",
            ),
        ],
        id="sales-order-detail-adjustments",
    )


def _order_detail_meta_panel():
    """Editable order header — static component IDs for callbacks."""
    return html.Div(
        [
            html.Div(id="sales-order-detail-doc-links", className="mb-2 small"),
            dcc.Store(id="sales-order-detail-customer-id"),
            dbc.Label("Customer", className="mb-1"),
            html.Div(
                id="sales-order-detail-customer-name", className="mb-2 text-muted small"
            ),
            dbc.Label("Channel", className="mb-1"),
            dcc.Dropdown(
                id="sales-order-detail-channel",
                options=[],
                clearable=True,
                placeholder="Select channel…",
            ),
            dbc.Label("Order ref", className="mb-1 mt-2"),
            dbc.Input(id="sales-order-detail-order-ref", placeholder="Order reference"),
            dbc.Label("PO number", className="mb-1 mt-2"),
            dbc.Input(id="sales-order-detail-po", placeholder="Customer PO"),
            dbc.Label("Order date", className="mb-1 mt-2"),
            dcc.DatePickerSingle(
                id="sales-order-detail-order-date",
                display_format="YYYY-MM-DD",
                placeholder="YYYY-MM-DD",
            ),
            dbc.Label("Delivery date", className="mb-1 mt-2"),
            dcc.DatePickerSingle(
                id="sales-order-detail-delivery-date",
                display_format="YYYY-MM-DD",
                placeholder="YYYY-MM-DD",
            ),
            dbc.Label("Status", className="mb-1 mt-2"),
            dcc.Dropdown(
                id="sales-order-detail-status",
                options=ORDER_STATUS_OPTIONS,
                clearable=False,
            ),
            dbc.Label("Order discount (ex GST)", className="mb-1 mt-2"),
            dbc.Input(
                id="sales-order-detail-discount",
                type="number",
                min=0,
                step=0.01,
                placeholder="0.00",
            ),
            dbc.Label("Entered by", className="mb-1 mt-2"),
            dbc.Input(id="sales-order-detail-entered-by", placeholder="Optional"),
            dbc.Label("Notes", className="mb-1 mt-2"),
            dbc.Textarea(
                id="sales-order-detail-notes", rows=2, placeholder="Order notes…"
            ),
            html.Div(
                id="sales-order-detail-invoice-number",
                className="small text-muted mt-2",
            ),
            dbc.Checklist(
                id="sales-order-detail-paid",
                options=[{"label": "Invoice paid", "value": "paid"}],
                value=[],
                className="mt-2",
                switch=True,
            ),
        ],
        style={"overflowY": "auto", "maxHeight": "70vh"},
    )


def _order_detail_lines_toolbar():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="sales-order-detail-add-product",
                            options=[],
                            placeholder="Add product…",
                        ),
                        md=5,
                    ),
                    dbc.Col(
                        dbc.Input(
                            id="sales-order-detail-add-qty",
                            type="number",
                            min=0,
                            step=1,
                            placeholder="Qty",
                        ),
                        md=2,
                    ),
                    dbc.Col(
                        dbc.Input(
                            id="sales-order-detail-add-price",
                            type="number",
                            min=0,
                            step=0.01,
                            placeholder="Unit ex (opt)",
                        ),
                        md=2,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Add line",
                            id="sales-order-detail-add-line",
                            color="secondary",
                            size="sm",
                            className="w-100",
                        ),
                        md=3,
                    ),
                ],
                className="g-2 mb-2 align-items-center",
            ),
            dbc.Button(
                "Remove selected line",
                id="sales-order-detail-remove-line",
                color="outline-danger",
                size="sm",
                className="mb-2",
            ),
            dbc.Alert(
                id="sales-order-detail-line-feedback",
                is_open=False,
                duration=3000,
                className="py-1 mb-2",
            ),
        ]
    )


def _order_detail_body_layout():
    """Fixed layout shell — table and inputs keep stable IDs for callbacks."""
    return dbc.Row(
        [
            dbc.Col(_order_detail_meta_panel(), width=4, className="pe-2"),
            dbc.Col(
                [
                    html.Div("Line items", className="small text-muted mb-1"),
                    _order_detail_lines_toolbar(),
                    dash_table.DataTable(
                        id="sales-order-detail-table",
                        columns=ORDER_DETAIL_LINE_COLUMNS,
                        data=[],
                        editable=True,
                        row_selectable="single",
                        selected_rows=[],
                        page_size=100,
                        page_action="none",
                        style_cell={"padding": "0.3rem"},
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                        },
                        style_table={"overflowX": "auto"},
                    ),
                    _order_detail_adjustments_panel(),
                ],
                width=8,
                className="ps-2 border-start",
                style={"overflowY": "auto", "maxHeight": "75vh"},
            ),
        ],
        className="g-2",
    )


def _order_unsaved_changes_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Unsaved changes")),
            dbc.ModalBody("Save your changes before closing, or discard them?"),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Keep editing",
                        id="sales-order-unsaved-keep",
                        color="secondary",
                        size="sm",
                    ),
                    dbc.Button(
                        "Discard",
                        id="sales-order-unsaved-discard",
                        color="warning",
                        size="sm",
                    ),
                    dbc.Button(
                        "Save",
                        id="sales-order-unsaved-save",
                        color="primary",
                        size="sm",
                    ),
                ],
                className="d-flex flex-wrap gap-2",
            ),
        ],
        id="sales-order-unsaved-modal",
        is_open=False,
        centered=True,
    )


def _order_save_confirm_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Save order changes?")),
            dbc.ModalBody(
                "Save all order changes — header, lines, freight, commission, and payment details?"
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="sales-order-save-cancel",
                        color="secondary",
                        size="sm",
                    ),
                    dbc.Button(
                        "Save",
                        id="sales-order-save-confirm",
                        color="primary",
                        size="sm",
                    ),
                ],
                className="d-flex flex-wrap gap-2",
            ),
        ],
        id="sales-order-save-confirm-modal",
        is_open=False,
        centered=True,
    )


def _order_detail_footer():
    """Static footer — IDs must not be recreated on order load (prevents spurious callback fires)."""
    return [
        dbc.Button(
            "Create delivery docket",
            id="sales-order-print-delivery",
            color="secondary",
            size="sm",
            disabled=True,
        ),
        dbc.Button(
            "Create picking slip",
            id="sales-order-print-picking",
            color="secondary",
            size="sm",
            disabled=True,
        ),
        dbc.Button(
            "Convert to delivery",
            id="sales-order-convert-delivery",
            color="info",
            size="sm",
        ),
        dbc.Button(
            "Convert to invoice",
            id="sales-order-convert-invoice",
            color="info",
            size="sm",
        ),
        dbc.Button(
            "Create invoice",
            id="sales-order-print-invoice",
            color="secondary",
            size="sm",
            disabled=True,
        ),
        dbc.Button("Mark paid", id="sales-order-mark-paid", color="success", size="sm"),
        dbc.Button(
            "Delete order", id="sales-order-delete-btn", color="danger", size="sm"
        ),
        dbc.Button("Save", id="sales-order-detail-save", color="primary", size="sm"),
        dbc.Button(
            "Discard changes",
            id="sales-order-detail-cancel",
            color="warning",
            outline=True,
            size="sm",
        ),
        dbc.Button(
            "Close", id="sales-order-detail-close", color="secondary", size="sm"
        ),
    ]


def _order_detail_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle(id="sales-order-detail-title"),
                close_button=False,
            ),
            dbc.ModalBody(_order_detail_body_layout()),
            dbc.ModalFooter(
                _order_detail_footer(),
                className="d-flex flex-wrap gap-2",
            ),
        ],
        id="sales-order-detail-modal",
        size="xl",
        is_open=False,
        className="sales-order-modal-resizable",
        style={"maxWidth": "98vw", "width": "min(98vw, 1850px)"},
        backdrop="static",
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


def _convert_invoice_modal():
    """Confirm invoice number and date before creating an invoice from an order."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Create invoice")),
            dbc.ModalBody(
                [
                    html.P(
                        "Set the invoice number and date. For ALM channel, the number is "
                        "suggested from the delivery docket (e.g. DD260050 → A260050).",
                        className="small text-muted mb-3",
                    ),
                    dbc.Label("Invoice number", className="mb-1"),
                    dbc.Input(
                        id="sales-convert-invoice-number",
                        placeholder="e.g. A260050",
                    ),
                    dbc.Label("Invoice date", className="mb-1 mt-3"),
                    dcc.DatePickerSingle(
                        id="sales-convert-invoice-date",
                        display_format="YYYY-MM-DD",
                        placeholder="YYYY-MM-DD",
                    ),
                    dbc.Alert(
                        id="sales-convert-invoice-feedback",
                        is_open=False,
                        duration=4000,
                        className="mt-3 mb-0",
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="sales-convert-invoice-cancel",
                        color="secondary",
                        size="sm",
                    ),
                    dbc.Button(
                        "Create invoice",
                        id="sales-convert-invoice-confirm",
                        color="primary",
                        size="sm",
                    ),
                ],
                className="d-flex flex-wrap gap-2",
            ),
        ],
        id="sales-convert-invoice-modal",
        is_open=False,
        centered=True,
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
