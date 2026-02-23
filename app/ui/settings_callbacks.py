"""Settings page callbacks for tab switching."""

from dash import Input, Output
from dash.exceptions import PreventUpdate


def register_settings_callbacks(app):
    """Register settings page callbacks for tab switching."""

    @app.callback(
        [
            Output("runtime-config-tab-content", "style"),
            Output("units-tab-content", "style"),
            Output("excise-rates-tab-content", "style"),
            Output("purchase-formats-tab-content", "style"),
            Output("qc-tests-tab-content", "style"),
            Output("work-areas-tab-content", "style"),
        ],
        Input("settings-tabs", "active_tab"),
    )
    def toggle_settings_tabs(active_tab):
        """Show/hide tab content based on active tab."""
        tab_order = [
            "runtime-config",
            "units",
            "excise-rates",
            "purchase-formats",
            "qc-tests",
            "work-areas",
        ]
        if active_tab not in tab_order:
            raise PreventUpdate
        return tuple(
            {"display": "block"} if active_tab == tab else {"display": "none"}
            for tab in tab_order
        )
