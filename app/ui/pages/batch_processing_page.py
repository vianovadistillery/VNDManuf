"""Batch Processing page for Dash UI (stub – page was removed; placeholder for nav)."""

import dash_bootstrap_components as dbc
from dash import html


class BatchProcessingPage:
    """Batch Processing page – placeholder layout."""

    @staticmethod
    def get_layout():
        return dbc.Container(
            [
                dbc.Row(
                    dbc.Col(
                        html.H2("Batch Processing", className="mb-4"),
                    )
                ),
                dbc.Row(
                    dbc.Col(
                        html.P(
                            "This page is currently unavailable.",
                            className="text-muted",
                        )
                    )
                ),
            ],
            fluid=True,
        )
