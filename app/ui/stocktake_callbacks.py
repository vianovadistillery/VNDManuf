"""Stocktake callbacks for Dash UI."""

import json

import dash
from dash import Input, Output, State
from dash.exceptions import PreventUpdate


def register_stocktake_callbacks(app, make_api_request):
    """Register stocktake page callbacks."""

    @app.callback(
        Output("stocktake-table", "data", allow_duplicate=True),
        Input("stocktake-start", "n_clicks"),
        prevent_initial_call=True,
    )
    def start_stocktake(n_clicks):
        """Load purchasable products with current system SOH."""
        if not n_clicks:
            raise PreventUpdate

        response = make_api_request(
            "GET", "/inventory/stocktake/sheet", {"is_purchase": True}
        )
        if isinstance(response, dict) and "error" in response:
            return []

        items = response.get("items", []) if isinstance(response, dict) else []
        return items

    @app.callback(
        [
            Output("stocktake-table", "data", allow_duplicate=True),
            Output("stocktake-total-items", "children", allow_duplicate=True),
            Output("stocktake-variance-count", "children", allow_duplicate=True),
            Output("stocktake-total-variance", "children", allow_duplicate=True),
            Output("stocktake-status", "children", allow_duplicate=True),
        ],
        Input("stocktake-calc", "n_clicks"),
        State("stocktake-table", "data"),
        prevent_initial_call=True,
    )
    def calculate_variances(n_clicks, rows):
        """Recalculate variance columns from physical counts."""
        if not n_clicks or not rows:
            raise PreventUpdate

        updated = []
        variance_count = 0
        total_variance = 0.0

        for row in rows:
            row = dict(row)
            system_soh = float(row.get("system_soh") or 0)
            physical = row.get("physical_count")
            try:
                physical_count = float(physical if physical is not None else system_soh)
            except (TypeError, ValueError):
                physical_count = system_soh

            variance = physical_count - system_soh
            variance_pct = (variance / system_soh * 100) if system_soh > 0 else 0.0

            row["physical_count"] = physical_count
            row["variance"] = variance
            row["variance_pct"] = variance_pct
            updated.append(row)

            if abs(variance) > 0.0005:
                variance_count += 1
                total_variance += variance

        return (
            updated,
            str(len(updated)),
            str(variance_count),
            f"{total_variance:.3f}",
            "Variances calculated",
        )

    @app.callback(
        [
            Output("stocktake-table", "data", allow_duplicate=True),
            Output("stocktake-status", "children", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
        ],
        Input("stocktake-update", "n_clicks"),
        [
            State("stocktake-table", "data"),
            State("stocktake-ref", "value"),
            State("stocktake-counter", "value"),
            State("stocktake-date", "date"),
        ],
        prevent_initial_call=True,
    )
    def apply_stocktake(n_clicks, rows, reference, counter, stocktake_date):
        """Apply stocktake adjustments for lines with variance."""
        if not n_clicks or not rows:
            raise PreventUpdate

        counts = []
        for row in rows:
            product_id = row.get("product_id")
            if not product_id:
                continue
            physical = row.get("physical_count")
            try:
                physical_count = float(physical if physical is not None else 0)
            except (TypeError, ValueError):
                physical_count = 0.0
            system_soh = float(row.get("system_soh") or 0)
            if abs(physical_count - system_soh) < 0.0005:
                continue
            counts.append(
                {
                    "product_id": product_id,
                    "physical_count": physical_count,
                    "update_soh": True,
                    "notes": row.get("notes"),
                }
            )

        if not counts:
            return (
                rows,
                "No variances to apply",
                True,
                "Stocktake",
                "No lines with variance to update.",
            )

        payload = {
            "reference": reference,
            "counter": counter,
            "stocktake_date": stocktake_date,
            "apply_adjustments": True,
            "counts": counts,
        }
        response = make_api_request("POST", "/inventory/stocktake", payload)

        if isinstance(response, dict) and "error" in response:
            error_msg = response["error"]
            if isinstance(error_msg, str):
                try:
                    error_msg = json.loads(error_msg).get("message", error_msg)
                except (json.JSONDecodeError, TypeError):
                    pass
            return rows, "Update failed", True, "Error", str(error_msg)

        variances = response.get("variances", []) if isinstance(response, dict) else []
        by_product = {v.get("product_id"): v for v in variances}

        refreshed = []
        for row in rows:
            row = dict(row)
            product_id = row.get("product_id")
            if product_id in by_product:
                v = by_product[product_id]
                row["system_soh"] = v.get("physical_count", row.get("system_soh"))
                row["variance"] = 0.0
                row["variance_pct"] = 0.0
            refreshed.append(row)

        adjusted = (
            response.get("items_adjusted", 0) if isinstance(response, dict) else 0
        )
        status = f"Updated {adjusted} item(s)"
        return (
            refreshed,
            status,
            True,
            "Stocktake complete",
            f"Applied adjustments to {adjusted} product(s).",
        )

    @app.callback(
        Output("stocktake-table", "data", allow_duplicate=True),
        Input("stocktake-table", "data_timestamp"),
        State("stocktake-table", "data"),
        prevent_initial_call=True,
    )
    def sync_variance_on_edit(_ts, rows):
        """Keep variance columns in sync when physical counts are edited inline."""
        ctx = dash.callback_context
        if not ctx.triggered or not rows:
            raise PreventUpdate

        updated = []
        for row in rows:
            row = dict(row)
            system_soh = float(row.get("system_soh") or 0)
            physical = row.get("physical_count")
            try:
                physical_count = float(physical if physical is not None else system_soh)
            except (TypeError, ValueError):
                physical_count = system_soh
            variance = physical_count - system_soh
            variance_pct = (variance / system_soh * 100) if system_soh > 0 else 0.0
            row["physical_count"] = physical_count
            row["variance"] = variance
            row["variance_pct"] = variance_pct
            updated.append(row)
        return updated
