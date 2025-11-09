from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import List

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ...models import (
    SKU,
    Brand,
    Product,
    PurchasePrice,
)
from ...models.product import PRODUCT_FORMATS, PRODUCT_SPIRITS, categories_for
from ...services.costs import create_purchase_price
from ...services.db import session_scope
from ..components import data_table, loading_wrapper, modal_form
from .skus import _load_sku_options  # reuse existing helper for SKU labels

PURCHASE_PRICE_TABLE_ID = "purchase-table-prices"
REFRESH_STORE_ID = "purchase-price-refresh"
SPIRIT_FILTER_ID = "purchase-filter-spirit"
FORMAT_FILTER_ID = "purchase-filter-format"
SPIRIT_OPTIONS = [
    {"label": spirit.title(), "value": spirit} for spirit in PRODUCT_SPIRITS
]
FORMAT_OPTIONS = [
    {"label": "RTD" if fmt == "rtd" else fmt.title(), "value": fmt}
    for fmt in PRODUCT_FORMATS
]


def layout() -> dbc.Container:
    sku_options_full = _load_sku_options(include_deleted=True)
    price_options_full = _load_purchase_price_options(include_deleted=True)
    initial_data = _load_purchase_price_table_data()
    return dbc.Container(
        [
            dcc.Store(id=REFRESH_STORE_ID, data={"ts": datetime.utcnow().isoformat()}),
            html.H2("Purchase Prices", className="mb-4"),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Filters", className="fw-semibold"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Checklist(
                                        id=SPIRIT_FILTER_ID,
                                        options=SPIRIT_OPTIONS,
                                        value=[],
                                        inline=True,
                                    ),
                                    md=6,
                                ),
                                dbc.Col(
                                    dbc.Checklist(
                                        id=FORMAT_FILTER_ID,
                                        options=FORMAT_OPTIONS,
                                        value=[],
                                        inline=True,
                                    ),
                                    md=6,
                                ),
                            ],
                            className="g-3",
                        ),
                    ]
                ),
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Add Purchase Price",
                            id="purchase-open-add",
                            color="primary",
                            className="mb-2",
                        ),
                        md="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Edit Purchase Price",
                            id="purchase-open-edit",
                            color="secondary",
                            outline=True,
                            className="mb-2",
                        ),
                        md="auto",
                    ),
                ],
                className="g-2 mb-3",
            ),
            loading_wrapper(
                "purchase-table-wrapper",
                data_table(
                    PURCHASE_PRICE_TABLE_ID,
                    columns=[
                        {"id": "category", "name": "Category"},
                        {"id": "sku", "name": "SKU"},
                        {"id": "price_type", "name": "Type"},
                        {"id": "effective_date", "name": "Effective"},
                        {"id": "unit_price", "name": "Unit Price"},
                        {"id": "pack_price", "name": "Pack Price"},
                        {"id": "carton_price", "name": "Carton Price"},
                        {"id": "currency", "name": "Currency"},
                    ],
                    data=initial_data,
                    paginated=True,
                    page_size=25,
                ),
            ),
            _purchase_price_modal(sku_options_full),
            _edit_purchase_price_modal(price_options_full, sku_options_full),
            dbc.Toast(
                id="purchase-toast",
                header="Purchase Prices",
                is_open=False,
                duration=4000,
                icon="success",
                className="position-fixed top-0 end-0 m-3",
            ),
        ],
        fluid=True,
    )


def register_callbacks(app):  # pragma: no cover - Dash wiring
    @app.callback(
        Output(PURCHASE_PRICE_TABLE_ID, "data"),
        Output("purchase-edit-select", "options"),
        Input(REFRESH_STORE_ID, "data"),
        Input(SPIRIT_FILTER_ID, "value"),
        Input(FORMAT_FILTER_ID, "value"),
    )
    def refresh_table(_refresh, spirits, formats):
        categories = (
            categories_for(spirits or None, formats or None)
            if (spirits or formats)
            else None
        )
        data = _load_purchase_price_table_data(spirits, formats)
        options = _load_purchase_price_options(
            include_deleted=True, categories=categories
        )
        return data, options

    _modal_toggle(app, "purchase-open-add", "purchase-add-cancel", "purchase-add-modal")
    _modal_toggle(
        app, "purchase-open-edit", "purchase-edit-cancel", "purchase-edit-modal"
    )

    @app.callback(
        Output("purchase-edit-sku", "value"),
        Output("purchase-edit-type", "value"),
        Output("purchase-edit-effective", "date"),
        Output("purchase-edit-unit", "value"),
        Output("purchase-edit-pack", "value"),
        Output("purchase-edit-carton", "value"),
        Output("purchase-edit-currency", "value"),
        Output("purchase-edit-notes", "value"),
        Output("purchase-edit-status", "children"),
        Input("purchase-edit-select", "value"),
    )
    def load_purchase_details(price_id):
        if not price_id:
            return None, "known", None, None, None, None, "AUD", "", ""
        with session_scope() as session:
            price = session.get(PurchasePrice, price_id)
            if not price:
                return (
                    None,
                    "known",
                    None,
                    None,
                    None,
                    None,
                    "AUD",
                    "",
                    "Selected purchase price could not be found.",
                )
            return (
                price.sku_id,
                price.cost_type,
                price.effective_date.isoformat(),
                float(price.cost_per_unit) if price.cost_per_unit is not None else None,
                float(price.cost_per_pack) if price.cost_per_pack is not None else None,
                float(price.cost_per_carton)
                if price.cost_per_carton is not None
                else None,
                price.cost_currency or "AUD",
                price.notes or "",
                _format_status(price.deleted_at),
            )

    @app.callback(
        Output("purchase-toast", "children", allow_duplicate=True),
        Output("purchase-toast", "icon", allow_duplicate=True),
        Output("purchase-toast", "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Output("purchase-edit-modal", "is_open", allow_duplicate=True),
        Output("purchase-edit-status", "children", allow_duplicate=True),
        Input("purchase-edit-save", "n_clicks"),
        Input("purchase-edit-archive", "n_clicks"),
        Input("purchase-edit-restore", "n_clicks"),
        State("purchase-edit-select", "value"),
        State("purchase-edit-sku", "value"),
        State("purchase-edit-type", "value"),
        State("purchase-edit-effective", "date"),
        State("purchase-edit-unit", "value"),
        State("purchase-edit-pack", "value"),
        State("purchase-edit-carton", "value"),
        State("purchase-edit-currency", "value"),
        State("purchase-edit-notes", "value"),
        prevent_initial_call=True,
    )
    def handle_purchase_updates(
        save_clicks,
        archive_clicks,
        restore_clicks,
        price_id,
        sku_id,
        price_type,
        effective_date,
        unit_price,
        pack_price,
        carton_price,
        currency,
        notes,
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update, no_update, no_update
        action = ctx.triggered[0]["prop_id"].split(".")[0]
        if not price_id:
            return (
                "Select a purchase price first.",
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )
        with session_scope() as session:
            price = session.get(PurchasePrice, price_id)
            if not price:
                return (
                    "Purchase price not found.",
                    "danger",
                    True,
                    no_update,
                    no_update,
                    "Selected purchase price could not be found.",
                )
            if action == "purchase-edit-save":
                if not (sku_id and price_type and effective_date):
                    return (
                        "SKU, price type, and effective date are required.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(price.deleted_at),
                    )
                session_sku = session.get(SKU, sku_id)
                if not session_sku:
                    return (
                        "SKU not found.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(price.deleted_at),
                    )
                price_type_value = str(price_type).lower()
                if price_type_value not in {"known", "estimated"}:
                    return (
                        "Invalid price type.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(price.deleted_at),
                    )
                try:
                    effective = date.fromisoformat(effective_date)
                except ValueError:
                    return (
                        "Invalid effective date.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(price.deleted_at),
                    )
                try:
                    unit_dec = _optional_decimal_field(unit_price)
                    pack_dec = _optional_decimal_field(pack_price)
                    carton_dec = _optional_decimal_field(carton_price)
                except ValueError as exc:
                    return (
                        str(exc),
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(price.deleted_at),
                    )
                currency_value = (currency or "AUD").strip().upper()
                price.sku_id = sku_id
                price.cost_type = price_type_value
                price.effective_date = effective
                price.cost_currency = currency_value
                price.cost_per_unit = unit_dec
                price.cost_per_pack = pack_dec
                price.cost_per_carton = carton_dec
                price.notes = (notes or "").strip() or None
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    return (
                        "Update failed due to a constraint.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(price.deleted_at),
                    )
                return (
                    "Purchase price updated.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(price.deleted_at),
                )
            if action == "purchase-edit-archive":
                price.deleted_at = _utcnow()
                session.commit()
                return (
                    "Purchase price archived.",
                    "warning",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(price.deleted_at),
                )
            if action == "purchase-edit-restore":
                price.deleted_at = None
                session.commit()
                return (
                    "Purchase price restored.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(price.deleted_at),
                )
        return no_update, no_update, no_update, no_update, no_update, no_update

    @app.callback(
        Output("purchase-toast", "children", allow_duplicate=True),
        Output("purchase-toast", "icon", allow_duplicate=True),
        Output("purchase-toast", "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Input("purchase-add-submit", "n_clicks"),
        State("purchase-add-sku", "value"),
        State("purchase-add-type", "value"),
        State("purchase-add-unit", "value"),
        State("purchase-add-pack", "value"),
        State("purchase-add-carton", "value"),
        State("purchase-add-currency", "value"),
        State("purchase-add-effective", "date"),
        State("purchase-add-notes", "value"),
        prevent_initial_call=True,
    )
    def add_purchase_price(
        n_clicks,
        sku_id,
        price_type,
        unit_price,
        pack_price,
        carton_price,
        currency,
        effective_date,
        notes,
    ):
        if not n_clicks:
            return no_update, no_update, no_update, no_update
        if not (sku_id and price_type and effective_date):
            return (
                "SKU, price type, and effective date are required",
                "danger",
                True,
                no_update,
            )
        try:
            effective = date.fromisoformat(effective_date)
        except ValueError:
            return ("Invalid effective date", "danger", True, no_update)
        try:
            unit_dec = _optional_decimal_field(unit_price)
            pack_dec = _optional_decimal_field(pack_price)
            carton_dec = _optional_decimal_field(carton_price)
        except ValueError as exc:
            return (str(exc), "danger", True, no_update)
        currency_value = (currency or "AUD").strip().upper()
        with session_scope() as session:
            sku = session.get(SKU, sku_id)
            if not sku:
                return ("SKU not found", "danger", True, no_update)
            create_purchase_price(
                session,
                sku_id=sku.id,
                cost_type=price_type,
                effective_date=effective,
                cost_currency=currency_value,
                cost_per_unit=unit_dec,
                cost_per_pack=pack_dec,
                cost_per_carton=carton_dec,
                notes=(notes or "").strip() or None,
            )
            session.commit()
        return (
            "Purchase price saved",
            "success",
            True,
            {"ts": datetime.utcnow().isoformat()},
        )


def _load_purchase_price_table_data(
    spirits: List[str] | None = None, formats: List[str] | None = None
) -> List[dict]:
    category_filters = (
        categories_for(spirits or None, formats or None) if (spirits or formats) else []
    )
    with session_scope() as session:
        stmt = (
            select(
                PurchasePrice,
                SKU.gtin,
                Brand.name,
                Product.name,
                Product.category,
            )
            .join(PurchasePrice.sku)
            .join(SKU.product)
            .join(Product.brand)
            .where(
                PurchasePrice.deleted_at.is_(None),
                SKU.deleted_at.is_(None),
                Brand.deleted_at.is_(None),
            )
            .order_by(
                Brand.name,
                Product.name,
                PurchasePrice.effective_date.desc(),
                PurchasePrice.cost_type.desc(),
            )
        )
        if category_filters:
            stmt = stmt.where(Product.category.in_(category_filters))
        rows = session.execute(stmt).all()
    results: List[dict] = []
    for price, sku_gtin, brand_name, product_name, category in rows:
        label = f"{brand_name} - {product_name}"
        if sku_gtin:
            label += f" ({sku_gtin})"
        results.append(
            {
                "category": _format_category_label(category),
                "sku": label,
                "price_type": price.cost_type.title(),
                "effective_date": price.effective_date.isoformat(),
                "unit_price": _format_money(price.cost_per_unit),
                "pack_price": _format_money(price.cost_per_pack),
                "carton_price": _format_money(price.cost_per_carton),
                "currency": price.cost_currency,
            }
        )
    return results


def _load_purchase_price_options(
    include_deleted: bool = False, categories: List[str] | None = None
) -> List[dict]:
    with session_scope() as session:
        stmt = (
            select(
                PurchasePrice,
                SKU.gtin,
                Brand.name,
                Product.name,
            )
            .join(PurchasePrice.sku)
            .join(SKU.product)
            .join(Product.brand)
            .order_by(
                Brand.name,
                Product.name,
                PurchasePrice.cost_type,
                PurchasePrice.effective_date.desc(),
            )
        )
        if not include_deleted:
            stmt = stmt.where(
                PurchasePrice.deleted_at.is_(None),
                Brand.deleted_at.is_(None),
                Product.deleted_at.is_(None),
            )
        if categories:
            stmt = stmt.where(Product.category.in_(categories))
        rows = session.execute(stmt).all()
    options: List[dict] = []
    for price, sku_gtin, brand_name, product_name in rows:
        label_parts = [
            brand_name,
            product_name,
            price.cost_type.capitalize(),
            price.effective_date.isoformat(),
        ]
        label = " - ".join(label_parts)
        if sku_gtin:
            label += f" [{sku_gtin}]"
        if price.deleted_at:
            label += " (archived)"
        options.append({"label": label, "value": price.id, "sku_id": price.sku_id})
    return options


def _purchase_price_modal(sku_options: List[dict]) -> dbc.Modal:
    body = [
        dbc.Select(
            id="purchase-add-sku", options=sku_options, placeholder="Select SKU"
        ),
        dbc.RadioItems(
            id="purchase-add-type",
            options=[
                {"label": "Known", "value": "known"},
                {"label": "Estimated", "value": "estimated"},
            ],
            value="known",
            inline=True,
            className="mt-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(
                        id="purchase-add-unit",
                        type="number",
                        step=0.0001,
                        placeholder="Cost per unit",
                    ),
                    md=4,
                    className="mt-3",
                ),
                dbc.Col(
                    dbc.Input(
                        id="purchase-add-pack",
                        type="number",
                        step=0.0001,
                        placeholder="Cost per pack",
                    ),
                    md=4,
                    className="mt-3",
                ),
                dbc.Col(
                    dbc.Input(
                        id="purchase-add-carton",
                        type="number",
                        step=0.0001,
                        placeholder="Cost per carton",
                    ),
                    md=4,
                    className="mt-3",
                ),
            ],
            className="g-2",
        ),
        dbc.Input(
            id="purchase-add-currency",
            value="AUD",
            placeholder="Currency",
            className="mt-3",
        ),
        dcc.DatePickerSingle(
            id="purchase-add-effective",
            display_format="YYYY-MM-DD",
            className="mt-3",
            date=date.today(),
        ),
        dbc.Textarea(id="purchase-add-notes", placeholder="Notes", className="mt-3"),
    ]
    return modal_form(
        "purchase-add-modal",
        "Add Purchase Price",
        body,
        submit_id="purchase-add-submit",
        close_id="purchase-add-cancel",
        size="md",
    )


def _edit_purchase_price_modal(
    price_options: List[dict], sku_options: List[dict]
) -> dbc.Modal:
    return dbc.Modal(
        [
            dbc.ModalHeader("Edit Purchase Price"),
            dbc.ModalBody(
                [
                    dbc.Select(
                        id="purchase-edit-select",
                        options=price_options,
                        placeholder="Select a purchase price",
                        className="mb-3",
                    ),
                    dbc.Select(
                        id="purchase-edit-sku",
                        options=sku_options,
                        placeholder="Select SKU",
                        className="mb-3",
                    ),
                    dbc.RadioItems(
                        id="purchase-edit-type",
                        options=[
                            {"label": "Known", "value": "known"},
                            {"label": "Estimated", "value": "estimated"},
                        ],
                        value="known",
                        inline=True,
                        className="mb-3",
                    ),
                    dcc.DatePickerSingle(
                        id="purchase-edit-effective", display_format="YYYY-MM-DD"
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(
                                    id="purchase-edit-unit",
                                    type="number",
                                    step="0.0001",
                                    placeholder="Cost per unit",
                                ),
                                md=4,
                                className="mt-3",
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="purchase-edit-pack",
                                    type="number",
                                    step="0.0001",
                                    placeholder="Cost per pack",
                                ),
                                md=4,
                                className="mt-3",
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="purchase-edit-carton",
                                    type="number",
                                    step="0.0001",
                                    placeholder="Cost per carton",
                                ),
                                md=4,
                                className="mt-3",
                            ),
                        ]
                    ),
                    dbc.Input(
                        id="purchase-edit-currency",
                        value="AUD",
                        placeholder="Currency",
                        className="mt-3",
                    ),
                    dbc.Textarea(
                        id="purchase-edit-notes", placeholder="Notes", className="mt-3"
                    ),
                    html.Div(
                        id="purchase-edit-status", className="text-muted small mt-2"
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="purchase-edit-cancel",
                        color="secondary",
                        className="me-2",
                    ),
                    dbc.Button(
                        "Archive",
                        id="purchase-edit-archive",
                        color="danger",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button(
                        "Restore",
                        id="purchase-edit-restore",
                        color="warning",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button("Save", id="purchase-edit-save", color="primary"),
                ]
            ),
        ],
        id="purchase-edit-modal",
        size="lg",
        backdrop="static",
    )


def _format_money(value) -> str:
    if value is None:
        return ""
    return f"{Decimal(value):.4f}"


def _format_category_label(category: str) -> str:
    if not category:
        return ""
    parts = category.split("_", 1)
    if len(parts) == 2:
        spirit, format_part = parts
        return f"{spirit.title()} {format_part.upper() if format_part == 'rtd' else format_part.title()}"
    return category.replace("_", " ").title()


def _optional_decimal_field(raw_value):
    if raw_value is None:
        return None
    raw = str(raw_value).strip()
    if not raw:
        return None
    try:
        return Decimal(raw).quantize(Decimal("0.0001"))
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid decimal value: {raw}")


def _format_status(deleted_at) -> str:
    if deleted_at:
        try:
            display = deleted_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        except AttributeError:
            display = str(deleted_at)
        return f"Status: Archived ({display})"
    return "Status: Active"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _modal_toggle(app, open_id, close_id, modal_id):
    @app.callback(
        Output(modal_id, "is_open", allow_duplicate=True),
        Input(open_id, "n_clicks"),
        Input(close_id, "n_clicks"),
        State(modal_id, "is_open"),
        prevent_initial_call=True,
    )
    def toggle(open_clicks, close_clicks, is_open):
        if not (open_clicks or close_clicks):
            return is_open
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == open_id:
            return True
        return False


__all__ = ["layout", "register_callbacks"]
