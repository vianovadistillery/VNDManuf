from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dash_table import DataTable


def kpi_card(card_id: str, title: str, icon: str | None = None) -> dbc.Card:
    header_children = []
    if icon:
        header_children.append(html.Span(icon, className="me-2"))
    header_children.append(html.Span(title))
    return dbc.Card(
        [
            dbc.CardHeader(header_children, className="d-flex align-items-center"),
            dbc.CardBody(
                html.H2(
                    "--", id=card_id, className="display-6 fw-semibold text-primary"
                ),
            ),
        ],
        className="shadow-sm",
    )


def data_table(table_id: str, columns: list[dict], **kwargs) -> DataTable:
    default_kwargs = dict(
        style_table={"overflowX": "auto"},
        style_header={"fontWeight": "600"},
        style_cell={"padding": "0.5rem"},
        page_action="none",
        sort_action="none",
    )
    default_kwargs.update(kwargs)
    return DataTable(id=table_id, columns=columns, **default_kwargs)


def filter_dropdown(
    component_id: str,
    label: str,
    options: list[dict] | None = None,
    *,
    multi: bool = True,
    placeholder: str | None = None,
) -> html.Div:
    return html.Div(
        [
            dbc.Label(label, className="fw-semibold"),
            dcc.Dropdown(
                id=component_id,
                options=options or [],
                multi=multi,
                placeholder=placeholder or f"Select {label.lower()}",
                clearable=True,
            ),
        ],
        className="mb-3",
    )


def modal_form(
    modal_id: str,
    header: str,
    body_children: list,
    *,
    submit_id: str,
    close_id: str,
    size: str = "lg",
) -> dbc.Modal:
    return dbc.Modal(
        [
            dbc.ModalHeader(header),
            dbc.ModalBody(body_children),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel", id=close_id, color="secondary", className="me-2"
                    ),
                    dbc.Button("Save", id=submit_id, color="primary"),
                ]
            ),
        ],
        id=modal_id,
        size=size,
        backdrop="static",
    )


def loading_wrapper(component_id: str, child) -> dcc.Loading:
    return dcc.Loading(id=f"{component_id}-loading", type="default", children=child)
