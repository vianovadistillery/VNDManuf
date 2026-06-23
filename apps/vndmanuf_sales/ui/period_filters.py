"""Shared period preset dropdown and date-range sync for Sales tabs."""

from __future__ import annotations

from dash import Input, Output, State, dcc, no_update

from apps.vndmanuf_sales.services.analytics import default_period, resolve_period_preset
from apps.vndmanuf_sales.ui.components import filter_dropdown

PERIOD_PRESET_OPTIONS = [
    {"label": "Current month", "value": "current_month"},
    {"label": "Last month", "value": "last_month"},
    {"label": "Last quarter", "value": "last_quarter"},
    {"label": "Current financial year", "value": "current_fy"},
    {"label": "Previous financial year", "value": "previous_fy"},
    {"label": "Custom", "value": "custom"},
]

DEFAULT_PERIOD_PRESET = "current_fy"


def default_period_iso() -> tuple[str, str]:
    start, end = default_period()
    return start.isoformat(), end.isoformat()


def period_preset_dropdown(dropdown_id: str):
    return filter_dropdown(
        dropdown_id,
        "Period",
        PERIOD_PRESET_OPTIONS,
        value=DEFAULT_PERIOD_PRESET,
    )


def period_applying_store(store_id: str):
    return dcc.Store(id=store_id, data=None)


def register_period_preset_callbacks(app, *, prefix: str) -> None:
    """Wire period preset dropdown to a DatePickerRange for the given ID prefix."""
    preset_id = f"{prefix}-period-preset"
    range_id = f"{prefix}-date-range"
    store_id = f"{prefix}-applying-preset"

    @app.callback(
        [
            Output(range_id, "start_date", allow_duplicate=True),
            Output(range_id, "end_date", allow_duplicate=True),
            Output(store_id, "data"),
        ],
        Input(preset_id, "value"),
        prevent_initial_call=True,
    )
    def _apply_period_preset(preset):
        if not preset or preset == "custom":
            return no_update, no_update, no_update
        start, end = resolve_period_preset(preset)
        return start.isoformat(), end.isoformat(), preset

    @app.callback(
        [
            Output(preset_id, "value", allow_duplicate=True),
            Output(store_id, "data", allow_duplicate=True),
        ],
        [
            Input(range_id, "start_date"),
            Input(range_id, "end_date"),
        ],
        [
            State(store_id, "data"),
            State(preset_id, "value"),
        ],
        prevent_initial_call=True,
    )
    def _manual_date_change(start_date, end_date, applying_preset, current_preset):
        if applying_preset and applying_preset == current_preset:
            return no_update, None
        return "custom", no_update
