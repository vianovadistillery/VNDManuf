"""Analytics sub-tab layout."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html


def _sample_time_series():
    fig = px.line(
        x=["Jan", "Feb", "Mar", "Apr", "May"],
        y=[12000, 13500, 14200, 16800, 17400],
        title="Revenue by Month",
        markers=True,
    )
    fig.update_layout(template="plotly_white")
    return fig


def _sample_channel_area():
    fig = px.area(
        x=["Jan", "Feb", "Mar", "Apr", "May"],
        y=[50, 65, 70, 80, 90],
        title="Channel Mix",
    )
    fig.update_layout(template="plotly_white")
    return fig


def _sample_heatmap():
    fig = px.imshow(
        [
            [5, 7, 3, 2, 1],
            [3, 9, 4, 2, 0],
            [1, 2, 6, 8, 3],
            [0, 1, 2, 4, 7],
        ],
        x=["Mon", "Tue", "Wed", "Thu", "Fri"],
        y=["10:00", "14:00", "18:00", "21:00"],
        color_continuous_scale="Blues",
        title="Orders by Weekday & Hour",
    )
    fig.update_layout(template="plotly_white")
    return fig


def layout():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            id="sales-analytics-revenue-trend",
                            figure=_sample_time_series(),
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dcc.Graph(
                            id="sales-analytics-channel-area",
                            figure=_sample_channel_area(),
                        ),
                        md=6,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            id="sales-analytics-cohort",
                            figure=px.line(
                                x=["Month 1", "Month 2", "Month 3", "Month 4"],
                                y=[100, 72, 58, 45],
                                title="Cohort Retention",
                                markers=True,
                            ).update_layout(template="plotly_white"),
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dcc.Graph(
                            id="sales-analytics-heatmap", figure=_sample_heatmap()
                        ),
                        md=6,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            id="sales-analytics-pareto",
                            figure=px.line(
                                x=list(range(1, 11)),
                                y=[15, 28, 39, 48, 56, 63, 69, 74, 78, 81],
                                title="Pareto – Cumulative Customer Contribution",
                            ).update_layout(template="plotly_white"),
                        )
                    )
                ]
            ),
        ],
        className="sales-analytics-tab",
    )
