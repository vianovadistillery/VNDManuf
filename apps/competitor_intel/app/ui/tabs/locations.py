from __future__ import annotations

from datetime import datetime
from typing import List

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ...models import Company, Location
from ...services.db import session_scope
from ..components import data_table, loading_wrapper, modal_form

TABLE_ID = "locations-table"
REFRESH_STORE_ID = "locations-refresh-store"
ADD_MODAL_ID = "locations-add-modal"
EDIT_MODAL_ID = "locations-edit-modal"
TOAST_ID = "locations-toast"


def layout() -> dbc.Container:
    locations = _load_locations()
    company_options = _load_company_options()
    location_options = _build_location_options(locations)
    return dbc.Container(
        [
            html.H2("Locations", className="mb-4"),
            dcc.Store(id=REFRESH_STORE_ID, data={"ts": _timestamp()}),
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
                        {"id": "state", "name": "State"},
                        {"id": "suburb", "name": "Suburb"},
                        {"id": "postcode", "name": "Postcode"},
                        {"id": "lat", "name": "Latitude"},
                        {"id": "lon", "name": "Longitude"},
                    ],
                    data=locations,
                ),
            ),
            _add_modal(company_options),
            _edit_modal(company_options, location_options),
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

    @app.callback(
        Output(TABLE_ID, "data"),
        Output("locations-add-company", "options"),
        Output("locations-edit-company", "options"),
        Output("locations-edit-select", "options"),
        Input(REFRESH_STORE_ID, "data"),
    )
    def refresh_locations(_refresh):
        locations = _load_locations()
        company_options = _load_company_options()
        return (
            locations,
            company_options,
            company_options,
            _build_location_options(locations),
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
                state=state.strip(),
                suburb=suburb.strip(),
                postcode=(postcode or "").strip() or None,
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
        Output("locations-edit-lat", "value"),
        Output("locations-edit-lon", "value"),
        Input("locations-edit-select", "value"),
    )
    def populate_edit_fields(location_id):
        if not location_id:
            return (no_update,) * 7
        with session_scope() as session:
            location = session.get(Location, location_id)
            if not location:
                return (no_update,) * 7
            return (
                location.company_id,
                location.store_name,
                location.state,
                location.suburb,
                location.postcode,
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
            location.state = state.strip()
            location.suburb = suburb.strip()
            location.postcode = (postcode or "").strip() or None
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
                Location.state,
                Location.suburb,
                Location.postcode,
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
            "state": state,
            "suburb": suburb,
            "postcode": postcode or "",
            "lat": lat,
            "lon": lon,
        }
        for loc_id, company, store, state, suburb, postcode, lat, lon in rows
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
