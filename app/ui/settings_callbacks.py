"""Settings page callbacks for tab switching."""

from dash import Input, Output
from dash.exceptions import PreventUpdate


def register_settings_callbacks(app):
    """Register settings page callbacks for tab switching."""

    @app.callback(
        [
            Output("units-tab-content", "style"),
            Output("excise-rates-tab-content", "style"),
        ],
        Input("settings-tabs", "active_tab"),
    )
    def toggle_settings_tabs(active_tab):
        """Show/hide tab content based on active tab."""
        if active_tab == "units":
            return {"display": "block"}, {"display": "none"}
        elif active_tab == "excise-rates":
            return {"display": "none"}, {"display": "block"}
        raise PreventUpdate
