"""Contacts page for Dash UI."""
from dash import html
import dash_bootstrap_components as dbc
from dash import dash_table


class ContactsPage:
    """Contacts management page."""
    
    @staticmethod
    def get_layout():
        return dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H2("Contacts", className="mb-4")
                ])
            ]),
            
            # Filters
            dbc.Row([
                dbc.Col([
                    dbc.InputGroup([
                        dbc.InputGroupText("Search:"),
                        dbc.Input(id="contacts-search-filter", placeholder="Search by name...", style={"width": "300px"}),
                        dbc.Button("Search", id="contacts-search-btn", color="primary", className="ms-2"),
                        dbc.Button("Clear", id="contacts-clear-btn", color="secondary", className="ms-2"),
                    ], size="sm")
                ]),
                dbc.Col([
                    html.Div([
                        dbc.Label("Active Only:", className="me-2", style={"display": "inline-block", "marginRight": "10px"}),
                        dbc.Checkbox(id="contacts-active-filter", label="", value=True, style={"display": "inline-block"}),
                    ])
                ]),
                dbc.Col([
                    html.Div([
                        dbc.Label("Filter by Type:", className="me-2", style={"display": "inline-block", "marginRight": "10px"}),
                        dbc.Checkbox(id="contacts-filter-customer", label="Customer", value=True, className="me-2", style={"display": "inline-block"}),
                        dbc.Checkbox(id="contacts-filter-supplier", label="Supplier", value=True, className="me-2", style={"display": "inline-block"}),
                        dbc.Checkbox(id="contacts-filter-other", label="Other", value=True, style={"display": "inline-block"}),
                    ])
                ])
            ], className="mb-3"),
            
            # Action Buttons
            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("Add Contact", id="contacts-add-btn", color="success"),
                        dbc.Button("Edit", id="contacts-edit-btn", color="primary"),
                        dbc.Button("Delete", id="contacts-delete-btn", color="danger"),
                        dbc.Button("🔄 Refresh", id="contacts-refresh-btn", color="secondary"),
                    ])
                ])
            ], className="mb-3"),
            
            # Data Table
            dbc.Row([
                dbc.Col([
                    dash_table.DataTable(
                        id="contacts-table",
                        columns=[
                            {"name": "Code", "id": "code"},
                            {"name": "Name", "id": "name"},
                            {"name": "Contact", "id": "contact_person"},
                            {"name": "Email", "id": "email"},
                            {"name": "Phone", "id": "phone"},
                            {"name": "Customer", "id": "is_customer", "type": "text"},
                            {"name": "Supplier", "id": "is_supplier", "type": "text"},
                            {"name": "Other", "id": "is_other", "type": "text"},
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
                dbc.ModalHeader(dbc.ModalTitle(id="contacts-modal-title")),
                dbc.ModalBody([
                    dbc.Form([
                        html.Div(id="contacts-form-id-hidden", style={"display": "none"}),
                        dbc.Label("Code (leave blank to auto-generate)"),
                        dbc.Input(id="contacts-form-code", type="text", placeholder="5 characters, e.g., ABC12"),
                        dbc.Label("Name *"),
                        dbc.Input(id="contacts-form-name", type="text", required=True),
                        dbc.Label("Contact Person"),
                        dbc.Input(id="contacts-form-contact", type="text"),
                        dbc.Label("Email"),
                        dbc.Input(id="contacts-form-email", type="email"),
                        dbc.Label("Phone"),
                        dbc.Input(id="contacts-form-phone", type="tel"),
                        dbc.Label("Address"),
                        dbc.Textarea(id="contacts-form-address", rows=3),
                        dbc.Label("XERO ID (UUID)"),
                        dbc.Input(id="contacts-form-xero-id", type="text", placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000"),
                        html.Hr(),
                        dbc.Label("Contact Types:"),
                        dbc.Checkbox(id="contacts-form-is-customer", label="Customer", className="me-2"),
                        dbc.Checkbox(id="contacts-form-is-supplier", label="Supplier", className="me-2"),
                        dbc.Checkbox(id="contacts-form-is-other", label="Other", className="mb-3"),
                        dbc.Switch(
                            id="contacts-form-active",
                            label="Active",
                            value=True,
                            className="mt-3"
                        )
                    ])
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="contacts-modal-cancel", color="secondary"),
                    dbc.Button("Save", id="contacts-modal-save", color="primary")
                ])
            ], id="contacts-modal", is_open=False),
            
            # Delete Confirmation Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Confirm Delete")),
                dbc.ModalBody([
                    html.P("Are you sure you want to delete this contact?"),
                    html.P(id="contacts-delete-name", className="fw-bold text-danger")
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="contacts-delete-cancel", color="secondary"),
                    dbc.Button("Delete", id="contacts-delete-confirm", color="danger")
                ])
            ], id="contacts-delete-modal", is_open=False)
        ], fluid=True)


