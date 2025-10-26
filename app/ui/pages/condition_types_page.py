"""Condition Types page for Dash UI."""
from dash import html, dcc, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
from typing import Dict, List, Any


class ConditionTypesPage:
    """Condition Types management page for hazard codes and MSDS flags."""
    
    @staticmethod
    def get_layout():
        return dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H2("Condition Types & Hazard Codes", className="mb-4")
                ])
            ]),
            
            # Tabs
            dbc.Row([
                dbc.Col([
                    dbc.Tabs(
                        id="condition-tabs",
                        active_tab="hazard",
                        children=[
                            dbc.Tab(label="Hazard Codes", tab_id="hazard"),
                            dbc.Tab(label="Condition Types", tab_id="condition"),
                            dbc.Tab(label="MSDS Tracking", tab_id="msds"),
                        ],
                        className="mb-3"
                    )
                ])
            ]),
            
            # Hazard Content (default shown)
            html.Div(id="hazard-content", children=[
                dbc.Card([
                    dbc.CardHeader("Hazard Codes"),
                    dbc.CardBody([
                        dbc.ButtonGroup([
                            dbc.Button("Add", id="hazard-add", color="success"),
                            dbc.Button("Edit", id="hazard-edit", color="primary"),
                            dbc.Button("Delete", id="hazard-delete", color="danger"),
                        ]),
                        dash_table.DataTable(
                            id="hazard-table",
                            columns=[
                                {"name": "Code", "id": "code", "editable": True},
                                {"name": "Description", "id": "description", "editable": True},
                                {"name": "Extended Description", "id": "extended_desc", "editable": True},
                            ],
                            data=[],
                            sort_action="native",
                            row_selectable="single",
                            editable=True,
                        )
                    ])
                ], className="mt-3")
            ]),
            
            # Condition Content (hidden by default)
            html.Div(id="condition-content", children=[
                dbc.Card([
                    dbc.CardHeader("Storage Conditions"),
                    dbc.CardBody([
                        dbc.ButtonGroup([
                            dbc.Button("Add", id="condition-add", color="success"),
                            dbc.Button("Edit", id="condition-edit", color="primary"),
                            dbc.Button("Delete", id="condition-delete", color="danger"),
                        ]),
                        dash_table.DataTable(
                            id="condition-table",
                            columns=[
                                {"name": "Code", "id": "code", "editable": True},
                                {"name": "Description", "id": "description", "editable": True},
                                {"name": "Temp Range", "id": "temp_range", "editable": True},
                            ],
                            data=[],
                            sort_action="native",
                            row_selectable="single",
                            editable=True,
                        )
                    ])
                ], className="mt-3")
            ], style={"display": "none"}),
            
            # MSDS Content (hidden by default)
            html.Div(id="msds-content", children=[
                dbc.Card([
                    dbc.CardHeader("Materials with MSDS Requirements"),
                    dbc.CardBody([
                        dbc.Label("Filter by MSDS Flag:"),
                        dbc.Select(
                            id="msds-filter",
                            options=[
                                {"label": "All", "value": "all"},
                                {"label": "MSDS Required", "value": "Y"},
                                {"label": "No MSDS", "value": "N"},
                            ],
                            value="all"
                        ),
                        dash_table.DataTable(
                            id="msds-table",
                            columns=[
                                {"name": "Code", "id": "code"},
                                {"name": "Material", "id": "desc1"},
                                {"name": "Hazard", "id": "hazard"},
                                {"name": "MSDS Flag", "id": "msds_flag"},
                                {"name": "Last Updated", "id": "last_movement_date"},
                            ],
                            data=[],
                            sort_action="native",
                            row_selectable="single",
                            export_format="csv",
                        )
                    ])
                ], className="mt-3")
            ], style={"display": "none"})
        ], fluid=True)

