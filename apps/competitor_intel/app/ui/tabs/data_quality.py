from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Set

import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from sqlalchemy import select

from ...models import SKU, Brand, Company, ManufacturingCost, PriceObservation, Product
from ...services import (
    ObservationFilters,
    get_duplicate_overview,
    get_missing_gtins,
    get_price_outliers,
)
from ...services.db import session_scope
from ..components import data_table, filter_dropdown, loading_wrapper

BRAND_FILTER_ID = "dq-filter-brand"
DATE_FILTER_ID = "dq-filter-date"
DUPLICATES_TABLE_ID = "dq-duplicates"
MISSING_GTIN_TABLE_ID = "dq-missing-gtin"
OUTLIERS_TABLE_ID = "dq-outliers"
COST_GAPS_TABLE_ID = "dq-cost-gaps"
NEGATIVE_GP_TABLE_ID = "dq-negative-gp"


def layout() -> dbc.Container:
    brand_options = _load_brand_options()
    return dbc.Container(
        [
            html.H2("Data Quality", className="mb-4"),
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    filter_dropdown(
                                        BRAND_FILTER_ID,
                                        "Brands",
                                        brand_options,
                                        placeholder="All brands",
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
                        ),
                    ]
                ),
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        loading_wrapper(
                            DUPLICATES_TABLE_ID,
                            data_table(
                                DUPLICATES_TABLE_ID,
                                columns=[
                                    {"id": "hash_key", "name": "Hash"},
                                    {"id": "count", "name": "Duplicates"},
                                    {
                                        "id": "observation_ids",
                                        "name": "Observation IDs",
                                    },
                                ],
                                page_action="native",
                                page_size=10,
                            ),
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        loading_wrapper(
                            MISSING_GTIN_TABLE_ID,
                            data_table(
                                MISSING_GTIN_TABLE_ID,
                                columns=[
                                    {"id": "brand", "name": "Brand"},
                                    {"id": "product", "name": "Product"},
                                    {"id": "sku_id", "name": "SKU ID"},
                                    {"id": "is_active", "name": "Active"},
                                ],
                                page_action="native",
                                page_size=10,
                            ),
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        loading_wrapper(
                            OUTLIERS_TABLE_ID,
                            data_table(
                                OUTLIERS_TABLE_ID,
                                columns=[
                                    {"id": "brand", "name": "Brand"},
                                    {"id": "product", "name": "Product"},
                                    {"id": "company", "name": "Company"},
                                    {"id": "price_per_litre", "name": "Price/Litre"},
                                    {"id": "z_score", "name": "Z-Score"},
                                ],
                                page_action="native",
                                page_size=10,
                            ),
                        ),
                        md=4,
                    ),
                ],
                className="g-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        loading_wrapper(
                            COST_GAPS_TABLE_ID,
                            data_table(
                                COST_GAPS_TABLE_ID,
                                columns=[
                                    {"id": "sku", "name": "SKU"},
                                    {"id": "missing_known", "name": "Missing Known"},
                                    {
                                        "id": "missing_estimated",
                                        "name": "Missing Estimated",
                                    },
                                ],
                                page_action="native",
                                page_size=10,
                            ),
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        loading_wrapper(
                            NEGATIVE_GP_TABLE_ID,
                            data_table(
                                NEGATIVE_GP_TABLE_ID,
                                columns=[
                                    {"id": "brand", "name": "Brand"},
                                    {"id": "product", "name": "Product"},
                                    {"id": "company", "name": "Company"},
                                    {"id": "unit_gp_pct", "name": "Unit GP %"},
                                    {"id": "price_basis", "name": "Basis"},
                                    {"id": "observation_dt", "name": "Observed"},
                                ],
                                page_action="native",
                                page_size=10,
                            ),
                        ),
                        md=6,
                    ),
                ],
                className="g-3 mt-1",
            ),
        ],
        fluid=True,
    )


def register_callbacks(app):  # pragma: no cover - Dash wiring
    @app.callback(
        Output(DUPLICATES_TABLE_ID, "data"),
        Output(MISSING_GTIN_TABLE_ID, "data"),
        Output(OUTLIERS_TABLE_ID, "data"),
        Output(COST_GAPS_TABLE_ID, "data"),
        Output(NEGATIVE_GP_TABLE_ID, "data"),
        Input(BRAND_FILTER_ID, "value"),
        Input(DATE_FILTER_ID, "start_date"),
        Input(DATE_FILTER_ID, "end_date"),
    )
    def update_quality_tables(brand_ids, start_date, end_date):
        brands = brand_ids or []
        filters = ObservationFilters(
            brand_ids=brands,
            start_dt=_to_datetime(start_date),
            end_dt=_to_datetime(end_date),
        )
        with session_scope() as session:
            duplicates = get_duplicate_overview(session, limit=100)
            missing_gtins = get_missing_gtins(session)
            outliers = get_price_outliers(session, filters)
            cost_gaps = _get_cost_gaps(session)
            negative_gp = _get_negative_gp(session, filters)

        brand_names = _brand_names_from_ids(brands) if brands else set()

        duplicates_formatted = [
            {
                "hash_key": row["hash_key"],
                "count": row["count"],
                "observation_ids": ", ".join(row["observation_ids"][:5])
                + ("…" if len(row["observation_ids"]) > 5 else ""),
            }
            for row in duplicates
        ]
        missing_formatted = [
            {
                "brand": row["brand"],
                "product": row["product"],
                "sku_id": row["sku_id"],
                "is_active": "Yes" if row["is_active"] else "No",
            }
            for row in missing_gtins
            if (not brands) or (row["brand"] in brand_names)
        ]
        outlier_formatted = [
            {
                "brand": row["brand"],
                "product": row["product"],
                "company": row["company"],
                "price_per_litre": f"${row['price_per_litre']:.2f}",
                "z_score": row["z_score"],
            }
            for row in outliers
        ]
        cost_gap_formatted = [
            {
                "sku": row["sku"],
                "missing_known": "Yes" if row["missing_known"] else "No",
                "missing_estimated": "Yes" if row["missing_estimated"] else "No",
            }
            for row in cost_gaps
            if (not brands) or (row["brand"] in brand_names)
        ]
        negative_gp_formatted = [
            {
                "brand": row["brand"],
                "product": row["product"],
                "company": row["company"],
                "unit_gp_pct": f"{row['unit_gp_pct']:.2f}%"
                if row["unit_gp_pct"] is not None
                else "",
                "price_basis": row["price_basis"],
                "observation_dt": row["observation_dt"],
            }
            for row in negative_gp
        ]
        return (
            duplicates_formatted,
            missing_formatted,
            outlier_formatted,
            cost_gap_formatted,
            negative_gp_formatted,
        )


def _load_brand_options() -> List[dict]:
    with session_scope() as session:
        return [
            {"label": brand.name, "value": brand.id}
            for brand in session.execute(
                select(Brand).where(Brand.deleted_at.is_(None)).order_by(Brand.name)
            ).scalars()
        ]


def _brand_names_from_ids(ids: List[str]) -> Set[str]:
    if not ids:
        return set()
    with session_scope() as session:
        return {
            brand.name
            for brand in session.execute(
                select(Brand).where(Brand.id.in_(ids))
            ).scalars()
        }


def _to_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _get_cost_gaps(session) -> List[dict]:
    known_ids = {
        row[0]
        for row in session.execute(
            select(ManufacturingCost.sku_id).where(
                ManufacturingCost.deleted_at.is_(None),
                ManufacturingCost.cost_type == "known",
            )
        ).all()
    }
    estimated_ids = {
        row[0]
        for row in session.execute(
            select(ManufacturingCost.sku_id).where(
                ManufacturingCost.deleted_at.is_(None),
                ManufacturingCost.cost_type == "estimated",
            )
        ).all()
    }
    results: List[dict] = []
    rows = session.execute(
        select(
            SKU.id,
            SKU.gtin,
            Product.name,
            Brand.name,
        )
        .join(SKU.product)
        .join(Product.brand)
        .where(
            SKU.deleted_at.is_(None),
            Product.deleted_at.is_(None),
            Brand.deleted_at.is_(None),
        )
        .order_by(Brand.name, Product.name)
    ).all()
    for sku_id, gtin, product_name, brand_name in rows:
        missing_known = sku_id not in known_ids
        missing_estimated = sku_id not in estimated_ids
        if missing_known or missing_estimated:
            results.append(
                {
                    "sku_id": sku_id,
                    "sku": f"{brand_name} - {product_name}"
                    + (f" ({gtin})" if gtin else ""),
                    "brand": brand_name,
                    "missing_known": missing_known,
                    "missing_estimated": missing_estimated,
                }
            )
    return results


def _get_negative_gp(session, filters: ObservationFilters) -> List[dict]:
    stmt = (
        select(
            Brand.name,
            Product.name,
            Company.name,
            PriceObservation.gp_unit_pct,
            PriceObservation.price_basis,
            PriceObservation.observation_dt,
        )
        .join(PriceObservation.sku)
        .join(SKU.product)
        .join(Product.brand)
        .join(Company, PriceObservation.company_id == Company.id)
        .where(
            PriceObservation.deleted_at.is_(None),
            SKU.deleted_at.is_(None),
            Product.deleted_at.is_(None),
            Brand.deleted_at.is_(None),
            Company.deleted_at.is_(None),
            PriceObservation.gp_unit_abs < 0,
        )
    )
    if filters.brand_ids:
        stmt = stmt.where(Brand.id.in_(filters.brand_ids))
    if filters.start_dt:
        stmt = stmt.where(PriceObservation.observation_dt >= filters.start_dt)
    if filters.end_dt:
        stmt = stmt.where(PriceObservation.observation_dt <= filters.end_dt)
    rows = session.execute(stmt.limit(200)).all()
    formatted: List[dict] = []
    for brand, product, company, gp_pct, basis, obs_dt in rows:
        formatted.append(
            {
                "brand": brand,
                "product": product,
                "company": company or "",
                "unit_gp_pct": float(gp_pct * Decimal("100"))
                if gp_pct is not None
                else None,
                "price_basis": (basis or "unit").title(),
                "observation_dt": obs_dt.isoformat(),
            }
        )
    return formatted
