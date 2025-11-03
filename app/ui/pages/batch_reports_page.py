"""Batch Reporting page for Dash UI."""

import dash_bootstrap_components as dbc
from dash import dash_table, html


class BatchReportsPage:
    """Batch Reporting page with history and variance analysis."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                # Header
                dbc.Row(
                    [dbc.Col([html.H2("Batch Reporting & Analysis", className="mb-4")])]
                ),
                # Filters
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Year (YY):"),
                                                                dbc.Input(
                                                                    id="batch-report-year",
                                                                    placeholder="22",
                                                                    maxLength=2,
                                                                    style={
                                                                        "width": "80px"
                                                                    },
                                                                ),
                                                            ],
                                                            md=3,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Formula:"),
                                                                dbc.Input(
                                                                    id="batch-report-formula",
                                                                    placeholder="Code...",
                                                                ),
                                                            ],
                                                            md=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Status:"),
                                                                dbc.Select(
                                                                    id="batch-report-status",
                                                                    options=[
                                                                        {
                                                                            "label": "All",
                                                                            "value": "all",
                                                                        },
                                                                        {
                                                                            "label": "Completed",
                                                                            "value": "COMPLETED",
                                                                        },
                                                                        {
                                                                            "label": "In Progress",
                                                                            "value": "EXECUTED",
                                                                        },
                                                                    ],
                                                                    value="all",
                                                                ),
                                                            ],
                                                            md=3,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Button(
                                                                    "Run Report",
                                                                    id="batch-report-run",
                                                                    color="primary",
                                                                    className="mt-4",
                                                                ),
                                                            ],
                                                            md=2,
                                                        ),
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ],
                    className="mb-3",
                ),
                # Action Buttons
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            "Export CSV",
                                            id="batch-report-export",
                                            color="info",
                                        ),
                                        dbc.Button(
                                            "Print Selected",
                                            id="batch-report-print",
                                            color="warning",
                                        ),
                                        dbc.Button(
                                            "Variance Analysis",
                                            id="batch-report-variance",
                                            color="secondary",
                                        ),
                                    ]
                                )
                            ]
                        )
                    ],
                    className="mb-3",
                ),
                # Batch History Table
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Batch History"),
                                        dbc.CardBody(
                                            [
                                                dash_table.DataTable(
                                                    id="batch-report-table",
                                                    columns=[
                                                        {
                                                            "name": "Batch Code",
                                                            "id": "batch_code",
                                                        },
                                                        {"name": "Date", "id": "date"},
                                                        {
                                                            "name": "Formula",
                                                            "id": "formula_code",
                                                        },
                                                        {
                                                            "name": "Target (kg)",
                                                            "id": "target_kg",
                                                            "type": "numeric",
                                                            "format": {
                                                                "specifier": ".3f"
                                                            },
                                                        },
                                                        {
                                                            "name": "Actual (kg)",
                                                            "id": "actual_kg",
                                                            "type": "numeric",
                                                            "format": {
                                                                "specifier": ".3f"
                                                            },
                                                        },
                                                        {
                                                            "name": "Actual (L)",
                                                            "id": "actual_l",
                                                            "type": "numeric",
                                                            "format": {
                                                                "specifier": ".2f"
                                                            },
                                                        },
                                                        {
                                                            "name": "Variance %",
                                                            "id": "variance_pct",
                                                            "type": "numeric",
                                                            "format": {
                                                                "specifier": ".1f"
                                                            },
                                                        },
                                                        {
                                                            "name": "Operator",
                                                            "id": "operator",
                                                        },
                                                        {
                                                            "name": "Status",
                                                            "id": "status",
                                                        },
                                                    ],
                                                    data=[],
                                                    sort_action="native",
                                                    filter_action="native",
                                                    row_selectable="single",
                                                    page_action="native",
                                                    page_size=25,
                                                    style_cell={"fontSize": "11px"},
                                                    style_header={
                                                        "backgroundColor": "rgb(230, 230, 230)",
                                                        "fontWeight": "bold",
                                                    },
                                                    style_data_conditional=[
                                                        {
                                                            "if": {
                                                                "filter_query": "{variance_pct} < -5"
                                                            },
                                                            "backgroundColor": "#fee",
                                                            "color": "black",
                                                        },
                                                        {
                                                            "if": {
                                                                "filter_query": "{variance_pct} > 5"
                                                            },
                                                            "backgroundColor": "#ffc",
                                                            "color": "black",
                                                        },
                                                    ],
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                # Variance Summary (collapsible)
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Collapse(
                                    [
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Variance Summary"),
                                                dbc.CardBody(
                                                    [
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Batches with variance < -5%:"
                                                                        ),
                                                                        html.Div(
                                                                            id="batch-variance-low",
                                                                            className="text-danger",
                                                                        ),
                                                                    ],
                                                                    md=4,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Batches with variance > 5%:"
                                                                        ),
                                                                        html.Div(
                                                                            id="batch-variance-high",
                                                                            className="text-warning",
                                                                        ),
                                                                    ],
                                                                    md=4,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(
                                                                            "Average variance:"
                                                                        ),
                                                                        html.Div(
                                                                            id="batch-variance-avg",
                                                                            className="text-info",
                                                                        ),
                                                                    ],
                                                                    md=4,
                                                                ),
                                                            ]
                                                        )
                                                    ]
                                                ),
                                            ]
                                        )
                                    ],
                                    id="batch-variance-collapse",
                                    is_open=False,
                                )
                            ]
                        )
                    ],
                    className="mt-3",
                ),
                # Print Preview Modal
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Batch Ticket Print Preview")),
                        dbc.ModalBody(
                            [
                                html.Pre(
                                    id="batch-print-content",
                                    style={
                                        "whiteSpace": "pre-wrap",
                                        "fontFamily": "monospace",
                                    },
                                )
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Close", id="batch-print-close", color="secondary"
                                )
                            ]
                        ),
                    ],
                    id="batch-print-modal",
                    is_open=False,
                    size="lg",
                ),
            ],
            fluid=True,
        )
