"""Work Orders page for Dash UI."""

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


class WorkOrdersPage:
    """Work Orders page with list, detail, and workflow tabs."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                # Header
                dbc.Row([dbc.Col([html.H2("Work Orders", className="mb-4")])]),
                # Main tabs
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Tabs(
                                    id="wo-main-tabs",
                                    active_tab="list",
                                    children=[
                                        dbc.Tab(label="List", tab_id="list"),
                                        dbc.Tab(label="Detail", tab_id="detail"),
                                        dbc.Tab(label="Rate Manager", tab_id="rates"),
                                        dbc.Tab(
                                            label="Batch Lookup", tab_id="batch-lookup"
                                        ),
                                    ],
                                    className="mb-3",
                                )
                            ]
                        )
                    ]
                ),
                # Hidden placeholder buttons for callbacks (must be outside dynamic content)
                html.Div(
                    [
                        dbc.Button(
                            "Issue Material",
                            id="wo-issue-submit-btn",
                            style={"display": "none"},
                        ),
                        dbc.Button(
                            "Record QC Test",
                            id="wo-qc-submit-btn",
                            style={"display": "none"},
                        ),
                        dbc.Button(
                            "Complete Work Order",
                            id="wo-complete-submit-btn",
                            style={"display": "none"},
                        ),
                        dbc.Button(
                            "Release",
                            id="wo-release-btn",
                            style={"display": "none"},
                        ),
                        dbc.Button(
                            "Start",
                            id="wo-start-btn",
                            style={"display": "none"},
                        ),
                        dbc.Button(
                            "Void",
                            id="wo-void-btn",
                            style={"display": "none"},
                        ),
                    ],
                    style={"display": "none"},
                ),
                # Filters (always visible)
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Status:"),
                                dcc.Dropdown(
                                    id="wo-status-filter",
                                    options=[
                                        {
                                            "label": "All",
                                            "value": "",
                                        },
                                        {
                                            "label": "Draft",
                                            "value": "draft",
                                        },
                                        {
                                            "label": "Released",
                                            "value": "released",
                                        },
                                        {
                                            "label": "In Progress",
                                            "value": "in_progress",
                                        },
                                        {
                                            "label": "Complete",
                                            "value": "complete",
                                        },
                                        {
                                            "label": "Hold",
                                            "value": "hold",
                                        },
                                        {
                                            "label": "Void",
                                            "value": "void",
                                        },
                                    ],
                                    value="",
                                ),
                            ],
                            md=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Product:"),
                                dcc.Dropdown(
                                    id="wo-product-filter",
                                    options=[],
                                    value=None,
                                ),
                            ],
                            md=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Date From:"),
                                dbc.Input(
                                    id="wo-date-from",
                                    type="date",
                                ),
                            ],
                            md=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Date To:"),
                                dbc.Input(
                                    id="wo-date-to",
                                    type="date",
                                ),
                            ],
                            md=3,
                        ),
                    ],
                    className="mb-3",
                ),
                # Work Orders Table (always in layout, visibility controlled by wrapper div)
                html.Div(
                    id="wo-list-table-wrapper",
                    children=[
                        dash_table.DataTable(
                            id="wo-list-table",
                            columns=[
                                {"name": "WO Number", "id": "code"},
                                {"name": "Product", "id": "product"},
                                {
                                    "name": "Planned Qty",
                                    "id": "planned_qty",
                                },
                                {"name": "UOM", "id": "uom"},
                                {"name": "Status", "id": "status"},
                                {
                                    "name": "Issued Date",
                                    "id": "released_at",
                                },
                                {
                                    "name": "Completed Date",
                                    "id": "completed_at",
                                },
                                {
                                    "name": "Actual Qty",
                                    "id": "actual_qty",
                                },
                                {
                                    "name": "Est. Cost",
                                    "id": "estimated_cost",
                                },
                                {
                                    "name": "Act Cost",
                                    "id": "actual_cost",
                                },
                                {
                                    "name": "QC Status",
                                    "id": "qc_status",
                                },
                                {
                                    "name": "Cost/Unit",
                                    "id": "unit_cost",
                                },
                            ],
                            data=[],
                            sort_action="native",
                            filter_action="native",
                            row_selectable="single",
                            page_action="native",
                            page_current=0,
                            page_size=20,
                        ),
                    ],
                    style={
                        "display": "none"
                    },  # Hidden by default, shown by tab callback
                ),
                html.Div(
                    id="wo-create-btn-wrapper",
                    children=[
                        dbc.Button(
                            "Create Work Order",
                            id="wo-create-btn",
                            color="primary",
                            className="mt-3 mb-3",
                        ),
                    ],
                    style={
                        "display": "none"
                    },  # Hidden by default, shown by tab callback
                ),
                # Tab content
                html.Div(
                    id="wo-main-tab-content",
                    children=[
                        # List view placeholder (table is above, always in layout)
                        html.Div("Work Orders List", id="wo-list-placeholder"),
                    ],
                ),
                # Create Work Order Modal
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Create Work Order")),
                        dbc.ModalBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Product *"),
                                                dcc.Dropdown(
                                                    id="wo-create-product-dropdown",
                                                    options=[],
                                                    placeholder="Select product",
                                                ),
                                            ],
                                            md=6,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Assembly (Recipe)"),
                                                dcc.Dropdown(
                                                    id="wo-create-assembly-dropdown",
                                                    options=[],
                                                    placeholder="Select assembly (optional, uses primary if not selected)",
                                                ),
                                            ],
                                            md=6,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Planned Quantity *"),
                                                dbc.Input(
                                                    id="wo-create-planned-qty",
                                                    type="number",
                                                    step=0.001,
                                                    placeholder="0.000",
                                                ),
                                            ],
                                            md=4,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Unit of Measure"),
                                                dcc.Dropdown(
                                                    id="wo-create-uom",
                                                    options=[],
                                                    value="KG",
                                                    placeholder="Select unit...",
                                                    searchable=True,
                                                ),
                                            ],
                                            md=4,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Work Center"),
                                                dcc.Dropdown(
                                                    id="wo-create-work-center",
                                                    options=[],
                                                    placeholder="Select work center...",
                                                    searchable=True,
                                                    clearable=True,
                                                ),
                                            ],
                                            md=4,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    [
                                                        "Batch Code (Preview)",
                                                        html.Small(
                                                            " Preview only - final code generated on save",
                                                            className="text-muted d-block",
                                                            style={
                                                                "fontSize": "0.875rem"
                                                            },
                                                        ),
                                                    ]
                                                ),
                                                dbc.Input(
                                                    id="wo-create-batch-code",
                                                    type="text",
                                                    placeholder="Auto-generated",
                                                    readonly=True,
                                                    style={
                                                        "backgroundColor": "#f8f9fa"
                                                    },
                                                ),
                                            ],
                                            md=6,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Notes"),
                                                dbc.Textarea(
                                                    id="wo-create-notes",
                                                    placeholder="Optional notes",
                                                ),
                                            ],
                                            md=6,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                # Assembly Details Table (shown when assembly is selected)
                                html.Div(
                                    id="wo-create-assembly-details",
                                    children=[],
                                    className="mb-3",
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Cancel",
                                    id="wo-create-cancel-btn",
                                    color="secondary",
                                    className="me-2",
                                ),
                                dbc.Button(
                                    "Create",
                                    id="wo-create-submit-btn",
                                    color="primary",
                                ),
                            ]
                        ),
                    ],
                    id="wo-create-modal",
                    is_open=False,
                    size="lg",
                ),
                # Detail view placeholder (always in layout for callbacks)
                html.Div(
                    id="wo-detail-content",
                    children=html.Div("Select a work order to view details"),
                    style={
                        "display": "none"
                    },  # Hidden by default, shown by tab callback
                ),
                html.Div(id="wo-detail-wo-id", style={"display": "none"}),
                # Toast notifications
                dbc.Toast(
                    id="wo-issue-toast",
                    header="Material Issue",
                    is_open=False,
                    dismissable=True,
                    duration=4000,
                    style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                ),
                dbc.Toast(
                    id="wo-qc-toast",
                    header="QC Test",
                    is_open=False,
                    dismissable=True,
                    duration=4000,
                    style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                ),
                dbc.Toast(
                    id="wo-complete-toast",
                    header="Work Order Complete",
                    is_open=False,
                    dismissable=True,
                    duration=4000,
                    style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                ),
                dbc.Toast(
                    id="wo-action-toast",
                    header="Action",
                    is_open=False,
                    dismissable=True,
                    duration=4000,
                    style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                ),
            ],
            fluid=True,
        )
