from __future__ import annotations

from typing import Callable, Dict

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, dcc, html
from flask import Response

from ..config import CONFIG
from .tabs import (
    analytics,
    data_quality,
    import_export,
    locations,
    observations,
    overview,
    settings,
    skus,
)
from .tabs import map as map_tab

TABS: Dict[str, Callable[[], dbc.Container]] = {
    "overview": overview.layout,
    "skus": skus.layout,
    "locations": locations.layout,
    "observations": observations.layout,
    "analytics": analytics.layout,
    "map": map_tab.layout,
    "data_quality": data_quality.layout,
    "import_export": import_export.layout,
    "settings": settings.layout,
}


def create_app() -> Dash:
    app = Dash(
        __name__,
        title="Competitor Intel",
        external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
        suppress_callback_exceptions=True,
        requests_pathname_prefix=CONFIG.requests_pathname_prefix,
    )
    app.layout = html.Div(
        [
            dcc.Location(id="app-location"),
            dcc.Store(id="app-current-tab", data="overview", storage_type="session"),
            dcc.Interval(id="interval-refresh-options", interval=60_000, n_intervals=0),
            dbc.Container(
                [
                    dcc.Tabs(
                        id="app-top-level-tabs",
                        value="competitor-intel",
                        children=[
                            dcc.Tab(
                                label="Competitor Intel",
                                value="competitor-intel",
                                children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dcc.Tabs(
                                                    id="app-subtabs",
                                                    value="overview",
                                                    children=[
                                                        dcc.Tab(
                                                            label="Overview",
                                                            value="overview",
                                                        ),
                                                        dcc.Tab(
                                                            label="SKUs", value="skus"
                                                        ),
                                                        dcc.Tab(
                                                            label="Locations",
                                                            value="locations",
                                                        ),
                                                        dcc.Tab(
                                                            label="Observations",
                                                            value="observations",
                                                        ),
                                                        dcc.Tab(
                                                            label="Analytics",
                                                            value="analytics",
                                                        ),
                                                        dcc.Tab(
                                                            label="Map", value="map"
                                                        ),
                                                        dcc.Tab(
                                                            label="Data Quality",
                                                            value="data_quality",
                                                        ),
                                                        dcc.Tab(
                                                            label="Import / Export",
                                                            value="import_export",
                                                        ),
                                                        dcc.Tab(
                                                            label="Settings",
                                                            value="settings",
                                                        ),
                                                    ],
                                                ),
                                                width=12,
                                            )
                                        ]
                                    ),
                                    html.Div(id="app-subtab-content", className="mt-4"),
                                ],
                            )
                        ],
                    )
                ],
                fluid=True,
                className="py-4",
            ),
        ]
    )

    _register_callbacks(app)
    overview.register_callbacks(app)
    observations.register_callbacks(app)
    skus.register_callbacks(app)
    locations.register_callbacks(app)
    analytics.register_callbacks(app)
    map_tab.register_callbacks(app)
    data_quality.register_callbacks(app)
    import_export.register_callbacks(app)
    settings.register_callbacks(app)

    server = app.server

    @server.get("/health")  # type: ignore[misc]
    def health():  # pragma: no cover - simple healthcheck
        return Response("ok", status=200, mimetype="text/plain")

    return app


def _register_callbacks(app: Dash) -> None:
    @app.callback(
        Output("app-subtabs", "value"),
        Output("app-current-tab", "data"),
        Input("app-location", "search"),
        State("app-subtabs", "value"),
    )
    def sync_url_to_tab(search: str, current_value: str):
        if not search:
            return current_value, current_value
        search = search.lstrip("?")
        for param in search.split("&"):
            if param.startswith("tab="):
                value = param.split("=", 1)[1]
                if value in TABS:
                    return value, value
        return current_value, current_value

    @app.callback(
        Output("app-subtab-content", "children"),
        Input("app-subtabs", "value"),
    )
    def render_subtab(value: str):
        layout_fn = TABS.get(value, overview.layout)
        return layout_fn()


def main() -> None:
    app = create_app()
    app.run(host=CONFIG.host, port=CONFIG.port, debug=CONFIG.debug)


if __name__ == "__main__":
    main()
