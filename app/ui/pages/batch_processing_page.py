"""Batch Processing page for Dash UI."""

import dash_bootstrap_components as dbc
from dash import dash_table, html


class BatchProcessingPage:
    """Batch Processing page with Plan/Execute/QC/History tabs."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                # Header
                dbc.Row([dbc.Col([html.H2("Batch Processing", className="mb-4")])]),
                # Tabs for workflow stages
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Tabs(
                                    id="batch-process-tabs",
                                    active_tab="plan",
                                    children=[
                                        dbc.Tab(label="Plan", tab_id="plan"),
                                        dbc.Tab(label="Execute", tab_id="execute"),
                                        dbc.Tab(label="QC Testing", tab_id="qc"),
                                        dbc.Tab(label="History", tab_id="history"),
                                    ],
                                    className="mb-3",
                                )
                            ]
                        )
                    ]
                ),
                # Tab content (Plan)
                html.Div(
                    id="batch-plan-content",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardHeader("Create New Batch"),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Formula:"),
                                                        dbc.Select(
                                                            id="batch-formula-select",
                                                            options=[],
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Revision:"),
                                                        dbc.Input(
                                                            id="batch-formula-revision",
                                                            type="number",
                                                            value=1,
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Target Yield (kg):"),
                                                        dbc.Input(
                                                            id="batch-target-kg",
                                                            type="number",
                                                            step=0.001,
                                                            required=True,
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Target Yield (litres):"
                                                        ),
                                                        dbc.Input(
                                                            id="batch-target-litres",
                                                            type="number",
                                                            step=0.001,
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                            ],
                                            className="mt-2",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Operator:"),
                                                        dbc.Input(
                                                            id="batch-operator",
                                                            maxLength=3,
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Notes:"),
                                                        dbc.Textarea(
                                                            id="batch-notes-plan",
                                                            rows=3,
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                            ],
                                            className="mt-2",
                                        ),
                                        dbc.Button(
                                            "Create Batch",
                                            id="batch-create-btn",
                                            color="success",
                                            className="mt-3",
                                        ),
                                    ]
                                ),
                            ],
                            className="mt-3",
                        ),
                        # Formula Lines Preview
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Formula Ingredients (material reservation)"
                                ),
                                dbc.CardBody(
                                    [
                                        dash_table.DataTable(
                                            id="batch-formula-lines",
                                            columns=[
                                                {"name": "Seq", "id": "sequence"},
                                                {
                                                    "name": "Material",
                                                    "id": "ingredient_name",
                                                },
                                                {
                                                    "name": "Qty (kg)",
                                                    "id": "quantity_kg",
                                                    "type": "numeric",
                                                },
                                                {
                                                    "name": "Available SOH",
                                                    "id": "available_soh",
                                                    "type": "numeric",
                                                },
                                            ],
                                            data=[],
                                            editable=False,
                                            style_cell={"fontSize": "11px"},
                                        )
                                    ]
                                ),
                            ],
                            className="mt-3",
                        ),
                    ],
                ),
                # Tab content (Execute) - hidden by default
                html.Div(
                    id="batch-execute-content",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardHeader("Record Actual Production"),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.H5(
                                                            id="batch-execute-batch-code",
                                                            children="No batch selected",
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Actual Yield (kg):"),
                                                        dbc.Input(
                                                            id="batch-actual-kg",
                                                            type="number",
                                                            step=0.001,
                                                        ),
                                                    ],
                                                    md=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Actual Yield (litres):"
                                                        ),
                                                        dbc.Input(
                                                            id="batch-actual-litres",
                                                            type="number",
                                                            step=0.001,
                                                        ),
                                                    ],
                                                    md=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Variance %:"),
                                                        dbc.Input(
                                                            id="batch-variance",
                                                            type="number",
                                                            step=0.01,
                                                            disabled=True,
                                                        ),
                                                    ],
                                                    md=4,
                                                ),
                                            ],
                                            className="mt-2",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Production Notes:"),
                                                        dbc.Textarea(
                                                            id="batch-notes-execute",
                                                            rows=3,
                                                        ),
                                                    ],
                                                    md=12,
                                                ),
                                            ],
                                            className="mt-2",
                                        ),
                                        dbc.Button(
                                            "Record Actuals",
                                            id="batch-record-actual-btn",
                                            color="primary",
                                            className="mt-2",
                                        ),
                                    ]
                                ),
                            ],
                            className="mt-3",
                        )
                    ],
                    style={"display": "none"},
                ),
                # Tab content (QC) - hidden by default
                html.Div(
                    id="batch-qc-content",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardHeader("Quality Control Test Results"),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Batch Code:"),
                                                        html.Div(
                                                            id="batch-qc-batch-code",
                                                            className="text-muted",
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("SG:"),
                                                        dbc.Input(
                                                            id="batch-qc-sg",
                                                            type="number",
                                                            step=0.0001,
                                                        ),
                                                    ],
                                                    md=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Viscosity:"),
                                                        dbc.Input(
                                                            id="batch-qc-visc",
                                                            type="number",
                                                            step=0.1,
                                                        ),
                                                    ],
                                                    md=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("pH:"),
                                                        dbc.Input(
                                                            id="batch-qc-ph",
                                                            type="number",
                                                            step=0.01,
                                                        ),
                                                    ],
                                                    md=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Filter Flag:"),
                                                        dbc.Select(
                                                            id="batch-qc-filter",
                                                            options=[
                                                                {
                                                                    "label": "Yes",
                                                                    "value": "Y",
                                                                },
                                                                {
                                                                    "label": "No",
                                                                    "value": "N",
                                                                },
                                                            ],
                                                        ),
                                                    ],
                                                    md=3,
                                                ),
                                            ],
                                            className="mt-2",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Grind:"),
                                                        dbc.Input(
                                                            id="batch-qc-grind",
                                                            type="number",
                                                            step=0.1,
                                                        ),
                                                    ],
                                                    md=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Vol Solid (vsol):"),
                                                        dbc.Input(
                                                            id="batch-qc-vsol",
                                                            type="number",
                                                            step=0.1,
                                                        ),
                                                    ],
                                                    md=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Wt Solid (wsol):"),
                                                        dbc.Input(
                                                            id="batch-qc-wsol",
                                                            type="number",
                                                            step=0.1,
                                                        ),
                                                    ],
                                                    md=4,
                                                ),
                                            ],
                                            className="mt-2",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Drying Times:"),
                                                        dbc.Input(
                                                            id="batch-qc-dry-dust",
                                                            placeholder="Dust Free (hrs)",
                                                            type="number",
                                                            step=0.1,
                                                        ),
                                                    ],
                                                    md=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Input(
                                                            id="batch-qc-dry-tack",
                                                            placeholder="Tack Free (hrs)",
                                                            type="number",
                                                            step=0.1,
                                                        ),
                                                    ],
                                                    md=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Input(
                                                            id="batch-qc-dry-hard",
                                                            placeholder="Hard Dry (hrs)",
                                                            type="number",
                                                            step=0.1,
                                                        ),
                                                    ],
                                                    md=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Input(
                                                            id="batch-qc-dry-bake",
                                                            placeholder="Bake (hrs)",
                                                            type="number",
                                                            step=0.1,
                                                        ),
                                                    ],
                                                    md=3,
                                                ),
                                            ],
                                            className="mt-2",
                                        ),
                                        dbc.Button(
                                            "Record QC Results",
                                            id="batch-record-qc-btn",
                                            color="primary",
                                            className="mt-2",
                                        ),
                                    ]
                                ),
                            ],
                            className="mt-3",
                        )
                    ],
                    style={"display": "none"},
                ),
                # Tab content (History) - hidden by default
                html.Div(
                    id="batch-history-content",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardHeader("Batch History"),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Filter by Year:"),
                                                        dbc.Input(
                                                            id="batch-history-year",
                                                            placeholder="YY",
                                                            maxLength=2,
                                                        ),
                                                    ],
                                                    md=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Status:"),
                                                        dbc.Select(
                                                            id="batch-history-status",
                                                            options=[
                                                                {
                                                                    "label": "All",
                                                                    "value": "all",
                                                                },
                                                                {
                                                                    "label": "DRAFT",
                                                                    "value": "DRAFT",
                                                                },
                                                                {
                                                                    "label": "EXECUTED",
                                                                    "value": "EXECUTED",
                                                                },
                                                                {
                                                                    "label": "QC_COMPLETE",
                                                                    "value": "QC_COMPLETE",
                                                                },
                                                                {
                                                                    "label": "COMPLETED",
                                                                    "value": "COMPLETED",
                                                                },
                                                            ],
                                                            value="all",
                                                        ),
                                                    ],
                                                    md=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Refresh",
                                                            id="batch-history-refresh",
                                                            color="primary",
                                                        ),
                                                    ],
                                                    md=4,
                                                ),
                                            ]
                                        ),
                                        dash_table.DataTable(
                                            id="batch-history-table",
                                            columns=[
                                                {
                                                    "name": "Batch Code",
                                                    "id": "batch_code",
                                                },
                                                {
                                                    "name": "Formula",
                                                    "id": "formula_code",
                                                },
                                                {
                                                    "name": "Target (kg)",
                                                    "id": "quantity_kg",
                                                    "type": "numeric",
                                                },
                                                {
                                                    "name": "Actual (kg)",
                                                    "id": "yield_actual",
                                                    "type": "numeric",
                                                },
                                                {
                                                    "name": "Variance %",
                                                    "id": "variance_percent",
                                                    "type": "numeric",
                                                },
                                                {"name": "Status", "id": "status"},
                                                {"name": "Started", "id": "started_at"},
                                            ],
                                            data=[],
                                            sort_action="native",
                                            row_selectable="single",
                                            page_action="native",
                                            page_size=25,
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
