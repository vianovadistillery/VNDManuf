"""Formulas page for Dash UI with master-detail view."""

import dash_bootstrap_components as dbc
from dash import dash_table, html


class FormulasPage:
    """Formulas management page with master-detail view."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                # Header
                dbc.Row([dbc.Col([html.H2("Assemblies", className="mb-4")])]),
                # Filter Bar
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText("Search:"),
                                        dbc.Input(
                                            id="formula-search",
                                            placeholder="Code or description...",
                                            style={"width": "300px"},
                                        ),
                                        dbc.Button(
                                            "Search",
                                            id="formula-search-btn",
                                            color="primary",
                                            className="ms-2",
                                        ),
                                        dbc.Button(
                                            "Clear",
                                            id="formula-clear-btn",
                                            color="secondary",
                                            className="ms-1",
                                        ),
                                        dbc.Button(
                                            "Refresh",
                                            id="formula-refresh-btn",
                                            color="info",
                                            className="ms-2",
                                        ),
                                    ],
                                    size="sm",
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
                                            "New Formula",
                                            id="formula-add-btn",
                                            color="success",
                                        ),
                                        dbc.Button(
                                            "Edit Formula",
                                            id="formula-edit-btn",
                                            color="primary",
                                        ),
                                        dbc.Button(
                                            "New Revision",
                                            id="formula-revision-btn",
                                            color="info",
                                        ),
                                        dbc.Button(
                                            "Clone",
                                            id="formula-clone-btn",
                                            color="secondary",
                                        ),
                                        dbc.Button(
                                            "Print",
                                            id="formula-print-btn",
                                            color="warning",
                                        ),
                                    ]
                                )
                            ]
                        )
                    ],
                    className="mb-3",
                ),
                # Master-Detail Layout
                dbc.Row(
                    [
                        # Left: Formula List (Master)
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Formula List"),
                                        dbc.CardBody(
                                            [
                                                dash_table.DataTable(
                                                    id="formula-master-table",
                                                    columns=[
                                                        {
                                                            "name": "Code",
                                                            "id": "formula_code",
                                                        },
                                                        {
                                                            "name": "Name",
                                                            "id": "formula_name",
                                                            "presentation": "markdown",
                                                        },
                                                        {
                                                            "name": "Version",
                                                            "id": "version",
                                                        },
                                                        {
                                                            "name": "Product (SKU - Name)",
                                                            "id": "product_name",
                                                        },
                                                        {
                                                            "name": "Active",
                                                            "id": "is_active",
                                                        },
                                                    ],
                                                    data=[],
                                                    sort_action="native",
                                                    filter_action="native",
                                                    row_selectable="single",
                                                    selected_rows=[],
                                                    page_action="native",
                                                    page_current=0,
                                                    page_size=20,
                                                    style_cell={
                                                        "textAlign": "left",
                                                        "fontSize": "12px",
                                                    },
                                                    style_header={
                                                        "backgroundColor": "rgb(230, 230, 230)",
                                                        "fontWeight": "bold",
                                                    },
                                                    style_data_conditional=[
                                                        {
                                                            "if": {
                                                                "filter_query": "{is_active} = False"
                                                            },
                                                            "backgroundColor": "#fee",
                                                            "color": "black",
                                                        }
                                                    ],
                                                    markdown_options={"html": True},
                                                )
                                            ]
                                        ),
                                    ],
                                    style={"height": "600px"},
                                )
                            ],
                            md=4,
                        ),
                        # Right: Formula Details (Detail)
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.H5(
                                                    id="formula-detail-title",
                                                    children="Select a formula...",
                                                )
                                            ]
                                        ),
                                        dbc.CardBody(
                                            [
                                                # Formula Info
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Formula Code:"
                                                                ),
                                                                html.Div(
                                                                    id="formula-info-code",
                                                                    className="text-muted",
                                                                ),
                                                            ],
                                                            md=6,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Version:"),
                                                                html.Div(
                                                                    id="formula-info-version",
                                                                    className="text-muted",
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
                                                                dbc.Label("Product:"),
                                                                html.Div(
                                                                    id="formula-info-product",
                                                                    className="text-muted",
                                                                ),
                                                            ],
                                                            md=6,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Status:"),
                                                                html.Div(
                                                                    id="formula-info-status",
                                                                    className="text-muted",
                                                                ),
                                                            ],
                                                            md=6,
                                                        ),
                                                    ],
                                                    className="mb-3",
                                                ),
                                                html.Hr(),
                                                # Formula Lines Table
                                                html.H6("Ingredients:"),
                                                html.Div(
                                                    id="formula-lines-table-container",
                                                    children=[
                                                        dash_table.DataTable(
                                                            id="formula-lines-table",
                                                            columns=[
                                                                {
                                                                    "name": "SKU",
                                                                    "id": "product_sku",
                                                                },
                                                                {
                                                                    "name": "Product",
                                                                    "id": "product_name",
                                                                },
                                                                {
                                                                    "name": "Quantity",
                                                                    "id": "quantity",
                                                                    "type": "numeric",
                                                                    "format": {
                                                                        "specifier": ".3f"
                                                                    },
                                                                },
                                                                {
                                                                    "name": "Unit",
                                                                    "id": "unit",
                                                                },
                                                                {
                                                                    "name": "Qty (kg)",
                                                                    "id": "quantity_kg",
                                                                    "type": "numeric",
                                                                    "format": {
                                                                        "specifier": ".3f"
                                                                    },
                                                                },
                                                                {
                                                                    "name": "Unit Cost",
                                                                    "id": "unit_cost",
                                                                    "type": "numeric",
                                                                    "format": {
                                                                        "specifier": ".4f"
                                                                    },
                                                                },
                                                                {
                                                                    "name": "Line Cost",
                                                                    "id": "line_cost",
                                                                    "type": "numeric",
                                                                    "format": {
                                                                        "specifier": ".4f"
                                                                    },
                                                                },
                                                            ],
                                                            data=[],
                                                            sort_action="native",
                                                            style_cell={
                                                                "textAlign": "left",
                                                                "fontSize": "11px",
                                                                "padding": "4px",
                                                            },
                                                            style_header={
                                                                "backgroundColor": "rgb(230, 230, 230)",
                                                                "fontWeight": "bold",
                                                            },
                                                            style_table={
                                                                "overflowX": "auto"
                                                            },
                                                        ),
                                                        # Summary totals (same as product detail view)
                                                        html.Div(
                                                            id="formula-summary-totals",
                                                            style={
                                                                "fontSize": "12px",
                                                                "fontWeight": "bold",
                                                                "marginTop": "10px",
                                                            },
                                                        ),
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                    style={"height": "600px"},
                                )
                            ],
                            md=8,
                        ),
                    ]
                ),
                # Revision History Modal
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Revision History")),
                        dbc.ModalBody(
                            [
                                dash_table.DataTable(
                                    id="formula-revision-table",
                                    columns=[
                                        {"name": "Version", "id": "version"},
                                        {"name": "Created", "id": "created_at"},
                                        {"name": "Status", "id": "is_active"},
                                    ],
                                    data=[],
                                    row_selectable="single",
                                ),
                                html.Div(
                                    [
                                        dbc.Button(
                                            "View Version",
                                            id="formula-view-revision-btn",
                                            color="primary",
                                            className="mt-2",
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Close",
                                    id="formula-revision-close-btn",
                                    color="secondary",
                                )
                            ]
                        ),
                    ],
                    id="formula-revision-modal",
                    is_open=False,
                    size="lg",
                ),
                # Formula Editor Modal
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle(id="formula-editor-title")),
                        dbc.ModalBody(
                            [
                                dbc.Tabs(
                                    [
                                        # Header Tab
                                        dbc.Tab(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Version:"),
                                                                dbc.Input(
                                                                    id="formula-input-version",
                                                                    type="number",
                                                                    value=1,
                                                                    required=True,
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
                                                                dbc.Label(
                                                                    "Formula Name:"
                                                                ),
                                                                dbc.Input(
                                                                    id="formula-input-name",
                                                                    required=True,
                                                                ),
                                                            ],
                                                            md=12,
                                                        ),
                                                    ],
                                                    className="mt-2",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Product:"),
                                                                dbc.Select(
                                                                    id="formula-input-product",
                                                                    required=True,
                                                                ),
                                                            ],
                                                            md=12,
                                                        ),
                                                    ],
                                                    className="mt-2",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Yield Factor:"
                                                                ),
                                                                dbc.Input(
                                                                    id="formula-input-yield-factor",
                                                                    type="number",
                                                                    step="0.01",
                                                                    min="0.01",
                                                                    placeholder="1.00",
                                                                    value=1.0,
                                                                ),
                                                            ],
                                                            md=6,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Active:"),
                                                                dbc.Switch(
                                                                    id="formula-input-active",
                                                                    value=True,
                                                                ),
                                                            ],
                                                            md=6,
                                                        ),
                                                    ],
                                                    className="mt-2",
                                                ),
                                            ],
                                            label="Header",
                                            tab_id="header",
                                        ),
                                        # Lines Tab
                                        dbc.Tab(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Button(
                                                                    "Add Line",
                                                                    id="formula-add-line-btn",
                                                                    color="success",
                                                                    className="me-2",
                                                                ),
                                                                dbc.Button(
                                                                    "Edit Line",
                                                                    id="formula-edit-line-btn",
                                                                    color="primary",
                                                                    className="me-2",
                                                                ),
                                                                dbc.Button(
                                                                    "Delete Line",
                                                                    id="formula-delete-line-btn",
                                                                    color="danger",
                                                                ),
                                                            ]
                                                        )
                                                    ],
                                                    className="mb-3",
                                                ),
                                                # Ingredient Selection Modal
                                                dbc.Modal(
                                                    [
                                                        dbc.ModalHeader(
                                                            dbc.ModalTitle(
                                                                "Select Ingredient"
                                                            )
                                                        ),
                                                        dbc.ModalBody(
                                                            [
                                                                dbc.InputGroup(
                                                                    [
                                                                        dbc.InputGroupText(
                                                                            "🔍 Search:"
                                                                        ),
                                                                        dbc.Input(
                                                                            id="ingredient-search-input",
                                                                            placeholder="Search by code or description...",
                                                                            debounce=True,
                                                                        ),
                                                                    ],
                                                                    className="mb-3",
                                                                ),
                                                                dbc.Alert(
                                                                    id="ingredient-search-message",
                                                                    color="info",
                                                                    className="mb-2",
                                                                ),
                                                                html.Div(
                                                                    id="ingredient-search-results",
                                                                    style={
                                                                        "maxHeight": "400px",
                                                                        "overflowY": "auto",
                                                                    },
                                                                ),
                                                            ]
                                                        ),
                                                        dbc.ModalFooter(
                                                            [
                                                                dbc.Button(
                                                                    "Cancel",
                                                                    id="ingredient-modal-cancel",
                                                                    color="secondary",
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                    id="ingredient-selection-modal",
                                                    is_open=False,
                                                    size="xl",
                                                ),
                                                # Hidden store for selected ingredient
                                                html.Div(
                                                    id="selected-ingredient-store",
                                                    style={"display": "none"},
                                                ),
                                                html.Div(
                                                    id="current-line-index-store",
                                                    style={"display": "none"},
                                                ),
                                                dash_table.DataTable(
                                                    id="formula-editor-lines",
                                                    columns=[
                                                        {
                                                            "name": "Seq",
                                                            "id": "sequence",
                                                            "editable": False,
                                                        },
                                                        {
                                                            "name": "Ingredient",
                                                            "id": "ingredient_name",
                                                            "type": "text",
                                                        },
                                                        {
                                                            "name": "Quantity",
                                                            "id": "quantity",
                                                            "editable": True,
                                                            "type": "numeric",
                                                            "format": {
                                                                "specifier": ".3f"
                                                            },
                                                        },
                                                        {
                                                            "name": "Unit",
                                                            "id": "unit",
                                                            "editable": True,
                                                            "type": "text",
                                                        },
                                                        {
                                                            "name": "Notes",
                                                            "id": "notes",
                                                            "editable": True,
                                                        },
                                                    ],
                                                    data=[],
                                                    row_selectable="single",
                                                    editable=True,
                                                    tooltip_data=[],
                                                    style_cell={
                                                        "textAlign": "left",
                                                        "fontSize": "12px",
                                                        "padding": "10px",
                                                    },
                                                    style_header={
                                                        "backgroundColor": "rgb(240, 240, 240)",
                                                        "fontWeight": "bold",
                                                    },
                                                    style_data={
                                                        "whiteSpace": "normal",
                                                        "height": "auto",
                                                    },
                                                    style_data_conditional=[
                                                        {
                                                            "if": {
                                                                "column_id": "ingredient_name"
                                                            },
                                                            "cursor": "pointer",
                                                            "backgroundColor": "#f8f9fa",
                                                        },
                                                        {
                                                            "if": {
                                                                "filter_query": '{ingredient_name} = "[Click to select ingredient]"'
                                                            },
                                                            "color": "#007bff",
                                                            "textDecoration": "underline",
                                                            "fontStyle": "italic",
                                                        },
                                                    ],
                                                    dropdown={
                                                        "unit": {
                                                            "options": [
                                                                {
                                                                    "label": "kg",
                                                                    "value": "kg",
                                                                },
                                                                {
                                                                    "label": "g",
                                                                    "value": "g",
                                                                },
                                                                {
                                                                    "label": "L",
                                                                    "value": "L",
                                                                },
                                                                {
                                                                    "label": "mL",
                                                                    "value": "mL",
                                                                },
                                                                {
                                                                    "label": "oz",
                                                                    "value": "oz",
                                                                },
                                                                {
                                                                    "label": "lb",
                                                                    "value": "lb",
                                                                },
                                                            ]
                                                        }
                                                    },
                                                ),
                                                dbc.Alert(
                                                    [
                                                        html.Strong("Instructions:"),
                                                        html.Ul(
                                                            [
                                                                html.Li(
                                                                    "Click on an ingredient cell to select a raw material"
                                                                ),
                                                                html.Li(
                                                                    "Edit quantity and unit (kg, g, L, mL, oz, lb) directly in the table"
                                                                ),
                                                                html.Li(
                                                                    "Click 'Edit Line' to change the ingredient selection"
                                                                ),
                                                            ],
                                                            className="mb-0",
                                                        ),
                                                    ],
                                                    color="info",
                                                    className="mt-2",
                                                ),
                                            ],
                                            label="Lines",
                                            tab_id="lines",
                                        ),
                                    ],
                                    id="formula-editor-tabs",
                                )
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Cancel",
                                    id="formula-editor-cancel-btn",
                                    color="secondary",
                                    className="me-2",
                                ),
                                dbc.Button(
                                    "Save",
                                    id="formula-editor-save-btn",
                                    color="primary",
                                ),
                            ]
                        ),
                    ],
                    id="formula-editor-modal",
                    is_open=False,
                    size="xl",
                ),
            ],
            fluid=True,
        )
