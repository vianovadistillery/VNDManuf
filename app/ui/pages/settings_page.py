"""Settings page with Units CRUD and runtime configuration overview."""

import os

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from app.services.openai_config import public_openai_config
from app.settings import settings

from .condition_types_page import ConditionTypesPage


def _info_list(items):
    """Render a simple list of label/value pairs."""
    return html.Ul(
        [
            html.Li(
                [
                    html.Strong(f"{label}:"),
                    html.Span(str(value), className="ms-2 text-monospace"),
                ]
            )
            for label, value in items
        ],
        className="list-unstyled mb-0",
    )


class SettingsPage:
    """Settings management page with Units CRUD and runtime configuration."""

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
                                        dbc.Tab(
                                            label="Runtime Config",
                                            tab_id="runtime-config",
                                        ),
                                        dbc.Tab(label="Units", tab_id="units"),
                                        dbc.Tab(
                                            label="Excise Rates", tab_id="excise-rates"
                                        ),
                                        dbc.Tab(
                                            label="Purchase Formats",
                                            tab_id="purchase-formats",
                                        ),
                                        dbc.Tab(label="QC Tests", tab_id="qc-tests"),
                                        dbc.Tab(
                                            label="Work Areas",
                                            tab_id="work-areas",
                                        ),
                                        dbc.Tab(
                                            label="Conditions",
                                            tab_id="conditions",
                                        ),
                                    ],
                                    className="mb-4",
                                ),
                            ]
                        )
                    ]
                ),
                # Runtime configuration tab
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.H4(
                                                                "Environment",
                                                                className="mb-3",
                                                            ),
                                                            _info_list(
                                                                [
                                                                    (
                                                                        "Environment",
                                                                        settings.environment,
                                                                    ),
                                                                    (
                                                                        "App Name",
                                                                        settings.app_name,
                                                                    ),
                                                                    (
                                                                        "Version",
                                                                        settings.app_version,
                                                                    ),
                                                                    (
                                                                        "Project Root",
                                                                        settings.project_root,
                                                                    ),
                                                                ]
                                                            ),
                                                        ]
                                                    ),
                                                    className="mb-3",
                                                ),
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.H4(
                                                                "Database",
                                                                className="mb-3",
                                                            ),
                                                            _info_list(
                                                                [
                                                                    (
                                                                        "URL",
                                                                        settings.database.database_url,
                                                                    ),
                                                                    (
                                                                        "Pool Size",
                                                                        settings.database.pool_size,
                                                                    ),
                                                                    (
                                                                        "Max Overflow",
                                                                        settings.database.max_overflow,
                                                                    ),
                                                                    (
                                                                        "Pool Timeout (s)",
                                                                        settings.database.pool_timeout,
                                                                    ),
                                                                ]
                                                            ),
                                                        ]
                                                    ),
                                                ),
                                            ],
                                            lg=6,
                                            className="mb-3",
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.H4(
                                                                "API Server",
                                                                className="mb-3",
                                                            ),
                                                            _info_list(
                                                                [
                                                                    (
                                                                        "Host",
                                                                        settings.api.host,
                                                                    ),
                                                                    (
                                                                        "Port",
                                                                        settings.api.port,
                                                                    ),
                                                                    (
                                                                        "Debug Mode",
                                                                        "Yes"
                                                                        if settings.api.debug
                                                                        else "No",
                                                                    ),
                                                                    (
                                                                        "CORS Origins",
                                                                        ", ".join(
                                                                            settings.api.cors_origins
                                                                        ),
                                                                    ),
                                                                    (
                                                                        "Rate Limit (per min)",
                                                                        settings.api.rate_limit_per_minute,
                                                                    ),
                                                                ]
                                                            ),
                                                        ]
                                                    ),
                                                    className="mb-3",
                                                ),
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.H4(
                                                                "UI / Dashboard",
                                                                className="mb-3",
                                                            ),
                                                            _info_list(
                                                                [
                                                                    (
                                                                        "Host",
                                                                        settings.ui.host,
                                                                    ),
                                                                    (
                                                                        "Port",
                                                                        settings.ui.port,
                                                                    ),
                                                                    (
                                                                        "Debug Mode",
                                                                        "Yes"
                                                                        if settings.ui.debug
                                                                        else "No",
                                                                    ),
                                                                    (
                                                                        "API Base URL",
                                                                        settings.ui.api_base_url,
                                                                    ),
                                                                    (
                                                                        "Demo Mode",
                                                                        "Enabled"
                                                                        if settings.ui.enable_demo_mode
                                                                        else "Disabled",
                                                                    ),
                                                                ]
                                                            ),
                                                        ]
                                                    ),
                                                ),
                                            ],
                                            lg=6,
                                            className="mb-3",
                                        ),
                                    ],
                                    className="g-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.H4(
                                                                "Integrations",
                                                                className="mb-3",
                                                            ),
                                                            dbc.Button(
                                                                "Open Competitor Intel →",
                                                                id="open-competitor-intel",
                                                                color="info",
                                                                href=os.getenv(
                                                                    "COMPINTEL_URL",
                                                                    "http://127.0.0.1:8060",
                                                                ),
                                                                external_link=True,
                                                                target="_blank",
                                                                title="Open Competitor Intel in a new tab",
                                                            )
                                                            if os.getenv(
                                                                "COMPINTEL_ENABLED",
                                                                "false",
                                                            ).lower()
                                                            == "true"
                                                            else html.P(
                                                                "Competitor Intel is disabled. Set COMPINTEL_ENABLED=true and COMPINTEL_URL to enable.",
                                                                className="text-muted mb-0",
                                                            ),
                                                        ]
                                                    ),
                                                    className="mb-3",
                                                ),
                                            ],
                                            lg=6,
                                            className="mb-3",
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.H4(
                                                                "Nova University (OpenAI)",
                                                                className="mb-3",
                                                            ),
                                                            _info_list(
                                                                [
                                                                    (
                                                                        "API Key",
                                                                        "Configured"
                                                                        if public_openai_config().get(
                                                                            "configured"
                                                                        )
                                                                        else "Not set",
                                                                    ),
                                                                    (
                                                                        "Model",
                                                                        public_openai_config().get(
                                                                            "model",
                                                                            "gpt-4o-mini",
                                                                        ),
                                                                    ),
                                                                    (
                                                                        "LLM Ask",
                                                                        "Enabled"
                                                                        if public_openai_config().get(
                                                                            "enabled",
                                                                            True,
                                                                        )
                                                                        else "Disabled",
                                                                    ),
                                                                    (
                                                                        "Config file",
                                                                        "config/openai.json",
                                                                    ),
                                                                ]
                                                            ),
                                                            html.P(
                                                                [
                                                                    "Set your key in ",
                                                                    html.Strong(
                                                                        "Nova University → AI Settings"
                                                                    ),
                                                                    ", or copy ",
                                                                    html.Code(
                                                                        "config/openai.json.example"
                                                                    ),
                                                                    " to ",
                                                                    html.Code(
                                                                        "config/openai.json"
                                                                    ),
                                                                    ". Same embedded pattern as VND-DAQ.",
                                                                ],
                                                                className="text-muted small mt-3 mb-0",
                                                            ),
                                                        ]
                                                    ),
                                                    className="mb-3",
                                                ),
                                            ],
                                            lg=6,
                                            className="mb-3",
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ],
                    id="runtime-config-tab-content",
                    style={"display": "none"},
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
                # QC Tests Tab
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
                                                            "Refresh",
                                                            id="qc-test-types-refresh",
                                                            color="info",
                                                        ),
                                                    ],
                                                    width=12,
                                                )
                                            ],
                                            className="mb-3",
                                        ),
                                        dash_table.DataTable(
                                            id="qc-test-types-table",
                                            columns=[
                                                {"name": "Code", "id": "code"},
                                                {"name": "Name", "id": "name"},
                                                {"name": "Unit", "id": "unit"},
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
                                            style_cell={
                                                "textAlign": "left",
                                                "whiteSpace": "normal",
                                                "height": "auto",
                                            },
                                            style_header={
                                                "backgroundColor": "rgb(230, 230, 230)",
                                                "fontWeight": "bold",
                                            },
                                        ),
                                    ],
                                    id="qc-test-types-list-content",
                                )
                            ]
                        )
                    ],
                    id="qc-tests-tab-content",
                ),
                # Work Areas Tab
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
                                                            "Add Work Area",
                                                            id="add-work-area-btn",
                                                            color="success",
                                                            className="me-2",
                                                        ),
                                                        dbc.Button(
                                                            "Edit Selected",
                                                            id="edit-work-area-btn",
                                                            color="primary",
                                                            className="me-2",
                                                            disabled=True,
                                                        ),
                                                        dbc.Button(
                                                            "Delete Selected",
                                                            id="delete-work-area-btn",
                                                            color="danger",
                                                            className="me-2",
                                                            disabled=True,
                                                        ),
                                                        dbc.Button(
                                                            "Refresh",
                                                            id="work-areas-refresh",
                                                            color="info",
                                                        ),
                                                    ],
                                                    width=12,
                                                )
                                            ],
                                            className="mb-3",
                                        ),
                                        dash_table.DataTable(
                                            id="work-areas-table",
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
                                    id="work-areas-list-content",
                                )
                            ]
                        )
                    ],
                    id="work-areas-tab-content",
                ),
                # Work Area Form Modal
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle(id="work-area-modal-title")),
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
                                                            id="work-area-code",
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
                                                            id="work-area-name",
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
                                                            id="work-area-description",
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
                                                            id="work-area-is-active",
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
                                    id="save-work-area-btn",
                                    color="primary",
                                ),
                                dbc.Button(
                                    "Cancel",
                                    id="cancel-work-area-btn",
                                    color="secondary",
                                ),
                            ]
                        ),
                    ],
                    id="work-area-form-modal",
                    is_open=False,
                    size="lg",
                ),
                # Hidden field for work area ID
                html.Div(id="work-area-form-hidden", style={"display": "none"}),
                # Conditions tab (Condition Types & Hazard Codes)
                dbc.Row(
                    [
                        dbc.Col(
                            [ConditionTypesPage.get_layout()],
                            width=12,
                        )
                    ],
                    id="conditions-tab-content",
                    style={"display": "none"},
                ),
            ],
            fluid=True,
        )
