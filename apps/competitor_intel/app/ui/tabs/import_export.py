from __future__ import annotations

import base64
import io
import os
import tempfile
from pathlib import Path
from typing import Dict

import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update

from ...config import BASE_DIR
from ...services import ObservationImporter, SKUImporter, session_scope

DOWNLOAD_SKU_ID = "import-export-download-skus"
DOWNLOAD_OBS_ID = "import-export-download-observations"
UPLOAD_SKU_ID = "import-export-upload-skus"
UPLOAD_OBS_ID = "import-export-upload-observations"
RESULT_SKU_ID = "import-export-result-skus"
RESULT_OBS_ID = "import-export-result-observations"
ALLOW_CREATE_SKU_ID = "import-export-allow-create-skus"
ALLOW_CREATE_OBS_ID = "import-export-allow-create-observations"

TEMPLATE_SKUS = BASE_DIR / "data_templates" / "skus.csv"
TEMPLATE_OBS = BASE_DIR / "data_templates" / "observations.csv"


def layout() -> dbc.Container:
    return dbc.Container(
        [
            dcc.Download(id=DOWNLOAD_SKU_ID),
            dcc.Download(id=DOWNLOAD_OBS_ID),
            html.H2("Import / Export", className="mb-4"),
            dbc.Row(
                [
                    dbc.Col(_export_card(), md=6),
                    dbc.Col(_import_card(), md=6),
                ],
                className="g-3",
            ),
        ],
        fluid=True,
    )


def register_callbacks(app):  # pragma: no cover - Dash wiring
    @app.callback(
        Output(DOWNLOAD_SKU_ID, "data"),
        Input("import-export-download-skus-btn", "n_clicks"),
    )
    def download_sku_template(n_clicks):
        if not n_clicks:
            return no_update
        return dcc.send_file(str(TEMPLATE_SKUS))

    @app.callback(
        Output(DOWNLOAD_OBS_ID, "data"),
        Input("import-export-download-obs-btn", "n_clicks"),
    )
    def download_obs_template(n_clicks):
        if not n_clicks:
            return no_update
        return dcc.send_file(str(TEMPLATE_OBS))

    @app.callback(
        Output(RESULT_SKU_ID, "children"),
        Output(RESULT_SKU_ID, "color"),
        Output(RESULT_SKU_ID, "is_open"),
        Input(UPLOAD_SKU_ID, "contents"),
        State(UPLOAD_SKU_ID, "filename"),
        State(ALLOW_CREATE_SKU_ID, "value"),
        prevent_initial_call=True,
    )
    def import_skus(contents, filename, allow_create):
        if not contents or not filename:
            return no_update, no_update, no_update
        result = _process_upload(
            contents, importer="sku", allow_create=bool(allow_create)
        )
        return _format_result_message(result)

    @app.callback(
        Output(RESULT_OBS_ID, "children"),
        Output(RESULT_OBS_ID, "color"),
        Output(RESULT_OBS_ID, "is_open"),
        Input(UPLOAD_OBS_ID, "contents"),
        State(UPLOAD_OBS_ID, "filename"),
        State(ALLOW_CREATE_OBS_ID, "value"),
        prevent_initial_call=True,
    )
    def import_observations(contents, filename, allow_create):
        if not contents or not filename:
            return no_update, no_update, no_update
        result = _process_upload(
            contents, importer="observations", allow_create=bool(allow_create)
        )
        return _format_result_message(result)


def _export_card() -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.H4("Download Templates", className="mb-3"),
                dbc.Button(
                    "Download SKUs Template",
                    id="import-export-download-skus-btn",
                    color="primary",
                    className="me-2",
                ),
                dbc.Button(
                    "Download Observations Template",
                    id="import-export-download-obs-btn",
                    color="primary",
                    outline=True,
                ),
                html.P(
                    "Templates include pack, carton, cost, and margin columns—see README for details on each field.",
                    className="text-muted small mt-3",
                ),
            ]
        )
    )


def _import_card() -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.H4("Import Data", className="mb-3"),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Checkbox(
                                id=ALLOW_CREATE_SKU_ID, value=True, className="me-2"
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            dbc.Label(
                                "Allow creation of referenced entities when importing SKUs",
                                html_for=ALLOW_CREATE_SKU_ID,
                            ),
                            className="d-flex align-items-center",
                        ),
                    ],
                    className="align-items-center g-0",
                ),
                dcc.Upload(
                    id=UPLOAD_SKU_ID,
                    children=html.Div(["Drag and drop or click to upload SKUs CSV"]),
                    multiple=False,
                    className="border border-secondary rounded p-3 mb-3 text-center text-muted",
                ),
                html.P(
                    "Required columns include brand, product, package, pack/carton metadata, and manufacturing cost fields.",
                    className="text-muted small fst-italic mb-3",
                ),
                dbc.Alert(id=RESULT_SKU_ID, is_open=False, className="mb-4"),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Checkbox(
                                id=ALLOW_CREATE_OBS_ID, value=False, className="me-2"
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            dbc.Label(
                                "Allow creation of missing entities when importing observations",
                                html_for=ALLOW_CREATE_OBS_ID,
                            ),
                            className="d-flex align-items-center",
                        ),
                    ],
                    className="align-items-center g-0",
                ),
                dcc.Upload(
                    id=UPLOAD_OBS_ID,
                    children=html.Div(
                        ["Drag and drop or click to upload Observations CSV"]
                    ),
                    multiple=False,
                    className="border border-secondary rounded p-3 mb-3 text-center text-muted",
                ),
                html.P(
                    "Observation CSV supports pack/carton pricing (price_basis) and margin columns; leave unused fields blank if not applicable.",
                    className="text-muted small fst-italic mb-3",
                ),
                dbc.Alert(id=RESULT_OBS_ID, is_open=False),
            ]
        )
    )


def _process_upload(
    contents: str, *, importer: str, allow_create: bool
) -> Dict[str, int | str]:
    header, data = contents.split(",", 1)
    decoded = base64.b64decode(data)
    buffer = io.StringIO(decoded.decode("utf-8"))
    buffer.seek(0)
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".csv") as tmp:
        tmp.write(buffer.read())
        tmp_path = Path(tmp.name)
    try:
        with session_scope() as session:
            if importer == "sku":
                importer_instance = SKUImporter(session, allow_create=allow_create)
            else:
                importer_instance = ObservationImporter(
                    session, allow_create=allow_create
                )
            report = importer_instance.run(tmp_path)
            session.commit()
    finally:
        if tmp_path.exists():
            os.unlink(tmp_path)
    return report.to_dict()


def _format_result_message(report: Dict[str, int | str]):
    message = f"Inserted: {report['inserted']} | Updated: {report.get('updated', 0)} | Duplicates: {report.get('duplicates', 0)}"
    if report.get("errors"):
        details = "\n".join(
            f"Row {err['row_number']}: {err['message']}" for err in report["errors"][:5]
        )
        message += f"\nErrors:\n{details}"
        return message, "danger", True
    return message, "success", True
