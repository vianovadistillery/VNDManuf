"""Sales Overview sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html

from apps.vndmanuf_sales.services.analytics import default_period
from apps.vndmanuf_sales.ui.components import (
    date_range_picker,
    filter_dropdown,
    kpi_card,
    sparkline_graph,
    top_table,
)

_default_start, _default_end = default_period()


def layout():
    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardHeader(html.H6("Period & Filters", className="mb-0")),
                    dbc.CardBody(
                        dbc.Row(
                            [
                                dbc.Col(
                                    date_range_picker(
                                        "sales-overview-date-range",
                                        "Date range",
                                        start_date=_default_start.isoformat(),
                                        end_date=_default_end.isoformat(),
                                    ),
                                    md=4,
                                ),
                                dbc.Col(
                                    filter_dropdown(
                                        "sales-overview-channel-filter",
                                        "Channel",
                                        [],
                                    ),
                                    md=4,
                                ),
                                dbc.Col(
                                    filter_dropdown(
                                        "sales-overview-pricebook-filter",
                                        "Pricebook",
                                        [],
                                    ),
                                    md=4,
                                ),
                            ],
                            className="g-2",
                        )
                    ),
                ],
                className="mb-3 shadow-sm",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        kpi_card("sales-kpi-total-orders", "Total Orders", "—"), md=3
                    ),
                    dbc.Col(
                        kpi_card("sales-kpi-total-revenue", "Revenue (Inc GST)", "—"),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card("sales-kpi-average-order", "Average Order Value", "—"),
                        md=3,
                    ),
                    dbc.Col(
                        kpi_card("sales-kpi-repeat-rate", "Repeat Rate", "—"), md=3
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
                                    html.H6("Sales Trend", className="mb-0")
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
                                        id="sales-overview-customer-mix",
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
