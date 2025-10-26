"""Stocktake page for Dash UI."""
from dash import html, dcc, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
from typing import Dict, List, Any


class StocktakePage:
    """Stocktake page for physical inventory counts."""
    
    @staticmethod
    def get_layout():
        return dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H2("Stocktake", className="mb-4")
                ])
            ]),
            
            # Stocktake Info
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Stocktake Date:"),
                                    dcc.DatePickerSingle(id="stocktake-date", date=None, display_format="YYYY-MM-DD"),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Reference:"),
                                    dbc.Input(id="stocktake-ref", placeholder="e.g., ST-2025-001"),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Counted By:"),
                                    dbc.Input(id="stocktake-counter", maxLength=3),
                                ], md=4),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Start Stocktake", id="stocktake-start", color="success", className="mt-3"),
                                    dbc.Button("Import CSV", id="stocktake-import", color="info", className="mt-3 ms-2"),
                                    dbc.Button("Export CSV", id="stocktake-export", color="secondary", className="mt-3 ms-2"),
                                ])
                            ])
                        ])
                    ])
                ])
            ], className="mb-3"),
            
            # Count Entry Table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Physical Counts"),
                        dbc.CardBody([
                            dash_table.DataTable(
                                id="stocktake-table",
                                columns=[
                                    {"name": "Code", "id": "code"},
                                    {"name": "Material", "id": "desc1", "editable": False},
                                    {"name": "System SOH", "id": "system_soh", "type": "numeric", "editable": False, "format": {"specifier": ".3f"}},
                                    {"name": "Physical Count", "id": "physical_count", "type": "numeric", "editable": True, "format": {"specifier": ".3f"}},
                                    {"name": "Variance", "id": "variance", "type": "numeric", "editable": False, "format": {"specifier": ".3f"}},
                                    {"name": "Variance %", "id": "variance_pct", "type": "numeric", "editable": False, "format": {"specifier": ".1f"}},
                                ],
                                data=[],
                                sort_action="native",
                                editable=True,
                                style_data_conditional=[
                                    {
                                        'if': {'filter_query': '{variance} < 0'},
                                        'backgroundColor': '#fee',
                                    },
                                    {
                                        'if': {'filter_query': '{variance} > 0'},
                                        'backgroundColor': '#efe',
                                    }
                                ],
                                export_format="csv",
                            )
                        ])
                    ])
                ])
            ], className="mb-3"),
            
            # Summary Card
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Summary"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Strong("Total Items:"),
                                    html.Div(id="stocktake-total-items", className="text-muted")
                                ], md=3),
                                dbc.Col([
                                    html.Strong("Items with Variance:"),
                                    html.Div(id="stocktake-variance-count", className="text-warning")
                                ], md=3),
                                dbc.Col([
                                    html.Strong("Total Variance (kg):"),
                                    html.Div(id="stocktake-total-variance", className="text-info")
                                ], md=3),
                                dbc.Col([
                                    html.Strong("Status:"),
                                    html.Div(id="stocktake-status", className="text-success")
                                ], md=3),
                            ])
                        ])
                    ])
                ])
            ], className="mb-3"),
            
            # Actions
            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("Calculate Variances", id="stocktake-calc", color="primary"),
                        dbc.Button("Update SOH", id="stocktake-update", color="success"),
                        dbc.Button("Export Report", id="stocktake-export-report", color="secondary"),
                    ])
                ])
            ])
        ], fluid=True)

