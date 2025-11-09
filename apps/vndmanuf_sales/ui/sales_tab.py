"""Top-level Sales tab layout and callbacks."""

from __future__ import annotations

from pathlib import Path

from dash import Input, Output, dcc, html

from apps.vndmanuf_sales.ui.pages import (
    analytics,
    customers,
    import_export,
    orders,
    overview,
    products,
    settings,
)

SUB_TAB_COMPONENTS = {
    "sales-overview": overview.layout,
    "sales-orders": orders.layout,
    "sales-customers": customers.layout,
    "sales-products": products.layout,
    "sales-analytics": analytics.layout,
    "sales-import-export": import_export.layout,
    "sales-settings": settings.layout,
}


def layout():
    return html.Div(
        [
            dcc.Tabs(
                id="sales-subtabs",
                value="sales-overview",
                children=[
                    dcc.Tab(label="Overview", value="sales-overview"),
                    dcc.Tab(label="Orders", value="sales-orders"),
                    dcc.Tab(label="Customers & Sites", value="sales-customers"),
                    dcc.Tab(label="Products", value="sales-products"),
                    dcc.Tab(label="Analytics", value="sales-analytics"),
                    dcc.Tab(label="Import / Export", value="sales-import-export"),
                    dcc.Tab(label="Settings", value="sales-settings"),
                ],
                className="mb-3",
            ),
            html.Div(id="sales-subtab-content"),
            dcc.Store(id="sales-import-summary-store"),
        ],
        className="sales-tab",
    )


def register_callbacks(app):
    @app.callback(
        Output("sales-subtab-content", "children"),
        Input("sales-subtabs", "value"),
        prevent_initial_call=False,
    )
    def render_subtab(subtab_value):
        layout_factory = SUB_TAB_COMPONENTS.get(subtab_value, overview.layout)
        return layout_factory()

    @app.callback(
        Output("sales-import-summary-store", "data"),
        Input("sales-import-upload", "filename"),
        prevent_initial_call=True,
    )
    def handle_import(filename):
        if not filename:
            return []
        name = Path(filename).name
        return [
            {
                "order_ref": "—",
                "customer": "—",
                "lines": "—",
                "status": "Queued",
                "message": f"Queued import for {name}",
            }
        ]

    @app.callback(
        Output("sales-import-summary-table", "data"),
        Input("sales-import-summary-store", "data"),
        prevent_initial_call=False,
    )
    def update_import_table(data):
        return data or []
