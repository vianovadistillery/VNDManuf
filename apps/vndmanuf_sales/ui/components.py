"""Reusable UI components for the Sales tab."""

from __future__ import annotations

from typing import List, Optional

import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dash_table, dcc, html


def kpi_card(
    card_id: str, title: str, value: str = "—", subtitle: Optional[str] = None
):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H6(title, className="text-muted text-uppercase mb-2"),
                    html.H3(id=card_id, children=value, className="fw-bold"),
                    html.Small(subtitle, className="text-secondary")
                    if subtitle
                    else None,
                ]
            )
        ],
        className="mb-3 shadow-sm",
    )


def sparkline_graph(graph_id: str):
    sample_fig = px.area(
        x=[1, 2, 3, 4, 5, 6, 7],
        y=[2000, 2200, 2100, 2600, 3100, 3300, 3600],
        template="plotly_white",
    )
    sample_fig.update_layout(
        height=160,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False,
    )
    sample_fig.update_traces(line_color="#0d6efd", fillcolor="rgba(13,110,253,0.2)")
    return dcc.Graph(id=graph_id, figure=sample_fig, config={"displayModeBar": False})


def top_table(table_id: str, title: str, columns: List[str]):
    return dbc.Card(
        [
            dbc.CardHeader(html.H6(title, className="mb-0")),
            dash_table.DataTable(
                id=table_id,
                columns=[{"name": col, "id": col} for col in columns],
                data=[],
                style_table={"height": "300px", "overflowY": "auto"},
                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
                style_cell={"padding": "0.5rem"},
            ),
        ],
        className="mb-3 shadow-sm",
    )


def filter_dropdown(
    dropdown_id: str, label: str, options: List[dict], multi: bool = False
):
    return dbc.FormFloating(
        [
            dcc.Dropdown(id=dropdown_id, options=options, multi=multi, clearable=True),
            html.Label(label),
        ],
        className="mb-2",
    )


def date_range_picker(range_id: str, label: str):
    return dbc.FormFloating(
        [
            dcc.DatePickerRange(id=range_id, clearable=True),
            html.Label(label),
        ],
        className="mb-2",
    )
