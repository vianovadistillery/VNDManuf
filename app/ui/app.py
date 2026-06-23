"""Dash UI application for VNDManuf (tabs + callbacks mounting)."""

from __future__ import annotations

# stdlib
import importlib.util
import json
import os
import sys
from typing import Any, Dict, Optional

# third-party
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import requests

# (…rest of your file…)
# stdlib/third-party imports first
from dash import (
    Input,
    Output,
    State,
    callback_context,
    dcc,
    html,
    no_update,
)
from dash.exceptions import PreventUpdate

from apps.vndmanuf_sales.ui.analytics_callbacks import (
    register_sales_analytics_callbacks,
)

# local imports (after third-party)
from apps.vndmanuf_sales.ui.crm_callbacks import register_crm_callbacks
from apps.vndmanuf_sales.ui.crm_settings_callbacks import (
    register_crm_settings_callbacks,
)
from apps.vndmanuf_sales.ui.customers_callbacks import (
    register_sales_customers_callbacks,
)
from apps.vndmanuf_sales.ui.import_callbacks import register_sales_import_callbacks
from apps.vndmanuf_sales.ui.map_callbacks import register_sales_map_callbacks
from apps.vndmanuf_sales.ui.orders_callbacks import register_sales_orders_callbacks
from apps.vndmanuf_sales.ui.pages import crm as crm_page
from apps.vndmanuf_sales.ui.sales_tab import (
    layout as sales_tab_layout,
)
from apps.vndmanuf_sales.ui.sales_tab import (
    register_callbacks as register_sales_tab_callbacks,
)

from .contacts_callbacks import register_contacts_callbacks  # noqa: E402
from .excise_rates_callbacks import register_excise_rates_callbacks  # noqa: E402
from .formulas_callbacks import register_formulas_callbacks  # noqa: E402
from .pages.batch_processing_page import BatchProcessingPage  # noqa: E402
from .pages.batch_reports_page import BatchReportsPage  # noqa: E402
from .pages.contacts_page import ContactsPage  # noqa: E402

# Import new page modules from pages/ subdirectory (the directory)
from .pages.formulas_page import FormulasPage  # noqa: E402
from .pages.home_page import HOME_NAV_ITEMS, HomePage  # noqa: E402
from .pages.rm_reports_page import RmReportsPage  # noqa: E402
from .pages.stocktake_page import StocktakePage  # noqa: E402
from .pages.work_orders_page import WorkOrdersPage  # noqa: E402
from .pages_enhanced import products_page_enhanced  # noqa: E402
from .product_section_callbacks import register_product_section_callbacks  # noqa: E402
from .products_callbacks import register_product_callbacks  # noqa: E402
from .purchase_formats_callbacks import (
    register_purchase_formats_callbacks,  # noqa: E402
)
from .purchase_usage_callbacks import register_purchase_usage_callbacks  # noqa: E402
from .qc_test_types_callbacks import register_qc_test_types_callbacks  # noqa: E402
from .settings_callbacks import register_settings_callbacks  # noqa: E402
from .stocktake_callbacks import register_stocktake_callbacks  # noqa: E402
from .training_callbacks import register_training_callbacks  # noqa: E402
from .units_callbacks import register_units_callbacks  # noqa: E402
from .work_areas_callbacks import register_work_areas_callbacks  # noqa: E402

# Register work orders callbacks
from .work_orders_callbacks import register_work_orders_callbacks  # noqa: E402

# Load pages.py as a module
spec = importlib.util.spec_from_file_location(
    "pages_old", os.path.join(os.path.dirname(__file__), "pages.py")
)
pages_old = importlib.util.module_from_spec(spec)
sys.modules["pages_old"] = pages_old
spec.loader.exec_module(pages_old)

# Access functions from old pages.py
batches_page = pages_old.batches_page
inventory_page = pages_old.inventory_page
reports_page = pages_old.reports_page


# Xero integration temporarily disabled - will re-enable later
# from .pages.accounting_integration_page import accounting_integration_page

# Initialize Dash app with Bootstrap theme
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS_FOLDER = os.path.join(PROJECT_ROOT, "assets")

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    assets_folder=ASSETS_FOLDER,
)

# API base URL
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# Header: both images use same height for vertical alignment
HEADER_IMG_HEIGHT = "52px"

# Header content helper: left side = vndmanuf branding image, right side = logo (added in layout)
header_children = [
    html.Img(
        src="/assets/vndmanuf.jpg",
        alt="VNDManuf",
        style={
            "height": HEADER_IMG_HEIGHT,
            "width": "auto",
            "objectFit": "contain",
            "display": "block",
        },
    ),
    dbc.Alert(
        id="demo-mode-alert",
        children="Connecting to API...",
        color="info",
        dismissable=True,
        className="mb-3",
        style={"display": "none"},
    ),
]
header_children.append(html.Hr())

# App layout
app.layout = dbc.Container(
    [
        # Header: vndmanuf centered, logo right-aligned; same image height for alignment
        dbc.Row(
            [
                dbc.Col(
                    [*header_children],
                    width="auto",
                    className="flex-grow-1 d-flex flex-column justify-content-center align-items-center",
                ),
                dbc.Col(
                    html.Img(
                        src="/assets/logo.jpg",
                        alt="Logo",
                        style={
                            "height": HEADER_IMG_HEIGHT,
                            "width": "auto",
                            "objectFit": "contain",
                        },
                    ),
                    width="auto",
                    className="d-flex justify-content-end align-items-center",
                ),
            ],
            className="align-items-center mb-2",
        ),
        # Navigation tabs (level 1: Home, Manufacturing, Contacts, Sales, …)
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Tabs(
                            id="main-tabs",
                            active_tab="home",
                            children=[
                                dbc.Tab(label="Home", tab_id="home"),
                                dbc.Tab(label="Manufacturing", tab_id="manufacturing"),
                                dbc.Tab(label="Contacts", tab_id="contacts"),
                                dbc.Tab(label="Sales", tab_id="sales"),
                                dbc.Tab(label="CRM", tab_id="crm"),
                                dbc.Tab(label="Reports", tab_id="reports"),
                                dbc.Tab(label="Settings", tab_id="settings"),
                                dbc.Tab(label="Nova University", tab_id="training"),
                            ],
                            className="mb-4",
                        )
                    ],
                    width=12,
                )
            ]
        ),
        # Effective tab store (manufacturing sub-tab or main tab when not manufacturing)
        dcc.Store(id="effective-tab-store", data="home"),
        # Tab content
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(id="tab-content"),
                        # Xero integration temporarily disabled - will re-enable later
                        # accounting_integration_page.register_callbacks(app)
                    ]
                )
            ]
        ),
        # Toast notifications
        dbc.Toast(
            id="toast",
            header="Notification",
            is_open=False,
            dismissable=True,
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        ),
    ],
    fluid=True,
)

app.validation_layout = html.Div(
    [
        app.layout,
        html.Button(id="wo-issue-submit-btn"),
        dcc.Store(id="wo-detail-refresh-trigger"),
        dcc.Store(id="wo-planned-qty-refresh"),
        dcc.Store(id="wo-detail-allow-input-edit"),
        html.Div(
            [
                dbc.Button(id="wo-release-btn"),
                dbc.Button(id="wo-start-btn"),
                dbc.Button(id="wo-void-btn"),
                dbc.Button(id="wo-reopen-btn"),
                dbc.Button(id="wo-planned-qty-save"),
                dbc.Input(id="wo-planned-qty-input"),
                html.Div(id="wo-detail-tab-content"),
            ],
            style={"display": "none"},
        ),
    ]
)


def make_api_request(
    method: str, endpoint: str, data: Optional[Dict] = None
) -> Dict[str, Any]:
    """Make API request and return response."""
    try:
        url = f"{API_BASE_URL}{endpoint}"

        if method.upper() == "GET":
            response = requests.get(url, params=data)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data)
        elif method.upper() == "PATCH":
            response = requests.patch(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        else:
            return {"error": f"Unsupported method: {method}"}

        # Handle successful responses (204 No Content has no body)
        if response.status_code in [200, 201]:
            return response.json()
        if response.status_code == 204:
            return {}
        # Handle error responses
        else:
            try:
                # Try to parse JSON error response
                error_data = response.json()
                if isinstance(error_data, dict):
                    if "message" in error_data:
                        return {"error": json.dumps(error_data)}
                    elif "detail" in error_data:
                        return {"error": json.dumps({"message": error_data["detail"]})}
            except (ValueError, KeyError, TypeError):
                pass

            return {
                "error": json.dumps(
                    {
                        "message": f"API Error {response.status_code}: {response.text[:100]}"
                    }
                )
            }

    except requests.exceptions.ConnectionError:
        # Return sample data when API is not available
        print(f"API not available, using sample data for {endpoint}")
        return get_sample_data(endpoint)
    except Exception as e:
        return {"error": json.dumps({"message": f"Request failed: {str(e)}"})}


def get_sample_data(endpoint: str) -> Dict[str, Any]:
    """Return sample data when API is not available."""
    print(f"Getting sample data for: {endpoint}")  # Debug print

    if endpoint == "/products/":
        return {
            "products": [
                {
                    "id": "1",
                    "sku": "PAINT-001",
                    "name": "Trade Paint Base",
                    "description": "White base paint for tinting",
                    "density_kg_per_l": 1.2,
                    "abv_percent": None,
                    "is_active": True,
                },
                {
                    "id": "2",
                    "sku": "PAINT-002",
                    "name": "Clear Varnish",
                    "description": "Clear protective varnish",
                    "density_kg_per_l": 0.9,
                    "abv_percent": None,
                    "is_active": True,
                },
                {
                    "id": "3",
                    "sku": "SOLVENT-001",
                    "name": "Paint Thinner",
                    "description": "Mineral spirits for thinning paint",
                    "density_kg_per_l": 0.8,
                    "abv_percent": None,
                    "is_active": True,
                },
            ]
        }
    elif endpoint == "/batches/":
        return {
            "batches": [
                {
                    "id": "1",
                    "batch_code": "B060149",
                    "work_order_id": "WO-001",
                    "product_id": "PAINT-001",
                    "planned_quantity_kg": 370.0,
                    "actual_quantity_kg": 365.5,
                    "status": "completed",
                },
                {
                    "id": "2",
                    "batch_code": "B060150",
                    "work_order_id": "WO-002",
                    "product_id": "PAINT-002",
                    "planned_quantity_kg": 200.0,
                    "actual_quantity_kg": 198.2,
                    "status": "in_progress",
                },
            ]
        }
    elif endpoint == "/inventory/lots/":
        return {
            "lots": [
                {
                    "id": "1",
                    "lot_code": "LOT-001",
                    "product_id": "PAINT-001",
                    "quantity_kg": 1000.0,
                    "unit_cost": 15.50,
                    "received_at": "2024-01-15T08:00:00",
                    "is_active": True,
                },
                {
                    "id": "2",
                    "lot_code": "LOT-002",
                    "product_id": "PAINT-002",
                    "quantity_kg": 500.0,
                    "unit_cost": 18.75,
                    "received_at": "2024-01-16T09:30:00",
                    "is_active": True,
                },
            ]
        }
    elif "/batches/" in endpoint and "/print" in endpoint:
        return {
            "text": """ T R A D E   P A I N T S
 BOSTIK CLEARSEAL........ANDREW
┌─────────────────────────┬─────────────────┬─────────────────────────────┐
│Formula 850D Rev. 1     │ Class 410.15    │ Custom Yield: 370 Lt.      │
├─────────────────────────┼─────────────────┼─────────────────────────────┤
│ COMPONENT               │ LITRE           │HAZ│ KILO           │CHECK│ INSTRUCTIONS │
└─────────────────────────┴─────────────────┴───┴─────────────────┴─────┴─────────────┘

Sample batch ticket content for demonstration purposes."""
        }
    elif endpoint == "/contacts/":
        return [
            {
                "id": "1",
                "code": "CONT001",
                "name": "Acme Chemicals",
                "contact_person": "John Smith",
                "email": "john@acme.com",
                "phone": "555-0101",
                "address": "123 Main St",
                "is_customer": False,
                "is_supplier": True,
                "is_other": False,
                "tax_rate": 10.0,
                "xero_contact_id": None,
                "is_active": True,
                "created_at": "2024-01-15T08:00:00",
            },
            {
                "id": "2",
                "code": "CONT002",
                "name": "Paint Distributors Inc",
                "contact_person": "Jane Customer",
                "email": "jane@paintdist.com",
                "phone": "555-0202",
                "address": "456 Oak Ave",
                "is_customer": True,
                "is_supplier": False,
                "is_other": False,
                "tax_rate": 10.0,
                "xero_contact_id": None,
                "is_active": True,
                "created_at": "2024-01-16T09:30:00",
            },
            {
                "id": "3",
                "code": "CONT003",
                "name": "Global Materials Ltd",
                "contact_person": "Bob Johnson",
                "email": "bob@global.com",
                "phone": "555-0303",
                "address": "789 Pine Rd",
                "is_customer": False,
                "is_supplier": True,
                "is_other": False,
                "tax_rate": 10.0,
                "xero_contact_id": None,
                "is_active": True,
                "created_at": "2024-01-17T10:00:00",
            },
        ]
    else:
        return {"error": f"No sample data available for {endpoint}"}


def show_toast(message: str, header: str = "Notification", is_open: bool = True):
    """Show toast notification."""
    return {"is_open": is_open, "header": header, "children": message}


# API connectivity check callback
@app.callback(
    [
        Output("demo-mode-alert", "children"),
        Output("demo-mode-alert", "color"),
        Output("demo-mode-alert", "style"),
    ],
    Input("main-tabs", "active_tab"),
)
def check_api_connectivity(active_tab):
    """Check API connectivity and update alert."""
    try:
        # Try to connect to API health endpoint
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        if response.status_code == 200:
            return (
                "",
                "success",
                {"display": "none"},
            )  # Hide alert when API is available
        else:
            return (
                "API server is running but not responding correctly",
                "warning",
                {"display": "block"},
            )
    except requests.exceptions.ConnectionError:
        return (
            "Demo Mode: API server not available. Using sample data.",
            "info",
            {"display": "block"},
        )
    except Exception as e:
        return f"API connection error: {str(e)}", "danger", {"display": "block"}


# Tab content callback
@app.callback(Output("tab-content", "children"), Input("main-tabs", "active_tab"))
def render_tab_content(active_tab):
    """Render content based on active tab. Manufacturing and Sales panels stay in the
    DOM (hidden when inactive) so callbacks targeting their component IDs do not fail."""
    print(f"Rendering tab: {active_tab}")  # Debug print

    is_manufacturing = active_tab == "manufacturing"
    is_sales = active_tab == "sales"
    is_crm = active_tab == "crm"
    is_training = active_tab == "training"

    manufacturing_panel = html.Div(
        [
            dbc.Tabs(
                id="manufacturing-sub-tabs",
                active_tab="products",
                children=[
                    dbc.Tab(label="Products", tab_id="products"),
                    dbc.Tab(label="Assemblies", tab_id="formulas"),
                    dbc.Tab(
                        label="Batch Processing",
                        tab_id="batch-processing",
                    ),
                    dbc.Tab(label="Work Orders", tab_id="work-orders"),
                    dbc.Tab(label="Inventory", tab_id="inventory"),
                    dbc.Tab(label="Batch Reports", tab_id="batch-reports"),
                    dbc.Tab(label="RM Reports", tab_id="rm-reports"),
                    dbc.Tab(label="Stocktake", tab_id="stocktake"),
                ],
                className="vnd-sub-tabs mb-3",
            ),
            html.Div(id="manufacturing-content"),
        ],
        id="manufacturing-panel",
        style={"display": "block" if is_manufacturing else "none"},
    )

    sales_panel = html.Div(
        sales_tab_layout(),
        id="sales-panel-root",
        style={"display": "block" if is_sales else "none"},
    )

    crm_panel = html.Div(
        crm_page.layout(),
        id="crm-panel-root",
        style={"display": "block" if is_crm else "none"},
    )

    from .pages.training_page import TrainingPage

    training_panel = html.Div(
        TrainingPage.get_layout(),
        id="training-panel-root",
        style={"display": "block" if is_training else "none"},
    )

    if active_tab == "home":
        other_layout = HomePage.get_layout()
    elif active_tab == "contacts":
        other_layout = ContactsPage.get_layout()
        print("Contacts layout created")  # Debug print
    elif active_tab == "reports":
        other_layout = reports_page.get_layout()
        print("Reports layout created")  # Debug print
    elif active_tab == "settings":
        from .pages.settings_page import SettingsPage

        other_layout = SettingsPage.get_layout()
        print("Settings layout created")  # Debug print
    elif active_tab in ("manufacturing", "sales", "crm", "training"):
        other_layout = html.Div()
    else:
        other_layout = html.Div("Select a tab to view content")

    other_panel = html.Div(
        other_layout,
        id="other-tab-panel",
        style={
            "display": "block"
            if active_tab not in ("manufacturing", "sales", "crm", "training")
            else "none"
        },
    )

    # Render visible panel first so it's the first child of tab-content. This avoids
    # the hidden manufacturing panel (when on Sales/Orders etc.) from being first in
    # the DOM and potentially capturing focus or causing the main tab to switch.
    if active_tab == "home":
        return [
            other_panel,
            manufacturing_panel,
            sales_panel,
            crm_panel,
            training_panel,
        ]
    if is_manufacturing:
        return [
            manufacturing_panel,
            sales_panel,
            crm_panel,
            training_panel,
            other_panel,
        ]
    if is_sales:
        return [
            sales_panel,
            manufacturing_panel,
            crm_panel,
            training_panel,
            other_panel,
        ]
    if is_crm:
        return [
            crm_panel,
            manufacturing_panel,
            sales_panel,
            training_panel,
            other_panel,
        ]
    if is_training:
        return [
            training_panel,
            manufacturing_panel,
            sales_panel,
            crm_panel,
            other_panel,
        ]
    return [other_panel, manufacturing_panel, sales_panel, crm_panel, training_panel]


@app.callback(
    Output("main-tabs", "active_tab", allow_duplicate=True),
    [Input(f"home-nav-{tab_id}", "n_clicks") for tab_id, _, _ in HOME_NAV_ITEMS],
    prevent_initial_call=True,
)
def navigate_from_home(*_clicks):
    """Switch main tab when a home-screen navigation card is clicked."""
    triggered = callback_context.triggered_id
    if triggered and str(triggered).startswith("home-nav-"):
        return str(triggered).replace("home-nav-", "", 1)
    return no_update


# Manufacturing sub-tab content
@app.callback(
    Output("manufacturing-content", "children"),
    Input("manufacturing-sub-tabs", "active_tab"),
)
def render_manufacturing_content(active_tab):
    """Render Manufacturing sub-tab content."""
    if active_tab == "products":
        return products_page_enhanced.get_layout()
    if active_tab == "formulas":
        return FormulasPage.get_layout()
    if active_tab == "batch-processing":
        return BatchProcessingPage.get_layout()
    if active_tab == "work-orders":
        return WorkOrdersPage.get_layout()
    if active_tab == "inventory":
        return inventory_page.get_layout()
    if active_tab == "batch-reports":
        return BatchReportsPage.get_layout()
    if active_tab == "rm-reports":
        return RmReportsPage.get_layout()
    if active_tab == "stocktake":
        return StocktakePage.get_layout()
    return html.Div("Select a sub-tab")


# Sync effective-tab store when main tab changes (runs on every layout; manufacturing-sub-tabs may not exist)
@app.callback(
    Output("effective-tab-store", "data"),
    Input("main-tabs", "active_tab"),
)
def sync_effective_tab_from_main(active_tab):
    """When main tab is manufacturing, default to products; else use main tab."""
    if active_tab == "manufacturing":
        return "products"
    return active_tab or "home"


# Sync effective-tab store when manufacturing sub-tab changes (only runs when Manufacturing is visible)
@app.callback(
    Output("effective-tab-store", "data", allow_duplicate=True),
    Input("manufacturing-sub-tabs", "active_tab"),
    State("main-tabs", "active_tab"),
    prevent_initial_call=True,
)
def sync_effective_tab_from_manufacturing(active_tab, main_tab):
    """Reflect manufacturing sub-tab in effective-tab store (only while Manufacturing is active)."""
    if main_tab != "manufacturing":
        raise PreventUpdate
    return active_tab or "products"


# Products page callbacks - Initial table data load and filter
@app.callback(
    Output("products-table", "data"),
    [
        Input("effective-tab-store", "data"),
        Input("products-refresh", "n_clicks"),
        Input("filter-purchase", "value"),
        Input("filter-sell", "value"),
        Input("filter-assemble", "value"),
        Input("products-refresh-trigger", "children"),
    ],
    prevent_initial_call=False,
)
def load_products_table(
    effective_tab,
    refresh_clicks,
    filter_purchase,
    filter_sell,
    filter_assemble,
    refresh_trigger,
):
    """Load products table when products tab is activated, refresh is clicked, or filters change."""
    # Only load if we're on the products tab (Manufacturing > Products)
    if effective_tab != "products":
        return []

    print(
        f"[load_products_table] effective_tab={effective_tab}, filters: purchase={filter_purchase}, sell={filter_sell}, assemble={filter_assemble}"
    )

    # Initialize products list
    all_products = []

    try:
        # Fetch all products (we'll filter client-side for OR logic)
        print(
            f"[load_products_table] Filters: purchase={filter_purchase}, sell={filter_sell}, assemble={filter_assemble}"
        )

        # Fetch all products - API now defaults to 10,000 limit
        try:
            response = make_api_request("GET", "/products/")
            print(f"[load_products_table] Response: type={type(response).__name__}")

            if isinstance(response, list):
                print(f"[load_products_table] Got {len(response)} products as list")
                all_products = response
            elif isinstance(response, dict):
                if "error" in response:
                    print(f"[load_products_table] Error: {response.get('error')}")
                    all_products = []  # Ensure assignment on error
                elif "products" in response:
                    print(
                        f"[load_products_table] Got {len(response['products'])} products from dict"
                    )
                    all_products = response["products"]
                else:
                    print(
                        f"[load_products_table] Unexpected dict keys: {list(response.keys())}"
                    )
                    all_products = []
            else:
                all_products = []
        except Exception as e:
            print(f"[load_products_table] Error fetching products: {e}")
            import traceback

            traceback.print_exc()
            all_products = []

        # Apply OR filter logic client-side
        # If all filters are checked (all True), show all products (no filtering)
        # If some filters are checked, show products matching ANY of those types
        # If all filters are unchecked (all False/None), show all products
        active_filters = []
        if filter_purchase is True:
            active_filters.append("is_purchase")
        if filter_sell is True:
            active_filters.append("is_sell")
        if filter_assemble is True:
            active_filters.append("is_assemble")

        # If all three filters are checked, don't filter (show all products)
        # This is the default state and means "show everything"
        if len(active_filters) == 3:
            print(
                "[load_products_table] All filters checked - showing all products (no filtering)"
            )
            active_filters = []  # Clear filters to show all products

        if active_filters:
            print(f"[load_products_table] Applying OR filter for: {active_filters}")
            filtered_products = []
            for product in all_products:
                # Check if product matches ANY of the active filters
                # Note: is_purchase, is_sell, is_assemble are boolean values from API
                matches = False
                for filter_type in active_filters:
                    # Check the actual boolean value (before it gets converted to markdown)
                    filter_value = product.get(filter_type)
                    # Handle boolean True, string "✓", or truthy values
                    if filter_value is True:
                        matches = True
                        break
                    # Also check for string representations (in case conversion happened)
                    elif filter_value == "✓" or (
                        isinstance(filter_value, str) and filter_value.strip() == "✓"
                    ):
                        matches = True
                        break
                if matches:
                    filtered_products.append(product)
                else:
                    # Debug: log products that don't match for gin42
                    sku = product.get("sku", "")
                    if sku and "gin42" in sku.lower():
                        print(
                            f"[load_products_table] DEBUG: Product {sku} filtered out - is_purchase={product.get('is_purchase')}, is_sell={product.get('is_sell')}, is_assemble={product.get('is_assemble')}, active_filters={active_filters}"
                        )
            all_products = filtered_products
            print(
                f"[load_products_table] After OR filter: {len(all_products)} products"
            )

        print(f"[load_products_table] Total products: {len(all_products)}")

        # Remove duplicates
        seen_ids = set()
        unique_products = []
        for product in all_products:
            if not isinstance(product, dict):
                continue
            prod_id = product.get("id")
            if prod_id and prod_id not in seen_ids:
                seen_ids.add(prod_id)
                unique_products.append(product)

        print(f"[load_products_table] Unique products: {len(unique_products)}")

        # Flatten nested fields and format for table
        for product in unique_products:
            # Convert variants list to string - ensure no objects/dicts remain
            if "variants" in product:
                variants_val = product["variants"]
                if isinstance(variants_val, list):
                    variant_names = [
                        str(v.get("variant_name") or v.get("variant_code", ""))
                        for v in variants_val
                        if isinstance(v, dict)
                        and (v.get("variant_name") or v.get("variant_code"))
                    ]
                    product["variants"] = (
                        ", ".join(variant_names) if variant_names else ""
                    )
                elif isinstance(variants_val, dict):
                    # Single variant object - convert to string
                    product["variants"] = str(
                        variants_val.get("variant_name")
                        or variants_val.get("variant_code", "")
                    )
                else:
                    # Not a list or dict - set to empty string
                    product["variants"] = ""
            else:
                product["variants"] = ""
            # Convert capabilities to checkmarks
            product["is_purchase"] = "✓" if product.get("is_purchase") else ""
            product["is_sell"] = "✓" if product.get("is_sell") else ""
            product["is_assemble"] = "✓" if product.get("is_assemble") else ""
            # Convert datetime objects to strings and format dates
            for date_field in ["created_at", "updated_at"]:
                if date_field in product and product[date_field]:
                    try:
                        from datetime import datetime

                        if isinstance(product[date_field], str):
                            # Try to parse and format
                            try:
                                dt = datetime.fromisoformat(
                                    product[date_field].replace("Z", "+00:00")
                                )
                                product[date_field] = dt.strftime("%Y-%m-%d %H:%M")
                            except (ValueError, TypeError, AttributeError):
                                product[date_field] = str(product[date_field])
                        else:
                            product[date_field] = str(product[date_field])
                    except (ValueError, TypeError, AttributeError):
                        product[date_field] = str(product[date_field])
                elif date_field not in product:
                    product[date_field] = "-"

            # Add record status/version info
            # Determine record type based on available fields
            if not product.get("is_active", True):
                pass
            # Add version info if available
            if "version" in product:
                product["record_version"] = str(product.get("version", ""))
            else:
                product["record_version"] = "-"

            # Add last modified date for versioning
            product["last_modified"] = product.get(
                "updated_at", product.get("created_at", "-")
            )

            # Add placeholder fields for table display - format stock as number without unit
            stock_value = product.get("stock_on_hand", 0.0) or 0.0
            product["stock"] = round(float(stock_value), 3) if stock_value else 0.0
            product["primary_assembly_cost"] = (
                product.get("manufactured_cost_ex_gst")
                or product.get("purchase_cost_ex_gst")
                or product.get("usage_cost_ex_gst")
                or 0.0
            )

        # Prepare DataFrame
        if unique_products:
            try:
                df = pd.DataFrame(unique_products)
                # Filter out columns with lists/dicts
                scalar_cols = []
                for col in df.columns:
                    if not df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                        scalar_cols.append(col)

                if scalar_cols:
                    df = df[scalar_cols]
                    result = df.to_dict("records")
                    print(f"[load_products_table] Returning {len(result)} records")
                    return result
                else:
                    print(
                        "[load_products_table] No scalar columns found, returning as-is"
                    )
                    return unique_products
            except Exception as e:
                print(f"[load_products_table] DataFrame error: {e}")
                import traceback

                traceback.print_exc()
                return unique_products

        print("[load_products_table] No products to return")
        return []
    except Exception as e:
        print(f"[load_products_table] Fatal error: {e}")
        import traceback

        traceback.print_exc()
        return []


# Batches page callbacks
@app.callback(
    [Output("batches-table", "data"), Output("batches-table", "columns")],
    [Input("effective-tab-store", "data")],
)
def update_batches_table(effective_tab):
    """Update batches table."""
    # Load data when batches tab is active (legacy)
    if effective_tab == "batches":
        response = make_api_request("GET", "/batches/")

        if "error" in response:
            return [], []

        # API returns a list directly, not wrapped in a dict
        batches = (
            response if isinstance(response, list) else response.get("batches", [])
        )

        if batches:
            # Flatten nested fields for DataTable display
            for batch in batches:
                # Convert components list to string representation
                if "components" in batch and isinstance(batch["components"], list):
                    component_info = []
                    for comp in batch["components"]:
                        if isinstance(comp, dict):
                            component_info.append(
                                f"{comp.get('ingredient_product_id', 'N/A')} ({comp.get('quantity_kg', 0)} kg)"
                            )
                    batch["components"] = (
                        "; ".join(component_info) if component_info else "None"
                    )
                # Convert datetime fields to strings
                if "started_at" in batch and batch["started_at"]:
                    batch["started_at"] = str(batch["started_at"])
                if "completed_at" in batch and batch["completed_at"]:
                    batch["completed_at"] = str(batch["completed_at"])

            # Create DataFrame and get column info
            df = pd.DataFrame(batches)

            # Filter out non-scalar columns that might cause issues
            scalar_cols = []
            for col in df.columns:
                # Check if all values in this column are scalar
                if not df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                    scalar_cols.append(col)

            df = df[scalar_cols] if scalar_cols else df

            columns = [
                {"name": col.replace("_", " ").title(), "id": col} for col in df.columns
            ]
            return df.to_dict("records"), columns
        else:
            return [], []

    return [], []


@app.callback(
    Output("batch-print-preview", "children"),
    [Input("batch-print-btn", "n_clicks")],
    [State("batches-table", "selected_rows"), State("batches-table", "data")],
)
def show_batch_print_preview(n_clicks, selected_rows, data):
    """Show batch print preview."""
    if not n_clicks or not selected_rows or not data:
        return html.Div("Select a batch to print")

    batch_data = data[selected_rows[0]]
    batch_code = batch_data.get("batch_code", "")

    if not batch_code:
        return html.Div("No batch code found")

    response = make_api_request(
        "GET", f"/batches/{batch_code}/print", {"format": "text"}
    )

    if "error" in response:
        return html.Div(f"Error: {response['error']}")

    print_text = response.get("text", "")

    return html.Div(
        [
            html.H5(f"Batch Ticket: {batch_code}"),
            html.Pre(
                print_text,
                style={
                    "background": "#f8f9fa",
                    "padding": "15px",
                    "border": "1px solid #dee2e6",
                    "border-radius": "5px",
                    "font-family": "monospace",
                    "font-size": "12px",
                    "white-space": "pre-wrap",
                },
            ),
        ]
    )


# Inventory page callbacks
@app.callback(
    [Output("inventory-table", "data"), Output("inventory-table", "columns")],
    [Input("effective-tab-store", "data")],
)
def update_inventory_table(effective_tab):
    """Update inventory table."""
    # Load data when Manufacturing > Inventory is active
    if effective_tab == "inventory":
        response = make_api_request("GET", "/inventory/lots/")

        if "error" in response:
            return [], []

        lots = response if isinstance(response, list) else response.get("lots", [])

        if lots:
            df = pd.DataFrame(lots)
            columns = [
                {"name": col.replace("_", " ").title(), "id": col} for col in df.columns
            ]
            return df.to_dict("records"), columns
        else:
            return [], []

    return [], []


# Reports page callbacks
@app.callback(
    Output("reports-output", "children"),
    [Input("generate-report-btn", "n_clicks")],
    [
        State("report-type", "value"),
        State("report-start-date", "date"),
        State("report-end-date", "date"),
    ],
)
def generate_report(n_clicks, report_type, start_date, end_date):
    """Generate report."""
    if not n_clicks:
        return html.Div("Click 'Generate Report' to create a report")

    if not report_type:
        return html.Div("Please select a report type")

    # This would call a reports API endpoint when implemented
    return html.Div(
        [
            html.H5(f"Report: {report_type}"),
            html.P(f"Date Range: {start_date} to {end_date}"),
            html.P(
                "Report generation functionality will be implemented when the reports API is available."
            ),
        ]
    )


# Register CRUD callbacks
register_product_callbacks(app, make_api_request)
register_product_section_callbacks(app)
register_purchase_usage_callbacks(app, make_api_request)
register_formulas_callbacks(app, make_api_request)
register_contacts_callbacks(app, make_api_request)
register_units_callbacks(app, make_api_request)
register_excise_rates_callbacks(app, make_api_request)
register_purchase_formats_callbacks(app, make_api_request)
register_qc_test_types_callbacks(app, make_api_request)
register_work_areas_callbacks(app, make_api_request)
register_settings_callbacks(app)
register_sales_tab_callbacks(app)
register_sales_orders_callbacks(
    app,
    make_api_request,
    api_base_url=API_BASE_URL.replace("/api/v1", "").rstrip("/")
    or "http://127.0.0.1:8000",
)
register_sales_customers_callbacks(app, make_api_request)
register_crm_callbacks(
    app,
    make_api_request,
    api_base_url=API_BASE_URL.replace("/api/v1", "").rstrip("/")
    or "http://127.0.0.1:8000",
)
register_crm_settings_callbacks(app, make_api_request)
register_sales_import_callbacks(app, make_api_request)
register_sales_analytics_callbacks(app, make_api_request)
register_sales_map_callbacks(app, make_api_request)


register_work_orders_callbacks(app, API_BASE_URL, make_api_request)
register_stocktake_callbacks(app, make_api_request)
register_training_callbacks(app, make_api_request)

# Xero integration temporarily disabled - will re-enable later
# # Add Flask routes for Xero OAuth
# from flask import request, redirect
# from app.services.xero_oauth import get_auth_url, exchange_code_for_tokens
#
# server = app.server  # Dash exposes Flask server
#
# @server.route("/xero/connect")
# def xero_connect():
#     """Redirect to Xero OAuth authorization."""
#     url = get_auth_url()
#     return redirect(url)
#
#
# @server.route("/xero/callback")
# def xero_callback():
#     """Handle Xero OAuth callback."""
#     code = request.args.get("code")
#     if not code:
#         return "Missing authorization code", 400
#
#     try:
#         result = exchange_code_for_tokens(code)
#         return f"""
#         <html>
#         <body>
#             <h1>Xero Connected Successfully</h1>
#             <p>Tenant ID: {result['tenant_id']}</p>
#             <p><a href="/">Return to Dashboard</a></p>
#         </body>
#         </html>
#         """
#     except Exception as e:
#         return f"<h1>Error connecting to Xero</h1><p>{str(e)}</p>", 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
