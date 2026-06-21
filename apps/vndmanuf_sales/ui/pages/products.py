"""Sales Products sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, html

from apps.vndmanuf_sales.services.analytics import default_period
from apps.vndmanuf_sales.ui.components import date_range_picker, filter_dropdown

_default_start, _default_end = default_period()


def layout():
    filters = dbc.Card(
        [
            dbc.CardHeader(html.H6("Filters", className="mb-0")),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                date_range_picker(
                                    "sales-products-date-range",
                                    "Date range",
                                    start_date=_default_start.isoformat(),
                                    end_date=_default_end.isoformat(),
                                ),
                                md=4,
                            ),
                            dbc.Col(
                                filter_dropdown(
                                    "sales-products-channel-filter",
                                    "Channel",
                                    [],
                                ),
                                md=2,
                            ),
                            dbc.Col(
                                filter_dropdown(
                                    "sales-products-pricebook-filter",
                                    "Pricebook",
                                    [],
                                ),
                                md=3,
                            ),
                            dbc.Col(
                                filter_dropdown(
                                    "sales-products-type-filter",
                                    "Segment",
                                    [
                                        {"label": "Top movers", "value": "top"},
                                        {"label": "Slow movers", "value": "slow"},
                                        {
                                            "label": "New SKUs (first sale in period)",
                                            "value": "new",
                                        },
                                    ],
                                ),
                                md=3,
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
            {
                "name": "Units Sold",
                "id": "units",
                "type": "numeric",
                "format": {"specifier": ",.2f"},
            },
            {
                "name": "Revenue (Inc GST)",
                "id": "revenue",
                "type": "numeric",
                "format": {"specifier": "$,.2f"},
            },
            {
                "name": "On Hand",
                "id": "inventory",
                "type": "numeric",
                "format": {"specifier": ",.2f"},
            },
            {"name": "Channel Mix", "id": "channel_mix"},
        ],
        data=[],
        page_size=20,
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"padding": "0.5rem"},
        style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
    )

    totals_bar = html.Div(
        id="sales-products-totals",
        className="mt-3 p-3 bg-light rounded border fw-semibold",
        children="Totals: —",
    )

    return html.Div(
        [
            filters,
            dbc.Card(
                [
                    dbc.CardHeader(html.H6("Products Sold", className="mb-0")),
                    dbc.CardBody([table, totals_bar]),
                ],
                className="shadow-sm",
            ),
        ],
        className="sales-products-tab",
    )
