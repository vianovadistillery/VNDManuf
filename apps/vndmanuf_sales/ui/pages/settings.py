"""Sales Settings sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html


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

    return html.Div(
        [
            defaults_card,
            feature_flags,
            dbc.Button("Save Settings", id="sales-settings-save", color="primary"),
            html.Div(id="sales-settings-save-alert", className="mt-3"),
        ],
        className="sales-settings-tab",
    )
