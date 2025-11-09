from __future__ import annotations

from datetime import datetime
from typing import Dict, List

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, dcc, html
from sqlalchemy import select

from ...models import SKU, Brand, PriceObservation, Product
from ...models.product import PRODUCT_FORMATS, PRODUCT_SPIRITS, categories_for
from ...services import (
    ObservationFilters,
    get_filtered_counts,
    get_price_distribution,
    get_price_time_series,
)
from ...services.db import session_scope
from ..components import filter_dropdown, loading_wrapper

BRAND_FILTER_ID = "analytics-filter-brand"
SKU_FILTER_ID = "analytics-filter-sku"
CHANNEL_FILTER_ID = "analytics-filter-channel"
DATE_FILTER_ID = "analytics-filter-date"
SPIRIT_FILTER_ID = "analytics-filter-spirit"
FORMAT_FILTER_ID = "analytics-filter-format"
TIME_SERIES_GRAPH_ID = "analytics-time-series"
DISTRIBUTION_GRAPH_ID = "analytics-distribution"
SUMMARY_CONTAINER_ID = "analytics-summary"


def layout() -> dbc.Container:
    options = _load_filter_options()
    return dbc.Container(
        [
            html.H2("Analytics", className="mb-4"),
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
                                        SKU_FILTER_ID,
                                        "SKUs",
                                        options["skus"],
                                        placeholder="All SKUs",
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
                            ],
                            className="g-3",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    filter_dropdown(
                                        SPIRIT_FILTER_ID,
                                        "Spirit",
                                        options["spirits"],
                                        placeholder="All spirits",
                                    ),
                                    md=6,
                                ),
                                dbc.Col(
                                    filter_dropdown(
                                        FORMAT_FILTER_ID,
                                        "Format",
                                        options["formats"],
                                        placeholder="All formats",
                                    ),
                                    md=6,
                                ),
                            ],
                            className="g-3 mt-2",
                        ),
                        dbc.Row(
                            [
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
                            className="g-3 mt-2",
                        ),
                    ]
                ),
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        loading_wrapper(
                            TIME_SERIES_GRAPH_ID,
                            dcc.Graph(
                                id=TIME_SERIES_GRAPH_ID,
                                config={"displayModeBar": False},
                            ),
                        ),
                        md=8,
                    ),
                    dbc.Col(
                        [
                            loading_wrapper(
                                DISTRIBUTION_GRAPH_ID,
                                dcc.Graph(
                                    id=DISTRIBUTION_GRAPH_ID,
                                    config={"displayModeBar": False},
                                ),
                            ),
                            dbc.Card(
                                dbc.CardBody(id=SUMMARY_CONTAINER_ID, className="mt-3"),
                                className="mt-3",
                            ),
                        ],
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
        Output(TIME_SERIES_GRAPH_ID, "figure"),
        Output(DISTRIBUTION_GRAPH_ID, "figure"),
        Output(SUMMARY_CONTAINER_ID, "children"),
        Input(BRAND_FILTER_ID, "value"),
        Input(SKU_FILTER_ID, "value"),
        Input(SPIRIT_FILTER_ID, "value"),
        Input(FORMAT_FILTER_ID, "value"),
        Input(CHANNEL_FILTER_ID, "value"),
        Input(DATE_FILTER_ID, "start_date"),
        Input(DATE_FILTER_ID, "end_date"),
    )
    def update_analytics(
        brand_ids, sku_ids, spirits, formats, channels, start_date, end_date
    ):
        categories = (
            categories_for(spirits or None, formats or None)
            if (spirits or formats)
            else []
        )
        package_types = []
        if formats:
            if "bottle" in formats:
                package_types.append("bottle")
            if "rtd" in formats:
                package_types.append("can")
        filters = ObservationFilters(
            brand_ids=brand_ids or [],
            sku_ids=sku_ids or [],
            categories=categories,
            package_types=package_types,
            channels=channels or [],
            start_dt=_to_datetime(start_date),
            end_dt=_to_datetime(end_date),
        )
        with session_scope() as session:
            ts_rows = get_price_time_series(session, filters)
            dist_rows = get_price_distribution(session, filters)
            summary_counts = get_filtered_counts(session, filters)

        ts_fig = _build_time_series_figure(ts_rows)
        dist_fig = _build_distribution_figure(dist_rows)
        summary = _build_summary(summary_counts)
        return ts_fig, dist_fig, summary


def _build_time_series_figure(rows: List[dict]):
    if not rows:
        fig = px.line()
        fig.update_layout(
            title="No observations match the selected filters",
            xaxis_title="Week",
            yaxis_title="Avg Price (inc GST)",
        )
        return fig
    df = pd.DataFrame(rows)
    # Convert ISO-style "YYYY-WW" strings (or missing values) into timestamps
    df["period"] = df["period"].apply(
        lambda value: f"{value}-1" if isinstance(value, str) and value else None
    )
    df["period"] = pd.to_datetime(df["period"], format="%Y-%W-%w", errors="coerce")
    df = df.dropna(subset=["period"]).copy()
    if df.empty:
        fig = px.line()
        fig.update_layout(
            title="No observations match the selected filters",
            xaxis_title="Week",
            yaxis_title="Avg Price (inc GST)",
        )
        return fig
    df.sort_values(["period", "sku_label"], inplace=True)
    fig = px.line(
        df,
        x="period",
        y="avg_price",
        color="sku_label",
        markers=True,
        hover_data={"samples": True},
    )
    fig.update_layout(
        title="Average Price (inc GST) by Week",
        xaxis_title="Week",
        yaxis_title="Avg Price (inc GST)",
        legend_title="SKU",
    )
    return fig


def _build_distribution_figure(rows: List[dict]):
    if not rows:
        fig = px.bar()
        fig.update_layout(
            title="No retailer distribution available",
            xaxis_title="Retailer",
            yaxis_title="Avg Price/Litre",
        )
        return fig
    df = pd.DataFrame(rows)
    fig = px.bar(
        df,
        x="company",
        y="avg_price_per_litre",
        hover_data={"samples": True},
    )
    fig.update_layout(
        title="Average Price per Litre by Company",
        xaxis_title="Company",
        yaxis_title="Avg Price per Litre",
    )
    return fig


def _build_summary(counts: Dict[str, int]) -> dbc.ListGroup:
    return dbc.ListGroup(
        [
            dbc.ListGroupItem(f"Brands: {counts['brands']:,}"),
            dbc.ListGroupItem(f"SKUs: {counts['skus']:,}"),
            dbc.ListGroupItem(f"Observations: {counts['observations']:,}"),
        ]
    )


def _load_filter_options() -> Dict[str, List[dict]]:
    with session_scope() as session:
        brands = [
            {"label": brand.name, "value": brand.id}
            for brand in session.execute(
                select(Brand).where(Brand.deleted_at.is_(None)).order_by(Brand.name)
            ).scalars()
        ]
        skus = [
            {
                "label": f"{brand_name} - {product_name}",
                "value": sku_id,
            }
            for sku_id, product_name, brand_name in session.execute(
                select(SKU.id, Product.name, Brand.name)
                .join(SKU.product)
                .join(Product.brand)
                .where(
                    SKU.deleted_at.is_(None),
                    Product.deleted_at.is_(None),
                    Brand.deleted_at.is_(None),
                )
                .order_by(Brand.name, Product.name)
            )
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
    return {
        "brands": brands,
        "skus": skus,
        "channels": channels,
        "spirits": [
            {"label": spirit.title(), "value": spirit} for spirit in PRODUCT_SPIRITS
        ],
        "formats": [
            {"label": "RTD" if fmt == "rtd" else fmt.title(), "value": fmt}
            for fmt in PRODUCT_FORMATS
        ],
    }


def _to_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)
