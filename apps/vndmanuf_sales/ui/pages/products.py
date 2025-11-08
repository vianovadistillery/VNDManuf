"""Sales Products sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


def layout():
    filters = dbc.Card(
        [
            dbc.CardHeader(html.H6("Filters", className="mb-0")),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Dropdown(
                                    id="sales-products-channel-filter",
                                    options=[
                                        {"label": "Retail", "value": "RETAIL"},
                                        {"label": "Venue", "value": "VENUE"},
                                        {"label": "Online", "value": "ONLINE"},
                                        {"label": "Direct", "value": "DIRECT"},
                                    ],
                                    placeholder="Channel",
                                ),
                                md=4,
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="sales-products-pricebook-filter",
                                    options=[],
                                    placeholder="Pricebook",
                                ),
                                md=4,
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="sales-products-type-filter",
                                    options=[
                                        {"label": "Top movers", "value": "top"},
                                        {"label": "Slow movers", "value": "slow"},
                                        {"label": "New SKUs", "value": "new"},
                                    ],
                                    placeholder="Segment",
                                ),
                                md=4,
                            ),
                        ],
                        className="g-2",
                    )
                ]
            ),
        ],
        className="mb-3 shadow-sm",
    )

    table = dash_table.DataTable(
        id="sales-products-table",
        columns=[
            {"name": "SKU", "id": "sku"},
            {"name": "Name", "id": "name"},
            {"name": "Units Sold", "id": "units"},
            {"name": "Revenue (Inc GST)", "id": "revenue"},
            {"name": "On Hand", "id": "inventory"},
            {"name": "Channel Mix", "id": "channel_mix"},
        ],
        data=[],
        page_size=15,
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"padding": "0.5rem"},
        style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
    )

    return html.Div(
        [
            filters,
            dbc.Card(
                [
                    dbc.CardHeader(html.H6("Products Performance", className="mb-0")),
                    dbc.CardBody(table),
                ],
                className="shadow-sm",
            ),
        ],
        className="sales-products-tab",
    )
