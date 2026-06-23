"""Sales Settings sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


def layout():
    defaults_card = dbc.Card(
        [
            dbc.CardHeader(html.H6("Defaults", className="mb-0")),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.FormFloating(
                                    [
                                        dbc.Input(
                                            id="sales-settings-gst-rate",
                                            type="number",
                                            min=0,
                                            max=100,
                                            step=0.01,
                                            value=10.0,
                                        ),
                                        html.Label("Default GST rate (%)"),
                                    ]
                                ),
                                md=4,
                            ),
                            dbc.Col(
                                dbc.FormFloating(
                                    [
                                        dbc.Select(
                                            id="sales-settings-default-pricebook",
                                            options=[],
                                        ),
                                        html.Label("Default Pricebook"),
                                    ]
                                ),
                                md=4,
                            ),
                            dbc.Col(
                                dbc.FormFloating(
                                    [
                                        dbc.Select(
                                            id="sales-settings-default-currency",
                                            options=[
                                                {"label": "AUD", "value": "AUD"},
                                                {"label": "NZD", "value": "NZD"},
                                                {"label": "USD", "value": "USD"},
                                            ],
                                            value="AUD",
                                        ),
                                        html.Label("Currency"),
                                    ]
                                ),
                                md=4,
                            ),
                        ],
                        className="g-3",
                    )
                ]
            ),
        ],
        className="mb-4 shadow-sm",
    )

    feature_flags = dbc.Card(
        [
            dbc.CardHeader(html.H6("Feature Flags", className="mb-0")),
            dbc.CardBody(
                dbc.Checklist(
                    options=[
                        {"label": "Enable API imports", "value": "api"},
                        {"label": "Enable Xero sync preparation", "value": "xero"},
                        {
                            "label": "Require approval for discounts",
                            "value": "discount-approval",
                        },
                    ],
                    value=["api"],
                    id="sales-settings-feature-flags",
                    switch=True,
                )
            ),
        ],
        className="mb-4 shadow-sm",
    )

    reps_card = dbc.Card(
        [
            dbc.CardHeader(
                dbc.Row(
                    [
                        dbc.Col(html.H6("Sales reps", className="mb-0"), width="auto"),
                        dbc.Col(
                            dbc.Button(
                                "Refresh",
                                id="sales-reps-refresh",
                                size="sm",
                                color="secondary",
                                outline=True,
                            ),
                            className="text-end",
                        ),
                    ],
                    className="align-items-center",
                )
            ),
            dbc.CardBody(
                [
                    dash_table.DataTable(
                        id="sales-reps-table",
                        columns=[
                            {"name": "Code", "id": "code"},
                            {"name": "Name", "id": "name"},
                            {"name": "Email", "id": "email"},
                            {"name": "Phone", "id": "phone"},
                            {"name": "Active", "id": "is_active"},
                        ],
                        data=[],
                        hidden_columns=["id"],
                        page_size=8,
                        row_selectable="single",
                        style_table={"overflowX": "auto"},
                        style_cell={"padding": "0.5rem"},
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                        },
                    ),
                    html.Hr(),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    "Edit selected",
                                    id="sales-rep-edit-btn",
                                    color="secondary",
                                    disabled=True,
                                ),
                                md=2,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Delete selected",
                                    id="sales-rep-delete-btn",
                                    color="danger",
                                    outline=True,
                                    disabled=True,
                                ),
                                md=2,
                            ),
                        ],
                        className="g-2 mb-3",
                    ),
                    html.H6("Add rep", className="text-muted"),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(id="sales-rep-code", placeholder="Code"),
                                md=2,
                            ),
                            dbc.Col(
                                dbc.Input(id="sales-rep-name", placeholder="Name *"),
                                md=3,
                            ),
                            dbc.Col(
                                dbc.Input(id="sales-rep-email", placeholder="Email"),
                                md=3,
                            ),
                            dbc.Col(
                                dbc.Input(id="sales-rep-phone", placeholder="Phone"),
                                md=2,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Add rep", id="sales-rep-add", color="primary"
                                ),
                                md=2,
                            ),
                        ],
                        className="g-2",
                    ),
                    html.Div(id="sales-rep-feedback", className="small mt-2"),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
    )

    groups_card = dbc.Card(
        [
            dbc.CardHeader(html.H6("Buying groups", className="mb-0")),
            dbc.CardBody(
                [
                    dash_table.DataTable(
                        id="sales-buying-groups-table",
                        columns=[
                            {"name": "Code", "id": "code"},
                            {"name": "Name", "id": "name"},
                            {"name": "Colour", "id": "map_color"},
                            {"name": "Description", "id": "description"},
                            {"name": "Active", "id": "is_active"},
                        ],
                        data=[],
                        hidden_columns=["id"],
                        page_size=8,
                        row_selectable="single",
                        style_table={"overflowX": "auto"},
                        style_cell={"padding": "0.5rem"},
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                        },
                    ),
                    html.Hr(),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    "Edit selected",
                                    id="sales-buying-group-edit-btn",
                                    color="secondary",
                                    disabled=True,
                                ),
                                md=2,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Delete selected",
                                    id="sales-buying-group-delete-btn",
                                    color="danger",
                                    outline=True,
                                    disabled=True,
                                ),
                                md=2,
                            ),
                        ],
                        className="g-2 mb-3",
                    ),
                    html.H6("Add buying group", className="text-muted"),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(
                                    id="sales-buying-group-code", placeholder="Code"
                                ),
                                md=2,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="sales-buying-group-name", placeholder="Name *"
                                ),
                                md=3,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="sales-buying-group-color",
                                    type="color",
                                    value="#9E9E9E",
                                ),
                                md=1,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="sales-buying-group-desc",
                                    placeholder="Description",
                                ),
                                md=4,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Add group",
                                    id="sales-buying-group-add",
                                    color="primary",
                                ),
                                md=2,
                            ),
                        ],
                        className="g-2",
                    ),
                    html.Div(id="sales-buying-group-feedback", className="small mt-2"),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
    )

    return html.Div(
        [
            defaults_card,
            feature_flags,
            reps_card,
            groups_card,
            dbc.Button("Save Settings", id="sales-settings-save", color="primary"),
            html.Div(id="sales-settings-save-alert", className="mt-3"),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="sales-rep-modal-title")),
                    dbc.ModalBody(
                        [
                            dbc.Input(
                                id="sales-rep-modal-code",
                                placeholder="Code",
                                className="mb-2",
                            ),
                            dbc.Input(
                                id="sales-rep-modal-name",
                                placeholder="Name *",
                                className="mb-2",
                            ),
                            dbc.Input(
                                id="sales-rep-modal-email",
                                placeholder="Email",
                                type="email",
                                className="mb-2",
                            ),
                            dbc.Input(
                                id="sales-rep-modal-phone",
                                placeholder="Phone",
                                className="mb-2",
                            ),
                            dbc.Checkbox(
                                id="sales-rep-modal-active",
                                label="Active",
                                value=True,
                            ),
                            dcc.Store(id="sales-rep-modal-id"),
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Cancel",
                                id="sales-rep-modal-cancel",
                                color="secondary",
                                outline=True,
                            ),
                            dbc.Button(
                                "Save",
                                id="sales-rep-modal-save",
                                color="primary",
                            ),
                        ]
                    ),
                ],
                id="sales-rep-modal",
                is_open=False,
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(id="sales-buying-group-modal-title")
                    ),
                    dbc.ModalBody(
                        [
                            dbc.Input(
                                id="sales-buying-group-modal-code",
                                placeholder="Code",
                                className="mb-2",
                            ),
                            dbc.Input(
                                id="sales-buying-group-modal-name",
                                placeholder="Name *",
                                className="mb-2",
                            ),
                            dbc.Textarea(
                                id="sales-buying-group-modal-desc",
                                placeholder="Description",
                                style={"width": "100%", "minHeight": "80px"},
                                className="mb-2",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label("Map colour"),
                                            dbc.Input(
                                                id="sales-buying-group-modal-color",
                                                type="color",
                                                value="#9E9E9E",
                                            ),
                                        ],
                                        md=4,
                                    ),
                                ],
                                className="mb-2",
                            ),
                            dbc.Checkbox(
                                id="sales-buying-group-modal-active",
                                label="Active",
                                value=True,
                            ),
                            dcc.Store(id="sales-buying-group-modal-id"),
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Cancel",
                                id="sales-buying-group-modal-cancel",
                                color="secondary",
                                outline=True,
                            ),
                            dbc.Button(
                                "Save",
                                id="sales-buying-group-modal-save",
                                color="primary",
                            ),
                        ]
                    ),
                ],
                id="sales-buying-group-modal",
                is_open=False,
            ),
        ],
        className="sales-settings-tab",
    )
