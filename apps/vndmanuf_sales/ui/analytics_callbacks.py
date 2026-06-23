"""Dash callbacks for Sales Overview and Products analytics tabs."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from dash import Input, Output, html, no_update
from dash.exceptions import PreventUpdate

from apps.vndmanuf_sales.ui.period_filters import register_period_preset_callbacks


def _parse_date_range(
    start_date: Optional[str], end_date: Optional[str]
) -> Tuple[Optional[str], Optional[str]]:
    if not start_date or not end_date:
        return None, None
    return start_date, end_date


def _analytics_params(
    start_date: Optional[str],
    end_date: Optional[str],
    channel_id: Optional[str],
    pricebook_id: Optional[str],
    segment: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    start, end = _parse_date_range(start_date, end_date)
    if not start or not end:
        return None
    params: Dict[str, Any] = {"start_date": start, "end_date": end}
    if channel_id:
        params["channel_id"] = channel_id
    if pricebook_id:
        params["pricebook_id"] = pricebook_id
    if segment:
        params["segment"] = segment
    return params


def _with_all_option(options: List[dict]) -> List[dict]:
    return [{"label": "All", "value": ""}] + list(options or [])


def _money(value: float) -> str:
    return f"${value:,.2f}"


def register_sales_analytics_callbacks(app, make_api_request):
    """Register Overview and Products analytics callbacks."""

    register_period_preset_callbacks(app, prefix="sales-overview")
    register_period_preset_callbacks(app, prefix="sales-products")

    @app.callback(
        [
            Output("sales-overview-channel-filter", "options"),
            Output("sales-analytics-filter-options-store", "data"),
        ],
        Input("sales-subtabs", "value"),
        prevent_initial_call=False,
    )
    def load_overview_filter_options(subtab_value):
        if subtab_value != "sales-overview":
            return no_update, no_update

        response = make_api_request("GET", "/sales/analytics/filter-options")
        if isinstance(response, dict) and response.get("error"):
            return [], None

        channels = _with_all_option(response.get("channels", []))
        return channels, response

    @app.callback(
        [
            Output("sales-products-channel-filter", "options"),
            Output("sales-products-pricebook-filter", "options"),
        ],
        Input("sales-subtabs", "value"),
        prevent_initial_call=False,
    )
    def load_products_filter_options(subtab_value):
        if subtab_value != "sales-products":
            return no_update, no_update

        response = make_api_request("GET", "/sales/analytics/filter-options")
        if isinstance(response, dict) and response.get("error"):
            return [], []

        channels = _with_all_option(response.get("channels", []))
        pricebooks = _with_all_option(response.get("pricebooks", []))
        return channels, pricebooks

    @app.callback(
        [
            Output("sales-kpi-total-orders", "children"),
            Output("sales-kpi-total-revenue", "children"),
            Output("sales-kpi-average-order", "children"),
            Output("sales-kpi-repeat-rate", "children"),
            Output("sales-overview-sparkline", "figure"),
            Output("sales-overview-customer-mix", "children"),
            Output("sales-overview-top-skus", "data"),
            Output("sales-overview-top-customers", "data"),
        ],
        [
            Input("sales-subtabs", "value"),
            Input("sales-overview-date-range", "start_date"),
            Input("sales-overview-date-range", "end_date"),
            Input("sales-overview-channel-filter", "value"),
        ],
        prevent_initial_call=False,
    )
    def refresh_overview(
        subtab_value,
        start_date,
        end_date,
        channel_id,
    ):
        if subtab_value != "sales-overview":
            raise PreventUpdate

        params = _analytics_params(start_date, end_date, channel_id, None)
        if not params:
            empty_mix = html.Ul(className="mb-0")
            return ("—", "—", "—", "—", no_update, empty_mix, [], [])

        response = make_api_request("GET", "/sales/analytics/overview", params)
        if isinstance(response, dict) and response.get("error"):
            return ("—", "—", "—", "—", no_update, [], [], [])

        trend = response.get("trend", [])
        figure = {
            "data": [
                {
                    "x": [row["date"] for row in trend],
                    "y": [row["revenue"] for row in trend],
                    "type": "scatter",
                    "mode": "lines",
                    "fill": "tozeroy",
                    "line": {"color": "#0d6efd"},
                    "fillcolor": "rgba(13,110,253,0.2)",
                    "name": "Revenue",
                }
            ],
            "layout": {
                "height": 160,
                "margin": {"l": 10, "r": 10, "t": 20, "b": 10},
                "showlegend": False,
                "template": "plotly_white",
                "xaxis": {"title": "Date"},
                "yaxis": {"title": "Revenue (Inc GST)"},
            },
        }

        customer_mix = html.Ul(
            [
                html.Li(f"New customers: {response.get('new_customers', 0)}"),
                html.Li(f"Repeat customers: {response.get('repeat_customers', 0)}"),
                html.Li(f"Inactive customers: {response.get('inactive_customers', 0)}"),
            ],
            className="mb-0",
        )

        return (
            f"{response.get('total_orders', 0):,}",
            _money(float(response.get("revenue_inc_gst", 0))),
            _money(float(response.get("average_order_value", 0))),
            f"{response.get('repeat_rate_pct', 0):.1f}%",
            figure,
            customer_mix,
            response.get("top_skus", []),
            response.get("top_customers", []),
        )

    @app.callback(
        [
            Output("sales-products-table", "data"),
            Output("sales-products-totals", "children"),
        ],
        [
            Input("sales-subtabs", "value"),
            Input("sales-products-date-range", "start_date"),
            Input("sales-products-date-range", "end_date"),
            Input("sales-products-channel-filter", "value"),
            Input("sales-products-pricebook-filter", "value"),
            Input("sales-products-type-filter", "value"),
        ],
        prevent_initial_call=False,
    )
    def refresh_products(
        subtab_value,
        start_date,
        end_date,
        channel_id,
        pricebook_id,
        segment,
    ):
        if subtab_value != "sales-products":
            raise PreventUpdate

        params = _analytics_params(
            start_date, end_date, channel_id, pricebook_id, segment
        )
        if not params:
            return [], "Totals: select a date range"

        response = make_api_request("GET", "/sales/analytics/products", params)
        if isinstance(response, dict) and response.get("error"):
            return [], "Totals: unable to load data"

        rows = []
        for row in response.get("rows", []):
            rows.append(
                {
                    "sku": row.get("sku", "—"),
                    "name": row.get("name", "—"),
                    "units": row.get("units", 0),
                    "revenue": row.get("revenue_inc_gst", 0),
                    "inventory": row.get("inventory", 0),
                    "channel_mix": row.get("channel_mix", "—"),
                }
            )

        total_units = float(response.get("total_units", 0))
        total_inc = float(response.get("total_revenue_inc_gst", 0))
        total_ex = float(response.get("total_revenue_ex_gst", 0))
        totals_text = (
            f"Totals: {total_units:,.2f} units · "
            f"{_money(total_inc)} inc GST · {_money(total_ex)} ex GST"
        )
        return rows, totals_text
