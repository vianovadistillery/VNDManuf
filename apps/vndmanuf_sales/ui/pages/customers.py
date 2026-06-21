"""Customers & Sites sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

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
            {"name": "Postcode", "id": "postcode"},
        ],
        data=[],
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={"padding": "0.5rem"},
        style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
    )

    add_site_card = dbc.Card(
        [
            dbc.CardHeader(html.H6("Add site", className="mb-0")),
            dbc.CardBody(
                [
                    html.P(
                        "Sites are delivery addresses per customer. Add a site here, then choose it when creating an order.",
                        className="text-muted small mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Customer"),
                                    dcc.Dropdown(
                                        id="sales-add-site-customer",
                                        placeholder="Select customer...",
                                    ),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Site name"),
                                    dbc.Input(
                                        id="sales-add-site-name",
                                        placeholder="e.g. Warehouse, Head Office",
                                    ),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("State"),
                                    dbc.Input(
                                        id="sales-add-site-state",
                                        placeholder="e.g. VIC, NSW",
                                        maxLength=8,
                                    ),
                                ],
                                md=2,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Suburb"),
                                    dbc.Input(
                                        id="sales-add-site-suburb",
                                        placeholder="Suburb",
                                    ),
                                ],
                                md=2,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Postcode"),
                                    dbc.Input(
                                        id="sales-add-site-postcode",
                                        placeholder="Postcode",
                                        maxLength=10,
                                    ),
                                ],
                                md=2,
                            ),
                        ],
                        className="g-2 mb-2",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Button(
                                        "Add site",
                                        id="sales-add-site-submit",
                                        color="primary",
                                    ),
                                    html.Span(
                                        id="sales-add-site-feedback",
                                        className="ms-2 small",
                                    ),
                                ],
                                md=12,
                            ),
                        ]
                    ),
                ]
            ),
        ],
        className="shadow-sm mb-4",
    )

    return html.Div(
        [
            dcc.Store(id="sales-customers-sites-refresh", data=0),
            metrics,
            add_site_card,
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
