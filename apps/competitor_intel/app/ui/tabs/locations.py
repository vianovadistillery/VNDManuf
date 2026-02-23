from __future__ import annotations

from datetime import datetime
from typing import List

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ...models import SKU, Brand, Company, Location, Product
from ...services import ensure_location_sku, fetch_location_inventory
from ...services.db import session_scope
from ..components import data_table, loading_wrapper, modal_form

TABLE_ID = "locations-table"
REFRESH_STORE_ID = "locations-refresh-store"
ADD_MODAL_ID = "locations-add-modal"
EDIT_MODAL_ID = "locations-edit-modal"
TOAST_ID = "locations-toast"
LINK_MODAL_ID = "locations-link-modal"
DETAIL_STORE_ID = "locations-detail-store"
DETAIL_SELECT_ID = "locations-detail-select"
DETAIL_TABLE_ID = "locations-detail-table"
DETAIL_HISTORY_ID = "locations-detail-history"
DETAIL_HISTORY_TOGGLE_ID = "locations-detail-history-toggle"
DETAIL_SUMMARY_ID = "locations-detail-summary"


def layout() -> dbc.Container:
    locations = _load_locations()
    company_options = _load_company_options()
    location_options = _build_location_options(locations)
    sku_options = _load_sku_options()
    return dbc.Container(
        [
            html.H2("Locations", className="mb-4"),
            dcc.Store(id=REFRESH_STORE_ID, data={"ts": _timestamp()}),
            dcc.Store(id=DETAIL_STORE_ID, data={}),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    "Add Location",
                                    id="locations-open-add",
                                    color="primary",
                                    size="sm",
                                ),
                                dbc.Button(
                                    "Edit / Delete Location",
                                    id="locations-open-edit",
                                    color="secondary",
                                    outline=True,
                                    size="sm",
                                ),
                            ]
                        ),
                        width="auto",
                    )
                ],
                className="g-2 mb-3",
            ),
            loading_wrapper(
                "locations-table-wrapper",
                data_table(
                    TABLE_ID,
                    columns=[
                        {"id": "company", "name": "Company"},
                        {"id": "store_name", "name": "Store Name"},
                        {"id": "address", "name": "Address"},
                        {"id": "state", "name": "State"},
                        {"id": "suburb", "name": "Suburb"},
                        {"id": "postcode", "name": "Postcode"},
                        {"id": "chain_alignment", "name": "Chain Alignment"},
                        {"id": "main_contact", "name": "Main Contact"},
                        {"id": "decision_maker", "name": "Decision Maker"},
                        {"id": "lat", "name": "Latitude"},
                        {"id": "lon", "name": "Longitude"},
                    ],
                    data=locations,
                ),
            ),
            loading_wrapper("locations-detail-wrapper", _detail_card(location_options)),
            _add_modal(company_options),
            _edit_modal(company_options, location_options),
            _link_modal(location_options, sku_options),
            dbc.Toast(
                id=TOAST_ID,
                header="Locations",
                is_open=False,
                dismissable=True,
                duration=4000,
                className="position-fixed top-0 end-0 m-3",
            ),
        ],
        fluid=True,
    )


def register_callbacks(app):  # pragma: no cover - Dash wiring
    _modal_toggle(app, "locations-open-add", "locations-add-cancel", ADD_MODAL_ID)
    _modal_toggle(app, "locations-open-edit", "locations-edit-cancel", EDIT_MODAL_ID)
    _modal_toggle(app, "locations-open-link", "locations-link-cancel", LINK_MODAL_ID)

    @app.callback(
        Output(TABLE_ID, "data"),
        Output("locations-add-company", "options"),
        Output("locations-edit-company", "options"),
        Output("locations-edit-select", "options"),
        Output(DETAIL_SELECT_ID, "options"),
        Output("locations-link-location", "options"),
        Output("locations-link-skus", "options"),
        Input(REFRESH_STORE_ID, "data"),
    )
    def refresh_locations(_refresh):
        locations = _load_locations()
        company_options = _load_company_options()
        location_options = _build_location_options(locations)
        sku_options = _load_sku_options()
        return (
            locations,
            company_options,
            company_options,
            location_options,
            location_options,
            location_options,
            sku_options,
        )

    @app.callback(
        Output(TOAST_ID, "children"),
        Output(TOAST_ID, "icon"),
        Output(TOAST_ID, "is_open"),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Output(ADD_MODAL_ID, "is_open", allow_duplicate=True),
        Input("locations-add-submit", "n_clicks"),
        State("locations-add-company", "value"),
        State("locations-add-store", "value"),
        State("locations-add-state", "value"),
        State("locations-add-suburb", "value"),
        State("locations-add-postcode", "value"),
        State("locations-add-address", "value"),
        State("locations-add-chain", "value"),
        State("locations-add-main-contact", "value"),
        State("locations-add-decision-maker", "value"),
        State("locations-add-lat", "value"),
        State("locations-add-lon", "value"),
        prevent_initial_call=True,
    )
    def save_new_location(
        n_clicks,
        company_id,
        store_name,
        state,
        suburb,
        postcode,
        address,
        chain_alignment,
        main_contact,
        decision_maker,
        lat,
        lon,
    ):
        if not n_clicks:
            return no_update, no_update, no_update, no_update, no_update
        if not company_id or not state or not suburb:
            return (
                "Company, state, and suburb are required.",
                "danger",
                True,
                no_update,
                True,
            )
        with session_scope() as session:
            location = Location(
                company_id=company_id,
                store_name=(store_name or "").strip() or None,
                address=(address or "").strip() or None,
                state=state.strip(),
                suburb=suburb.strip(),
                postcode=(postcode or "").strip() or None,
                chain_alignment=(chain_alignment or "").strip() or None,
                main_contact=(main_contact or "").strip() or None,
                decision_maker=(decision_maker or "").strip() or None,
                lat=_to_float(lat),
                lon=_to_float(lon),
            )
            session.add(location)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                return (
                    "A location with the same company, store, state, suburb, and postcode already exists.",
                    "danger",
                    True,
                    no_update,
                    True,
                )
        return ("Location created", "success", True, {"ts": _timestamp()}, False)

    @app.callback(
        Output("locations-edit-company", "value"),
        Output("locations-edit-store", "value"),
        Output("locations-edit-state", "value"),
        Output("locations-edit-suburb", "value"),
        Output("locations-edit-postcode", "value"),
        Output("locations-edit-address", "value"),
        Output("locations-edit-chain", "value"),
        Output("locations-edit-main-contact", "value"),
        Output("locations-edit-decision-maker", "value"),
        Output("locations-edit-lat", "value"),
        Output("locations-edit-lon", "value"),
        Input("locations-edit-select", "value"),
    )
    def populate_edit_fields(location_id):
        if not location_id:
            return (no_update,) * 11
        with session_scope() as session:
            location = session.get(Location, location_id)
            if not location:
                return (no_update,) * 11
            return (
                location.company_id,
                location.store_name,
                location.state,
                location.suburb,
                location.postcode,
                location.address,
                location.chain_alignment,
                location.main_contact,
                location.decision_maker,
                location.lat,
                location.lon,
            )

    @app.callback(
        Output(TOAST_ID, "children", allow_duplicate=True),
        Output(TOAST_ID, "icon", allow_duplicate=True),
        Output(TOAST_ID, "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Output(EDIT_MODAL_ID, "is_open", allow_duplicate=True),
        Input("locations-edit-save", "n_clicks"),
        Input("locations-edit-delete", "n_clicks"),
        State("locations-edit-select", "value"),
        State("locations-edit-company", "value"),
        State("locations-edit-store", "value"),
        State("locations-edit-state", "value"),
        State("locations-edit-suburb", "value"),
        State("locations-edit-postcode", "value"),
        State("locations-edit-address", "value"),
        State("locations-edit-chain", "value"),
        State("locations-edit-main-contact", "value"),
        State("locations-edit-decision-maker", "value"),
        State("locations-edit-lat", "value"),
        State("locations-edit-lon", "value"),
        prevent_initial_call=True,
    )
    def handle_edit(
        save_clicks,
        delete_clicks,
        location_id,
        company_id,
        store_name,
        state,
        suburb,
        postcode,
        address,
        chain_alignment,
        main_contact,
        decision_maker,
        lat,
        lon,
    ):
        ctx = dash.callback_context
        if not ctx.triggered or not location_id:
            return (
                "Choose a location before saving or deleting.",
                "warning",
                True,
                no_update,
                True,
            )
        action = ctx.triggered[0]["prop_id"].split(".")[0]
        if action == "locations-edit-delete":
            with session_scope() as session:
                location = session.get(Location, location_id)
                if not location:
                    return ("Location not found.", "danger", True, no_update, True)
                session.delete(location)
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    return (
                        "Cannot delete this location while observations reference it.",
                        "danger",
                        True,
                        no_update,
                        True,
                    )
            return ("Location deleted", "success", True, {"ts": _timestamp()}, False)

        if not company_id or not state or not suburb:
            return (
                "Company, state, and suburb are required.",
                "danger",
                True,
                no_update,
                True,
            )
        with session_scope() as session:
            location = session.get(Location, location_id)
            if not location:
                return ("Location not found.", "danger", True, no_update, True)
            location.company_id = company_id
            location.store_name = (store_name or "").strip() or None
            location.address = (address or "").strip() or None
            location.state = state.strip()
            location.suburb = suburb.strip()
            location.postcode = (postcode or "").strip() or None
            location.chain_alignment = (chain_alignment or "").strip() or None
            location.main_contact = (main_contact or "").strip() or None
            location.decision_maker = (decision_maker or "").strip() or None
            location.lat = _to_float(lat)
            location.lon = _to_float(lon)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                return (
                    "Update failed: duplicate location for this company.",
                    "danger",
                    True,
                    no_update,
                    True,
                )
        return ("Location updated", "success", True, {"ts": _timestamp()}, False)

    @app.callback(
        Output(TOAST_ID, "children", allow_duplicate=True),
        Output(TOAST_ID, "icon", allow_duplicate=True),
        Output(TOAST_ID, "is_open", allow_duplicate=True),
        Output(REFRESH_STORE_ID, "data", allow_duplicate=True),
        Output(LINK_MODAL_ID, "is_open", allow_duplicate=True),
        Output(DETAIL_SELECT_ID, "value", allow_duplicate=True),
        Input("locations-link-submit", "n_clicks"),
        State("locations-link-location", "value"),
        State("locations-link-skus", "value"),
        State("locations-link-notes", "value"),
        State(DETAIL_SELECT_ID, "value"),
        prevent_initial_call=True,
    )
    def link_skus(n_clicks, location_id, sku_ids, notes, current_detail):
        if not n_clicks:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        if not location_id:
            return (
                "Select a location before linking SKUs.",
                "danger",
                True,
                no_update,
                True,
                current_detail,
            )
        sku_ids = list(sku_ids or [])
        if not sku_ids:
            return (
                "Choose at least one SKU to link.",
                "warning",
                True,
                no_update,
                True,
                current_detail,
            )
        note_text = (notes or "").strip() or None
        with session_scope() as session:
            for sku_id in sku_ids:
                ensure_location_sku(
                    session,
                    location_id=location_id,
                    sku_id=sku_id,
                    observation_dt=None,
                    is_manual=True,
                    notes=note_text,
                )
        return (
            f"Linked {len(sku_ids)} SKU(s) to the selected location.",
            "success",
            True,
            {"ts": _timestamp()},
            False,
            location_id,
        )

    @app.callback(
        Output(DETAIL_STORE_ID, "data"),
        Output(DETAIL_TABLE_ID, "data"),
        Output(DETAIL_SUMMARY_ID, "children"),
        Output(DETAIL_HISTORY_ID, "children"),
        Input(DETAIL_SELECT_ID, "value"),
        Input(DETAIL_HISTORY_TOGGLE_ID, "value"),
        Input(REFRESH_STORE_ID, "data"),
        State(DETAIL_STORE_ID, "data"),
    )
    def update_detail(selected_location, history_toggle, _refresh, store_state):
        history_enabled = bool(history_toggle)
        location_id = selected_location or (store_state or {}).get("location_id")
        if not location_id:
            return (
                {},
                [],
                _render_location_prompt(),
                [],
            )
        with session_scope() as session:
            payload = fetch_location_inventory(
                session,
                location_id=location_id,
                include_history=history_enabled,
                history_limit=100 if history_enabled else 0,
            )
        items = payload.get("items") or []
        summary = _render_location_summary(payload.get("location"), len(items))
        table_rows = [_inventory_row(item) for item in items]
        history_children = _render_inventory_history(items) if history_enabled else []
        state = {
            "location_id": location_id,
            "include_history": history_enabled,
        }
        return state, table_rows, summary, history_children

    @app.callback(
        Output("locations-link-location", "value"),
        Input(DETAIL_SELECT_ID, "value"),
        prevent_initial_call=True,
    )
    def sync_link_location(selected_location):
        return selected_location


def _add_modal(company_options: List[dict]) -> dbc.Modal:
    body = [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Select(
                        id="locations-add-company",
                        options=company_options,
                        placeholder="Select Company",
                    ),
                    md=6,
                    className="mt-3",
                ),
                dbc.Col(
                    dbc.Input(id="locations-add-store", placeholder="Store name"),
                    md=6,
                    className="mt-3",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(id="locations-add-state", placeholder="State"),
                    md=4,
                    className="mt-3",
                ),
                dbc.Col(
                    dbc.Input(id="locations-add-suburb", placeholder="Suburb"),
                    md=4,
                    className="mt-3",
                ),
                dbc.Col(
                    dbc.Input(id="locations-add-postcode", placeholder="Postcode"),
                    md=4,
                    className="mt-3",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(id="locations-add-address", placeholder="Address line"),
                    md=6,
                    className="mt-3",
                ),
                dbc.Col(
                    dbc.Input(
                        id="locations-add-chain",
                        placeholder="Chain alignment (e.g., Dan Murphy's)",
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
                        id="locations-add-main-contact", placeholder="Main contact"
                    ),
                    md=6,
                    className="mt-3",
                ),
                dbc.Col(
                    dbc.Input(
                        id="locations-add-decision-maker",
                        placeholder="Decision maker",
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
                        id="locations-add-lat", type="number", placeholder="Latitude"
                    ),
                    md=6,
                    className="mt-3",
                ),
                dbc.Col(
                    dbc.Input(
                        id="locations-add-lon", type="number", placeholder="Longitude"
                    ),
                    md=6,
                    className="mt-3",
                ),
            ]
        ),
    ]
    return modal_form(
        ADD_MODAL_ID,
        "Add Location",
        body,
        submit_id="locations-add-submit",
        close_id="locations-add-cancel",
        size="lg",
    )


def _edit_modal(company_options: List[dict], location_options: List[dict]) -> dbc.Modal:
    return dbc.Modal(
        [
            dbc.ModalHeader("Edit / Delete Location"),
            dbc.ModalBody(
                [
                    dbc.Select(
                        id="locations-edit-select",
                        options=location_options,
                        placeholder="Select a location",
                        className="mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Select(
                                    id="locations-edit-company",
                                    options=company_options,
                                    placeholder="Company",
                                ),
                                md=6,
                                className="mt-3",
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="locations-edit-store", placeholder="Store name"
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
                                    id="locations-edit-state", placeholder="State"
                                ),
                                md=4,
                                className="mt-3",
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="locations-edit-suburb", placeholder="Suburb"
                                ),
                                md=4,
                                className="mt-3",
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="locations-edit-postcode", placeholder="Postcode"
                                ),
                                md=4,
                                className="mt-3",
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(
                                    id="locations-edit-address",
                                    placeholder="Address line",
                                ),
                                md=6,
                                className="mt-3",
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="locations-edit-chain",
                                    placeholder="Chain alignment (e.g., Dan Murphy's)",
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
                                    id="locations-edit-main-contact",
                                    placeholder="Main contact",
                                ),
                                md=6,
                                className="mt-3",
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="locations-edit-decision-maker",
                                    placeholder="Decision maker",
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
                                    id="locations-edit-lat",
                                    type="number",
                                    placeholder="Latitude",
                                ),
                                md=6,
                                className="mt-3",
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="locations-edit-lon",
                                    type="number",
                                    placeholder="Longitude",
                                ),
                                md=6,
                                className="mt-3",
                            ),
                        ]
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="locations-edit-cancel",
                        color="secondary",
                        className="me-2",
                    ),
                    dbc.Button(
                        "Delete",
                        id="locations-edit-delete",
                        color="danger",
                        className="me-2",
                    ),
                    dbc.Button("Save", id="locations-edit-save", color="primary"),
                ]
            ),
        ],
        id=EDIT_MODAL_ID,
        size="lg",
        backdrop="static",
    )


def _detail_card(location_options: List[dict]) -> dbc.Card:
    return dbc.Card(
        [
            dbc.CardHeader("Store Inventory"),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Dropdown(
                                    id=DETAIL_SELECT_ID,
                                    options=location_options,
                                    placeholder="Select a location",
                                    clearable=True,
                                ),
                                md=5,
                                className="mt-2",
                            ),
                            dbc.Col(
                                dbc.Checklist(
                                    id=DETAIL_HISTORY_TOGGLE_ID,
                                    options=[
                                        {
                                            "label": "Show observation history",
                                            "value": "history",
                                        }
                                    ],
                                    value=[],
                                    switch=True,
                                ),
                                md=4,
                                className="mt-3",
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Link SKUs Manually",
                                    id="locations-open-link",
                                    color="secondary",
                                    outline=True,
                                    className="mt-2",
                                ),
                                md=3,
                                className="d-flex justify-content-end align-items-start",
                            ),
                        ],
                        className="g-2",
                    ),
                    html.Div(id=DETAIL_SUMMARY_ID, className="mt-3"),
                    data_table(
                        DETAIL_TABLE_ID,
                        columns=[
                            {"id": "sku_label", "name": "SKU"},
                            {"id": "latest_observed", "name": "Last Observed"},
                            {"id": "price_basis", "name": "Price Basis"},
                            {"id": "price_inc_gst", "name": "Price (inc GST)"},
                            {"id": "price_ex_gst", "name": "Price (ex GST)"},
                            {"id": "unit_price_inc_gst", "name": "Unit Price"},
                            {"id": "channel", "name": "Channel"},
                            {"id": "price_context", "name": "Price Context"},
                            {"id": "cost_type", "name": "Cost Type"},
                            {"id": "cost_per_unit", "name": "Cost / Unit"},
                            {"id": "cost_per_pack", "name": "Cost / Pack"},
                            {"id": "cost_per_carton", "name": "Cost / Carton"},
                            {"id": "is_manual", "name": "Manual Link"},
                            {"id": "notes", "name": "Notes"},
                        ],
                        data=[],
                    ),
                    html.Div(id=DETAIL_HISTORY_ID, className="mt-4"),
                ]
            ),
        ],
        className="mt-4 shadow-sm",
    )


def _link_modal(location_options: List[dict], sku_options: List[dict]) -> dbc.Modal:
    return dbc.Modal(
        [
            dbc.ModalHeader("Link SKUs to Location"),
            dbc.ModalBody(
                [
                    dbc.Select(
                        id="locations-link-location",
                        options=location_options,
                        placeholder="Select a location",
                    ),
                    dcc.Dropdown(
                        id="locations-link-skus",
                        options=sku_options,
                        multi=True,
                        placeholder="Select SKUs to link",
                        className="mt-3",
                    ),
                    dbc.Textarea(
                        id="locations-link-notes",
                        placeholder="Notes (optional)",
                        className="mt-3",
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel",
                        id="locations-link-cancel",
                        color="secondary",
                        className="me-2",
                    ),
                    dbc.Button(
                        "Link SKUs",
                        id="locations-link-submit",
                        color="primary",
                    ),
                ]
            ),
        ],
        id=LINK_MODAL_ID,
        size="lg",
        backdrop="static",
    )


def _modal_toggle(app, open_id: str, close_id: str, modal_id: str) -> None:
    @app.callback(
        Output(modal_id, "is_open"),
        Input(open_id, "n_clicks"),
        Input(close_id, "n_clicks"),
        State(modal_id, "is_open"),
        prevent_initial_call=True,
    )
    def toggle(open_clicks, close_clicks, is_open):
        trigger = dash.callback_context.triggered_id
        if not trigger:
            return is_open
        if trigger == open_id:
            return True
        return False


def _load_locations() -> List[dict]:
    with session_scope() as session:
        rows = session.execute(
            select(
                Location.id,
                Company.name,
                Location.store_name,
                Location.address,
                Location.state,
                Location.suburb,
                Location.postcode,
                Location.chain_alignment,
                Location.main_contact,
                Location.decision_maker,
                Location.lat,
                Location.lon,
            )
            .join(Location.company)
            .where(Location.deleted_at.is_(None), Company.deleted_at.is_(None))
            .order_by(Company.name, Location.suburb, Location.store_name)
        ).all()
    return [
        {
            "id": loc_id,
            "company": company,
            "store_name": store or "",
            "address": address or "",
            "state": state,
            "suburb": suburb,
            "postcode": postcode or "",
            "chain_alignment": chain_alignment or "",
            "main_contact": main_contact or "",
            "decision_maker": decision_maker or "",
            "lat": lat,
            "lon": lon,
        }
        for (
            loc_id,
            company,
            store,
            address,
            state,
            suburb,
            postcode,
            chain_alignment,
            main_contact,
            decision_maker,
            lat,
            lon,
        ) in rows
    ]


def _load_company_options() -> List[dict]:
    with session_scope() as session:
        companies = session.execute(
            select(Company.id, Company.name)
            .where(Company.deleted_at.is_(None))
            .order_by(Company.name)
        ).all()
    return [{"label": name, "value": id_} for id_, name in companies]


def _build_location_options(locations: List[dict]) -> List[dict]:
    options: List[dict] = []
    for entry in locations:
        label_parts = [entry["company"]]
        if entry.get("store_name"):
            label_parts.append(entry["store_name"])
        label_parts.extend([entry["suburb"], entry["state"]])
        label = " • ".join(filter(None, label_parts))
        options.append({"label": label, "value": entry["id"]})
    return options


def _load_sku_options() -> List[dict]:
    with session_scope() as session:
        rows = session.execute(
            select(SKU.id, Brand.name, Product.name, SKU.gtin)
            .join(SKU.product)
            .join(Product.brand)
            .where(
                SKU.deleted_at.is_(None),
                Product.deleted_at.is_(None),
                Brand.deleted_at.is_(None),
            )
            .order_by(Brand.name, Product.name)
        ).all()
    options: List[dict] = []
    for sku_id, brand, product, gtin in rows:
        label = f"{brand} • {product}"
        if gtin:
            label = f"{label} (GTIN {gtin})"
        options.append({"label": label, "value": sku_id})
    return options


def _render_location_prompt():
    return html.Div(
        "Select a location to view linked products.",
        className="text-muted fst-italic",
    )


def _render_location_summary(location: dict | None, item_count: int) -> html.Div:
    if not location:
        return _render_location_prompt()
    store_name = location.get("store_name") or "Unnamed Store"
    address = location.get("address")
    suburb = location.get("suburb")
    state = location.get("state")
    postcode = location.get("postcode")
    location_line = " • ".join(filter(None, [suburb, state, postcode]))
    chain = location.get("chain_alignment")
    main_contact = location.get("main_contact")
    decision_maker = location.get("decision_maker")

    children = [
        html.H5(store_name, className="mb-1"),
        html.Div(location_line, className="text-muted"),
    ]
    if address:
        children.append(html.Div(address, className="text-muted"))
    if chain:
        children.append(html.Div(f"Chain: {chain}", className="text-muted"))
    if main_contact:
        children.append(
            html.Div(f"Main contact: {main_contact}", className="text-muted")
        )
    if decision_maker:
        children.append(
            html.Div(f"Decision maker: {decision_maker}", className="text-muted")
        )
    children.append(
        html.Div(
            f"{item_count} SKU{'s' if item_count != 1 else ''} linked to this location.",
            className="mt-3 fw-semibold",
        )
    )
    return html.Div(children)


def _format_datetime(value: datetime | None) -> str:
    if value is None:
        return ""
    try:
        if value.tzinfo is not None:
            value = value.astimezone()
    except (ValueError, OSError):
        pass
    return value.strftime("%Y-%m-%d %H:%M")


def _format_currency(value) -> str:
    if value is None:
        return ""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return ""
    return f"{numeric:,.2f}"


def _inventory_row(item) -> dict:
    latest = item.latest_observation
    cost = item.latest_cost
    observed_dt = (
        latest.observed_at if latest and latest.observed_at else item.last_observed_dt
    )
    return {
        "sku_label": item.sku_label,
        "latest_observed": _format_datetime(observed_dt),
        "price_basis": (latest.price_basis or "").title() if latest else "",
        "price_inc_gst": _format_currency(latest.price_inc_gst if latest else None),
        "price_ex_gst": _format_currency(latest.price_ex_gst if latest else None),
        "unit_price_inc_gst": _format_currency(
            latest.unit_price_inc_gst if latest else None
        ),
        "channel": latest.channel if latest else "",
        "price_context": latest.price_context if latest else "",
        "cost_type": (cost.cost_type or "").title() if cost else "",
        "cost_per_unit": _format_currency(cost.cost_per_unit if cost else None),
        "cost_per_pack": _format_currency(cost.cost_per_pack if cost else None),
        "cost_per_carton": _format_currency(cost.cost_per_carton if cost else None),
        "is_manual": "Yes" if item.is_manual else "No",
        "notes": item.notes or "",
    }


def _render_inventory_history(items) -> list:
    panels = []
    for item in items:
        if not item.history:
            continue
        entries = []
        for obs in item.history:
            entries.append(
                html.Li(
                    f"{_format_datetime(obs.observed_at)} — "
                    f"{(obs.price_basis or '').title()} "
                    f"{_format_currency(obs.price_inc_gst)} "
                    f"(Channel: {obs.channel}, Context: {obs.price_context})",
                    className="mb-1",
                )
            )
        panels.append(
            dbc.AccordionItem(
                html.Ul(entries, className="mb-0"),
                title=item.sku_label,
            )
        )
    if not panels:
        return [
            html.Div(
                "No observation history yet for this location.",
                className="text-muted fst-italic",
            )
        ]
    return [dbc.Accordion(panels, start_collapsed=True, flush=True)]


def _to_float(value) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _timestamp() -> str:
    return datetime.utcnow().isoformat()


__all__ = ["layout", "register_callbacks"]
