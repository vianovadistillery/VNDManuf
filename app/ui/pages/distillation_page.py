"""Distillation monitoring page."""

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


class DistillationPage:
    """UI layout for monitoring active distillation runs."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H2("Distillation Runs", className="mb-3"),
                                html.P(
                                    "Track continuous still operations, material movements, and run telemetry.",
                                    className="text-muted",
                                ),
                            ]
                        )
                    ]
                ),
                dcc.Store(id="distillation-run-store"),
                dcc.Store(id="distillation-selected-run-id"),
                dcc.Store(id="distillation-product-options"),
                dcc.Interval(
                    id="distillation-refresh-interval",
                    interval=60_000,
                    n_intervals=0,
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    "New Run",
                                    id="distillation-open-create",
                                    color="primary",
                                    className="mb-3",
                                ),
                                dbc.Button(
                                    "Refresh",
                                    id="distillation-refresh-btn",
                                    color="secondary",
                                    outline=True,
                                    className="mb-3 ms-2",
                                ),
                            ]
                        )
                    ]
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Create Distillation Run")),
                        dbc.ModalBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Run Code"),
                                                dbc.Input(
                                                    id="distillation-create-code",
                                                    placeholder="Leave blank to auto-generate",
                                                ),
                                            ],
                                            md=6,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("External Run Code"),
                                                dbc.Input(
                                                    id="distillation-create-external-code",
                                                    placeholder="External reference (optional)",
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
                                                dbc.Label("Still Code"),
                                                dbc.Input(
                                                    id="distillation-create-still",
                                                    placeholder="Still identifier (e.g. Still-01)",
                                                ),
                                            ],
                                            md=6,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Product"),
                                                dcc.Dropdown(
                                                    id="distillation-create-product",
                                                    options=[],
                                                    placeholder="Select product (optional)",
                                                    multi=False,
                                                    clearable=True,
                                                ),
                                            ],
                                            md=6,
                                        ),
                                    ],
                                    className="mt-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label("Open At"),
                                                dbc.Input(
                                                    id="distillation-create-open-at",
                                                    type="datetime-local",
                                                ),
                                            ],
                                            md=6,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label("Notes"),
                                                dbc.Textarea(
                                                    id="distillation-create-notes",
                                                    placeholder="Optional notes",
                                                    rows=3,
                                                ),
                                            ],
                                            md=6,
                                        ),
                                    ],
                                    className="mt-3",
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "Create",
                                    id="distillation-create-submit",
                                    color="primary",
                                ),
                                dbc.Button(
                                    "Cancel",
                                    id="distillation-create-cancel",
                                    color="secondary",
                                    className="ms-2",
                                ),
                            ]
                        ),
                    ],
                    id="distillation-create-modal",
                    is_open=False,
                    size="lg",
                    backdrop="static",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dash_table.DataTable(
                                id="distillation-run-table",
                                columns=[
                                    {"name": "Run Code", "id": "code"},
                                    {"name": "Still", "id": "still_code"},
                                    {"name": "Product", "id": "product_id"},
                                    {"name": "Status", "id": "status"},
                                    {"name": "Opened", "id": "open_at"},
                                    {"name": "Closed", "id": "close_at"},
                                    {"name": "Inputs (kg)", "id": "input_qty"},
                                    {"name": "Outputs (kg)", "id": "output_qty"},
                                ],
                                data=[],
                                sort_action="native",
                                filter_action="native",
                                row_selectable="single",
                                style_table={"overflowX": "auto"},
                                page_action="native",
                                page_current=0,
                                page_size=10,
                            ),
                            md=12,
                        )
                    ],
                    className="mb-4",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                [
                                    dbc.CardHeader("Run Detail"),
                                    dbc.CardBody(
                                        [
                                            html.Div(
                                                [
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    dbc.Label(
                                                                        "Run Code"
                                                                    ),
                                                                    dbc.Input(
                                                                        id="distillation-detail-code",
                                                                        placeholder="Run code",
                                                                    ),
                                                                ],
                                                                md=4,
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Label(
                                                                        "External Run Code"
                                                                    ),
                                                                    dbc.Input(
                                                                        id="distillation-detail-external-code",
                                                                    ),
                                                                ],
                                                                md=4,
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Label("Status"),
                                                                    dcc.Dropdown(
                                                                        id="distillation-detail-status",
                                                                        options=[
                                                                            {
                                                                                "label": "Open",
                                                                                "value": "open",
                                                                            },
                                                                            {
                                                                                "label": "Running",
                                                                                "value": "running",
                                                                            },
                                                                            {
                                                                                "label": "Paused",
                                                                                "value": "paused",
                                                                            },
                                                                            {
                                                                                "label": "Closed",
                                                                                "value": "closed",
                                                                            },
                                                                        ],
                                                                        clearable=False,
                                                                    ),
                                                                ],
                                                                md=4,
                                                            ),
                                                        ]
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    dbc.Label(
                                                                        "Still Code"
                                                                    ),
                                                                    dbc.Input(
                                                                        id="distillation-detail-still",
                                                                        placeholder="Still identifier",
                                                                    ),
                                                                ],
                                                                md=4,
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Label(
                                                                        "Product"
                                                                    ),
                                                                    dcc.Dropdown(
                                                                        id="distillation-detail-product",
                                                                        options=[],
                                                                        placeholder="Select product",
                                                                        clearable=True,
                                                                    ),
                                                                ],
                                                                md=4,
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Label(
                                                                        "Open At"
                                                                    ),
                                                                    dbc.Input(
                                                                        id="distillation-detail-open-at",
                                                                        type="datetime-local",
                                                                    ),
                                                                ],
                                                                md=4,
                                                            ),
                                                        ],
                                                        className="mt-3",
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    dbc.Label("Notes"),
                                                                    dbc.Textarea(
                                                                        id="distillation-detail-notes",
                                                                        rows=3,
                                                                    ),
                                                                ],
                                                                md=12,
                                                            )
                                                        ],
                                                        className="mt-3",
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    html.Div(
                                                                        id="distillation-detail-metadata",
                                                                        className="text-muted mt-2",
                                                                    )
                                                                ],
                                                                md=12,
                                                            )
                                                        ]
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    dbc.ButtonGroup(
                                                                        [
                                                                            dbc.Button(
                                                                                "Save Changes",
                                                                                id="distillation-detail-save",
                                                                                color="primary",
                                                                            ),
                                                                            dbc.Button(
                                                                                "Delete Run",
                                                                                id="distillation-detail-delete",
                                                                                color="danger",
                                                                                outline=True,
                                                                            ),
                                                                        ],
                                                                        className="mt-3",
                                                                    )
                                                                ],
                                                                md=12,
                                                            )
                                                        ]
                                                    ),
                                                ],
                                                id="distillation-run-detail",
                                            ),
                                            html.H5("Recent Events", className="mt-4"),
                                            dash_table.DataTable(
                                                id="distillation-event-table",
                                                columns=[
                                                    {
                                                        "name": "Time",
                                                        "id": "occurred_at",
                                                    },
                                                    {
                                                        "name": "Event",
                                                        "id": "event_type",
                                                    },
                                                    {"name": "Notes", "id": "note"},
                                                ],
                                                data=[],
                                                style_table={"overflowX": "auto"},
                                                page_action="native",
                                                page_current=0,
                                                page_size=10,
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            md=12,
                        )
                    ]
                ),
            ],
            fluid=True,
        )
