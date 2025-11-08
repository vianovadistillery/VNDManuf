"""Import / Export sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


def layout():
    upload = dbc.Card(
        [
            dbc.CardHeader(html.H6("Import Sales Orders", className="mb-0")),
            dbc.CardBody(
                [
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
                            }
                        ],
                        value=[],
                        id="sales-import-allow-create",
                        switch=True,
                        className="mb-3",
                    ),
                    dbc.Alert(
                        "Template columns: order_date, channel, customer, site_name, product_code, qty, unit_price_ex_gst, unit_price_inc_gst, order_ref, notes",
                        color="info",
                        className="mb-0",
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
    )

    summary_table = dash_table.DataTable(
        id="sales-import-summary-table",
        columns=[
            {"name": "Order Ref", "id": "order_ref"},
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

    return html.Div(
        [
            upload,
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
