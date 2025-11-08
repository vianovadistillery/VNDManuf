from __future__ import annotations

from datetime import datetime

import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, no_update
from sqlalchemy import select

from ...models import Brand, PriceObservation
from ...services import (
    ObservationFilters,
    get_filtered_counts,
    get_kpis,
    get_recent_observations,
)
from ...services.db import session_scope
from ...services.reports import fetch_observations
from ..components import data_table, filter_dropdown, kpi_card, loading_wrapper

FILTER_IDS = {
    "brand": "overview-filter-brand",
    "channel": "overview-filter-channel",
    "date": "overview-filter-date",
    "search": "overview-filter-search",
}

RECENT_TABLE_ID = "overview-recent-table"


def layout() -> dbc.Container:
    brand_options, channel_options = _load_filter_options()
    return dbc.Container(
        [
            html.H2("Overview", className="mb-4"),
            dbc.Row(
                [
                    dbc.Col(kpi_card("overview-kpi-brands", "Brands"), md=4),
                    dbc.Col(kpi_card("overview-kpi-skus", "SKUs"), md=4),
                    dbc.Col(
                        kpi_card("overview-kpi-observations", "Observations"), md=4
                    ),
                ],
                className="g-3 mb-4",
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    filter_dropdown(
                                        FILTER_IDS["brand"],
                                        "Brands",
                                        brand_options,
                                        placeholder="All brands",
                                    ),
                                    md=4,
                                ),
                                dbc.Col(
                                    filter_dropdown(
                                        FILTER_IDS["channel"],
                                        "Channels",
                                        channel_options,
                                        placeholder="All channels",
                                    ),
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Observation Date", className="fw-semibold"
                                        ),
                                        dcc.DatePickerRange(
                                            id=FILTER_IDS["date"],
                                            minimum_nights=0,
                                            display_format="YYYY-MM-DD",
                                            className="w-100",
                                        ),
                                    ],
                                    md=4,
                                ),
                            ],
                            className="g-3",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Input(
                                        id=FILTER_IDS["search"],
                                        placeholder="Search brand or product",
                                        type="text",
                                    ),
                                    md=6,
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        "Reset Filters",
                                        id="overview-reset-filters",
                                        color="secondary",
                                        outline=True,
                                        className="mt-sm-0 mt-3",
                                    ),
                                    md="auto",
                                ),
                            ],
                            className="g-2 mt-2 align-items-end",
                        ),
                    ]
                ),
                className="mb-4",
            ),
            loading_wrapper(
                "overview-recent-wrapper",
                data_table(
                    RECENT_TABLE_ID,
                    columns=[
                        {"id": "observation_dt", "name": "Observed"},
                        {"id": "brand", "name": "Brand"},
                        {"id": "product", "name": "Product"},
                        {"id": "company", "name": "Company"},
                        {"id": "channel", "name": "Channel"},
                        {"id": "price_inc_gst_norm", "name": "Price (inc GST)"},
                        {"id": "unit_price_inc_gst", "name": "Unit Price"},
                    ],
                ),
            ),
        ],
        fluid=True,
    )


def register_callbacks(app) -> None:  # pragma: no cover - Dash wiring
    @app.callback(
        Output("overview-kpi-brands", "children"),
        Output("overview-kpi-skus", "children"),
        Output("overview-kpi-observations", "children"),
        Output(RECENT_TABLE_ID, "data"),
        Input(FILTER_IDS["brand"], "value"),
        Input(FILTER_IDS["channel"], "value"),
        Input(FILTER_IDS["date"], "start_date"),
        Input(FILTER_IDS["date"], "end_date"),
        Input(FILTER_IDS["search"], "value"),
    )
    def update_overview(brand_ids, channels, start_date, end_date, search):
        filters = ObservationFilters(
            brand_ids=brand_ids or [],
            channels=channels or [],
            start_dt=_parse_date(start_date),
            end_dt=_parse_date(end_date),
            search=(search or "").strip() or None,
        )
        with session_scope() as session:
            totals = (
                get_filtered_counts(session, filters)
                if any(
                    [
                        filters.brand_ids,
                        filters.channels,
                        filters.start_dt,
                        filters.end_dt,
                        filters.search,
                    ]
                )
                else get_kpis(session)
            )
            recent = get_recent_observations(session, limit=25)
            if any(
                [
                    filters.brand_ids,
                    filters.channels,
                    filters.start_dt,
                    filters.end_dt,
                    filters.search,
                ]
            ):
                data_response = fetch_observations(
                    session,
                    filters,
                    page=1,
                    page_size=25,
                )
                recent = data_response["items"]
        return (
            f"{totals['brands']:,}",
            f"{totals['skus']:,}",
            f"{totals['observations']:,}",
            recent,
        )

    @app.callback(
        Output(FILTER_IDS["brand"], "value"),
        Output(FILTER_IDS["channel"], "value"),
        Output(FILTER_IDS["date"], "start_date"),
        Output(FILTER_IDS["date"], "end_date"),
        Output(FILTER_IDS["search"], "value"),
        Input("overview-reset-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(_):
        return no_update, no_update, None, None, ""


def _load_filter_options() -> tuple[list[dict], list[dict]]:
    with session_scope() as session:
        brands = session.execute(
            select(Brand.id, Brand.name)
            .where(Brand.deleted_at.is_(None))
            .order_by(Brand.name)
        ).all()
        channels = session.execute(
            select(PriceObservation.channel)
            .distinct()
            .order_by(PriceObservation.channel)
        ).all()
    brand_options = [{"label": name, "value": id_} for id_, name in brands]
    channel_options = [
        {"label": channel[0], "value": channel[0]} for channel in channels
    ]
    return brand_options, channel_options


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
