"""Callbacks for QC test types settings tab."""

from dash import Input, Output


def register_qc_test_types_callbacks(app, make_api_request):
    """Register callbacks for loading QC test types."""

    @app.callback(
        Output("qc-test-types-table", "data"),
        [
            Input("main-tabs", "active_tab"),
            Input("settings-tabs", "active_tab"),
            Input("qc-test-types-refresh", "n_clicks"),
        ],
    )
    def load_qc_test_types(main_tab, settings_tab, _refresh_clicks):
        """Load QC test types when the settings tab is active."""
        if main_tab != "settings" or settings_tab != "qc-tests":
            return []

        try:
            response = make_api_request("GET", "/work-orders/qc-test-types")

            if isinstance(response, dict):
                if response.get("error"):
                    return []
                raw_types = (
                    response.get("qc_test_types")
                    or response.get("items")
                    or response.get("data")
                    or []
                )
            elif isinstance(response, list):
                raw_types = response
            else:
                raw_types = []

            qc_types = []
            for item in raw_types:
                if not isinstance(item, dict):
                    continue

                formatted = dict(item)
                code = (item.get("code") or "").strip().upper()
                unit = (item.get("unit") or "").strip()

                if code == "ABV":
                    unit = unit or "%"
                    if unit.lower() in {"vol/vol"}:
                        unit = "%"
                elif code == "PH":
                    unit = unit or "pH"

                formatted["unit"] = unit
                if "is_active" in item:
                    formatted["is_active"] = "Yes" if item.get("is_active") else "No"
                qc_types.append(formatted)

            return qc_types
        except Exception as err:  # pragma: no cover - logging only
            print(f"Error loading QC test types: {err}")
            return []
