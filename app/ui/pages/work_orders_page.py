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
                # Tab content
                html.Div(
                    id="wo-main-tab-content",
                    children=[
                        # List view
                        dbc.Card(
                            [
                                dbc.CardHeader("Work Orders"),
                                dbc.CardBody(
                                    [
                                        # Filters
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
                                        # Table
                                        dash_table.DataTable(
                                            id="wo-list-table",
                                            columns=[
                                                {"name": "Code", "id": "code"},
                                                {"name": "Product", "id": "product"},
                                                {
                                                    "name": "Planned Qty",
                                                    "id": "planned_qty",
                                                },
                                                {"name": "Status", "id": "status"},
                                                {
                                                    "name": "Batch Code",
                                                    "id": "batch_code",
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
                                        dbc.Button(
                                            "Create Work Order",
                                            id="wo-create-btn",
                                            color="primary",
                                            className="mt-3",
                                        ),
                                    ]
                                ),
                            ]
                        ),
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
                                                dbc.Input(
                                                    id="wo-create-uom",
                                                    type="text",
                                                    value="KG",
                                                    placeholder="KG",
                                                ),
                                            ],
                                            md=4,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Work Center"),
                                                dbc.Input(
                                                    id="wo-create-work-center",
                                                    type="text",
                                                    placeholder="e.g., Still01",
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
                                                dbc.Label("Notes"),
                                                dbc.Textarea(
                                                    id="wo-create-notes",
                                                    placeholder="Optional notes",
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
                # Detail view placeholder
                html.Div(
                    id="wo-detail-content",
                    children=html.Div("Select a work order to view details"),
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
