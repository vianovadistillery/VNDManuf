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
                    children=[
                        html.Div("Select a work order to view details"),
                        dbc.Button(
                            id="wo-issue-submit-btn",
                            style={"display": "none"},
                        ),
                        html.Div(
                            [
                                dash_table.DataTable(
                                    id="wo-qc-table",
                                    columns=[],
                                    data=[],
                                ),
                                dbc.Button(
                                    id="wo-qc-edit-btn",
                                    style={"display": "none"},
                                ),
                                dbc.Button(
                                    id="wo-qc-delete-btn",
                                    style={"display": "none"},
                                ),
                                dbc.Button(
                                    id="wo-inputs-add-btn",
                                    style={"display": "none"},
                                ),
                                dcc.Dropdown(id="wo-qc-test-type", options=[]),
                                html.Div(id="wo-qc-unit-display"),
                                dbc.Input(id="wo-qc-result-value"),
                                dbc.Input(id="wo-qc-result-text"),
                                dcc.Dropdown(
                                    id="wo-qc-status",
                                    options=[
                                        {"label": "Pending", "value": "pending"},
                                        {"label": "Pass", "value": "pass"},
                                        {"label": "Fail", "value": "fail"},
                                    ],
                                ),
                                dbc.Input(id="wo-qc-tester"),
                                dbc.Input(id="wo-qc-note"),
                                dbc.Button(
                                    id="wo-qc-submit-btn",
                                    style={"display": "none"},
                                ),
                                dbc.Button(
                                    id="wo-start-btn",
                                    style={"display": "none"},
                                ),
                                dbc.Button(
                                    id="wo-reopen-btn",
                                    style={"display": "none"},
                                ),
                                dbc.Button(
                                    id="wo-release-btn",
                                    style={"display": "none"},
                                ),
                                dbc.Button(
                                    id="wo-void-btn",
                                    style={"display": "none"},
                                ),
                                dbc.Input(id="wo-complete-qty"),
                                dbc.Button(
                                    id="wo-complete-submit-btn",
                                    style={"display": "none"},
                                ),
                            ],
                            style={"display": "none"},
                        ),
                    ],
                    style={
                        "display": "none"
                    },  # Hidden by default, shown by tab callback
                ),
                dcc.Store(id="wo-detail-wo-id"),
                dcc.Store(id="wo-detail-active-tab", data="wo-detail-inputs"),
                dcc.Store(id="wo-qc-type-options", data=[]),
                dcc.Store(id="wo-qc-current-id"),
                dcc.Store(id="wo-detail-refresh-trigger"),
                dcc.Store(id="wo-planned-qty-refresh"),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Add Input Line")),
                        dbc.ModalBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Component *"),
                                                dcc.Dropdown(
                                                    id="wo-add-input-component-dropdown",
                                                    options=[],
                                                    placeholder="Select component",
                                                    searchable=True,
                                                ),
                                            ],
                                            md=7,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Planned Qty"),
                                                dbc.Input(
                                                    id="wo-add-input-planned-qty",
                                                    type="number",
                                                    step=0.001,
                                                    min=0,
                                                ),
                                            ],
                                            md=3,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("UOM"),
                                                dbc.Input(
                                                    id="wo-add-input-uom",
                                                    type="text",
                                                    placeholder="KG",
                                                ),
                                            ],
                                            md=2,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Note"),
                                                dbc.Textarea(
                                                    id="wo-add-input-note",
                                                    placeholder="Optional note",
                                                ),
                                            ]
                                        )
                                    ],
                                    className="mb-3",
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Cancel",
                                    id="wo-add-input-cancel-btn",
                                    color="secondary",
                                    className="me-2",
                                ),
                                dbc.Button(
                                    "Add Line",
                                    id="wo-add-input-submit-btn",
                                    color="primary",
                                ),
                            ]
                        ),
                    ],
                    id="wo-add-input-modal",
                    is_open=False,
                    size="lg",
                ),
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
