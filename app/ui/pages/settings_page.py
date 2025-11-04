"""Settings page with Units CRUD."""

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


class SettingsPage:
    """Settings management page with Units CRUD."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3("Settings", className="mb-4"),
                                dbc.Tabs(
                                    id="settings-tabs",
                                    active_tab="units",
                                    children=[
                                        dbc.Tab(label="Units", tab_id="units"),
                                        dbc.Tab(
                                            label="Excise Rates", tab_id="excise-rates"
                                        ),
                                        dbc.Tab(
                                            label="Purchase Formats",
                                            tab_id="purchase-formats",
                                        ),
                                    ],
                                    className="mb-4",
                                ),
                            ]
                        )
                    ]
                ),
                # Units Tab
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Add Unit",
                                                            id="add-unit-btn",
                                                            color="success",
                                                            className="me-2",
                                                        ),
                                                        dbc.Button(
                                                            "Edit Selected",
                                                            id="edit-unit-btn",
                                                            color="primary",
                                                            className="me-2",
                                                            disabled=True,
                                                        ),
                                                        dbc.Button(
                                                            "Delete Selected",
                                                            id="delete-unit-btn",
                                                            color="danger",
                                                            className="me-2",
                                                            disabled=True,
                                                        ),
                                                        dbc.Button(
                                                            "Refresh",
                                                            id="units-refresh",
                                                            color="info",
                                                        ),
                                                    ],
                                                    width=12,
                                                )
                                            ],
                                            className="mb-3",
                                        ),
                                        dash_table.DataTable(
                                            id="units-table",
                                            columns=[
                                                {"name": "Code", "id": "code"},
                                                {"name": "Name", "id": "name"},
                                                {"name": "Symbol", "id": "symbol"},
                                                {"name": "Type", "id": "unit_type"},
                                                {
                                                    "name": "Conversion Formula",
                                                    "id": "conversion_formula",
                                                    "presentation": "markdown",
                                                },
                                                {"name": "Active", "id": "is_active"},
                                            ],
                                            data=[],
                                            sort_action="native",
                                            filter_action="native",
                                            page_action="native",
                                            page_current=0,
                                            page_size=20,
                                            row_selectable="single",
                                            style_cell={
                                                "textAlign": "left",
                                                "whiteSpace": "pre-wrap",
                                                "fontSize": "12px",
                                            },
                                            style_data={
                                                "whiteSpace": "normal",
                                                "height": "auto",
                                            },
                                            style_cell_conditional=[
                                                {
                                                    "if": {
                                                        "column_id": "conversion_formula"
                                                    },
                                                    "width": "30%",
                                                    "textAlign": "left",
                                                },
                                            ],
                                            style_header={
                                                "backgroundColor": "rgb(230, 230, 230)",
                                                "fontWeight": "bold",
                                            },
                                        ),
                                    ],
                                    id="units-list-content",
                                )
                            ]
                        )
                    ],
                    id="units-tab-content",
                ),
                # Unit Form Modal
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle(id="unit-modal-title")),
                        dbc.ModalBody(
                            [
                                dbc.Form(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Code *"),
                                                        dbc.Input(
                                                            id="unit-code",
                                                            required=True,
                                                            maxLength=20,
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Name *"),
                                                        dbc.Input(
                                                            id="unit-name",
                                                            required=True,
                                                            maxLength=100,
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Symbol"),
                                                        dbc.Input(
                                                            id="unit-symbol",
                                                            maxLength=10,
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Type"),
                                                        dbc.Select(
                                                            id="unit-type",
                                                            options=[
                                                                {
                                                                    "label": "MASS",
                                                                    "value": "MASS",
                                                                },
                                                                {
                                                                    "label": "VOLUME",
                                                                    "value": "VOLUME",
                                                                },
                                                                {
                                                                    "label": "DENSITY",
                                                                    "value": "DENSITY",
                                                                },
                                                                {
                                                                    "label": "CONCENTRATION",
                                                                    "value": "CONCENTRATION",
                                                                },
                                                                {
                                                                    "label": "COUNT",
                                                                    "value": "COUNT",
                                                                },
                                                                {
                                                                    "label": "LENGTH",
                                                                    "value": "LENGTH",
                                                                },
                                                                {
                                                                    "label": "AREA",
                                                                    "value": "AREA",
                                                                },
                                                                {
                                                                    "label": "OTHER",
                                                                    "value": "OTHER",
                                                                },
                                                            ],
                                                            placeholder="Select unit type",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Description"),
                                                        dbc.Textarea(
                                                            id="unit-description",
                                                            rows=3,
                                                        ),
                                                    ],
                                                    width=12,
                                                )
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Conversion Formula"),
                                                        dbc.Textarea(
                                                            id="unit-conversion-formula",
                                                            rows=2,
                                                            placeholder="e.g., kg * 1000 = g",
                                                        ),
                                                        dbc.FormText(
                                                            "Optional: Mathematical formula for converting to/from this unit"
                                                        ),
                                                    ],
                                                    width=12,
                                                )
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Active"),
                                                        dbc.Switch(
                                                            id="unit-is-active",
                                                            value=True,
                                                        ),
                                                    ],
                                                    width=12,
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button("Save", id="save-unit-btn", color="primary"),
                                dbc.Button(
                                    "Cancel", id="cancel-unit-btn", color="secondary"
                                ),
                            ]
                        ),
                    ],
                    id="unit-form-modal",
                    is_open=False,
                    size="lg",
                ),
                # Hidden field for unit ID
                html.Div(id="unit-form-hidden", style={"display": "none"}),
                # Excise Rates Tab
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Add Excise Rate",
                                                            id="add-excise-rate-btn",
                                                            color="success",
                                                            className="me-2",
                                                        ),
                                                        dbc.Button(
                                                            "Edit Selected",
                                                            id="edit-excise-rate-btn",
                                                            color="primary",
                                                            className="me-2",
                                                            disabled=True,
                                                        ),
                                                        dbc.Button(
                                                            "Delete Selected",
                                                            id="delete-excise-rate-btn",
                                                            color="danger",
                                                            className="me-2",
                                                            disabled=True,
                                                        ),
                                                        dbc.Button(
                                                            "Refresh",
                                                            id="excise-rates-refresh",
                                                            color="info",
                                                        ),
                                                    ],
                                                    width=12,
                                                )
                                            ],
                                            className="mb-3",
                                        ),
                                        dash_table.DataTable(
                                            id="excise-rates-table",
                                            columns=[
                                                {
                                                    "name": "Date Active From",
                                                    "id": "date_active_from",
                                                },
                                                {
                                                    "name": "Rate ($/L ABV)",
                                                    "id": "rate_per_l_abv",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".2f"},
                                                },
                                                {
                                                    "name": "Effective Period",
                                                    "id": "effective_period",
                                                },
                                                {
                                                    "name": "Comment",
                                                    "id": "description",
                                                },
                                                {"name": "Active", "id": "is_active"},
                                                {"name": "Created", "id": "created_at"},
                                            ],
                                            data=[],
                                            sort_action="native",
                                            filter_action="native",
                                            page_action="native",
                                            page_current=0,
                                            page_size=20,
                                            row_selectable="single",
                                            selected_rows=[],
                                            style_cell={"textAlign": "left"},
                                            style_header={
                                                "backgroundColor": "rgb(230, 230, 230)",
                                                "fontWeight": "bold",
                                            },
                                        ),
                                    ],
                                    id="excise-rates-list-content",
                                )
                            ]
                        )
                    ],
                    id="excise-rates-tab-content",
                ),
                # Excise Rate Form Modal
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle(id="excise-rate-modal-title")),
                        dbc.ModalBody(
                            [
                                dbc.Form(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Date Active From *"),
                                                        dcc.DatePickerSingle(
                                                            id="excise-rate-date",
                                                            display_format="YYYY-MM-DD",
                                                            style={"width": "100%"},
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Rate ($/L ABV) *"),
                                                        dbc.Input(
                                                            id="excise-rate-rate",
                                                            type="number",
                                                            step="0.01",
                                                            required=True,
                                                            min=0,
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Comment"),
                                                        dbc.Textarea(
                                                            id="excise-rate-description",
                                                            rows=3,
                                                            placeholder="Optional comment about this excise rate entry",
                                                        ),
                                                    ],
                                                    width=12,
                                                )
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Active"),
                                                        dbc.Switch(
                                                            id="excise-rate-is-active",
                                                            value=True,
                                                        ),
                                                    ],
                                                    width=12,
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Save", id="save-excise-rate-btn", color="primary"
                                ),
                                dbc.Button(
                                    "Cancel",
                                    id="cancel-excise-rate-btn",
                                    color="secondary",
                                ),
                            ]
                        ),
                    ],
                    id="excise-rate-form-modal",
                    is_open=False,
                    size="lg",
                ),
                # Hidden field for excise rate ID
                html.Div(id="excise-rate-form-hidden", style={"display": "none"}),
                # Purchase Formats Tab
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Add Purchase Format",
                                                            id="add-purchase-format-btn",
                                                            color="success",
                                                            className="me-2",
                                                        ),
                                                        dbc.Button(
                                                            "Edit Selected",
                                                            id="edit-purchase-format-btn",
                                                            color="primary",
                                                            className="me-2",
                                                            disabled=True,
                                                        ),
                                                        dbc.Button(
                                                            "Delete Selected",
                                                            id="delete-purchase-format-btn",
                                                            color="danger",
                                                            className="me-2",
                                                            disabled=True,
                                                        ),
                                                        dbc.Button(
                                                            "Refresh",
                                                            id="purchase-formats-refresh",
                                                            color="info",
                                                        ),
                                                    ],
                                                    width=12,
                                                )
                                            ],
                                            className="mb-3",
                                        ),
                                        dash_table.DataTable(
                                            id="purchase-formats-table",
                                            columns=[
                                                {"name": "Code", "id": "code"},
                                                {"name": "Name", "id": "name"},
                                                {
                                                    "name": "Description",
                                                    "id": "description",
                                                },
                                                {"name": "Active", "id": "is_active"},
                                            ],
                                            data=[],
                                            sort_action="native",
                                            filter_action="native",
                                            page_action="native",
                                            page_current=0,
                                            page_size=20,
                                            row_selectable="single",
                                            style_cell={"textAlign": "left"},
                                            style_header={
                                                "backgroundColor": "rgb(230, 230, 230)",
                                                "fontWeight": "bold",
                                            },
                                        ),
                                    ],
                                    id="purchase-formats-list-content",
                                )
                            ]
                        )
                    ],
                    id="purchase-formats-tab-content",
                ),
                # Purchase Format Form Modal
                dbc.Modal(
                    [
                        dbc.ModalHeader(
                            dbc.ModalTitle(id="purchase-format-modal-title")
                        ),
                        dbc.ModalBody(
                            [
                                dbc.Form(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Code *"),
                                                        dbc.Input(
                                                            id="purchase-format-code",
                                                            required=True,
                                                            maxLength=20,
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Name *"),
                                                        dbc.Input(
                                                            id="purchase-format-name",
                                                            required=True,
                                                            maxLength=100,
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Description"),
                                                        dbc.Textarea(
                                                            id="purchase-format-description",
                                                            rows=3,
                                                        ),
                                                    ],
                                                    width=12,
                                                )
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Active"),
                                                        dbc.Switch(
                                                            id="purchase-format-is-active",
                                                            value=True,
                                                        ),
                                                    ],
                                                    width=12,
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Save",
                                    id="save-purchase-format-btn",
                                    color="primary",
                                ),
                                dbc.Button(
                                    "Cancel",
                                    id="cancel-purchase-format-btn",
                                    color="secondary",
                                ),
                            ]
                        ),
                    ],
                    id="purchase-format-form-modal",
                    is_open=False,
                    size="lg",
                ),
                # Hidden field for purchase format ID
                html.Div(id="purchase-format-form-hidden", style={"display": "none"}),
            ],
            fluid=True,
        )
