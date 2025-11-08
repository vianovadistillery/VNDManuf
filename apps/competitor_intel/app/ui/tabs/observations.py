from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update
from sqlalchemy import select

from ...models import SKU, Brand, Company, Location, PriceObservation, Product
from ...services import ObservationFilters, fetch_observations
from ...services.db import session_scope
from ...services.dedupe import apply_hash_to_observation
from ...services.normalize import normalize_price
from ..components import data_table, filter_dropdown, loading_wrapper, modal_form

FILTER_BRAND_ID = "observations-filter-brand"
FILTER_CHANNEL_ID = "observations-filter-channel"
FILTER_DATE_ID = "observations-filter-date"
FILTER_BASIS_ID = "observations-filter-basis"
TABLE_ID = "observations-table"
PAGINATION_ID = "observations-pagination"
STORE_ID = "observations-store"
DOWNLOAD_ID = "observations-download"
ADD_MODAL_ID = "observations-add-modal"

CHANNEL_LABELS = {
    "distributor_to_retailer": "Distributor → Retailer",
    "wholesale_to_venue": "Wholesale → Venue",
    "retail_instore": "Retail (In-Store)",
    "retail_online": "Retail (Online)",
    "direct_to_consumer": "Direct to Consumer",
}
CHANNEL_DEFAULT = "retail_instore"
BASIS_OPTIONS = [
    {"label": "Unit", "value": "unit"},
    {"label": "Pack", "value": "pack"},
    {"label": "Carton", "value": "carton"},
]


def layout() -> dbc.Container:
    options = _load_filter_options()
    return dbc.Container(
        [
            html.H2("Observations", className="mb-4"),
            dcc.Store(id=STORE_ID, data={"page": 1, "page_size": 25}),
            dcc.Download(id=DOWNLOAD_ID),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Filters", className="fw-semibold"),
                                    filter_dropdown(
                                        FILTER_BRAND_ID,
                                        "Brands",
                                        options["brands"],
                                        placeholder="All brands",
                                    ),
                                    filter_dropdown(
                                        FILTER_CHANNEL_ID,
                                        "Channels",
                                        options["channels"],
                                        placeholder="All channels",
                                    ),
                                    filter_dropdown(
                                        FILTER_BASIS_ID,
                                        "Price Basis",
                                        options["basis"],
                                        placeholder="All price bases",
                                    ),
                                    dbc.Label(
                                        "Observation Date", className="fw-semibold mt-3"
                                    ),
                                    dcc.DatePickerRange(
                                        id=FILTER_DATE_ID,
                                        minimum_nights=0,
                                        display_format="YYYY-MM-DD",
                                        className="w-100",
                                    ),
                                    dbc.Button(
                                        "Reset",
                                        id="observations-reset-filters",
                                        outline=True,
                                        color="secondary",
                                        className="mt-3",
                                    ),
                                ]
                            ),
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Button(
                                            "Add Observation",
                                            id="observations-open-add",
                                            color="primary",
                                        ),
                                        md="auto",
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "Export CSV",
                                            id="observations-export",
                                            color="primary",
                                            outline=True,
                                        ),
                                        md="auto",
                                    ),
                                ],
                                className="g-2 mb-3",
                            ),
                            loading_wrapper(
                                "observations-table-wrapper",
                                data_table(
                                    TABLE_ID,
                                    columns=[
                                        {"id": "observation_dt", "name": "Observed"},
                                        {"id": "brand", "name": "Brand"},
                                        {"id": "product", "name": "Product"},
                                        {"id": "company", "name": "Company"},
                                        {"id": "channel", "name": "Channel"},
                                        {
                                            "id": "price_inc_gst_norm",
                                            "name": "Price (inc GST)",
                                        },
                                        {
                                            "id": "unit_price_inc_gst",
                                            "name": "Unit Price",
                                        },
                                        {"id": "price_basis", "name": "Basis"},
                                        {
                                            "id": "pack_price_inc_gst",
                                            "name": "Pack Price",
                                        },
                                        {
                                            "id": "carton_price_inc_gst",
                                            "name": "Carton Price",
                                        },
                                        {
                                            "id": "price_per_litre",
                                            "name": "Price/Litre",
                                        },
                                        {"id": "gp_unit_pct", "name": "GP % (Unit)"},
                                        {"id": "gp_pack_pct", "name": "GP % (Pack)"},
                                        {
                                            "id": "gp_carton_pct",
                                            "name": "GP % (Carton)",
                                        },
                                    ],
                                ),
                            ),
                            dbc.Pagination(
                                id=PAGINATION_ID,
                                max_value=1,
                                active_page=1,
                                previous_next=True,
                                first_last=True,
                                className="mt-3",
                            ),
                        ],
                        md=9,
                    ),
                ],
                className="g-3",
            ),
            _add_modal(options),
        ],
        fluid=True,
    )


def register_callbacks(app) -> None:  # pragma: no cover - Dash wiring
    @app.callback(
        Output(TABLE_ID, "data"),
        Output(PAGINATION_ID, "max_value"),
        Output(PAGINATION_ID, "active_page"),
        Output(STORE_ID, "data"),
        Input(FILTER_BRAND_ID, "value"),
        Input(FILTER_CHANNEL_ID, "value"),
        Input(FILTER_BASIS_ID, "value"),
        Input(FILTER_DATE_ID, "start_date"),
        Input(FILTER_DATE_ID, "end_date"),
        Input(PAGINATION_ID, "active_page"),
        State(STORE_ID, "data"),
    )
    def update_table(
        brand_ids, channels, bases, start_date, end_date, active_page, store_state
    ):
        store_state = store_state or {"page": 1, "page_size": 25}
        filters = _build_filters(brand_ids, channels, bases, start_date, end_date)
        page = active_page or store_state.get("page", 1)
        page_size = store_state.get("page_size", 25)
        with session_scope() as session:
            result = fetch_observations(
                session, filters, page=page, page_size=page_size
            )
        total_pages = max(1, -(-result["total"] // page_size))
        store_state.update(
            {
                "page": min(page, total_pages),
                "page_size": page_size,
                "filters": {
                    "brand_ids": filters.brand_ids,
                    "channels": filters.channels,
                    "price_bases": filters.price_bases,
                    "start_dt": filters.start_dt.isoformat()
                    if filters.start_dt
                    else None,
                    "end_dt": filters.end_dt.isoformat() if filters.end_dt else None,
                },
            }
        )
        return result["items"], total_pages, min(page, total_pages), store_state

    @app.callback(
        Output(DOWNLOAD_ID, "data"),
        Input("observations-export", "n_clicks"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def export_csv(n_clicks, store_state):
        if not n_clicks or not store_state:
            return no_update
        filters = _filters_from_store(store_state.get("filters", {}))
        with session_scope() as session:
            result = fetch_observations(session, filters, page=1, page_size=1000)
        df = _rows_to_dataframe(result["items"])
        return dcc.send_data_frame(df.to_csv, "observations.csv", index=False)

    @app.callback(
        Output(FILTER_BRAND_ID, "value"),
        Output(FILTER_CHANNEL_ID, "value"),
        Output(FILTER_BASIS_ID, "value"),
        Output(FILTER_DATE_ID, "start_date"),
        Output(FILTER_DATE_ID, "end_date"),
        Input("observations-reset-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(_):
        return [], [], [], None, None

    @app.callback(
        Output(ADD_MODAL_ID, "is_open", allow_duplicate=True),
        Input("observations-open-add", "n_clicks"),
        Input("observations-add-cancel", "n_clicks"),
        State(ADD_MODAL_ID, "is_open"),
        prevent_initial_call=True,
    )
    def toggle_add_modal(open_clicks, cancel_clicks, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == "observations-open-add":
            return True
        return False

    @app.callback(
        Output("observations-add-feedback", "children"),
        Output("observations-add-feedback", "color"),
        Output("observations-add-feedback", "is_open"),
        Output(ADD_MODAL_ID, "is_open", allow_duplicate=True),
        Output(TABLE_ID, "data", allow_duplicate=True),
        Input("observations-add-submit", "n_clicks"),
        State("observations-add-sku", "value"),
        State("observations-add-company", "value"),
        State("observations-add-location", "value"),
        State("observations-add-channel", "value"),
        State("observations-add-price", "value"),
        State("observations-add-price-ex", "value"),
        State("observations-add-gst", "value"),
        State("observations-add-carton", "value"),
        State("observations-add-basis", "value"),
        State("observations-add-context", "value"),
        State("observations-add-availability", "value"),
        State("observations-add-date", "date"),
        State("observations-add-source", "value"),
        State("observations-add-url", "value"),
        State("observations-add-note", "value"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def submit_add_observation(
        n_clicks,
        sku_id,
        company_id,
        location_id,
        channel,
        price_inc,
        price_ex,
        gst_rate,
        carton_units,
        basis,
        price_context,
        availability,
        observation_date,
        source_type,
        source_url,
        source_note,
        store_state,
    ):
        if not n_clicks:
            return no_update, no_update, False, no_update, no_update
        required = [
            sku_id,
            company_id,
            channel,
            price_context,
            availability,
            observation_date,
            source_type,
        ]
        if any(value in (None, "") for value in required):
            return (
                "Please complete all required fields",
                "danger",
                True,
                True,
                no_update,
            )
        price_basis = (basis or "unit").lower()
        is_carton_price = price_basis == "carton"
        is_pack_price = price_basis == "pack"
        if is_carton_price:
            if not carton_units:
                return (
                    "Provide carton units for carton-level pricing",
                    "danger",
                    True,
                    True,
                    no_update,
                )
        payload = {
            "sku_id": sku_id,
            "company_id": company_id,
            "location_id": location_id,
            "channel": channel,
            "price_inc_gst_raw": price_inc,
            "price_ex_gst_raw": price_ex,
            "gst_rate": gst_rate,
            "carton_units": carton_units if is_carton_price else None,
            "is_carton_price": is_carton_price,
            "is_pack_price": is_pack_price,
            "price_basis": price_basis,
            "price_context": price_context,
            "availability": availability,
            "observation_dt": observation_date,
            "source_type": source_type,
            "source_url": source_url,
            "source_note": source_note,
        }
        success = _create_observation(payload)
        if not success:
            return (
                "Duplicate or invalid observation",
                "warning",
                True,
                False,
                no_update,
            )
        filters = (
            _filters_from_store(store_state.get("filters", {}))
            if store_state
            else ObservationFilters()
        )
        with session_scope() as session:
            result = fetch_observations(
                session,
                filters,
                page=store_state.get("page", 1),
                page_size=store_state.get("page_size", 25),
            )
        return ("Observation added", "success", True, False, result["items"])

    @app.callback(
        Output("observations-add-location", "options"),
        Input("observations-add-company", "value"),
    )
    def update_location_options(company_id):
        if not company_id:
            return []
        with session_scope() as session:
            rows = session.execute(
                select(
                    Location.id, Location.store_name, Location.suburb, Location.state
                )
                .where(Location.company_id == company_id, Location.deleted_at.is_(None))
                .order_by(Location.store_name)
            ).all()
        return [
            {
                "label": " ".join(
                    filter(None, [row.store_name, row.suburb, row.state])
                ),
                "value": row.id,
            }
            for row in rows
        ]


def _load_filter_options() -> Dict[str, List[dict]]:
    with session_scope() as session:
        brands = session.execute(
            select(Brand.id, Brand.name)
            .where(Brand.deleted_at.is_(None))
            .order_by(Brand.name)
        ).all()
        channels = session.execute(
            select(PriceObservation.channel)
            .where(PriceObservation.channel.is_not(None))
            .distinct()
            .order_by(PriceObservation.channel)
        ).all()
        bases = session.execute(
            select(PriceObservation.price_basis)
            .where(PriceObservation.price_basis.is_not(None))
            .distinct()
            .order_by(PriceObservation.price_basis)
        ).all()
        companies = session.execute(
            select(Company.id, Company.name)
            .where(Company.deleted_at.is_(None))
            .order_by(Company.name)
        ).all()
        skus = session.execute(
            select(SKU.id, Brand.name, SKU.gtin, Product.name)
            .join(SKU.product)
            .join(Product.brand)
            .where(SKU.deleted_at.is_(None))
            .order_by(Brand.name, Product.name)
        ).all()
    return {
        "brands": [{"label": name, "value": id_} for id_, name in brands],
        "channels": _build_channel_options([row[0] for row in channels if row[0]]),
        "channel_default": CHANNEL_DEFAULT,
        "basis": _build_basis_options([row[0] for row in bases if row[0]]),
        "companies": [{"label": name, "value": id_} for id_, name in companies],
        "skus": [
            {
                "label": f"{brand} - {product}" + (f" (GTIN: {gtin})" if gtin else ""),
                "value": sku_id,
            }
            for sku_id, brand, gtin, product in skus
        ],
    }


def _build_channel_options(existing: List[str]) -> List[dict]:
    seen: set[str] = set()
    options: List[dict] = []
    for value in existing:
        label = CHANNEL_LABELS.get(value, value.replace("_", " ").title())
        options.append({"label": label, "value": value})
        seen.add(value)
    for value, label in CHANNEL_LABELS.items():
        if value not in seen:
            options.append({"label": label, "value": value})
            seen.add(value)
    if not options:
        options = [
            {"label": label, "value": value} for value, label in CHANNEL_LABELS.items()
        ]
    return options


def _build_basis_options(existing: List[str]) -> List[dict]:
    seen: set[str] = set()
    options: List[dict] = []
    basis_lookup = {opt["value"]: opt["label"] for opt in BASIS_OPTIONS}
    for value in existing:
        label = basis_lookup.get(value, value.title())
        options.append({"label": label, "value": value})
        seen.add(value)
    for opt in BASIS_OPTIONS:
        if opt["value"] not in seen:
            options.append(opt)
            seen.add(opt["value"])
    if not options:
        options = BASIS_OPTIONS.copy()
    return options


def _build_filters(
    brand_ids, channels, bases, start_date, end_date
) -> ObservationFilters:
    return ObservationFilters(
        brand_ids=brand_ids or [],
        channels=channels or [],
        price_bases=bases or [],
        start_dt=datetime.fromisoformat(start_date) if start_date else None,
        end_dt=datetime.fromisoformat(end_date) if end_date else None,
    )


def _filters_from_store(data: Dict) -> ObservationFilters:
    start = data.get("start_dt")
    end = data.get("end_dt")
    return ObservationFilters(
        brand_ids=data.get("brand_ids", []),
        channels=data.get("channels", []),
        price_bases=data.get("price_bases", []),
        start_dt=datetime.fromisoformat(start) if start else None,
        end_dt=datetime.fromisoformat(end) if end else None,
    )


def _rows_to_dataframe(rows: List[dict]):
    import pandas as pd  # local import to keep optional dependency scoped

    return pd.DataFrame(rows)


def _add_modal(options: Dict[str, List[dict]]) -> dbc.Modal:
    return modal_form(
        ADD_MODAL_ID,
        "Add Observation",
        [
            dbc.Alert(id="observations-add-feedback", is_open=False, className="mb-3"),
            dbc.Select(
                id="observations-add-sku",
                options=options["skus"],
                placeholder="Select SKU",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Select(
                            id="observations-add-company",
                            options=options["companies"],
                            placeholder="Select Company",
                        ),
                        md=6,
                        className="mt-3",
                    ),
                    dbc.Col(
                        dbc.Select(
                            id="observations-add-location",
                            options=[],
                            placeholder="Select Location",
                        ),
                        md=6,
                        className="mt-3",
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="observations-add-price",
                            type="number",
                            placeholder="Price inc GST",
                        ),
                        md=6,
                        className="mt-3",
                    ),
                    dbc.Col(
                        dbc.Input(
                            id="observations-add-price-ex",
                            type="number",
                            placeholder="Price ex GST",
                        ),
                        md=6,
                        className="mt-3",
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="observations-add-gst",
                            type="number",
                            step=0.01,
                            value=0.10,
                            placeholder="GST Rate",
                        ),
                        md=4,
                        className="mt-3",
                    ),
                    dbc.Col(
                        dbc.Input(
                            id="observations-add-carton",
                            type="number",
                            placeholder="Carton Units",
                        ),
                        md=4,
                        className="mt-3",
                    ),
                    dbc.Col(
                        dbc.RadioItems(
                            id="observations-add-basis",
                            options=BASIS_OPTIONS,
                            value="unit",
                            inline=True,
                        ),
                        md=4,
                        className="mt-4",
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Select(
                            id="observations-add-channel",
                            options=options["channels"],
                            placeholder="Channel",
                            value=options.get("channel_default"),
                        ),
                        md=6,
                        className="mt-3",
                    ),
                    dbc.Col(
                        dbc.Select(
                            id="observations-add-context",
                            options=[
                                {"label": label.title(), "value": label}
                                for label in [
                                    "shelf",
                                    "promo",
                                    "member",
                                    "online",
                                    "quote",
                                    "other",
                                ]
                            ],
                            placeholder="Price Context",
                        ),
                        md=6,
                        className="mt-3",
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Select(
                            id="observations-add-availability",
                            options=[
                                {"label": label.title(), "value": label}
                                for label in [
                                    "in_stock",
                                    "low_stock",
                                    "out_of_stock",
                                    "unknown",
                                ]
                            ],
                            placeholder="Availability",
                        ),
                        md=6,
                        className="mt-3",
                    ),
                    dbc.Col(
                        dcc.DatePickerSingle(
                            id="observations-add-date", display_format="YYYY-MM-DD"
                        ),
                        md=6,
                        className="mt-3",
                    ),
                ]
            ),
            dbc.Select(
                id="observations-add-source",
                options=[
                    {"label": label.title(), "value": label}
                    for label in [
                        "web",
                        "in_store",
                        "brochure",
                        "email",
                        "verbal",
                        "receipt",
                        "photo",
                    ]
                ],
                placeholder="Source Type",
                className="mt-3",
            ),
            dbc.Input(
                id="observations-add-url", placeholder="Source URL", className="mt-3"
            ),
            dbc.Textarea(
                id="observations-add-note", placeholder="Notes", className="mt-3"
            ),
        ],
        submit_id="observations-add-submit",
        close_id="observations-add-cancel",
    )


def _create_observation(payload: Dict) -> bool:
    try:
        observation_dt = datetime.fromisoformat(payload["observation_dt"])
    except Exception:  # pragma: no cover - validation guard
        return False
    with session_scope() as session:
        sku = session.get(SKU, payload["sku_id"])
        company = session.get(Company, payload["company_id"])
        if not sku or not company:
            session.rollback()
            return False
        if payload.get("is_pack_price") and (
            not sku.pack_assignment or not sku.pack_assignment.pack_spec
        ):
            session.rollback()
            return False
        location = (
            session.get(Location, payload["location_id"])
            if payload.get("location_id")
            else None
        )
        normalized = normalize_price(
            sku=sku,
            price_ex_gst_raw=_to_decimal(payload.get("price_ex_gst_raw")),
            price_inc_gst_raw=_to_decimal(payload.get("price_inc_gst_raw")),
            gst_rate=_to_decimal(payload.get("gst_rate")) or Decimal("0.10"),
            carton_units=_to_int(payload.get("carton_units"))
            if payload.get("is_carton_price")
            else None,
            is_carton_price=payload.get("is_carton_price", False),
            is_pack_price=payload.get("is_pack_price", False),
        )
        observation = PriceObservation(
            sku=sku,
            company=company,
            location=location,
            channel=payload["channel"],
            price_context=payload["price_context"],
            promo_name=None,
            availability=payload["availability"],
            price_ex_gst_raw=_to_decimal(payload.get("price_ex_gst_raw")),
            price_inc_gst_raw=_to_decimal(payload.get("price_inc_gst_raw")),
            gst_rate=_to_decimal(payload.get("gst_rate")) or Decimal("0.10"),
            currency="AUD",
            is_carton_price=payload.get("is_carton_price", False),
            carton_units=_to_int(payload.get("carton_units")),
            price_ex_gst_norm=normalized.price_ex_gst,
            price_inc_gst_norm=normalized.price_inc_gst,
            unit_price_inc_gst=normalized.unit_price_inc_gst,
            pack_price_inc_gst=normalized.pack_price_inc_gst,
            carton_price_inc_gst=normalized.carton_price_inc_gst,
            price_per_litre=normalized.price_per_litre,
            price_per_unit_pure_alcohol=normalized.price_per_unit_pure_alcohol,
            standard_drinks=normalized.standard_drinks,
            price_basis=normalized.price_basis,
            gp_unit_abs=normalized.gp_unit_abs,
            gp_unit_pct=normalized.gp_unit_pct,
            gp_pack_abs=normalized.gp_pack_abs,
            gp_pack_pct=normalized.gp_pack_pct,
            gp_carton_abs=normalized.gp_carton_abs,
            gp_carton_pct=normalized.gp_carton_pct,
            observation_dt=observation_dt,
            source_type=payload["source_type"],
            source_url=payload.get("source_url"),
            source_note=payload.get("source_note"),
        )
        apply_hash_to_observation(observation)
        exists = session.execute(
            select(PriceObservation.id).where(
                PriceObservation.hash_key == observation.hash_key
            )
        ).scalar_one_or_none()
        if exists:
            session.rollback()
            return False
        session.add(observation)
        session.commit()
        return True


def _to_decimal(value) -> Optional[Decimal]:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (TypeError, ValueError):  # pragma: no cover
        return None


def _to_int(value) -> Optional[int]:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):  # pragma: no cover
        return None
