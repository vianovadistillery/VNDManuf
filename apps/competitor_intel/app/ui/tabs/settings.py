from __future__ import annotations

from typing import Dict

import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, no_update

from ...config import BASE_DIR, CONFIG

ENV_PATH = BASE_DIR / ".env"


def layout() -> dbc.Container:
    return dbc.Container(
        [
            html.H2("Settings", className="mb-4"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H4("Runtime Configuration", className="mb-3"),
                                    html.Div(
                                        [
                                            dbc.Label("Host"),
                                            dbc.Input(
                                                id="settings-host", value=CONFIG.host
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    html.Div(
                                        [
                                            dbc.Label("Port"),
                                            dbc.Input(
                                                id="settings-port",
                                                type="number",
                                                value=CONFIG.port,
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    html.Div(
                                        [
                                            dbc.Label("Default GST Rate"),
                                            dbc.Input(
                                                id="settings-gst",
                                                type="number",
                                                step=0.01,
                                                value=CONFIG.default_gst_rate,
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    html.Div(
                                        [
                                            dbc.Label("Default Currency"),
                                            dbc.Input(
                                                id="settings-currency",
                                                value=CONFIG.default_currency,
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    html.Div(
                                        [
                                            dbc.Label("Evidence Folder"),
                                            dbc.Input(
                                                id="settings-evidence",
                                                value=str(CONFIG.evidence_root),
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    dbc.Button(
                                        "Save",
                                        id="settings-save",
                                        color="primary",
                                        className="mt-4",
                                    ),
                                    dbc.Alert(
                                        id="settings-feedback",
                                        is_open=False,
                                        className="mt-3",
                                    ),
                                ]
                            ),
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H4("Instructions", className="mb-3"),
                                    html.P(
                                        "Settings are stored in apps/competitor_intel/.env. Saving here updates that file. "
                                        "Restart the app to apply host/port changes.",
                                        className="text-muted",
                                    ),
                                    html.P(
                                        "Evidence folder paths are relative to the project root unless an absolute path is provided.",
                                        className="text-muted",
                                    ),
                                ]
                            ),
                        ),
                        md=6,
                    ),
                ],
                className="g-3",
            ),
        ],
        fluid=True,
    )


def register_callbacks(app):  # pragma: no cover - Dash wiring
    @app.callback(
        Output("settings-feedback", "children"),
        Output("settings-feedback", "color"),
        Output("settings-feedback", "is_open"),
        Input("settings-save", "n_clicks"),
        State("settings-host", "value"),
        State("settings-port", "value"),
        State("settings-gst", "value"),
        State("settings-currency", "value"),
        State("settings-evidence", "value"),
        prevent_initial_call=True,
    )
    def save_settings(n_clicks, host, port, gst, currency, evidence):
        if not n_clicks:
            return no_update, no_update, no_update
        try:
            updated = {
                "COMPINTEL_APP_HOST": host,
                "COMPINTEL_APP_PORT": str(port),
                "COMPINTEL_DEFAULT_GST_RATE": f"{float(gst):.4f}",
                "COMPINTEL_DEFAULT_CURRENCY": (currency or "AUD").upper(),
                "COMPINTEL_EVIDENCE_ROOT": evidence or str(CONFIG.evidence_root),
            }
            _write_env(updated)
        except Exception as exc:  # pragma: no cover - safeguard
            return (f"Failed to save settings: {exc}", "danger", True)
        return ("Settings updated", "success", True)


def _write_env(updates: Dict[str, str]) -> None:
    existing = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            existing[key.strip()] = value.strip()
    existing.update(updates)
    content = "\n".join(f"{key}={value}" for key, value in existing.items()) + "\n"
    ENV_PATH.write_text(content)
