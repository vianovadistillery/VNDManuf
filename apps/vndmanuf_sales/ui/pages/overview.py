"""Sales Overview sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html

from apps.vndmanuf_sales.ui.components import kpi_card, sparkline_graph, top_table


def layout():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        kpi_card("sales-kpi-total-orders", "Total Orders", "128"), md=3
                    ),
                    dbc.Col(
                        kpi_card(
                            "sales-kpi-total-revenue", "Revenue (Inc GST)", "$184,200"
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card(
                            "sales-kpi-average-order", "Average Order Value", "$1,440"
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card("sales-kpi-repeat-rate", "Repeat Rate", "42%"), md=3
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H6(
                                        "Sales Trend (Last 90 days)", className="mb-0"
                                    )
                                ),
                                dbc.CardBody(
                                    sparkline_graph("sales-overview-sparkline")
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H6("Customer Mix", className="mb-0")
                                ),
                                dbc.CardBody(
                                    html.Ul(
                                        [
                                            html.Li("New customers: 24"),
                                            html.Li("Repeat customers: 34"),
                                            html.Li("Churned customers: 5"),
                                        ],
                                        className="mb-0",
                                    )
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        md=6,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        top_table(
                            "sales-overview-top-skus",
                            "Top 5 SKUs",
                            ["SKU", "Name", "Units", "Revenue"],
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        top_table(
                            "sales-overview-top-customers",
                            "Top 5 Customers",
                            ["Customer", "Orders", "Revenue"],
                        ),
                        md=6,
                    ),
                ]
            ),
        ],
        className="sales-overview-tab",
    )
