"""Dash callbacks for Sales Customers & Sites sub-tab."""

from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate


def register_sales_customers_callbacks(app, make_api_request):
    """Register callbacks for Customers & Sites: customer/site dropdowns, tables, Add site."""

    @app.callback(
        [
            Output("sales-add-site-customer", "options"),
            Output("sales-customers-table", "data"),
            Output("sales-customer-sites-table", "data"),
        ],
        [
            Input("sales-subtabs", "value"),
            Input("sales-customers-sites-refresh", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_customers_and_sites(subtab_value, refresh_signal):
        if subtab_value != "sales-customers":
            return no_update, no_update, no_update
        customers_response = make_api_request("GET", "/sales/customers")
        sites_response = make_api_request("GET", "/sales/customer-sites")
        customers = customers_response if isinstance(customers_response, list) else []
        sites = sites_response if isinstance(sites_response, list) else []
        customer_options = [
            {"label": f"{c.get('name', '')} ({c.get('code', '')})", "value": c["id"]}
            for c in customers
        ]
        customer_map = {c["id"]: c.get("name", "") for c in customers}
        customers_table_data = [
            {
                "customer": c.get("name", ""),
                "type": c.get("customer_type") or "—",
                "email": c.get("email") or "—",
                "phone": c.get("phone") or "—",
                "orders": "—",
                "revenue": "—",
                "last_order": "—",
            }
            for c in customers
        ]
        sites_table_data = [
            {
                "customer": customer_map.get(s.get("customer_id", ""), "—"),
                "site": s.get("site_name", ""),
                "state": s.get("state", ""),
                "suburb": s.get("suburb") or "—",
                "postcode": s.get("postcode") or "—",
            }
            for s in sites
        ]
        return customer_options, customers_table_data, sites_table_data

    @app.callback(
        [
            Output("sales-add-site-feedback", "children"),
            Output("sales-add-site-customer", "value", allow_duplicate=True),
            Output("sales-add-site-name", "value", allow_duplicate=True),
            Output("sales-add-site-state", "value", allow_duplicate=True),
            Output("sales-add-site-suburb", "value", allow_duplicate=True),
            Output("sales-add-site-postcode", "value", allow_duplicate=True),
            Output("sales-customers-sites-refresh", "data", allow_duplicate=True),
        ],
        Input("sales-add-site-submit", "n_clicks"),
        State("sales-add-site-customer", "value"),
        State("sales-add-site-name", "value"),
        State("sales-add-site-state", "value"),
        State("sales-add-site-suburb", "value"),
        State("sales-add-site-postcode", "value"),
        State("sales-customers-sites-refresh", "data"),
        prevent_initial_call=True,
    )
    def submit_add_site(
        n_clicks,
        customer_id,
        site_name,
        state,
        suburb,
        postcode,
        refresh_data,
    ):
        if not n_clicks:
            raise PreventUpdate
        if not customer_id:
            return (
                "Select a customer.",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        if not (site_name or "").strip():
            return (
                "Enter a site name.",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        if not (state or "").strip():
            return (
                "Enter state (e.g. VIC, NSW).",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        payload = {
            "customer_id": customer_id,
            "site_name": (site_name or "").strip(),
            "state": (state or "").strip()[:8],
            "suburb": (suburb or "").strip() or None,
            "postcode": (postcode or "").strip() or None,
        }
        response = make_api_request("POST", "/sales/customer-sites", payload)
        if isinstance(response, dict) and response.get("error"):
            return (
                response["error"],
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        return (
            "Site added. You can select it when creating an order.",
            None,
            "",
            "",
            "",
            "",
            (refresh_data or 0) + 1,
        )
