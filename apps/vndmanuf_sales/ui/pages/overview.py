"""Sales Overview sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import dash_leaflet as dl
from dash import dcc, html

from apps.vndmanuf_sales.ui.components import (
    date_range_picker,
    filter_dropdown,
    kpi_card,
    sparkline_graph,
    top_table,
)
from apps.vndmanuf_sales.ui.period_filters import (
    default_period_iso,
    period_applying_store,
    period_preset_dropdown,
)

_default_start, _default_end = default_period_iso()


def layout():
    return html.Div(
        [
            period_applying_store("sales-overview-applying-preset"),
            dbc.Card(
                [
                    dbc.CardHeader(html.H6("Period & Filters", className="mb-0")),
                    dbc.CardBody(
                        dbc.Row(
                            [
                                dbc.Col(
                                    period_preset_dropdown(
                                        "sales-overview-period-preset"
                                    ),
                                    md=3,
                                ),
                                dbc.Col(
                                    date_range_picker(
                                        "sales-overview-date-range",
                                        "Date range",
                                        start_date=_default_start,
                                        end_date=_default_end,
                                    ),
                                    md=5,
                                ),
                                dbc.Col(
                                    filter_dropdown(
                                        "sales-overview-channel-filter",
                                        "Channel",
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
            dbc.Card(
                [
                    dbc.CardHeader(
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.H6("Customer Map", className="mb-0"),
                                    width="auto",
                                ),
                                dbc.Col(
                                    html.Small(
                                        id="sales-map-summary",
                                        className="text-muted",
                                    ),
                                    className="text-end",
                                ),
                                dbc.Col(
                                    dbc.ButtonGroup(
                                        [
                                            dbc.Button(
                                                "Look up addresses (OSM)",
                                                id="sales-map-enrich-btn",
                                                size="sm",
                                                color="secondary",
                                                outline=True,
                                            ),
                                            dbc.Button(
                                                "Look up with AI",
                                                id="sales-map-enrich-ai-btn",
                                                size="sm",
                                                color="secondary",
                                                outline=True,
                                            ),
                                        ],
                                        className="mt-2",
                                    ),
                                    width="auto",
                                    className="text-end",
                                ),
                            ],
                            className="align-items-center",
                        )
                    ),
                    dbc.CardBody(
                        [
                            html.Div(
                                id="sales-map-enrich-feedback",
                                className="small text-muted mb-2",
                            ),
                            dcc.Store(id="sales-map-enrich-store", data=0),
                            dbc.Alert(
                                [
                                    html.Strong("How locations work: "),
                                    "Pins are placed using ",
                                    html.Strong("latitude/longitude"),
                                    " (stored on the customer or site). If those are missing, ",
                                    "the map falls back to an approximate state-centre position. ",
                                    "Use ",
                                    html.Strong("Look up addresses (OSM)"),
                                    " to search OpenStreetMap by name, or ",
                                    html.Strong("Look up with AI"),
                                    " (needs OpenAI key in Nova U → AI Settings) when OSM has no match. ",
                                    "Both save street address fields and coordinates when found.",
                                ],
                                color="light",
                                className="small py-2 mb-2",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        filter_dropdown(
                                            "sales-map-rep-filter",
                                            "Sales rep",
                                            [],
                                        ),
                                        md=2,
                                    ),
                                    dbc.Col(
                                        filter_dropdown(
                                            "sales-map-buying-group-filter",
                                            "Buying group",
                                            [],
                                        ),
                                        md=2,
                                    ),
                                    dbc.Col(
                                        filter_dropdown(
                                            "sales-map-price-level-filter",
                                            "Price level",
                                            [],
                                        ),
                                        md=2,
                                    ),
                                    dbc.Col(
                                        filter_dropdown(
                                            "sales-map-volume-filter",
                                            "Sales volume",
                                            [],
                                        ),
                                        md=2,
                                    ),
                                    dbc.Col(
                                        filter_dropdown(
                                            "sales-map-status-filter",
                                            "Relationship",
                                            [],
                                        ),
                                        md=2,
                                    ),
                                    dbc.Col(
                                        html.Div(
                                            id="sales-map-legend",
                                            className="small mt-2",
                                        ),
                                        md=2,
                                    ),
                                ],
                                className="g-2 mb-3",
                            ),
                            dl.Map(
                                id="sales-customer-map",
                                center=[-25.27, 133.77],
                                zoom=4,
                                scrollWheelZoom=True,
                                style={"height": "1560px", "width": "100%"},
                                children=[
                                    dl.TileLayer(
                                        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                                        attribution=(
                                            '&copy; <a href="https://www.openstreetmap.org/'
                                            'copyright">OpenStreetMap</a>'
                                        ),
                                    ),
                                    dl.ScaleControl(
                                        position="bottomleft",
                                        imperial=False,
                                        metric=True,
                                    ),
                                    dl.LayerGroup(
                                        id="sales-customer-map-markers",
                                        children=[],
                                    ),
                                ],
                            ),
                        ]
                    ),
                ],
                className="mb-3 shadow-sm mt-4",
            ),
        ],
        className="sales-overview-tab",
    )
