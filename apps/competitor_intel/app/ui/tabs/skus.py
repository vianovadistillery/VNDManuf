from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from ...models import (
    SKU,
    Brand,
    CartonSpec,
    Company,
    PackageSpec,
    PackSpec,
    PriceObservation,
    Product,
    SKUCarton,
    SKUPack,
)
from ...models.product import PRODUCT_CATEGORY_DETAILS
from ...services.db import session_scope
from ..components import data_table, loading_wrapper, modal_form

BRAND_TABLE_ID = "skus-table-brands"
PRODUCT_TABLE_ID = "skus-table-products"
PACKAGE_TABLE_ID = "skus-table-packages"
SKU_TABLE_ID = "skus-table-skus"
CARTON_TABLE_ID = "skus-table-cartons"
PACK_TABLE_ID = "skus-table-packs"

REFRESH_STORE_ID = "skus-refresh-store"

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
ALLOWED_CAN_FORM_FACTORS = {"slim", "sleek", "classic"}


def _accordion_header_actions(title: str, buttons: List[dbc.Button]) -> html.Div:
    return html.Div(
        [
            html.Div(title, className="fw-semibold"),
            dbc.ButtonGroup(buttons, className="ms-auto"),
        ],
        className="d-flex align-items-center justify-content-between mb-3",
    )


def _normalize_category_value(category: str | None) -> str:
    if not category:
        return ""
    if category == "rtd_can":
        return "gin_rtd"
    return category


def _format_category_label(category: str | None) -> str:
    normalized = _normalize_category_value(category)
    detail = PRODUCT_CATEGORY_DETAILS.get(normalized)
    if detail:
        spirit = detail["spirit"].title()
        fmt = detail["format"]
        format_label = "RTD" if fmt == "rtd" else fmt.title()
        return f"{spirit} {format_label}"
    if normalized:
        return normalized.replace("_", " ").title()
    return ""


def _product_modal() -> dbc.Modal:
    options = _load_filter_options()
    body = [
        dbc.Select(
            id="skus-add-product-brand",
            options=options["brands"],
            placeholder="Select brand",
        ),
        dbc.Input(
            id="skus-add-product-name",
            placeholder="Product name",
            className="mt-3",
        ),
        dbc.Select(
            id="skus-add-product-category",
            options=[
                {"label": "Gin Bottle", "value": "gin_bottle"},
                {"label": "Gin RTD", "value": "gin_rtd"},
                {"label": "Vodka Bottle", "value": "vodka_bottle"},
                {"label": "Vodka RTD", "value": "vodka_rtd"},
            ],
            placeholder="Category",
            className="mt-3",
        ),
        dbc.Input(
            id="skus-add-product-abv",
            type="number",
            step=0.1,
            placeholder="ABV %",
            className="mt-3",
        ),
    ]
    return modal_form(
        "skus-add-product-modal",
        "Add Product",
        body,
        submit_id="skus-add-product-submit",
        close_id="skus-add-product-cancel",
        size="md",
    )


def _package_modal() -> dbc.Modal:
    body = [
        dbc.RadioItems(
            id="skus-add-package-type",
            options=[
                {"label": "Bottle", "value": "bottle"},
                {"label": "Can", "value": "can"},
            ],
            value="bottle",
            inline=True,
        ),
        dbc.Input(
            id="skus-add-package-volume",
            type="number",
            placeholder="Container volume (mL)",
            className="mt-3",
        ),
        dbc.Select(
            id="skus-add-package-form",
            options=[
                {"label": "Slim", "value": "slim"},
                {"label": "Sleek", "value": "sleek"},
                {"label": "Classic", "value": "classic"},
            ],
            placeholder="Can form factor",
            className="mt-3",
        ),
    ]
    return modal_form(
        "skus-add-package-modal",
        "Add Package Spec",
        body,
        submit_id="skus-add-package-submit",
        close_id="skus-add-package-cancel",
        size="md",
    )


def _sku_modal() -> dbc.Modal:
    options = _load_filter_options()
    body = [
        dbc.Select(
            id="skus-add-sku-product",
            options=options["products"],
            placeholder="Select product",
        ),
        dbc.Select(
            id="skus-add-sku-package",
            options=options["packages"],
            placeholder="Select package spec",
            className="mt-3",
        ),
        dbc.Input(
            id="skus-add-sku-gtin",
            placeholder="SKU GTIN",
            className="mt-3",
        ),
        dbc.Checklist(
            id="skus-add-sku-active",
            options=[{"label": "Active", "value": 1}],
            value=[1],
            className="mt-3",
            switch=True,
        ),
        dbc.Select(
            id="skus-add-sku-carton",
            options=options["cartons"],
            placeholder="Link carton spec (optional)",
            className="mt-3",
        ),
    ]
    return modal_form(
        "skus-add-sku-modal",
        "Add SKU",
        body,
        submit_id="skus-add-sku-submit",
        close_id="skus-add-sku-cancel",
        size="md",
    )


def _pack_modal() -> dbc.Modal:
    options = _load_filter_options()
    body = [
        dbc.Select(
            id="skus-add-pack-package",
            options=options["packages"],
            placeholder="Select package spec",
        ),
        dbc.Input(
            id="skus-add-pack-units",
            type="number",
            placeholder="Units per pack",
            className="mt-3",
        ),
        dbc.Input(
            id="skus-add-pack-gtin",
            placeholder="Pack GTIN",
            className="mt-3",
        ),
        dbc.Textarea(
            id="skus-add-pack-notes",
            placeholder="Notes",
            className="mt-3",
        ),
    ]
    return modal_form(
        "skus-add-pack-modal",
        "Add Pack Spec",
        body,
        submit_id="skus-add-pack-submit",
        close_id="skus-add-pack-cancel",
        size="md",
    )


def _carton_modal() -> dbc.Modal:
    options = _load_filter_options()
    body = [
        dbc.RadioItems(
            id="skus-add-carton-mode",
            options=[
                {"label": "Unit carton", "value": "unit"},
                {"label": "Pack carton", "value": "pack"},
            ],
            value="unit",
            inline=True,
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Select(
                        id="skus-add-carton-package",
                        options=options["packages"],
                        placeholder="Package spec (unit cartons)",
                    ),
                    md=6,
                ),
                dbc.Col(
                    dbc.Select(
                        id="skus-add-carton-pack",
                        options=options["packs"],
                        placeholder="Pack spec (pack cartons)",
                    ),
                    md=6,
                ),
            ],
            className="mt-3 g-2",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(
                        id="skus-add-carton-units",
                        type="number",
                        placeholder="Units per carton",
                    ),
                    md=6,
                ),
                dbc.Col(
                    dbc.Input(
                        id="skus-add-carton-pack-count",
                        type="number",
                        placeholder="Pack count",
                    ),
                    md=6,
                ),
            ],
            className="mt-3 g-2",
        ),
        dbc.Input(
            id="skus-add-carton-gtin",
            placeholder="Carton GTIN",
            className="mt-3",
        ),
        dbc.Textarea(
            id="skus-add-carton-notes",
            placeholder="Notes",
            className="mt-3",
        ),
    ]
    return modal_form(
        "skus-add-carton-modal",
        "Add Carton Spec",
        body,
        submit_id="skus-add-carton-submit",
        close_id="skus-add-carton-cancel",
        size="md",
    )


def layout() -> dbc.Container:
    data = _load_table_data()
    brand_options_full = _load_brand_options(include_deleted=True)
    product_options_full = _load_product_options(include_deleted=True)
    package_options_full = _load_package_options(include_deleted=True)
    sku_options_full = _load_sku_options(include_deleted=True)
    pack_options_full = _load_pack_options(include_deleted=True)
    carton_options_full = _load_carton_options(include_deleted=True)
    return dbc.Container(
        [
            dcc.Store(id=REFRESH_STORE_ID, data={"ts": datetime.utcnow().isoformat()}),
            html.H2("Catalog Management", className="mb-4"),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            _accordion_header_actions(
                                "Brands",
                                [
                                    dbc.Button(
                                        "Add",
                                        id="skus-open-add-brand",
                                        color="primary",
                                        size="sm",
                                    ),
                                    dbc.Button(
                                        "Edit",
                                        id="skus-open-edit-brand",
                                        color="secondary",
                                        outline=True,
                                        size="sm",
                                    ),
                                ],
                            ),
                            loading_wrapper(
                                "skus-brands-wrapper",
                                data_table(
                                    BRAND_TABLE_ID,
                                    columns=[
                                        {"id": "name", "name": "Name"},
                                        {"id": "owner_company", "name": "Owner"},
                                        {"id": "product_count", "name": "Products"},
                                    ],
                                    data=data["brands"],
                                    paginated=True,
                                    page_size=25,
                                ),
                            ),
                        ],
                        title="Brands",
                    ),
                    dbc.AccordionItem(
                        [
                            _accordion_header_actions(
                                "Products",
                                [
                                    dbc.Button(
                                        "Add",
                                        id="skus-open-add-product",
                                        color="primary",
                                        size="sm",
                                    ),
                                    dbc.Button(
                                        "Edit",
                                        id="skus-open-edit-product",
                                        color="secondary",
                                        outline=True,
                                        size="sm",
                                    ),
                                ],
                            ),
                            loading_wrapper(
                                "skus-products-wrapper",
                                data_table(
                                    PRODUCT_TABLE_ID,
                                    columns=[
                                        {"id": "name", "name": "Product"},
                                        {"id": "brand", "name": "Brand"},
                                        {"id": "category", "name": "Category"},
                                        {"id": "abv_percent", "name": "ABV %"},
                                    ],
                                    data=data["products"],
                                    paginated=True,
                                    page_size=25,
                                ),
                            ),
                        ],
                        title="Products",
                    ),
                    dbc.AccordionItem(
                        [
                            _accordion_header_actions(
                                "Package Specs",
                                [
                                    dbc.Button(
                                        "Add",
                                        id="skus-open-add-package",
                                        color="primary",
                                        size="sm",
                                    ),
                                    dbc.Button(
                                        "Edit",
                                        id="skus-open-edit-package",
                                        color="secondary",
                                        outline=True,
                                        size="sm",
                                    ),
                                ],
                            ),
                            loading_wrapper(
                                "skus-packages-wrapper",
                                data_table(
                                    PACKAGE_TABLE_ID,
                                    columns=[
                                        {"id": "type", "name": "Type"},
                                        {
                                            "id": "container_ml",
                                            "name": "Container (mL)",
                                        },
                                        {
                                            "id": "can_form_factor",
                                            "name": "Form Factor",
                                        },
                                    ],
                                    data=data["packages"],
                                    paginated=True,
                                    page_size=25,
                                ),
                            ),
                        ],
                        title="Package Specs",
                    ),
                    dbc.AccordionItem(
                        [
                            _accordion_header_actions(
                                "Pack Specs",
                                [
                                    dbc.Button(
                                        "Add",
                                        id="skus-open-add-pack",
                                        color="primary",
                                        size="sm",
                                    ),
                                    dbc.Button(
                                        "Edit",
                                        id="skus-open-edit-pack",
                                        color="secondary",
                                        outline=True,
                                        size="sm",
                                    ),
                                ],
                            ),
                            loading_wrapper(
                                "skus-packs-wrapper",
                                data_table(
                                    PACK_TABLE_ID,
                                    columns=[
                                        {"id": "package", "name": "Package"},
                                        {
                                            "id": "units_per_pack",
                                            "name": "Units per Pack",
                                        },
                                        {"id": "gtin", "name": "Pack GTIN"},
                                        {"id": "sku_count", "name": "Linked SKUs"},
                                        {"id": "carton_variants", "name": "Cartons"},
                                    ],
                                    data=data["packs"],
                                    paginated=True,
                                    page_size=25,
                                ),
                            ),
                        ],
                        title="Pack Specs",
                    ),
                    dbc.AccordionItem(
                        [
                            _accordion_header_actions(
                                "SKUs",
                                [
                                    dbc.Button(
                                        "Add",
                                        id="skus-open-add-sku",
                                        color="primary",
                                        size="sm",
                                    ),
                                    dbc.Button(
                                        "Edit",
                                        id="skus-open-edit-sku",
                                        color="secondary",
                                        outline=True,
                                        size="sm",
                                    ),
                                ],
                            ),
                            loading_wrapper(
                                "skus-skus-wrapper",
                                data_table(
                                    SKU_TABLE_ID,
                                    columns=[
                                        {"id": "product", "name": "Product"},
                                        {"id": "package", "name": "Package"},
                                        {"id": "gtin", "name": "GTIN"},
                                        {"id": "is_active", "name": "Active"},
                                    ],
                                    data=data["skus"],
                                    paginated=True,
                                    page_size=25,
                                ),
                            ),
                        ],
                        title="SKUs",
                    ),
                    dbc.AccordionItem(
                        [
                            _accordion_header_actions(
                                "Carton Specs",
                                [
                                    dbc.Button(
                                        "Add",
                                        id="skus-open-add-carton",
                                        color="primary",
                                        size="sm",
                                    ),
                                    dbc.Button(
                                        "Edit",
                                        id="skus-open-edit-carton",
                                        color="secondary",
                                        outline=True,
                                        size="sm",
                                    ),
                                ],
                            ),
                            loading_wrapper(
                                "skus-cartons-wrapper",
                                data_table(
                                    CARTON_TABLE_ID,
                                    columns=[
                                        {"id": "mode", "name": "Mode"},
                                        {"id": "package_label", "name": "Package Spec"},
                                        {"id": "pack_label", "name": "Pack Spec"},
                                        {"id": "pack_count", "name": "Pack Count"},
                                        {
                                            "id": "units_per_carton",
                                            "name": "Units / Carton",
                                        },
                                        {"id": "gtin", "name": "GTIN"},
                                        {"id": "notes", "name": "Notes"},
                                    ],
                                    data=data["cartons"],
                                    paginated=True,
                                    page_size=25,
                                ),
                            ),
                        ],
                        title="Carton Specs",
                    ),
                ],
                start_collapsed=False,
            ),
            _brand_modal(),
            _edit_brand_modal(brand_options_full),
            _product_modal(),
            _edit_product_modal(brand_options_full, product_options_full),
            _package_modal(),
            _edit_package_modal(package_options_full),
            _sku_modal(),
            _edit_sku_modal(
                product_options_full, package_options_full, sku_options_full
            ),
            _carton_modal(),
            _edit_carton_modal(
                package_options_full, pack_options_full, carton_options_full
            ),
            _pack_modal(),
            _edit_pack_modal(package_options_full, pack_options_full),
            dbc.Toast(
                id="skus-toast",
                header="Catalog",
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
        Output(BRAND_TABLE_ID, "data"),
        Output(PRODUCT_TABLE_ID, "data"),
        Output(PACKAGE_TABLE_ID, "data"),
        Output(SKU_TABLE_ID, "data"),
        Output(PACK_TABLE_ID, "data"),
        Output(CARTON_TABLE_ID, "data"),
        Output("skus-edit-brand-select", "options"),
        Output("skus-edit-product-select", "options"),
        Output("skus-edit-package-select", "options"),
        Output("skus-edit-sku-select", "options"),
        Output("skus-edit-pack-select", "options"),
        Output("skus-edit-carton-select", "options"),
        Input(REFRESH_STORE_ID, "data"),
        prevent_initial_call="initial_duplicate",
    )
    def refresh_tables(_refresh):
        data = _load_table_data()
        return (
            data["brands"],
            data["products"],
            data["packages"],
            data["skus"],
            data["packs"],
            data["cartons"],
            _load_brand_options(include_deleted=True),
            _load_product_options(include_deleted=True),
            _load_package_options(include_deleted=True),
            _load_sku_options(include_deleted=True),
            _load_pack_options(include_deleted=True),
            _load_carton_options(include_deleted=True),
        )

    _register_modal_callbacks(app)


def _register_modal_callbacks(app):
    _modal_toggle(
        app, "skus-open-add-brand", "skus-add-brand-cancel", "skus-add-brand-modal"
    )
    _modal_toggle(
        app, "skus-open-edit-brand", "skus-edit-brand-cancel", "skus-edit-brand-modal"
    )
    _modal_toggle(
        app,
        "skus-open-add-product",
        "skus-add-product-cancel",
        "skus-add-product-modal",
    )
    _modal_toggle(
        app,
        "skus-open-edit-product",
        "skus-edit-product-cancel",
        "skus-edit-product-modal",
    )
    _modal_toggle(
        app,
        "skus-open-add-package",
        "skus-add-package-cancel",
        "skus-add-package-modal",
    )
    _modal_toggle(
        app,
        "skus-open-edit-package",
        "skus-edit-package-cancel",
        "skus-edit-package-modal",
    )
    _modal_toggle(app, "skus-open-add-sku", "skus-add-sku-cancel", "skus-add-sku-modal")
    _modal_toggle(
        app, "skus-open-edit-sku", "skus-edit-sku-cancel", "skus-edit-sku-modal"
    )
    _modal_toggle(
        app, "skus-open-add-carton", "skus-add-carton-cancel", "skus-add-carton-modal"
    )
    _modal_toggle(
        app,
        "skus-open-edit-carton",
        "skus-edit-carton-cancel",
        "skus-edit-carton-modal",
    )
    _modal_toggle(
        app, "skus-open-add-pack", "skus-add-pack-cancel", "skus-add-pack-modal"
    )
    _modal_toggle(
        app, "skus-open-edit-pack", "skus-edit-pack-cancel", "skus-edit-pack-modal"
    )

    @app.callback(
        Output("skus-add-product-brand", "options"),
        Output("skus-add-sku-product", "options"),
        Output("skus-add-sku-package", "options"),
        Output("skus-add-sku-carton", "options"),
        Output("skus-add-pack-package", "options"),
        Output("skus-add-carton-package", "options"),
        Output("skus-add-carton-pack", "options"),
        Output("skus-edit-product-brand", "options"),
        Output("skus-edit-sku-product", "options"),
        Output("skus-edit-sku-package", "options"),
        Output("skus-edit-pack-package", "options"),
        Output("skus-edit-carton-package", "options"),
        Output("skus-edit-carton-pack", "options"),
        Input(REFRESH_STORE_ID, "data"),
        prevent_initial_call="initial_duplicate",
    )
    def refresh_modal_options(_refresh):
        options = _load_filter_options()
        return (
            options["brands"],
            options["products"],
            options["packages"],
            options["cartons"],
            options["packages"],
            options["packages"],
            options["packs"],
            options["brands"],
            options["products"],
            options["packages"],
            options["packages"],
            options["packages"],
            options["packs"],
        )

    @app.callback(
        Output("skus-edit-brand-name", "value"),
        Output("skus-edit-brand-owner", "value"),
        Output("skus-edit-brand-status", "children"),
        Input("skus-edit-brand-select", "value"),
    )
    def load_brand_details(brand_id):
        if not brand_id:
            return "", "", ""
        with session_scope() as session:
            brand = session.get(Brand, brand_id)
            if not brand:
                return "", "", "Selected brand could not be found."
            return (
                brand.name,
                brand.owner_company or "",
                _format_status(brand.deleted_at),
            )

    @app.callback(
        Output("skus-toast", "children", allow_duplicate=True),
        Output("skus-toast", "icon", allow_duplicate=True),
        Output("skus-toast", "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Output("skus-edit-brand-modal", "is_open", allow_duplicate=True),
        Output("skus-edit-brand-name", "value", allow_duplicate=True),
        Output("skus-edit-brand-owner", "value", allow_duplicate=True),
        Output("skus-edit-brand-status", "children", allow_duplicate=True),
        Input("skus-edit-brand-save", "n_clicks"),
        Input("skus-edit-brand-archive", "n_clicks"),
        Input("skus-edit-brand-restore", "n_clicks"),
        State("skus-edit-brand-select", "value"),
        State("skus-edit-brand-name", "value"),
        State("skus-edit-brand-owner", "value"),
        prevent_initial_call=True,
    )
    def handle_brand_updates(
        save_clicks, archive_clicks, restore_clicks, brand_id, name, owner
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        action = ctx.triggered[0]["prop_id"].split(".")[0]
        if not brand_id:
            return (
                "Select a brand first.",
                "warning",
                True,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        with session_scope() as session:
            brand = session.get(Brand, brand_id)
            if not brand:
                return (
                    "Brand not found.",
                    "danger",
                    True,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    "Selected brand could not be found.",
                )
            if action == "skus-edit-brand-save":
                if not name:
                    return (
                        "Name is required.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                    )
                brand.name = name.strip()
                brand.owner_company = (owner or "").strip() or None
                session.commit()
                return (
                    "Brand updated.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    brand.name,
                    brand.owner_company or "",
                    _format_status(brand.deleted_at),
                )
            if action == "skus-edit-brand-archive":
                brand.deleted_at = _utcnow()
                session.commit()
                return (
                    "Brand archived.",
                    "warning",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    brand.name,
                    brand.owner_company or "",
                    _format_status(brand.deleted_at),
                )
            if action == "skus-edit-brand-restore":
                brand.deleted_at = None
                session.commit()
                return (
                    "Brand restored.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    brand.name,
                    brand.owner_company or "",
                    _format_status(brand.deleted_at),
                )
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )

    @app.callback(
        Output("skus-toast", "children"),
        Output("skus-toast", "icon"),
        Output("skus-toast", "is_open"),
        Output(REFRESH_STORE_ID, "data"),
        Input("skus-add-brand-submit", "n_clicks"),
        State("skus-add-brand-name", "value"),
        State("skus-add-brand-owner", "value"),
        prevent_initial_call=True,
    )
    def save_brand(n_clicks, name, owner):
        if not n_clicks:
            return no_update, no_update, no_update, no_update
        if not name:
            return ("Name is required", "danger", True, no_update)
        with session_scope() as session:
            session.add(
                Brand(name=name.strip(), owner_company=(owner or "").strip() or None)
            )
            session.commit()
        return ("Brand created", "success", True, {"ts": datetime.utcnow().isoformat()})

    @app.callback(
        Output("skus-edit-product-brand", "value"),
        Output("skus-edit-product-name", "value"),
        Output("skus-edit-product-category", "value"),
        Output("skus-edit-product-abv", "value"),
        Output("skus-edit-product-status", "children"),
        Input("skus-edit-product-select", "value"),
    )
    def load_product_details(product_id):
        if not product_id:
            return None, "", None, None, ""
        with session_scope() as session:
            product = session.get(Product, product_id)
            if not product:
                return None, "", None, None, "Selected product could not be found."
            normalized_category = _normalize_category_value(product.category)
            return (
                product.brand_id,
                product.name,
                normalized_category,
                float(product.abv_percent),
                _format_status(product.deleted_at),
            )

    @app.callback(
        Output("skus-toast", "children", allow_duplicate=True),
        Output("skus-toast", "icon", allow_duplicate=True),
        Output("skus-toast", "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Output("skus-edit-product-modal", "is_open", allow_duplicate=True),
        Output("skus-edit-product-status", "children", allow_duplicate=True),
        Input("skus-edit-product-save", "n_clicks"),
        Input("skus-edit-product-archive", "n_clicks"),
        Input("skus-edit-product-restore", "n_clicks"),
        State("skus-edit-product-select", "value"),
        State("skus-edit-product-brand", "value"),
        State("skus-edit-product-name", "value"),
        State("skus-edit-product-category", "value"),
        State("skus-edit-product-abv", "value"),
        prevent_initial_call=True,
    )
    def handle_product_updates(
        save_clicks,
        archive_clicks,
        restore_clicks,
        product_id,
        brand_id,
        name,
        category,
        abv_value,
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update, no_update, no_update
        action = ctx.triggered[0]["prop_id"].split(".")[0]
        if not product_id:
            return (
                "Select a product first.",
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )
        with session_scope() as session:
            product = session.get(Product, product_id)
            if not product:
                return (
                    "Product not found.",
                    "danger",
                    True,
                    no_update,
                    no_update,
                    "Selected product could not be found.",
                )
            if action == "skus-edit-product-save":
                if not (
                    brand_id and name and category is not None and abv_value is not None
                ):
                    return (
                        "All fields are required.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(product.deleted_at),
                    )
                try:
                    abv_decimal = Decimal(str(abv_value)).quantize(Decimal("0.01"))
                except (InvalidOperation, ValueError):
                    return (
                        "Invalid ABV percentage.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(product.deleted_at),
                    )
                session_brand = session.get(Brand, brand_id)
                if not session_brand:
                    return (
                        "Brand not found.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(product.deleted_at),
                    )
                target_brand_id = brand_id
                target_name = name.strip()
                target_category = _normalize_category_value(category)
                if target_category not in PRODUCT_CATEGORY_DETAILS:
                    return (
                        "Invalid category selected.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(product.deleted_at),
                    )
                conflict = session.execute(
                    select(Product).where(
                        Product.brand_id == target_brand_id,
                        Product.name == target_name,
                        Product.id != product.id,
                    )
                ).scalar_one_or_none()
                if conflict:
                    return (
                        "Another product with this brand and name already exists.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(product.deleted_at),
                    )
                product.brand_id = target_brand_id
                product.name = target_name
                product.category = target_category
                product.abv_percent = abv_decimal
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    return (
                        "Update failed due to a uniqueness constraint.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(product.deleted_at),
                    )
                return (
                    "Product updated.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(product.deleted_at),
                )
            if action == "skus-edit-product-archive":
                product.deleted_at = _utcnow()
                session.commit()
                return (
                    "Product archived.",
                    "warning",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(product.deleted_at),
                )
            if action == "skus-edit-product-restore":
                product.deleted_at = None
                session.commit()
                return (
                    "Product restored.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(product.deleted_at),
                )
        return no_update, no_update, no_update, no_update, no_update, no_update

    @app.callback(
        Output("skus-edit-package-type", "value"),
        Output("skus-edit-package-volume", "value"),
        Output("skus-edit-package-form", "value"),
        Output("skus-edit-package-status", "children"),
        Input("skus-edit-package-select", "value"),
    )
    def load_package_details(package_id):
        if not package_id:
            return "bottle", None, None, ""
        with session_scope() as session:
            package = session.get(PackageSpec, package_id)
            if not package:
                return "bottle", None, None, "Selected package spec could not be found."
            return (
                package.type,
                package.container_ml,
                package.can_form_factor,
                _format_status(package.deleted_at),
            )

    @app.callback(
        Output("skus-toast", "children", allow_duplicate=True),
        Output("skus-toast", "icon", allow_duplicate=True),
        Output("skus-toast", "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Output("skus-edit-package-modal", "is_open", allow_duplicate=True),
        Output("skus-edit-package-status", "children", allow_duplicate=True),
        Input("skus-edit-package-save", "n_clicks"),
        Input("skus-edit-package-archive", "n_clicks"),
        Input("skus-edit-package-restore", "n_clicks"),
        State("skus-edit-package-select", "value"),
        State("skus-edit-package-type", "value"),
        State("skus-edit-package-volume", "value"),
        State("skus-edit-package-form", "value"),
        prevent_initial_call=True,
    )
    def handle_package_updates(
        save_clicks,
        archive_clicks,
        restore_clicks,
        package_id,
        package_type,
        volume,
        form_factor,
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update, no_update, no_update
        action = ctx.triggered[0]["prop_id"].split(".")[0]
        if not package_id:
            return (
                "Select a package spec first.",
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )
        with session_scope() as session:
            package = session.get(PackageSpec, package_id)
            if not package:
                return (
                    "Package spec not found.",
                    "danger",
                    True,
                    no_update,
                    no_update,
                    "Selected package spec could not be found.",
                )
            if action == "skus-edit-package-save":
                if package_type not in {"bottle", "can"} or volume is None:
                    return (
                        "Type and container volume are required.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(package.deleted_at),
                    )
                if package_type == "can":
                    if not form_factor:
                        return (
                            "Can form factor is required for cans.",
                            "danger",
                            True,
                            no_update,
                            no_update,
                            _format_status(package.deleted_at),
                        )
                    form_value = str(form_factor).strip().lower()
                    if form_value not in ALLOWED_CAN_FORM_FACTORS:
                        return (
                            "Invalid can form factor.",
                            "danger",
                            True,
                            no_update,
                            no_update,
                            _format_status(package.deleted_at),
                        )
                    package.can_form_factor = form_value
                else:
                    package.can_form_factor = None
                try:
                    package.container_ml = int(volume)
                except (TypeError, ValueError):
                    return (
                        "Container volume must be a whole number.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(package.deleted_at),
                    )
                if package.container_ml <= 0:
                    return (
                        "Container volume must be greater than zero.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(package.deleted_at),
                    )
                package.type = package_type
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    return (
                        "Update failed due to a uniqueness constraint.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(package.deleted_at),
                    )
                return (
                    "Package spec updated.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(package.deleted_at),
                )
            if action == "skus-edit-package-archive":
                package.deleted_at = _utcnow()
                session.commit()
                return (
                    "Package spec archived.",
                    "warning",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(package.deleted_at),
                )
            if action == "skus-edit-package-restore":
                package.deleted_at = None
                session.commit()
                return (
                    "Package spec restored.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(package.deleted_at),
                )
        return no_update, no_update, no_update, no_update, no_update, no_update

    @app.callback(
        Output("skus-edit-sku-product", "value"),
        Output("skus-edit-sku-package", "value"),
        Output("skus-edit-sku-gtin", "value"),
        Output("skus-edit-sku-active", "value"),
        Output("skus-edit-sku-status", "children"),
        Input("skus-edit-sku-select", "value"),
    )
    def load_sku_details(sku_id):
        if not sku_id:
            return None, None, "", True, ""
        with session_scope() as session:
            sku = session.get(SKU, sku_id)
            if not sku:
                return None, None, "", True, "Selected SKU could not be found."
            return (
                sku.product_id,
                sku.package_spec_id,
                sku.gtin or "",
                bool(sku.is_active),
                _format_status(sku.deleted_at),
            )

    @app.callback(
        Output("skus-toast", "children", allow_duplicate=True),
        Output("skus-toast", "icon", allow_duplicate=True),
        Output("skus-toast", "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Output("skus-edit-sku-modal", "is_open", allow_duplicate=True),
        Output("skus-edit-sku-status", "children", allow_duplicate=True),
        Input("skus-edit-sku-save", "n_clicks"),
        Input("skus-edit-sku-archive", "n_clicks"),
        Input("skus-edit-sku-restore", "n_clicks"),
        State("skus-edit-sku-select", "value"),
        State("skus-edit-sku-product", "value"),
        State("skus-edit-sku-package", "value"),
        State("skus-edit-sku-gtin", "value"),
        State("skus-edit-sku-active", "value"),
        prevent_initial_call=True,
    )
    def handle_sku_updates(
        save_clicks,
        archive_clicks,
        restore_clicks,
        sku_id,
        product_id,
        package_spec_id,
        gtin,
        is_active_value,
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update, no_update, no_update
        action = ctx.triggered[0]["prop_id"].split(".")[0]
        if not sku_id:
            return (
                "Select an SKU first.",
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )
        with session_scope() as session:
            sku = session.get(SKU, sku_id)
            if not sku:
                return (
                    "SKU not found.",
                    "danger",
                    True,
                    no_update,
                    no_update,
                    "Selected SKU could not be found.",
                )
            if action == "skus-edit-sku-save":
                if not (product_id and package_spec_id):
                    return (
                        "Product and package spec are required.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(sku.deleted_at),
                    )
                product = session.get(Product, product_id)
                package = session.get(PackageSpec, package_spec_id)
                if not product or not package:
                    return (
                        "Product or package not found.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(sku.deleted_at),
                    )
                sku.product_id = product_id
                sku.package_spec_id = package_spec_id
                sku.gtin = (gtin or "").strip() or None
                sku.is_active = bool(is_active_value)
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    return (
                        "Update failed due to a uniqueness constraint.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(sku.deleted_at),
                    )
                return (
                    "SKU updated.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(sku.deleted_at),
                )
            if action == "skus-edit-sku-archive":
                sku.deleted_at = _utcnow()
                sku.is_active = False
                session.commit()
                return (
                    "SKU archived.",
                    "warning",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(sku.deleted_at),
                )
            if action == "skus-edit-sku-restore":
                sku.deleted_at = None
                session.commit()
                return (
                    "SKU restored.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(sku.deleted_at),
                )
        return no_update, no_update, no_update, no_update, no_update, no_update

    @app.callback(
        Output("skus-edit-pack-package", "value"),
        Output("skus-edit-pack-units", "value"),
        Output("skus-edit-pack-gtin", "value"),
        Output("skus-edit-pack-notes", "value"),
        Output("skus-edit-pack-status", "children"),
        Input("skus-edit-pack-select", "value"),
    )
    def load_pack_details(pack_id):
        if not pack_id:
            return None, None, "", "", ""
        with session_scope() as session:
            pack = session.get(PackSpec, pack_id)
            if not pack:
                return None, None, "", "", "Selected pack spec could not be found."
            return (
                pack.package_spec_id,
                pack.units_per_pack,
                pack.gtin or "",
                pack.notes or "",
                _format_status(pack.deleted_at),
            )

    @app.callback(
        Output("skus-toast", "children", allow_duplicate=True),
        Output("skus-toast", "icon", allow_duplicate=True),
        Output("skus-toast", "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Output("skus-edit-pack-modal", "is_open", allow_duplicate=True),
        Output("skus-edit-pack-status", "children", allow_duplicate=True),
        Input("skus-edit-pack-save", "n_clicks"),
        Input("skus-edit-pack-archive", "n_clicks"),
        Input("skus-edit-pack-restore", "n_clicks"),
        State("skus-edit-pack-select", "value"),
        State("skus-edit-pack-package", "value"),
        State("skus-edit-pack-units", "value"),
        State("skus-edit-pack-gtin", "value"),
        State("skus-edit-pack-notes", "value"),
        prevent_initial_call=True,
    )
    def handle_pack_updates(
        save_clicks,
        archive_clicks,
        restore_clicks,
        pack_id,
        package_spec_id,
        units_per_pack,
        gtin,
        notes,
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update, no_update, no_update
        action = ctx.triggered[0]["prop_id"].split(".")[0]
        if not pack_id:
            return (
                "Select a pack spec first.",
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )
        with session_scope() as session:
            pack = session.get(PackSpec, pack_id)
            if not pack:
                return (
                    "Pack spec not found.",
                    "danger",
                    True,
                    no_update,
                    no_update,
                    "Selected pack spec could not be found.",
                )
            if action == "skus-edit-pack-save":
                if not (package_spec_id and units_per_pack):
                    return (
                        "Package and units per pack are required.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(pack.deleted_at),
                    )
                package = session.get(PackageSpec, package_spec_id)
                if not package:
                    return (
                        "Package spec not found.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(pack.deleted_at),
                    )
                try:
                    units_value = int(units_per_pack)
                except (TypeError, ValueError):
                    return (
                        "Units per pack must be an integer.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(pack.deleted_at),
                    )
                if units_value < 2:
                    return (
                        "Units per pack must be at least 2.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(pack.deleted_at),
                    )
                pack.package_spec_id = package_spec_id
                pack.units_per_pack = units_value
                pack.gtin = (gtin or "").strip() or None
                pack.notes = (notes or "").strip() or None
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    return (
                        "Update failed due to a uniqueness constraint.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(pack.deleted_at),
                    )
                return (
                    "Pack spec updated.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(pack.deleted_at),
                )
            if action == "skus-edit-pack-archive":
                pack.deleted_at = _utcnow()
                session.commit()
                return (
                    "Pack spec archived.",
                    "warning",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(pack.deleted_at),
                )
            if action == "skus-edit-pack-restore":
                pack.deleted_at = None
                session.commit()
                return (
                    "Pack spec restored.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(pack.deleted_at),
                )
        return no_update, no_update, no_update, no_update, no_update, no_update

    @app.callback(
        Output("skus-edit-carton-mode", "value"),
        Output("skus-edit-carton-package", "value"),
        Output("skus-edit-carton-pack", "value"),
        Output("skus-edit-carton-units", "value"),
        Output("skus-edit-carton-pack-count", "value"),
        Output("skus-edit-carton-gtin", "value"),
        Output("skus-edit-carton-notes", "value"),
        Output("skus-edit-carton-status", "children"),
        Input("skus-edit-carton-select", "value"),
    )
    def load_carton_details(carton_id):
        if not carton_id:
            return "unit", None, None, None, None, "", "", ""
        with session_scope() as session:
            carton = session.get(CartonSpec, carton_id)
            if not carton:
                return (
                    "unit",
                    None,
                    None,
                    None,
                    None,
                    "",
                    "",
                    "Selected carton spec could not be found.",
                )
            mode = "pack" if carton.pack_spec_id else "unit"
            return (
                mode,
                carton.package_spec_id,
                carton.pack_spec_id,
                carton.units_per_carton,
                carton.pack_count,
                carton.gtin or "",
                carton.notes or "",
                _format_status(carton.deleted_at),
            )

    @app.callback(
        Output("skus-toast", "children", allow_duplicate=True),
        Output("skus-toast", "icon", allow_duplicate=True),
        Output("skus-toast", "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Output("skus-edit-carton-modal", "is_open", allow_duplicate=True),
        Output("skus-edit-carton-status", "children", allow_duplicate=True),
        Input("skus-edit-carton-save", "n_clicks"),
        Input("skus-edit-carton-archive", "n_clicks"),
        Input("skus-edit-carton-restore", "n_clicks"),
        State("skus-edit-carton-select", "value"),
        State("skus-edit-carton-mode", "value"),
        State("skus-edit-carton-package", "value"),
        State("skus-edit-carton-pack", "value"),
        State("skus-edit-carton-units", "value"),
        State("skus-edit-carton-pack-count", "value"),
        State("skus-edit-carton-gtin", "value"),
        State("skus-edit-carton-notes", "value"),
        prevent_initial_call=True,
    )
    def handle_carton_updates(
        save_clicks,
        archive_clicks,
        restore_clicks,
        carton_id,
        mode,
        package_spec_id,
        pack_spec_id,
        units_per_carton,
        pack_count,
        gtin,
        notes,
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update, no_update, no_update
        action = ctx.triggered[0]["prop_id"].split(".")[0]
        if not carton_id:
            return (
                "Select a carton spec first.",
                "warning",
                True,
                no_update,
                no_update,
                no_update,
            )
        with session_scope() as session:
            carton = session.get(CartonSpec, carton_id)
            if not carton:
                return (
                    "Carton spec not found.",
                    "danger",
                    True,
                    no_update,
                    no_update,
                    "Selected carton spec could not be found.",
                )
            if action == "skus-edit-carton-save":
                try:
                    units_value = (
                        int(units_per_carton) if units_per_carton is not None else None
                    )
                except (TypeError, ValueError):
                    return (
                        "Units per carton must be an integer.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(carton.deleted_at),
                    )
                if mode == "unit":
                    if not package_spec_id or not units_value:
                        return (
                            "Package spec and units per carton are required for unit cartons.",
                            "danger",
                            True,
                            no_update,
                            no_update,
                            _format_status(carton.deleted_at),
                        )
                    package = session.get(PackageSpec, package_spec_id)
                    if not package:
                        return (
                            "Package spec not found.",
                            "danger",
                            True,
                            no_update,
                            no_update,
                            _format_status(carton.deleted_at),
                        )
                    carton.package_spec_id = package_spec_id
                    carton.pack_spec_id = None
                    carton.pack_count = None
                    carton.units_per_carton = units_value
                else:
                    if not pack_spec_id:
                        return (
                            "Pack spec is required for pack cartons.",
                            "danger",
                            True,
                            no_update,
                            no_update,
                            _format_status(carton.deleted_at),
                        )
                    pack_spec = session.get(PackSpec, pack_spec_id)
                    if not pack_spec:
                        return (
                            "Pack spec not found.",
                            "danger",
                            True,
                            no_update,
                            no_update,
                            _format_status(carton.deleted_at),
                        )
                    try:
                        pack_count_value = (
                            int(pack_count) if pack_count is not None else None
                        )
                    except (TypeError, ValueError):
                        return (
                            "Pack count must be an integer.",
                            "danger",
                            True,
                            no_update,
                            no_update,
                            _format_status(carton.deleted_at),
                        )
                    if not pack_count_value or pack_count_value <= 0:
                        return (
                            "Pack count must be greater than zero.",
                            "danger",
                            True,
                            no_update,
                            no_update,
                            _format_status(carton.deleted_at),
                        )
                    carton.pack_spec_id = pack_spec_id
                    carton.package_spec_id = None
                    carton.pack_count = pack_count_value
                    units_total = pack_spec.units_per_pack * pack_count_value
                    carton.units_per_carton = (
                        units_value if units_value else units_total
                    )
                if carton.units_per_carton <= 0:
                    return (
                        "Units per carton must be greater than zero.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(carton.deleted_at),
                    )
                carton.gtin = (gtin or "").strip() or None
                carton.notes = (notes or "").strip() or None
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    return (
                        "Update failed due to a uniqueness constraint.",
                        "danger",
                        True,
                        no_update,
                        no_update,
                        _format_status(carton.deleted_at),
                    )
                return (
                    "Carton spec updated.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(carton.deleted_at),
                )
            if action == "skus-edit-carton-archive":
                carton.deleted_at = _utcnow()
                session.commit()
                return (
                    "Carton spec archived.",
                    "warning",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(carton.deleted_at),
                )
            if action == "skus-edit-carton-restore":
                carton.deleted_at = None
                session.commit()
                return (
                    "Carton spec restored.",
                    "success",
                    True,
                    {"ts": datetime.utcnow().isoformat()},
                    no_update,
                    _format_status(carton.deleted_at),
                )
        return no_update, no_update, no_update, no_update, no_update, no_update

    @app.callback(
        Output("skus-toast", "children", allow_duplicate=True),
        Output("skus-toast", "icon", allow_duplicate=True),
        Output("skus-toast", "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Input("skus-add-product-submit", "n_clicks"),
        State("skus-add-product-brand", "value"),
        State("skus-add-product-name", "value"),
        State("skus-add-product-category", "value"),
        State("skus-add-product-abv", "value"),
        prevent_initial_call=True,
    )
    def save_product(n_clicks, brand_id, name, category, abv):
        if not n_clicks:
            return no_update, no_update, no_update, no_update
        if not (brand_id and name and category and abv is not None):
            return ("All fields are required", "danger", True, no_update)
        with session_scope() as session:
            brand = session.get(Brand, brand_id)
            if not brand:
                return ("Brand not found", "danger", True, no_update)
            product = Product(
                brand=brand,
                name=name.strip(),
                category=category,
                abv_percent=Decimal(str(abv)).quantize(Decimal("0.01")),
            )
            session.add(product)
            session.commit()
        return (
            "Product created",
            "success",
            True,
            {"ts": datetime.utcnow().isoformat()},
        )

    @app.callback(
        Output("skus-toast", "children", allow_duplicate=True),
        Output("skus-toast", "icon", allow_duplicate=True),
        Output("skus-toast", "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Input("skus-add-package-submit", "n_clicks"),
        State("skus-add-package-type", "value"),
        State("skus-add-package-volume", "value"),
        State("skus-add-package-form", "value"),
        prevent_initial_call=True,
    )
    def save_package(n_clicks, type_value, volume, form_factor):
        if not n_clicks:
            return no_update, no_update, no_update, no_update
        if type_value is None or volume is None:
            return ("Type and volume required", "danger", True, no_update)
        form_value: Optional[str] = None
        if type_value == "can":
            if not form_factor:
                return ("Can form factor required for cans", "danger", True, no_update)
            form_value = str(form_factor).strip().lower()
            if form_value not in ALLOWED_CAN_FORM_FACTORS:
                return ("Invalid can form factor", "danger", True, no_update)
        with session_scope() as session:
            spec = PackageSpec(
                type=type_value,
                container_ml=int(volume),
                can_form_factor=form_value if type_value == "can" else None,
            )
            session.add(spec)
            session.commit()
        return (
            "Package spec created",
            "success",
            True,
            {"ts": datetime.utcnow().isoformat()},
        )

    @app.callback(
        Output("skus-toast", "children", allow_duplicate=True),
        Output("skus-toast", "icon", allow_duplicate=True),
        Output("skus-toast", "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Input("skus-add-sku-submit", "n_clicks"),
        State("skus-add-sku-product", "value"),
        State("skus-add-sku-package", "value"),
        State("skus-add-sku-gtin", "value"),
        State("skus-add-sku-active", "value"),
        State("skus-add-sku-carton", "value"),
        prevent_initial_call=True,
    )
    def save_sku(
        n_clicks, product_id, package_id, gtin, is_active_value, carton_spec_id
    ):
        if not n_clicks:
            return no_update, no_update, no_update, no_update
        if not (product_id and package_id):
            return ("Product and package spec required", "danger", True, no_update)
        with session_scope() as session:
            product = session.get(Product, product_id)
            package = session.get(PackageSpec, package_id)
            if not product or not package:
                return ("Product or package not found", "danger", True, no_update)
            sku = SKU(
                product=product,
                package_spec=package,
                gtin=(gtin or "").strip() or None,
                is_active=bool(is_active_value),
            )
            session.add(sku)
            session.flush()
            if carton_spec_id:
                carton = session.get(CartonSpec, carton_spec_id)
                if carton:
                    session.add(SKUCarton(sku=sku, carton_spec=carton))
            session.commit()
        return ("SKU created", "success", True, {"ts": datetime.utcnow().isoformat()})

    @app.callback(
        Output("skus-toast", "children", allow_duplicate=True),
        Output("skus-toast", "icon", allow_duplicate=True),
        Output("skus-toast", "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Input("skus-add-carton-submit", "n_clicks"),
        State("skus-add-carton-mode", "value"),
        State("skus-add-carton-package", "value"),
        State("skus-add-carton-pack", "value"),
        State("skus-add-carton-units", "value"),
        State("skus-add-carton-pack-count", "value"),
        State("skus-add-carton-gtin", "value"),
        State("skus-add-carton-notes", "value"),
        prevent_initial_call=True,
    )
    def save_carton(
        n_clicks,
        mode,
        package_spec_id,
        pack_spec_id,
        units,
        pack_count,
        gtin,
        notes,
    ):
        if not n_clicks:
            return no_update, no_update, no_update, no_update
        mode_value = (mode or "unit").lower()
        with session_scope() as session:
            try:
                units_value = int(units) if units is not None else None
            except (TypeError, ValueError):
                return (
                    "Units per carton must be an integer.",
                    "danger",
                    True,
                    no_update,
                )

            if mode_value == "unit":
                if not (package_spec_id and units_value is not None):
                    return (
                        "Package spec and units per carton are required for unit cartons.",
                        "danger",
                        True,
                        no_update,
                    )
                package = session.get(PackageSpec, package_spec_id)
                if not package or package.deleted_at is not None:
                    return ("Package spec not found.", "danger", True, no_update)
                if units_value <= 0:
                    return (
                        "Units per carton must be greater than zero.",
                        "danger",
                        True,
                        no_update,
                    )
                carton = CartonSpec(
                    package_spec_id=package_spec_id,
                    units_per_carton=units_value,
                    pack_spec_id=None,
                    pack_count=None,
                )
            elif mode_value == "pack":
                if not pack_spec_id:
                    return (
                        "Pack spec is required for pack cartons.",
                        "danger",
                        True,
                        no_update,
                    )
                pack = session.get(PackSpec, pack_spec_id)
                if not pack or pack.deleted_at is not None:
                    return ("Pack spec not found.", "danger", True, no_update)
                try:
                    pack_count_value = (
                        int(pack_count) if pack_count is not None else None
                    )
                except (TypeError, ValueError):
                    return ("Pack count must be an integer.", "danger", True, no_update)
                if not pack_count_value or pack_count_value <= 0:
                    return (
                        "Pack count must be greater than zero.",
                        "danger",
                        True,
                        no_update,
                    )
                if units_value is None:
                    units_value = pack.units_per_pack * pack_count_value
                if units_value <= 0:
                    return (
                        "Units per carton must be greater than zero.",
                        "danger",
                        True,
                        no_update,
                    )
                carton = CartonSpec(
                    pack_spec_id=pack_spec_id,
                    pack_count=pack_count_value,
                    units_per_carton=units_value,
                    package_spec_id=None,
                )
            else:
                return ("Invalid carton mode.", "danger", True, no_update)

            carton.gtin = (gtin or "").strip() or None
            carton.notes = (notes or "").strip() or None
            session.add(carton)
            session.commit()
        return (
            "Carton spec created",
            "success",
            True,
            {"ts": datetime.utcnow().isoformat()},
        )

    @app.callback(
        Output("skus-toast", "children", allow_duplicate=True),
        Output("skus-toast", "icon", allow_duplicate=True),
        Output("skus-toast", "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Input("skus-add-pack-submit", "n_clicks"),
        State("skus-add-pack-package", "value"),
        State("skus-add-pack-units", "value"),
        State("skus-add-pack-gtin", "value"),
        State("skus-add-pack-notes", "value"),
        prevent_initial_call=True,
    )
    def save_pack(n_clicks, package_id, units, gtin, notes):
        if not n_clicks:
            return no_update, no_update, no_update, no_update
        if not (package_id and units):
            return ("Package and units per pack required", "danger", True, no_update)
        try:
            units_value = int(units)
        except (TypeError, ValueError):
            return ("Units per pack must be an integer", "danger", True, no_update)
        if units_value < 2:
            return ("Units per pack must be at least 2", "danger", True, no_update)
        with session_scope() as session:
            package = session.get(PackageSpec, package_id)
            if not package:
                return ("Package spec not found", "danger", True, no_update)
            existing = session.execute(
                select(PackSpec).where(
                    PackSpec.package_spec_id == package.id,
                    PackSpec.units_per_pack == units_value,
                    PackSpec.deleted_at.is_(None),
                )
            ).scalar_one_or_none()
            if existing:
                return (
                    "Pack spec already exists for this package",
                    "warning",
                    True,
                    no_update,
                )
            pack = PackSpec(
                package_spec=package,
                units_per_pack=units_value,
                gtin=(gtin or "").strip() or None,
                notes=(notes or "").strip() or None,
            )
            session.add(pack)
            session.commit()
        return (
            "Pack spec created",
            "success",
            True,
            {"ts": datetime.utcnow().isoformat()},
        )


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
        ctx = dash.callback_context  # dash>=2.0
        if not ctx.triggered:
            return is_open
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == open_id:
            return True
        return False


def _load_brand_options(include_deleted: bool = False) -> List[dict]:
    with session_scope() as session:
        stmt = select(Brand).order_by(Brand.name)
        if not include_deleted:
            stmt = stmt.where(Brand.deleted_at.is_(None))
        brands = session.execute(stmt).scalars().all()
    options: List[dict] = []
    for brand in brands:
        label = brand.name
        if brand.deleted_at:
            label += " (archived)"
        options.append({"label": label, "value": brand.id})
    return options


def _load_product_options(include_deleted: bool = False) -> List[dict]:
    with session_scope() as session:
        stmt = (
            select(Product, Brand.name)
            .join(Product.brand)
            .order_by(Brand.name, Product.name)
        )
        if not include_deleted:
            stmt = stmt.where(Product.deleted_at.is_(None), Brand.deleted_at.is_(None))
        rows = session.execute(stmt).all()
    options: List[dict] = []
    for product, brand_name in rows:
        label = f"{brand_name} - {product.name}"
        if product.deleted_at:
            label += " (archived)"
        options.append(
            {"label": label, "value": product.id, "brand_id": product.brand_id}
        )
    return options


def _load_package_options(include_deleted: bool = False) -> List[dict]:
    with session_scope() as session:
        stmt = select(PackageSpec).order_by(PackageSpec.type, PackageSpec.container_ml)
        if not include_deleted:
            stmt = stmt.where(PackageSpec.deleted_at.is_(None))
        specs = session.execute(stmt).scalars().all()
    options: List[dict] = []
    for spec in specs:
        label = f"{spec.type.title()} {spec.container_ml} mL"
        if spec.can_form_factor:
            label += f" ({spec.can_form_factor})"
        if spec.deleted_at:
            label += " (archived)"
        options.append({"label": label, "value": spec.id, "type": spec.type})
    return options


def _load_sku_options(include_deleted: bool = False) -> List[dict]:
    with session_scope() as session:
        stmt = (
            select(
                SKU,
                Product.name,
                Brand.name,
                PackageSpec.container_ml,
                PackageSpec.type,
            )
            .join(SKU.product)
            .join(Product.brand)
            .join(SKU.package_spec)
            .order_by(Brand.name, Product.name, PackageSpec.container_ml)
        )
        if not include_deleted:
            stmt = stmt.where(
                SKU.deleted_at.is_(None),
                Product.deleted_at.is_(None),
                Brand.deleted_at.is_(None),
                PackageSpec.deleted_at.is_(None),
            )
        rows = session.execute(stmt).all()
    options: List[dict] = []
    for sku, product_name, brand_name, container_ml, pkg_type in rows:
        label = f"{brand_name} - {product_name} ({pkg_type} {container_ml}mL)"
        if sku.deleted_at:
            label += " (archived)"
        options.append(
            {
                "label": label,
                "value": sku.id,
                "product_id": sku.product_id,
                "package_spec_id": sku.package_spec_id,
            }
        )
    return options


def _load_pack_options(include_deleted: bool = False) -> List[dict]:
    with session_scope() as session:
        stmt = (
            select(PackSpec, PackageSpec.type, PackageSpec.container_ml)
            .join(PackSpec.package_spec)
            .order_by(
                PackageSpec.type, PackageSpec.container_ml, PackSpec.units_per_pack
            )
        )
        if not include_deleted:
            stmt = stmt.where(
                PackSpec.deleted_at.is_(None), PackageSpec.deleted_at.is_(None)
            )
        rows = session.execute(stmt).all()
    options: List[dict] = []
    for pack_spec, pkg_type, container_ml in rows:
        label = f"{pkg_type.title()} {container_ml}mL - {pack_spec.units_per_pack} pack"
        if pack_spec.deleted_at:
            label += " (archived)"
        options.append(
            {
                "label": label,
                "value": pack_spec.id,
                "package_spec_id": pack_spec.package_spec_id,
            }
        )
    return options


def _load_carton_options(include_deleted: bool = False) -> List[dict]:
    with session_scope() as session:
        stmt = select(CartonSpec).order_by(CartonSpec.units_per_carton)
        if not include_deleted:
            stmt = stmt.where(CartonSpec.deleted_at.is_(None))
        specs = session.execute(stmt).scalars().all()
    options: List[dict] = []
    for spec in specs:
        label = f"{spec.units_per_carton} units"
        if spec.pack_count:
            label += f" ({spec.pack_count} packs)"
        if spec.deleted_at:
            label += " (archived)"
        options.append(
            {
                "label": label,
                "value": spec.id,
                "package_spec_id": spec.package_spec_id,
                "pack_spec_id": spec.pack_spec_id,
            }
        )
    return options


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


def _brand_modal() -> dbc.Modal:
    body = [
        dbc.Input(id="skus-add-brand-name", placeholder="Brand name"),
        dbc.Input(
            id="skus-add-brand-owner", placeholder="Owner company", className="mt-3"
        ),
    ]
    return modal_form(
        "skus-add-brand-modal",
        "Add Brand",
        body,
        submit_id="skus-add-brand-submit",
        close_id="skus-add-brand-cancel",
        size="md",
    )


def _edit_brand_modal(options: List[dict]) -> dbc.Modal:
    return dbc.Modal(
        [
            dbc.ModalHeader("Edit Brand"),
            dbc.ModalBody(
                [
                    dbc.Select(
                        id="skus-edit-brand-select",
                        options=options,
                        placeholder="Select a brand",
                        className="mb-3",
                    ),
                    dbc.Input(id="skus-edit-brand-name", placeholder="Brand name"),
                    dbc.Input(
                        id="skus-edit-brand-owner",
                        placeholder="Owner company",
                        className="mt-3",
                    ),
                    html.Div(
                        id="skus-edit-brand-status", className="text-muted small mt-2"
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="skus-edit-brand-cancel",
                        color="secondary",
                        className="me-2",
                    ),
                    dbc.Button(
                        "Archive",
                        id="skus-edit-brand-archive",
                        color="danger",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button(
                        "Restore",
                        id="skus-edit-brand-restore",
                        color="warning",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button("Save", id="skus-edit-brand-save", color="primary"),
                ]
            ),
        ],
        id="skus-edit-brand-modal",
        size="md",
        backdrop="static",
    )


def _edit_product_modal(
    brand_options: List[dict], product_options: List[dict]
) -> dbc.Modal:
    return dbc.Modal(
        [
            dbc.ModalHeader("Edit Product"),
            dbc.ModalBody(
                [
                    dbc.Select(
                        id="skus-edit-product-select",
                        options=product_options,
                        placeholder="Select a product",
                        className="mb-3",
                    ),
                    dbc.Select(
                        id="skus-edit-product-brand",
                        options=brand_options,
                        placeholder="Select brand",
                        className="mb-3",
                    ),
                    dbc.Input(id="skus-edit-product-name", placeholder="Product name"),
                    dbc.Select(
                        id="skus-edit-product-category",
                        options=[
                            {"label": "Gin Bottle", "value": "gin_bottle"},
                            {"label": "Gin RTD", "value": "gin_rtd"},
                            {"label": "Vodka Bottle", "value": "vodka_bottle"},
                            {"label": "Vodka RTD", "value": "vodka_rtd"},
                        ],
                        placeholder="Category",
                        className="mt-3",
                    ),
                    dbc.Input(
                        id="skus-edit-product-abv",
                        type="number",
                        step=0.1,
                        placeholder="ABV %",
                        className="mt-3",
                    ),
                    html.Div(
                        id="skus-edit-product-status", className="text-muted small mt-2"
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="skus-edit-product-cancel",
                        color="secondary",
                        className="me-2",
                    ),
                    dbc.Button(
                        "Archive",
                        id="skus-edit-product-archive",
                        color="danger",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button(
                        "Restore",
                        id="skus-edit-product-restore",
                        color="warning",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button("Save", id="skus-edit-product-save", color="primary"),
                ]
            ),
        ],
        id="skus-edit-product-modal",
        size="lg",
        backdrop="static",
    )


def _edit_package_modal(package_options: List[dict]) -> dbc.Modal:
    return dbc.Modal(
        [
            dbc.ModalHeader("Edit Package Spec"),
            dbc.ModalBody(
                [
                    dbc.Select(
                        id="skus-edit-package-select",
                        options=package_options,
                        placeholder="Select a package spec",
                        className="mb-3",
                    ),
                    dbc.RadioItems(
                        id="skus-edit-package-type",
                        options=[
                            {"label": "Bottle", "value": "bottle"},
                            {"label": "Can", "value": "can"},
                        ],
                        value="bottle",
                        inline=True,
                        className="mb-3",
                    ),
                    dbc.Input(
                        id="skus-edit-package-volume",
                        type="number",
                        placeholder="Container volume (mL)",
                    ),
                    dbc.Select(
                        id="skus-edit-package-form",
                        options=[
                            {"label": "Slim", "value": "slim"},
                            {"label": "Sleek", "value": "sleek"},
                            {"label": "Classic", "value": "classic"},
                        ],
                        placeholder="Can form factor",
                        className="mt-3",
                    ),
                    html.Div(
                        id="skus-edit-package-status", className="text-muted small mt-2"
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="skus-edit-package-cancel",
                        color="secondary",
                        className="me-2",
                    ),
                    dbc.Button(
                        "Archive",
                        id="skus-edit-package-archive",
                        color="danger",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button(
                        "Restore",
                        id="skus-edit-package-restore",
                        color="warning",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button("Save", id="skus-edit-package-save", color="primary"),
                ]
            ),
        ],
        id="skus-edit-package-modal",
        size="lg",
        backdrop="static",
    )


def _edit_sku_modal(
    product_options: List[dict],
    package_options: List[dict],
    sku_options: List[dict],
) -> dbc.Modal:
    return dbc.Modal(
        [
            dbc.ModalHeader("Edit SKU"),
            dbc.ModalBody(
                [
                    dbc.Select(
                        id="skus-edit-sku-select",
                        options=sku_options,
                        placeholder="Select an SKU",
                        className="mb-3",
                    ),
                    dbc.Select(
                        id="skus-edit-sku-product",
                        options=product_options,
                        placeholder="Select product",
                        className="mb-3",
                    ),
                    dbc.Select(
                        id="skus-edit-sku-package",
                        options=package_options,
                        placeholder="Select package spec",
                        className="mb-3",
                    ),
                    dbc.Input(id="skus-edit-sku-gtin", placeholder="GTIN (optional)"),
                    dbc.Checkbox(
                        id="skus-edit-sku-active",
                        value=True,
                        className="mt-3",
                        label="Active",
                    ),
                    html.Div(
                        id="skus-edit-sku-status", className="text-muted small mt-2"
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="skus-edit-sku-cancel",
                        color="secondary",
                        className="me-2",
                    ),
                    dbc.Button(
                        "Archive",
                        id="skus-edit-sku-archive",
                        color="danger",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button(
                        "Restore",
                        id="skus-edit-sku-restore",
                        color="warning",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button("Save", id="skus-edit-sku-save", color="primary"),
                ]
            ),
        ],
        id="skus-edit-sku-modal",
        size="lg",
        backdrop="static",
    )


def _edit_pack_modal(
    package_options: List[dict], pack_options: List[dict]
) -> dbc.Modal:
    return dbc.Modal(
        [
            dbc.ModalHeader("Edit Pack Spec"),
            dbc.ModalBody(
                [
                    dbc.Select(
                        id="skus-edit-pack-select",
                        options=pack_options,
                        placeholder="Select a pack spec",
                        className="mb-3",
                    ),
                    dbc.Select(
                        id="skus-edit-pack-package",
                        options=package_options,
                        placeholder="Select package spec",
                        className="mb-3",
                    ),
                    dbc.Input(
                        id="skus-edit-pack-units",
                        type="number",
                        placeholder="Units per pack",
                    ),
                    dbc.Input(
                        id="skus-edit-pack-gtin",
                        placeholder="Pack GTIN (optional)",
                        className="mt-3",
                    ),
                    dbc.Textarea(
                        id="skus-edit-pack-notes", placeholder="Notes", className="mt-3"
                    ),
                    html.Div(
                        id="skus-edit-pack-status", className="text-muted small mt-2"
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="skus-edit-pack-cancel",
                        color="secondary",
                        className="me-2",
                    ),
                    dbc.Button(
                        "Archive",
                        id="skus-edit-pack-archive",
                        color="danger",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button(
                        "Restore",
                        id="skus-edit-pack-restore",
                        color="warning",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button("Save", id="skus-edit-pack-save", color="primary"),
                ]
            ),
        ],
        id="skus-edit-pack-modal",
        size="lg",
        backdrop="static",
    )


def _edit_carton_modal(
    package_options: List[dict],
    pack_options: List[dict],
    carton_options: List[dict],
) -> dbc.Modal:
    return dbc.Modal(
        [
            dbc.ModalHeader("Edit Carton Spec"),
            dbc.ModalBody(
                [
                    dbc.Select(
                        id="skus-edit-carton-select",
                        options=carton_options,
                        placeholder="Select a carton spec",
                        className="mb-3",
                    ),
                    dbc.RadioItems(
                        id="skus-edit-carton-mode",
                        options=[
                            {"label": "Unit carton", "value": "unit"},
                            {"label": "Pack carton", "value": "pack"},
                        ],
                        value="unit",
                        inline=True,
                        className="mb-3",
                    ),
                    dbc.Select(
                        id="skus-edit-carton-package",
                        options=package_options,
                        placeholder="Package spec (unit cartons)",
                        className="mb-3",
                    ),
                    dbc.Select(
                        id="skus-edit-carton-pack",
                        options=pack_options,
                        placeholder="Pack spec (pack cartons)",
                        className="mb-3",
                    ),
                    dbc.Input(
                        id="skus-edit-carton-units",
                        type="number",
                        placeholder="Units per carton",
                    ),
                    dbc.Input(
                        id="skus-edit-carton-pack-count",
                        type="number",
                        placeholder="Pack count (for pack cartons)",
                        className="mt-3",
                    ),
                    dbc.Input(
                        id="skus-edit-carton-gtin",
                        placeholder="Carton GTIN (optional)",
                        className="mt-3",
                    ),
                    dbc.Textarea(
                        id="skus-edit-carton-notes",
                        placeholder="Notes",
                        className="mt-3",
                    ),
                    html.Div(
                        id="skus-edit-carton-status", className="text-muted small mt-2"
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="skus-edit-carton-cancel",
                        color="secondary",
                        className="me-2",
                    ),
                    dbc.Button(
                        "Archive",
                        id="skus-edit-carton-archive",
                        color="danger",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button(
                        "Restore",
                        id="skus-edit-carton-restore",
                        color="warning",
                        outline=True,
                        className="me-2",
                    ),
                    dbc.Button("Save", id="skus-edit-carton-save", color="primary"),
                ]
            ),
        ],
        id="skus-edit-carton-modal",
        size="lg",
        backdrop="static",
    )


def _load_table_data() -> Dict[str, List[dict]]:
    with session_scope() as session:
        brand_counts = dict(
            session.execute(
                select(Product.brand_id, func.count())
                .where(Product.deleted_at.is_(None))
                .group_by(Product.brand_id)
            ).all()
        )
        package_labels: Dict[str, str] = {}
        pack_labels: Dict[str, str] = {}
        brands_data = []
        for brand in session.execute(
            select(Brand).where(Brand.deleted_at.is_(None)).order_by(Brand.name)
        ).scalars():
            product_count = brand_counts.get(brand.id, 0)
            brands_data.append(
                {
                    "name": brand.name,
                    "owner_company": brand.owner_company or "",
                    "product_count": product_count,
                }
            )

        products_data = []
        products = session.execute(
            select(Product, Brand.name)
            .join(Brand, Product.brand_id == Brand.id)
            .where(Product.deleted_at.is_(None), Brand.deleted_at.is_(None))
            .order_by(Brand.name, Product.name)
        ).all()
        for product, brand_name in products:
            category_value = _normalize_category_value(product.category)
            category_label = _format_category_label(category_value)
            products_data.append(
                {
                    "name": product.name,
                    "brand": brand_name,
                    "category": category_label,
                    "abv_percent": float(product.abv_percent or 0),
                }
            )

        packages_data = []
        for package in session.execute(
            select(PackageSpec)
            .where(PackageSpec.deleted_at.is_(None))
            .order_by(PackageSpec.type, PackageSpec.container_ml)
        ).scalars():
            package_label = f"{package.type.title()} {package.container_ml}mL"
            if package.can_form_factor:
                package_label += f" ({package.can_form_factor})"
            package_labels[package.id] = package_label
            packages_data.append(
                {
                    "type": package.type,
                    "container_ml": package.container_ml,
                    "can_form_factor": package.can_form_factor or "",
                }
            )

        pack_carton_map: Dict[str, List[str]] = {}
        pack_carton_rows = session.execute(
            select(
                CartonSpec.pack_spec_id,
                CartonSpec.units_per_carton,
                CartonSpec.pack_count,
            ).where(
                CartonSpec.deleted_at.is_(None),
                CartonSpec.pack_spec_id.is_not(None),
            )
        ).all()
        for pack_id, units_per_carton, pack_count in pack_carton_rows:
            if pack_id is None:
                continue
            label = f"{units_per_carton} units"
            if pack_count:
                label += f" ({pack_count} packs)"
            pack_carton_map.setdefault(pack_id, []).append(label)

        packs_data = []
        pack_rows = session.execute(
            select(
                PackSpec,
                PackageSpec.type,
                PackageSpec.container_ml,
                PackageSpec.can_form_factor,
                func.count(SKUPack.id).label("sku_count"),
            )
            .join(PackSpec.package_spec)
            .outerjoin(SKUPack, SKUPack.pack_spec_id == PackSpec.id)
            .where(PackSpec.deleted_at.is_(None), PackageSpec.deleted_at.is_(None))
            .group_by(
                PackSpec.id,
                PackageSpec.type,
                PackageSpec.container_ml,
                PackageSpec.can_form_factor,
            )
            .order_by(
                PackageSpec.type, PackageSpec.container_ml, PackSpec.units_per_pack
            )
        ).all()
        for pack_spec, pkg_type, container_ml, form_factor, sku_count in pack_rows:
            package_label = f"{pkg_type} {container_ml}mL"
            if form_factor:
                package_label += f" ({form_factor})"
            pack_label = f"{package_label} - {pack_spec.units_per_pack} pack"
            pack_labels[pack_spec.id] = pack_label
            packs_data.append(
                {
                    "package": package_label,
                    "units_per_pack": pack_spec.units_per_pack,
                    "gtin": pack_spec.gtin or "",
                    "sku_count": sku_count,
                    "carton_variants": ", ".join(pack_carton_map.get(pack_spec.id, []))
                    or "—",
                }
            )

        skus_data = []
        skus_rows = session.execute(
            select(
                SKU,
                Product.name,
                Brand.name,
                PackageSpec.type,
                PackageSpec.container_ml,
                PackageSpec.can_form_factor,
            )
            .join(SKU.product)
            .join(Product.brand)
            .join(SKU.package_spec)
            .where(
                Brand.deleted_at.is_(None),
                SKU.deleted_at.is_(None),
                Product.deleted_at.is_(None),
                PackageSpec.deleted_at.is_(None),
            )
            .order_by(Brand.name, Product.name)
        ).all()
        for (
            sku,
            product_name,
            brand_name,
            pkg_type,
            container_ml,
            form_factor,
        ) in skus_rows:
            package_label = f"{pkg_type} {container_ml}mL"
            if form_factor:
                package_label += f" ({form_factor})"
            skus_data.append(
                {
                    "product": f"{brand_name} - {product_name}",
                    "package": package_label,
                    "gtin": sku.gtin or "",
                    "is_active": "Yes" if sku.is_active else "No",
                }
            )

        cartons_data = []
        for carton in session.execute(
            select(CartonSpec)
            .where(CartonSpec.deleted_at.is_(None))
            .order_by(CartonSpec.units_per_carton, CartonSpec.created_at)
        ).scalars():
            is_pack = carton.pack_spec_id is not None
            mode_label = "Pack" if is_pack else "Unit"
            package_label = ""
            pack_label = ""
            if carton.package_spec_id:
                package_label = package_labels.get(carton.package_spec_id, "")
            if carton.pack_spec_id:
                pack_label = pack_labels.get(carton.pack_spec_id, "")
            cartons_data.append(
                {
                    "mode": mode_label,
                    "package_label": package_label,
                    "pack_label": pack_label,
                    "pack_count": carton.pack_count or "",
                    "units_per_carton": carton.units_per_carton,
                    "gtin": carton.gtin or "",
                    "notes": carton.notes or "",
                }
            )

    return {
        "brands": brands_data,
        "products": products_data,
        "packages": packages_data,
        "skus": skus_data,
        "cartons": cartons_data,
        "packs": packs_data,
    }


def _load_filter_options() -> Dict[str, List[dict]]:
    with session_scope() as session:
        brands = [
            {"label": brand.name, "value": brand.id}
            for brand in session.execute(select(Brand).order_by(Brand.name)).scalars()
        ]
        products = [
            {"label": f"{row.brand_name} - {row.product_name}", "value": row.product_id}
            for row in session.execute(
                select(
                    Product.id.label("product_id"),
                    Product.name.label("product_name"),
                    Brand.name.label("brand_name"),
                )
                .join(Brand, Product.brand_id == Brand.id)
                .where(Product.deleted_at.is_(None), Brand.deleted_at.is_(None))
                .order_by(Brand.name, Product.name)
            )
        ]
        packages = [
            {
                "label": f"{pkg.type} {pkg.container_ml}mL"
                + (f" ({pkg.can_form_factor})" if pkg.can_form_factor else ""),
                "value": pkg.id,
            }
            for pkg in session.execute(
                select(PackageSpec)
                .where(PackageSpec.deleted_at.is_(None))
                .order_by(PackageSpec.type, PackageSpec.container_ml)
            ).scalars()
        ]
        packs = [
            {
                "label": f"{row.type.title()} {row.container_ml}mL - {row.units_per_pack} pack",
                "value": row.pack_spec_id,
            }
            for row in session.execute(
                select(
                    PackSpec.id.label("pack_spec_id"),
                    PackSpec.units_per_pack,
                    PackageSpec.type,
                    PackageSpec.container_ml,
                )
                .join(PackSpec.package_spec)
                .where(PackSpec.deleted_at.is_(None), PackageSpec.deleted_at.is_(None))
                .order_by(
                    PackageSpec.type, PackageSpec.container_ml, PackSpec.units_per_pack
                )
            )
        ]
        cartons = [
            {"label": f"{carton.units_per_carton} units", "value": carton.id}
            for carton in session.execute(
                select(CartonSpec)
                .where(CartonSpec.deleted_at.is_(None))
                .order_by(CartonSpec.units_per_carton)
            ).scalars()
        ]
        channels = [
            row[0]
            for row in session.execute(
                select(PriceObservation.channel)
                .where(PriceObservation.channel.is_not(None))
                .distinct()
                .order_by(PriceObservation.channel)
            )
        ]
        bases = [
            row[0]
            for row in session.execute(
                select(PriceObservation.price_basis)
                .where(PriceObservation.price_basis.is_not(None))
                .distinct()
                .order_by(PriceObservation.price_basis)
            )
        ]
        companies = [
            {"label": company.name, "value": company.id}
            for company in session.execute(
                select(Company)
                .where(Company.deleted_at.is_(None))
                .order_by(Company.name)
            ).scalars()
        ]
        sku_options = [
            {
                "label": f"{row.brand_name} - {row.product_name}"
                + (f" ({row.gtin})" if row.gtin else ""),
                "value": row.sku_id,
            }
            for row in session.execute(
                select(
                    SKU.id.label("sku_id"),
                    SKU.gtin,
                    Product.name.label("product_name"),
                    Brand.name.label("brand_name"),
                )
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
    return {
        "brands": brands,
        "products": products,
        "packages": packages,
        "packs": packs,
        "cartons": cartons,
        "channels": _build_channel_options([value for value in channels if value]),
        "channel_default": CHANNEL_DEFAULT,
        "basis": _build_basis_options([value for value in bases if value]),
        "companies": companies,
        "skus": sku_options,
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


def _format_money(value: Optional[Decimal]) -> str:
    if value is None:
        return ""
    return f"{Decimal(value):.4f}"


def _optional_decimal_field(raw_value: Optional[str]) -> Optional[Decimal]:
    if raw_value is None:
        return None
    raw = str(raw_value).strip()
    if not raw:
        return None
    try:
        return Decimal(raw).quantize(Decimal("0.0001"))
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid decimal value: {raw}")
