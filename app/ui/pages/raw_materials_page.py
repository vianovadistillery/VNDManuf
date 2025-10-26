"""Raw Materials page for Dash UI."""
from dash import html, dcc, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
from typing import Dict, List, Any


class RawMaterialsPage:
    """Raw Materials management page."""
    
    @staticmethod
    def get_layout():
        return dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H2("Raw Materials", className="mb-4")
                ])
            ]),
            
            # Filters
            dbc.Row([
                dbc.Col([
                    dbc.InputGroup([
                        dbc.InputGroupText("Status:"),
                        dbc.Select(
                            id="rm-status-filter",
                            options=[
                                {"label": "All", "value": "all"},
                                {"label": "Active", "value": "A"},
                                {"label": "Suspended", "value": "S"},
                                {"label": "Redundant", "value": "R"},
                                {"label": "Misc", "value": "M"},
                            ],
                            value="all",
                            style={"width": "200px"}
                        ),
                        dbc.InputGroupText("Group:"),
                        dbc.Select(id="rm-group-filter", options=[], value="all", style={"width": "200px"}),
                        dbc.InputGroupText("Search:"),
                        dbc.Input(id="rm-search-filter", placeholder="Code, Desc1, Desc2...", style={"width": "300px"}),
                        dbc.Button("Search", id="rm-search-btn", color="primary", className="ms-2"),
                    ], size="sm")
                ])
            ], className="mb-3"),
            
            # Action Buttons
            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("Add Raw Material", id="rm-add-btn", color="success"),
                        dbc.Button("Edit", id="rm-edit-btn", color="primary"),
                        dbc.Button("Delete", id="rm-delete-btn", color="danger"),
                        dbc.Button("🔄 Refresh", id="rm-refresh-btn", color="secondary"),
                        dbc.Button("Import CSV", id="rm-import-btn", color="info"),
                        dbc.Button("Export CSV", id="rm-export-btn", color="secondary"),
                    ])
                ])
            ], className="mb-3"),
            
            # Data Table
            dbc.Row([
                dbc.Col([
                    dash_table.DataTable(
                        id="rm-table",
                        columns=[
                            {"name": "Code", "id": "code"},
                            {"name": "Desc1", "id": "desc1"},
                            {"name": "Desc2", "id": "desc2"},
                            {"name": "Search", "id": "search_key"},
                            {"name": "SG", "id": "sg", "type": "numeric", "format": {"specifier": ".4f"}},
                            {"name": "Purchase Cost", "id": "purchase_cost", "type": "numeric", "format": {"specifier": ".2f"}},
                            {"name": "Purchase Unit", "id": "purchase_unit"},
                            {"name": "Usage Cost", "id": "usage_cost", "type": "numeric", "format": {"specifier": ".2f"}},
                            {"name": "Usage Unit", "id": "usage_unit"},
                            {"name": "Active", "id": "active_flag"},
                            {"name": "SOH", "id": "soh", "type": "numeric"},
                            {"name": "Hazard", "id": "hazard"},
                            {"name": "Condition", "id": "condition"},
                            {"name": "XERO Account", "id": "xero_account"},
                        ],
                        data=[],
                        sort_action="native",
                        filter_action="native",
                        page_action="native",
                        page_current=0,
                        page_size=25,
                        row_selectable="single",
                        selected_rows=[],
                        style_cell={'textAlign': 'left', 'fontSize': '12px'},
                        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                        style_data_conditional=[
                            {
                                'if': {'filter_query': '{active_flag} = S'},
                                'backgroundColor': '#fee',
                                'color': 'black',
                            },
                            {
                                'if': {'filter_query': '{active_flag} = R'},
                                'backgroundColor': '#eef',
                                'color': 'black',
                            },
                        ]
                    )
                ])
            ]),
            
            # Add/Edit Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(id="rm-modal-title")),
                dbc.ModalBody([
                    dbc.Tabs([
                        # Details Tab
                        dbc.Tab([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Active:"),
                                    dbc.Select(
                                        id="rm-input-active",
                                        options=[
                                            {"label": "Active", "value": "A"},
                                            {"label": "Suspended", "value": "S"},
                                            {"label": "Redundant", "value": "R"},
                                            {"label": "Misc", "value": "M"},
                                        ],
                                        value="A"
                                    ),
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Supplier:"),
                                    dbc.Select(
                                        id="rm-input-supplier",
                                        options=[],
                                        value=None
                                    ),
                                ], md=6),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Description 1:"),
                                    dbc.Input(id="rm-input-desc1", maxLength=25, required=True),
                                ], md=12),
                            ], className="mt-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Description 2:"),
                                    dbc.Input(id="rm-input-desc2", maxLength=25),
                                ], md=12),
                            ], className="mt-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Search Key:"),
                                    dbc.Input(id="rm-input-search-key", maxLength=5),
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Search Ext:"),
                                    dbc.Input(id="rm-input-search-ext", maxLength=8),
                                ], md=6),
                            ], className="mt-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Notes:"),
                                    dbc.Input(id="rm-input-notes", maxLength=25),
                                ], md=12),
                            ], className="mt-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("XERO Account:"),
                                    dbc.Input(id="rm-input-xero-account", maxLength=50),
                                ], md=12),
                            ], className="mt-2"),
                        ], label="Details", tab_id="details"),
                        
                        # Costs Tab
                        dbc.Tab([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("SG:"),
                                    dbc.Input(id="rm-input-sg", type="number", step=0.000001),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Purchase Cost:"),
                                    dbc.Input(id="rm-input-purcost", type="number", step=0.01),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Purchase Unit:"),
                                    dbc.Input(id="rm-input-purunit", maxLength=2),
                                ], md=4),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Usage Cost:"),
                                    dbc.Input(id="rm-input-usecost", type="number", step=0.01),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Usage Unit:"),
                                    dbc.Input(id="rm-input-useunit", maxLength=2),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Deal Cost:"),
                                    dbc.Input(id="rm-input-dealcost", type="number", step=0.01),
                                ], md=4),
                            ], className="mt-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Supplier Unit:"),
                                    dbc.Input(id="rm-input-supunit", maxLength=2),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Supplier Qty:"),
                                    dbc.Input(id="rm-input-supqty", type="number", step=0.001),
                                ], md=4),
                            ], className="mt-2"),
                        ], label="Costs", tab_id="costs"),
                        
                        # Stock Tab
                        dbc.Tab([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Stock on Hand (SOH):"),
                                    dbc.Input(id="rm-input-soh", type="number", step=0.001),
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Restock Level:"),
                                    dbc.Input(id="rm-input-restock", type="number", step=0.001),
                                ], md=6),
                            ], className="mt-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Opening SOH:"),
                                    dbc.Input(id="rm-input-osoh", type="number", step=0.001),
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("SOH Value:"),
                                    dbc.Input(id="rm-input-sohv", type="number", step=0.01),
                                ], md=6),
                            ], className="mt-2"),
                        ], label="Stock", tab_id="stock"),
                        
                        # Hazard Tab
                        dbc.Tab([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Hazard Code:"),
                                    dbc.Input(id="rm-input-hazard", maxLength=1),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Condition:"),
                                    dbc.Input(id="rm-input-condition", maxLength=1),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("MSDS Flag:"),
                                    dbc.Input(id="rm-input-msds", maxLength=1),
                                ], md=4),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Volume Solid:"),
                                    dbc.Input(id="rm-input-volsol", type="number", step=0.000001),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Solid SG:"),
                                    dbc.Input(id="rm-input-solidsg", type="number", step=0.000001),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label("Wt Solid:"),
                                    dbc.Input(id="rm-input-wtsol", type="number", step=0.000001),
                                ], md=4),
                            ], className="mt-2"),
                        ], label="Hazard/QC", tab_id="hazard"),
                    ], id="rm-modal-tabs")
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="rm-modal-cancel", color="secondary", className="me-2"),
                    dbc.Button("Save", id="rm-modal-save", color="primary"),
                ])
            ], id="rm-modal", is_open=False, size="xl"),
        ], fluid=True)

