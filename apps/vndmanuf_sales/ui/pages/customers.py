"""Customers & Sites sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, html

from apps.vndmanuf_sales.ui.components import kpi_card


def layout():
    metrics = dbc.Row(
        [
            dbc.Col(kpi_card("sales-customers-total", "Active Customers", "82"), md=3),
            dbc.Col(kpi_card("sales-customers-new", "New This Month", "6"), md=3),
            dbc.Col(
                kpi_card("sales-customers-lifetime", "Lifetime Value (avg)", "$12,400"),
                md=3,
            ),
            dbc.Col(
                kpi_card("sales-customers-last-order", "Last Order (days)", "4"), md=3
            ),
        ],
        className="mb-4",
    )

    customers_table = dash_table.DataTable(
        id="sales-customers-table",
        columns=[
            {"name": "Customer", "id": "customer"},
            {"name": "Type", "id": "type"},
            {"name": "Email", "id": "email"},
            {"name": "Phone", "id": "phone"},
            {"name": "Lifetime Orders", "id": "orders"},
            {"name": "Revenue (Inc GST)", "id": "revenue"},
            {"name": "Last Order", "id": "last_order"},
        ],
        data=[],
        page_size=12,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"padding": "0.5rem"},
        style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
    )

    sites_table = dash_table.DataTable(
        id="sales-customer-sites-table",
        columns=[
            {"name": "Customer", "id": "customer"},
            {"name": "Site", "id": "site"},
            {"name": "State", "id": "state"},
            {"name": "Suburb", "id": "suburb"},
            {"name": "Revenue (Inc GST)", "id": "revenue"},
            {"name": "Orders", "id": "orders"},
        ],
        data=[],
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={"padding": "0.5rem"},
        style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
    )

    return html.Div(
        [
            metrics,
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H6("Customers", className="mb-0")),
                                dbc.CardBody(customers_table),
                            ],
                            className="shadow-sm",
                        ),
                        md=7,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H6("Sites", className="mb-0")),
                                dbc.CardBody(sites_table),
                            ],
                            className="shadow-sm",
                        ),
                        md=5,
                    ),
                ]
            ),
        ],
        className="sales-customers-tab",
    )
