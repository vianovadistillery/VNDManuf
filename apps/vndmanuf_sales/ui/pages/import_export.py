"""Import / Export sub-tab layout."""

from __future__ import annotations

from pathlib import Path

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SALES_TEMPLATE = _DATA_DIR / "sales_orders_template.csv"
DOCKET_TEMPLATE = _DATA_DIR / "delivery_docket_template.csv"


def layout():
    upload = dbc.Card(
        [
            dbc.CardHeader(html.H6("Import Sales Orders", className="mb-0")),
            dbc.CardBody(
                [
                    dcc.Download(id="sales-import-download-sales-template"),
                    dcc.Download(id="sales-import-download-docket-template"),
                    dbc.ButtonGroup(
                        [
                            dbc.Button(
                                "Download Sales CSV Template",
                                id="sales-import-download-sales-btn",
                                color="secondary",
                                outline=True,
                                size="sm",
                            ),
                            dbc.Button(
                                "Download Delivery Docket CSV Template",
                                id="sales-import-download-docket-btn",
                                color="secondary",
                                outline=True,
                                size="sm",
                            ),
                        ],
                        className="mb-3",
                    ),
                    dcc.Upload(
                        id="sales-import-upload",
                        children=html.Div(
                            ["Drag and drop or ", html.A("select CSV file")]
                        ),
                        multiple=False,
                        className="mb-3 border border-secondary border-dashed p-4 text-center",
                    ),
                    dbc.Checklist(
                        options=[
                            {
                                "label": "Auto-create channels/customers/sites when missing",
                                "value": "allow-create",
                            },
                            {
                                "label": "Create delivery docket records (for docket CSV)",
                                "value": "create-docket",
                            },
                        ],
                        value=["create-docket"],
                        id="sales-import-options",
                        switch=True,
                        className="mb-3",
                    ),
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    html.P(
                                        "One row per order line. Rows with the same order_date, customer, and order_ref become one order.",
                                        className="mb-2",
                                    ),
                                    html.Pre(
                                        "order_date, channel, customer, site_name, product_code, qty, "
                                        "unit_price_ex_gst, unit_price_inc_gst, order_ref, notes",
                                        className="small bg-light p-2 rounded",
                                    ),
                                ],
                                title="Standard sales CSV",
                                item_id="sales-import-help-sales",
                            ),
                            dbc.AccordionItem(
                                [
                                    html.P(
                                        "Use this when extracting data from a delivery docket PDF (e.g. DD250116). "
                                        "One row per product line; repeat header fields on each row. "
                                        "delivered_qty becomes the sales quantity; ordered_qty is stored on the docket line.",
                                        className="mb-2",
                                    ),
                                    html.Pre(
                                        "docket_number, delivery_date, order_date, customer, attention, site_name, "
                                        "site_suburb, site_state, site_postcode, channel, po_number, product_code, "
                                        "description, ordered_qty, delivered_qty, unit",
                                        className="small bg-light p-2 rounded",
                                    ),
                                ],
                                title="Delivery docket CSV (from PDF)",
                                item_id="sales-import-help-docket",
                            ),
                        ],
                        start_collapsed=True,
                        always_open=False,
                        className="mb-3",
                    ),
                    dbc.Alert(
                        id="sales-import-result", is_open=False, className="mb-0"
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
    )

    customer_mapping = dbc.Card(
        [
            dbc.CardHeader(html.H6("Customer Name Mappings", className="mb-0")),
            dbc.CardBody(
                [
                    html.P(
                        "Map CSV customer names (typos or alternate spellings) to the correct customer record. "
                        "Matching is case-insensitive and ignores extra spaces.",
                        className="text-muted small mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(
                                    id="sales-customer-alias-input",
                                    placeholder="CSV name, e.g. Cellarbrations at Jacks",
                                    type="text",
                                ),
                                md=5,
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="sales-customer-alias-customer",
                                    placeholder="Maps to customer...",
                                ),
                                md=5,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Add mapping",
                                    id="sales-customer-alias-add",
                                    color="primary",
                                    className="w-100",
                                ),
                                md=2,
                            ),
                        ],
                        className="g-2 mb-3",
                    ),
                    dbc.Alert(
                        id="sales-customer-alias-alert",
                        is_open=False,
                        duration=4000,
                        className="mb-3",
                    ),
                    dash_table.DataTable(
                        id="sales-customer-alias-table",
                        columns=[
                            {"name": "CSV name", "id": "alias"},
                            {"name": "Customer", "id": "customer_name"},
                            {"name": "Notes", "id": "notes"},
                            {
                                "name": "",
                                "id": "delete_label",
                                "presentation": "markdown",
                            },
                        ],
                        data=[],
                        row_selectable="single",
                        selected_rows=[],
                        style_table={"overflowX": "auto"},
                        style_cell={"padding": "0.5rem", "textAlign": "left"},
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                        },
                        markdown_options={"html": True},
                    ),
                    dbc.Button(
                        "Remove selected mapping",
                        id="sales-customer-alias-remove",
                        color="outline-danger",
                        size="sm",
                        className="mt-2",
                    ),
                    dcc.Store(id="sales-customer-alias-refresh", data=0),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
    )

    site_mapping = dbc.Card(
        [
            dbc.CardHeader(html.H6("Site Name Mappings", className="mb-0")),
            dbc.CardBody(
                [
                    html.P(
                        "Map CSV delivery site names (often abbreviated) to the site name stored for a customer. "
                        "If no site matches and auto-create is off, orders still import without a linked site.",
                        className="text-muted small mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Dropdown(
                                    id="sales-site-alias-customer",
                                    placeholder="Customer...",
                                ),
                                md=4,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="sales-site-alias-input",
                                    placeholder="CSV site, e.g. CBN AT FOXXYS DAYLESFORD X",
                                    type="text",
                                ),
                                md=4,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="sales-site-alias-site-name",
                                    placeholder="Canonical site name",
                                    type="text",
                                ),
                                md=3,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Add",
                                    id="sales-site-alias-add",
                                    color="primary",
                                    className="w-100",
                                ),
                                md=1,
                            ),
                        ],
                        className="g-2 mb-3",
                    ),
                    dbc.Alert(
                        id="sales-site-alias-alert",
                        is_open=False,
                        duration=4000,
                        className="mb-3",
                    ),
                    dash_table.DataTable(
                        id="sales-site-alias-table",
                        columns=[
                            {"name": "Customer", "id": "customer_name"},
                            {"name": "CSV site", "id": "alias"},
                            {"name": "Site name", "id": "site_name"},
                        ],
                        data=[],
                        row_selectable="single",
                        selected_rows=[],
                        style_table={"overflowX": "auto"},
                        style_cell={"padding": "0.5rem"},
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                        },
                    ),
                    dbc.Button(
                        "Remove selected site mapping",
                        id="sales-site-alias-remove",
                        color="outline-danger",
                        size="sm",
                        className="mt-2",
                    ),
                    dcc.Store(id="sales-site-alias-refresh", data=0),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
    )

    summary_table = dash_table.DataTable(
        id="sales-import-summary-table",
        columns=[
            {"name": "Order / Docket", "id": "order_ref"},
            {"name": "Customer", "id": "customer"},
            {"name": "Lines", "id": "lines"},
            {"name": "Status", "id": "status"},
            {"name": "Message", "id": "message"},
        ],
        data=[],
        style_table={"overflowX": "auto"},
        style_cell={"padding": "0.5rem"},
        style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
    )

    export_controls = dbc.Card(
        [
            dbc.CardHeader(html.H6("Export Orders", className="mb-0")),
            dbc.CardBody(
                [
                    html.P(
                        "Download filtered orders and lines as CSV for analytics or Xero sync.",
                        className="text-muted",
                    ),
                    dbc.Button(
                        "Export Orders CSV",
                        id="sales-export-orders",
                        color="secondary",
                        className="me-2",
                    ),
                    dbc.Button(
                        "Export Lines CSV", id="sales-export-lines", color="secondary"
                    ),
                ]
            ),
        ],
        className="shadow-sm",
    )

    import_preview_modal = dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Review import before committing")),
            dbc.ModalBody(
                [
                    html.P(
                        id="sales-import-preview-summary",
                        className="text-muted small mb-3",
                    ),
                    html.P(
                        "Customer name mappings are applied below. "
                        "Duplicate or problematic records are unchecked by default — "
                        "tick the rows you want to import, then confirm.",
                        className="small mb-3",
                    ),
                    dash_table.DataTable(
                        id="sales-import-preview-table",
                        columns=[
                            {"name": "Order / Docket", "id": "order_ref"},
                            {"name": "CSV customer", "id": "customer_csv"},
                            {"name": "Resolved customer", "id": "customer_resolved"},
                            {"name": "Lines", "id": "line_count"},
                            {"name": "Status", "id": "flags"},
                        ],
                        data=[],
                        row_selectable="multi",
                        selected_rows=[],
                        style_table={
                            "overflowX": "auto",
                            "maxHeight": "420px",
                            "overflowY": "auto",
                        },
                        style_cell={
                            "padding": "0.5rem",
                            "textAlign": "left",
                            "whiteSpace": "normal",
                        },
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                        },
                        style_data_conditional=[
                            {
                                "if": {"filter_query": "{customer_missing} = true"},
                                "backgroundColor": "#fff3cd",
                            },
                            {
                                "if": {"filter_query": "{duplicate_in_db} = true"},
                                "backgroundColor": "#f8d7da",
                            },
                            {
                                "if": {"filter_query": "{duplicate_in_csv} = true"},
                                "backgroundColor": "#ffe5cc",
                            },
                        ],
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel", id="sales-import-preview-cancel", color="secondary"
                    ),
                    dbc.Button(
                        "Import selected",
                        id="sales-import-preview-confirm",
                        color="primary",
                    ),
                ]
            ),
        ],
        id="sales-import-preview-modal",
        is_open=False,
        size="xl",
        scrollable=True,
    )

    return html.Div(
        [
            upload,
            customer_mapping,
            site_mapping,
            import_preview_modal,
            dbc.Card(
                [
                    dbc.CardHeader(html.H6("Import Results", className="mb-0")),
                    dbc.CardBody(summary_table),
                ],
                className="mb-4 shadow-sm",
            ),
            export_controls,
        ],
        className="sales-import-tab",
    )
