"""Raw Material Reports page for Dash UI."""

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


class RmReportsPage:
    """Raw Material Reports page with usage, valuation, and reorder analysis."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                # Header
                dbc.Row([dbc.Col([html.H2("Raw Material Reports", className="mb-4")])]),
                # Report Type Tabs
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Tabs(
                                    id="rm-report-type",
                                    active_tab="usage",
                                    children=[
                                        dbc.Tab(label="Usage Report", tab_id="usage"),
                                        dbc.Tab(
                                            label="Stock Valuation", tab_id="valuation"
                                        ),
                                        dbc.Tab(
                                            label="Reorder Analysis", tab_id="reorder"
                                        ),
                                    ],
                                    className="mb-3",
                                )
                            ]
                        )
                    ]
                ),
                # Usage Report Content
                html.Div(
                    id="rm-usage-content",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardHeader("Material Usage Report"),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Start Date:"),
                                                        dcc.DatePickerSingle(
                                                            id="rm-usage-start-date",
                                                            date="2025-01-01",
                                                            display_format="YYYY-MM-DD",
                                                        ),
                                                    ],
                                                    md=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("End Date:"),
                                                        dcc.DatePickerSingle(
                                                            id="rm-usage-end-date",
                                                            date="2025-12-31",
                                                            display_format="YYYY-MM-DD",
                                                        ),
                                                    ],
                                                    md=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Generate Report",
                                                            id="rm-usage-generate",
                                                            color="primary",
                                                            className="mt-4",
                                                        ),
                                                    ],
                                                    md=4,
                                                ),
                                            ]
                                        ),
                                        dash_table.DataTable(
                                            id="rm-usage-table",
                                            columns=[
                                                {
                                                    "name": "Material",
                                                    "id": "material_desc",
                                                },
                                                {
                                                    "name": "Total (kg)",
                                                    "id": "total_kg",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".3f"},
                                                },
                                                {
                                                    "name": "Total Cost",
                                                    "id": "total_cost",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".2f"},
                                                },
                                                {
                                                    "name": "Batches",
                                                    "id": "batch_count",
                                                    "type": "numeric",
                                                },
                                            ],
                                            data=[],
                                            sort_action="native",
                                            export_format="csv",
                                        ),
                                    ]
                                ),
                            ],
                            className="mt-3",
                        )
                    ],
                ),
                # Stock Valuation Content (hidden by default)
                html.Div(
                    id="rm-valuation-content",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardHeader("Stock Valuation Report"),
                                dbc.CardBody(
                                    [
                                        dbc.Button(
                                            "Generate Report",
                                            id="rm-valuation-generate",
                                            color="primary",
                                            className="mb-3",
                                        ),
                                        dash_table.DataTable(
                                            id="rm-valuation-table",
                                            columns=[
                                                {
                                                    "name": "Material",
                                                    "id": "material_desc",
                                                },
                                                {
                                                    "name": "SOH (kg)",
                                                    "id": "soh",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".3f"},
                                                },
                                                {
                                                    "name": "Unit Cost",
                                                    "id": "unit_cost",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".2f"},
                                                },
                                                {
                                                    "name": "Value",
                                                    "id": "value",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".2f"},
                                                },
                                            ],
                                            data=[],
                                            sort_action="native",
                                            export_format="csv",
                                        ),
                                        html.Hr(),
                                        html.Div(
                                            id="rm-valuation-total",
                                            className="text-primary",
                                        ),
                                    ]
                                ),
                            ],
                            className="mt-3",
                        )
                    ],
                    style={"display": "none"},
                ),
                # Reorder Analysis Content (hidden by default)
                html.Div(
                    id="rm-reorder-content",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardHeader("Materials Below Reorder Level"),
                                dbc.CardBody(
                                    [
                                        dbc.Button(
                                            "Refresh",
                                            id="rm-reorder-refresh",
                                            color="primary",
                                            className="mb-3",
                                        ),
                                        dash_table.DataTable(
                                            id="rm-reorder-table",
                                            columns=[
                                                {
                                                    "name": "Material",
                                                    "id": "material_desc",
                                                },
                                                {
                                                    "name": "SOH (kg)",
                                                    "id": "soh",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".3f"},
                                                },
                                                {
                                                    "name": "Reorder Level",
                                                    "id": "restock_level",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".3f"},
                                                },
                                                {
                                                    "name": "Deficiency",
                                                    "id": "deficiency",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".3f"},
                                                },
                                                {
                                                    "name": "Purchase Cost",
                                                    "id": "purchase_cost",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".2f"},
                                                },
                                                {"name": "Unit", "id": "purchase_unit"},
                                            ],
                                            data=[],
                                            sort_action="native",
                                            style_data_conditional=[
                                                {
                                                    "if": {
                                                        "filter_query": "{deficiency} > 0"
                                                    },
                                                    "backgroundColor": "#fee",
                                                    "color": "black",
                                                }
                                            ],
                                            export_format="csv",
                                        ),
                                    ]
                                ),
                            ],
                            className="mt-3",
                        )
                    ],
                    style={"display": "none"},
                ),
            ],
            fluid=True,
        )
