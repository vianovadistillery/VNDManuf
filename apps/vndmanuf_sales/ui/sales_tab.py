"""Top-level Sales tab layout and callbacks."""

from __future__ import annotations

from pathlib import Path

from dash import Input, Output, dcc, html, no_update

from apps.vndmanuf_sales.ui.pages import (
    analytics,
    customers,
    import_export,
    orders,
    overview,
    products,
    settings,
)

_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SALES_TEMPLATE = _DATA_DIR / "sales_orders_template.csv"
DOCKET_TEMPLATE = _DATA_DIR / "delivery_docket_template.csv"

DEFAULT_SALES_SUBTAB = "sales-orders"

# All panels stay mounted (show/hide via style) so callbacks can target their IDs
# even when another sales sub-tab is active — same pattern as manufacturing-panel.
SALES_SUBTAB_PANELS = (
    ("sales-orders", "sales-panel-orders", orders.layout_orders_list),
    ("sales-overview", "sales-panel-overview", overview.layout),
    ("sales-customers", "sales-panel-customers", customers.layout),
    ("sales-products", "sales-panel-products", products.layout),
    ("sales-analytics", "sales-panel-analytics", analytics.layout),
    ("sales-import-export", "sales-panel-import-export", import_export.layout),
    ("sales-settings", "sales-panel-settings", settings.layout),
)


def _subtab_panel_style(active: bool) -> dict:
    return {"display": "block" if active else "none"}


def layout():
    return html.Div(
        [
            dcc.Tabs(
                id="sales-subtabs",
                value=DEFAULT_SALES_SUBTAB,
                children=[
                    dcc.Tab(label="Orders", value="sales-orders"),
                    dcc.Tab(label="Overview", value="sales-overview"),
                    dcc.Tab(label="Customers & Sites", value="sales-customers"),
                    dcc.Tab(label="Products", value="sales-products"),
                    dcc.Tab(label="Analytics", value="sales-analytics"),
                    dcc.Tab(label="Import / Export", value="sales-import-export"),
                    dcc.Tab(label="Settings", value="sales-settings"),
                ],
                className="mb-3",
            ),
            html.Div(
                id="sales-subtab-content",
                children=[
                    html.Div(
                        id=panel_id,
                        children=layout_factory(),
                        style=_subtab_panel_style(subtab_value == DEFAULT_SALES_SUBTAB),
                    )
                    for subtab_value, panel_id, layout_factory in SALES_SUBTAB_PANELS
                ],
            ),
            dcc.Store(id="sales-import-pending-store"),
            dcc.Store(id="sales-import-summary-store"),
            dcc.Store(id="sales-analytics-filter-options-store"),
        ],
        className="sales-tab",
    )


def register_callbacks(app):
    @app.callback(
        [Output(panel_id, "style") for _, panel_id, _ in SALES_SUBTAB_PANELS],
        Input("sales-subtabs", "value"),
        prevent_initial_call=False,
    )
    def show_subtab(subtab_value):
        active = subtab_value or DEFAULT_SALES_SUBTAB
        return [
            _subtab_panel_style(value == active) for value, _, _ in SALES_SUBTAB_PANELS
        ]

    @app.callback(
        Output("sales-import-download-sales-template", "data"),
        Input("sales-import-download-sales-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_sales_template(n_clicks):
        if not n_clicks:
            return no_update
        return dcc.send_file(str(SALES_TEMPLATE))

    @app.callback(
        Output("sales-import-download-docket-template", "data"),
        Input("sales-import-download-docket-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_docket_template(n_clicks):
        if not n_clicks:
            return no_update
        return dcc.send_file(str(DOCKET_TEMPLATE))

    @app.callback(
        Output("sales-import-summary-table", "data"),
        Input("sales-import-summary-store", "data"),
        prevent_initial_call=False,
    )
    def update_import_table(data):
        return data or []
