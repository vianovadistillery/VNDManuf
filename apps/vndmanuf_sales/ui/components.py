"""Reusable UI components for the Sales tab."""

from __future__ import annotations

from typing import List, Optional

import dash_bootstrap_components as dbc
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
    return dcc.Graph(
        id=graph_id,
        figure={
            "data": [],
            "layout": {
                "height": 160,
                "margin": {"l": 10, "r": 10, "t": 20, "b": 10},
                "showlegend": False,
                "template": "plotly_white",
                "xaxis": {"title": "Date"},
                "yaxis": {"title": "Revenue (Inc GST)"},
            },
        },
        config={"displayModeBar": False},
    )


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
    dropdown_id: str,
    label: str,
    options: List[dict],
    multi: bool = False,
    value: Optional[str] = None,
):
    return html.Div(
        [
            dbc.Label(label, className="form-label mb-1"),
            dcc.Dropdown(
                id=dropdown_id,
                options=options,
                value=value,
                multi=multi,
                clearable=True,
            ),
        ],
        className="mb-2",
    )


def date_range_picker(
    range_id: str,
    label: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Date range picker. start_date/end_date are ISO date strings (e.g. '2026-01-01')."""
    return html.Div(
        [
            dbc.Label(label, className="form-label mb-1"),
            dcc.DatePickerRange(
                id=range_id,
                clearable=True,
                start_date=start_date,
                end_date=end_date,
            ),
        ],
        className="mb-2",
    )
