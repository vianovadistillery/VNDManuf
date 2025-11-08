from __future__ import annotations

from datetime import datetime
from typing import Dict, List

import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, dcc, html
from sqlalchemy import select

from ...models import Brand, PriceObservation
from ...services import ObservationFilters, get_map_summary
from ...services.db import session_scope
from ..components import data_table, filter_dropdown, loading_wrapper

BRAND_FILTER_ID = "map-filter-brand"
CHANNEL_FILTER_ID = "map-filter-channel"
DATE_FILTER_ID = "map-filter-date"
MAP_GRAPH_ID = "map-graph"
TABLE_ID = "map-table"

STATE_COORDS = {
    "NSW": (-33.8688, 151.2093),
    "VIC": (-37.8136, 144.9631),
    "QLD": (-27.4698, 153.0251),
    "SA": (-34.9285, 138.6007),
    "WA": (-31.9505, 115.8605),
    "TAS": (-42.8821, 147.3272),
    "NT": (-12.4634, 130.8456),
    "ACT": (-35.2809, 149.1300),
}


def layout() -> dbc.Container:
    options = _load_filter_options()
    return dbc.Container(
        [
            html.H2("Price Map", className="mb-4"),
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    filter_dropdown(
                                        BRAND_FILTER_ID,
                                        "Brands",
                                        options["brands"],
                                        placeholder="All brands",
                                    ),
                                    md=4,
                                ),
                                dbc.Col(
                                    filter_dropdown(
                                        CHANNEL_FILTER_ID,
                                        "Channels",
                                        options["channels"],
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
                                            id=DATE_FILTER_ID,
                                            minimum_nights=0,
                                            display_format="YYYY-MM-DD",
                                            className="w-100",
                                        ),
                                    ],
                                    md=4,
                                ),
                            ],
                            className="g-3",
                        )
                    ]
                ),
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        loading_wrapper(
                            MAP_GRAPH_ID,
                            dcc.Graph(
                                id=MAP_GRAPH_ID, config={"displayModeBar": False}
                            ),
                        ),
                        md=8,
                    ),
                    dbc.Col(
                        data_table(
                            TABLE_ID,
                            columns=[
                                {"id": "state", "name": "State"},
                                {"id": "suburb", "name": "Suburb"},
                                {"id": "median_price_inc_gst", "name": "Median Price"},
                                {"id": "samples", "name": "Samples"},
                            ],
                            page_action="native",
                            page_size=10,
                        ),
                        md=4,
                    ),
                ],
                className="g-3",
            ),
        ],
        fluid=True,
    )


def register_callbacks(app):  # pragma: no cover - Dash wiring
    @app.callback(
        Output(MAP_GRAPH_ID, "figure"),
        Output(TABLE_ID, "data"),
        Input(BRAND_FILTER_ID, "value"),
        Input(CHANNEL_FILTER_ID, "value"),
        Input(DATE_FILTER_ID, "start_date"),
        Input(DATE_FILTER_ID, "end_date"),
    )
    def update_map(brand_ids, channels, start_date, end_date):
        filters = ObservationFilters(
            brand_ids=brand_ids or [],
            channels=channels or [],
            start_dt=_to_datetime(start_date),
            end_dt=_to_datetime(end_date),
        )
        with session_scope() as session:
            rows = get_map_summary(session, filters)

        fig = _build_map_figure(rows)
        table_data = [
            {
                "state": row["state"],
                "suburb": row["suburb"],
                "median_price_inc_gst": f"${row['median_price_inc_gst']:.2f}",
                "samples": row["samples"],
            }
            for row in rows
        ]
        return fig, table_data


def _build_map_figure(rows: List[dict]):
    if not rows:
        fig = px.scatter_geo()
        fig.update_layout(title="No observations to map", geo_scope="world")
        return fig
    df = _rows_with_coordinates(rows)
    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        color="median_price_inc_gst",
        size="samples",
        hover_name="label",
        scope="world",
        color_continuous_scale="Viridis",
    )
    fig.update_geos(fitbounds="locations", showcountries=True)
    fig.update_layout(
        title="Median Price by Location", margin=dict(l=0, r=0, t=50, b=0)
    )
    return fig


def _rows_with_coordinates(rows: List[dict]):
    data = []
    for row in rows:
        lat = row.get("lat")
        lon = row.get("lon")
        if lat is None or lon is None:
            coords = STATE_COORDS.get(row["state"])
            if coords is None:
                continue
            lat, lon = coords
        data.append(
            {
                "lat": lat,
                "lon": lon,
                "median_price_inc_gst": row["median_price_inc_gst"],
                "samples": row["samples"],
                "label": f"{row['suburb']}, {row['state']}",
            }
        )
    return data


def _load_filter_options() -> Dict[str, List[dict]]:
    with session_scope() as session:
        brands = [
            {"label": brand.name, "value": brand.id}
            for brand in session.execute(
                select(Brand).where(Brand.deleted_at.is_(None)).order_by(Brand.name)
            ).scalars()
        ]
        channels = [
            {"label": channel, "value": channel}
            for (channel,) in session.execute(
                select(PriceObservation.channel)
                .distinct()
                .where(PriceObservation.deleted_at.is_(None))
                .order_by(PriceObservation.channel)
            )
            if channel
        ]
    return {"brands": brands, "channels": channels}


def _to_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)
