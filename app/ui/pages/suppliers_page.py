"""Suppliers page for Dash UI."""
from dash import html
import dash_bootstrap_components as dbc
from dash import dash_table


class SuppliersPage:
    """Suppliers management page."""
    
    @staticmethod
    def get_layout():
        return dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H2("Suppliers", className="mb-4")
                ])
            ]),
            
            # Filters
            dbc.Row([
                dbc.Col([
                    dbc.InputGroup([
                        dbc.InputGroupText("Search:"),
                        dbc.Input(id="suppliers-search-filter", placeholder="Search by name...", style={"width": "300px"}),
                        dbc.Button("Search", id="suppliers-search-btn", color="primary", className="ms-2"),
                        dbc.Button("Clear", id="suppliers-clear-btn", color="secondary", className="ms-2"),
                    ], size="sm")
                ]),
                dbc.Col([
                    dbc.Checklist(
                        id="suppliers-active-filter",
                        options=[
                            {"label": " Active Only", "value": "active"}
                        ],
                        value=["active"]
                    )
                ])
            ], className="mb-3"),
            
            # Action Buttons
            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("Add Supplier", id="suppliers-add-btn", color="success"),
                        dbc.Button("Edit", id="suppliers-edit-btn", color="primary"),
                        dbc.Button("Delete", id="suppliers-delete-btn", color="danger"),
                        dbc.Button("🔄 Refresh", id="suppliers-refresh-btn", color="secondary"),
                    ])
                ])
            ], className="mb-3"),
            
            # Data Table
            dbc.Row([
                dbc.Col([
                    dash_table.DataTable(
                        id="suppliers-table",
                        columns=[
                            {"name": "ID", "id": "id"},
                            {"name": "Name", "id": "name"},
                            {"name": "Contact", "id": "contact_person"},
                            {"name": "Email", "id": "email"},
                            {"name": "Phone", "id": "phone"},
                            {"name": "Active", "id": "is_active", "type": "text"},
                        ],
                        data=[],
                        sort_action="native",
                        filter_action="native",
                        page_action="native",
                        page_current=0,
                        page_size=20,
                        style_cell={
                            "textAlign": "left",
                            "padding": "10px",
                            "fontSize": "14px"
                        },
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold"
                        },
                        style_data_conditional=[
                            {
                                "if": {"filter_query": "{is_active} = false"},
                                "backgroundColor": "#ffe6e6"
                            }
                        ],
                        row_selectable="single"
                    )
                ])
            ], className="mb-3"),
            
            # Add/Edit Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(id="suppliers-modal-title")),
                dbc.ModalBody([
                        dbc.Form([
                        dbc.Label("Name *"),
                        html.Div(id="suppliers-form-id-hidden", style={"display": "none"}),
                        dbc.Input(id="suppliers-form-name", type="text", required=True),
                        dbc.Label("Contact Person"),
                        dbc.Input(id="suppliers-form-contact", type="text"),
                        dbc.Label("Email"),
                        dbc.Input(id="suppliers-form-email", type="email"),
                        dbc.Label("Phone"),
                        dbc.Input(id="suppliers-form-phone", type="tel"),
                        dbc.Label("Address"),
                        dbc.Textarea(id="suppliers-form-address", rows=3),
                        dbc.Label("XERO ID (UUID)"),
                        dbc.Input(id="suppliers-form-xero-id", type="text", placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000"),
                        dbc.Switch(
                            id="suppliers-form-active",
                            label="Active",
                            value=True,
                            className="mt-3"
                        )
                    ])
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="suppliers-modal-cancel", color="secondary"),
                    dbc.Button("Save", id="suppliers-modal-save", color="primary")
                ])
            ], id="suppliers-modal", is_open=False),
            
            # Delete Confirmation Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Confirm Delete")),
                dbc.ModalBody([
                    html.P("Are you sure you want to delete this supplier?"),
                    html.P(id="suppliers-delete-name", className="fw-bold text-danger")
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="suppliers-delete-cancel", color="secondary"),
                    dbc.Button("Delete", id="suppliers-delete-confirm", color="danger")
                ])
            ], id="suppliers-delete-modal", is_open=False)
        ], fluid=True)

