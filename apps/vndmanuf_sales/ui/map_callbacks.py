"""Dash callbacks for the sales overview customer map (OpenStreetMap tiles)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import dash_leaflet as dl
from dash import Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate


def _dropdown_option(option: dict) -> dict:
    return {"label": option.get("label", ""), "value": option.get("value", "")}


def _with_all_option(options: List[dict]) -> List[dict]:
    return [{"label": "All", "value": ""}] + [
        _dropdown_option(o) for o in (options or [])
    ]


def _map_params(
    start_date: Optional[str],
    end_date: Optional[str],
    sales_rep_id: Optional[str],
    buying_group_id: Optional[str],
    price_level: Optional[str],
    volume_band: Optional[str],
    relationship_status: Optional[str],
) -> Optional[Dict[str, Any]]:
    if not start_date or not end_date:
        return None
    params: Dict[str, Any] = {
        "start_date": start_date,
        "end_date": end_date,
    }
    if sales_rep_id:
        params["sales_rep_id"] = sales_rep_id
    if buying_group_id:
        params["buying_group_id"] = buying_group_id
    if price_level:
        params["price_level"] = price_level
    if volume_band:
        params["volume_band"] = volume_band
    if relationship_status:
        params["relationship_status"] = relationship_status
    return params


def _map_viewport(points: List[dict]) -> Tuple[List[float], int]:
    """Centre map on Australia or on customer cluster."""
    if not points:
        return [-25.27, 133.77], 4
    lats = [p["lat"] for p in points]
    lons = [p["lon"] for p in points]
    center = [sum(lats) / len(lats), sum(lons) / len(lons)]
    span = max(max(lats) - min(lats), max(lons) - min(lons), 0.05)
    if span > 25:
        zoom = 4
    elif span > 8:
        zoom = 5
    elif span > 3:
        zoom = 6
    elif span > 1:
        zoom = 8
    elif span > 0.2:
        zoom = 10
    else:
        zoom = 12
    return center, zoom


def _marker_radius(revenue: float) -> int:
    return int(max(7, min(22, 7 + revenue / 2500)))


def _build_markers(points: List[dict]) -> list:
    markers = []
    for p in points:
        color = p.get("buying_group_color") or "#9E9E9E"
        addr = p.get("address_display") or "—"
        loc = p.get("location_label") or p.get("location_source") or "—"
        markers.append(
            dl.CircleMarker(
                center=[p["lat"], p["lon"]],
                radius=_marker_radius(float(p.get("period_revenue") or 0)),
                color="#ffffff",
                weight=2,
                fillColor=color,
                fillOpacity=0.88,
                children=[
                    dl.Popup(
                        [
                            html.B(p["name"]),
                            html.Br(),
                            html.Span(addr),
                            html.Br(),
                            html.Em(loc),
                            html.Br(),
                            html.Span(f"Group: {p.get('buying_group_name', '—')}"),
                            html.Br(),
                            html.Span(f"Revenue: ${p.get('period_revenue', 0):,.0f}"),
                        ]
                    )
                ],
            )
        )
    return markers


def _legend_children(legend: List[dict]) -> list:
    if not legend:
        return [html.Span("No groups", className="text-muted")]
    return [
        html.Span(
            [
                html.Span(
                    style={
                        "display": "inline-block",
                        "width": "12px",
                        "height": "12px",
                        "borderRadius": "50%",
                        "backgroundColor": item.get("color", "#9E9E9E"),
                        "marginRight": "4px",
                    }
                ),
                item.get("name", "?"),
            ],
            className="me-3 d-inline-block",
        )
        for item in legend
    ]


def register_sales_map_callbacks(app, make_api_request):
    @app.callback(
        [
            Output("sales-map-rep-filter", "options"),
            Output("sales-map-buying-group-filter", "options"),
            Output("sales-map-price-level-filter", "options"),
            Output("sales-map-volume-filter", "options"),
            Output("sales-map-status-filter", "options"),
        ],
        Input("sales-subtabs", "value"),
        prevent_initial_call=False,
    )
    def load_map_filter_options(subtab_value):
        if subtab_value != "sales-overview":
            return (no_update,) * 5
        response = make_api_request(
            "GET", "/sales/analytics/customer-map/filter-options"
        )
        if isinstance(response, dict) and response.get("error"):
            return [], [], [], [], []
        return (
            _with_all_option(response.get("sales_reps", [])),
            _with_all_option(response.get("buying_groups", [])),
            _with_all_option(response.get("price_levels", [])),
            _with_all_option(response.get("volume_bands", [])),
            _with_all_option(response.get("relationship_statuses", [])),
        )

    @app.callback(
        [
            Output("sales-map-enrich-feedback", "children"),
            Output("sales-map-enrich-store", "data"),
        ],
        Input("sales-map-enrich-btn", "n_clicks"),
        State("sales-map-enrich-store", "data"),
        prevent_initial_call=True,
    )
    def enrich_osm(n_clicks, refresh):
        if not n_clicks:
            raise PreventUpdate
        response = make_api_request(
            "POST",
            "/sales/customers/enrich-locations",
            {"limit": 15, "dry_run": False, "use_llm": False},
        )
        if isinstance(response, dict) and response.get("error"):
            return response["error"], no_update
        msg = (
            f"[OpenStreetMap] {response.get('updated', 0)} updated, "
            f"{response.get('not_found', 0)} not found, "
            f"{response.get('skipped', 0)} skipped (≈1/sec)."
        )
        return msg, (refresh or 0) + 1

    @app.callback(
        [
            Output("sales-map-enrich-feedback", "children", allow_duplicate=True),
            Output("sales-map-enrich-store", "data", allow_duplicate=True),
        ],
        Input("sales-map-enrich-ai-btn", "n_clicks"),
        State("sales-map-enrich-store", "data"),
        prevent_initial_call=True,
    )
    def enrich_ai(n_clicks, refresh):
        if not n_clicks:
            raise PreventUpdate
        response = make_api_request(
            "POST",
            "/sales/customers/enrich-locations",
            {"limit": 8, "dry_run": False, "use_llm": True},
        )
        if isinstance(response, dict) and response.get("error"):
            return response["error"], no_update
        msg = (
            f"[AI + OSM] {response.get('updated', 0)} updated, "
            f"{response.get('not_found', 0)} not found. "
            f"Requires OpenAI key (Nova U → AI Settings)."
        )
        return msg, (refresh or 0) + 1

    @app.callback(
        [
            Output("sales-customer-map-markers", "children"),
            Output("sales-customer-map", "center"),
            Output("sales-customer-map", "zoom"),
            Output("sales-map-legend", "children"),
            Output("sales-map-summary", "children"),
        ],
        [
            Input("sales-subtabs", "value"),
            Input("sales-overview-date-range", "start_date"),
            Input("sales-overview-date-range", "end_date"),
            Input("sales-map-rep-filter", "value"),
            Input("sales-map-buying-group-filter", "value"),
            Input("sales-map-price-level-filter", "value"),
            Input("sales-map-volume-filter", "value"),
            Input("sales-map-status-filter", "value"),
            Input("sales-map-enrich-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def refresh_customer_map(
        subtab_value,
        start_date,
        end_date,
        sales_rep_id,
        buying_group_id,
        price_level,
        volume_band,
        relationship_status,
        _enrich_tick,
    ):
        if subtab_value != "sales-overview":
            raise PreventUpdate

        params = _map_params(
            start_date,
            end_date,
            sales_rep_id,
            buying_group_id,
            price_level,
            volume_band,
            relationship_status,
        )
        if not params:
            center, zoom = _map_viewport([])
            return [], center, zoom, [], "Select a date range"

        response = make_api_request("GET", "/sales/analytics/customer-map", params)
        if isinstance(response, dict) and response.get("error"):
            center, zoom = _map_viewport([])
            return [], center, zoom, [], response["error"]

        points = response.get("points", [])
        legend = response.get("legend", [])
        exact = sum(
            1 for p in points if p.get("location_source") in ("customer", "site")
        )
        approx = sum(
            1 for p in points if p.get("location_source", "").startswith("state")
        )
        summary = (
            f"{response.get('mapped_customers', 0)} on map "
            f"({exact} exact, {approx} approximate) · "
            f"{response.get('unmapped_customers', 0)} without location"
        )
        center, zoom = _map_viewport(points)
        return (
            _build_markers(points),
            center,
            zoom,
            _legend_children(legend),
            summary,
        )
