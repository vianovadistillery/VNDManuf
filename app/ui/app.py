"""Dash UI application for TPManuf Modern System."""

# Import page components from old pages.py (the file, not the directory)
import importlib.util
import json
import os
import sys
from typing import Any, Dict, Optional

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import requests
from dash import Input, Output, State, html, no_update

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
pricing_page = pages_old.pricing_page
packaging_page = pages_old.packaging_page
invoices_page = pages_old.invoices_page
reports_page = pages_old.reports_page

from .contacts_callbacks import register_contacts_callbacks  # noqa: E402
from .excise_rates_callbacks import register_excise_rates_callbacks  # noqa: E402
from .formulas_callbacks import register_formulas_callbacks  # noqa: E402
from .pages.batch_processing_page import BatchProcessingPage  # noqa: E402
from .pages.batch_reports_page import BatchReportsPage  # noqa: E402
from .pages.condition_types_page import ConditionTypesPage  # noqa: E402
from .pages.contacts_page import ContactsPage  # noqa: E402

# Import new page modules from pages/ subdirectory (the directory)
from .pages.formulas_page import FormulasPage  # noqa: E402
from .pages.rm_reports_page import RmReportsPage  # noqa: E402
from .pages.stocktake_page import StocktakePage  # noqa: E402
from .pages.suppliers_page import SuppliersPage  # noqa: E402
from .pages_enhanced import products_page_enhanced  # noqa: E402
from .products_callbacks import register_product_callbacks  # noqa: E402
from .suppliers_callbacks import register_suppliers_callbacks  # noqa: E402
from .units_callbacks import register_units_callbacks  # noqa: E402

# Xero integration temporarily disabled - will re-enable later
# from .pages.accounting_integration_page import accounting_integration_page

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

# API base URL
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# App layout
app.layout = dbc.Container(
    [
        # Header
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("VNDManuf", className="text-center mb-4"),
                        dbc.Alert(
                            id="demo-mode-alert",
                            children="Connecting to API...",
                            color="info",
                            dismissable=True,
                            className="mb-3",
                            style={"display": "none"},
                        ),
                        html.Hr(),
                    ]
                )
            ]
        ),
        # Navigation tabs
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Tabs(
                            id="main-tabs",
                            active_tab="products",
                            children=[
                                dbc.Tab(label="Products", tab_id="products"),
                                dbc.Tab(label="Formulas", tab_id="formulas"),
                                dbc.Tab(
                                    label="Batch Processing", tab_id="batch-processing"
                                ),
                                dbc.Tab(label="Suppliers", tab_id="suppliers"),
                                dbc.Tab(label="Contacts", tab_id="contacts"),
                                dbc.Tab(label="Inventory", tab_id="inventory"),
                                dbc.Tab(label="Pricing", tab_id="pricing"),
                                dbc.Tab(label="Packaging", tab_id="packaging"),
                                dbc.Tab(label="Invoices", tab_id="invoices"),
                                dbc.Tab(label="Batch Reports", tab_id="batch-reports"),
                                dbc.Tab(label="RM Reports", tab_id="rm-reports"),
                                dbc.Tab(label="Stocktake", tab_id="stocktake"),
                                dbc.Tab(label="Conditions", tab_id="conditions"),
                                dbc.Tab(label="Settings", tab_id="settings"),
                                dbc.Tab(label="Reports", tab_id="reports"),
                                # Xero integration temporarily disabled - will re-enable later
                                # dbc.Tab(label="Accounting", tab_id="accounting"),
                            ],
                            className="mb-4",
                        )
                    ]
                )
            ]
        ),
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
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        else:
            return {"error": f"Unsupported method: {method}"}

        # Handle successful responses
        if response.status_code in [200, 201]:
            return response.json()
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
    elif endpoint == "/pricing/lists/":
        return {
            "price_lists": [
                {
                    "id": "1",
                    "code": "DEFAULT",
                    "name": "Default Price List",
                    "effective_date": "2024-01-01T00:00:00",
                    "is_active": True,
                },
                {
                    "id": "2",
                    "code": "PREMIUM",
                    "name": "Premium Price List",
                    "effective_date": "2024-01-01T00:00:00",
                    "is_active": True,
                },
            ]
        }
    elif endpoint == "/pack/units/":
        return {
            "pack_units": [
                {
                    "id": "1",
                    "code": "CAN",
                    "name": "Can",
                    "description": "Standard paint can",
                    "is_active": True,
                },
                {
                    "id": "2",
                    "code": "4PK",
                    "name": "4-Pack",
                    "description": "Pack of 4 cans",
                    "is_active": True,
                },
                {
                    "id": "3",
                    "code": "CTN",
                    "name": "Carton",
                    "description": "Carton of 12 cans",
                    "is_active": True,
                },
            ]
        }
    elif endpoint == "/invoices/":
        return {
            "invoices": [
                {
                    "id": "1",
                    "invoice_number": "00086633",
                    "customer_id": "CUST-001",
                    "invoice_date": "2024-01-20",
                    "status": "issued",
                    "total_inc_tax": 501.84,
                },
                {
                    "id": "2",
                    "invoice_number": "00086634",
                    "customer_id": "CUST-002",
                    "invoice_date": "2024-01-21",
                    "status": "draft",
                    "total_inc_tax": 325.50,
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
    elif "/invoices/" in endpoint and "/print" in endpoint:
        return {
            "text": """C3j
 Invoiced to: Delivery:
 W1Paint Factory Bayswater W0
 W1Unit 31,172 Canterbu W0
 W1 W0
 W1BAYSWATER NORTH 3153W0
 86633...

Sample invoice content for demonstration purposes."""
        }
    elif endpoint == "/suppliers/":
        return [
            {
                "id": "1",
                "code": "SUP001",
                "name": "Acme Chemicals",
                "contact_person": "John Smith",
                "email": "john@acme.com",
                "phone": "555-0101",
                "address": "123 Main St",
                "is_active": True,
                "created_at": "2024-01-15T08:00:00",
            },
            {
                "id": "2",
                "code": "SUP002",
                "name": "Global Materials Ltd",
                "contact_person": "Jane Doe",
                "email": "jane@global.com",
                "phone": "555-0202",
                "address": "456 Oak Ave",
                "is_active": True,
                "created_at": "2024-01-16T09:30:00",
            },
            {
                "id": "3",
                "code": "SUP003",
                "name": "Industrial Supplies",
                "contact_person": "Bob Johnson",
                "email": "bob@industrial.com",
                "phone": "555-0303",
                "address": "789 Pine Rd",
                "is_active": True,
                "created_at": "2024-01-17T10:00:00",
            },
        ]
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
    """Render content based on active tab."""
    print(f"Rendering tab: {active_tab}")  # Debug print

    if active_tab == "products":
        layout = products_page_enhanced.get_layout()
        print("Products layout created")  # Debug print
        return layout
    elif active_tab == "formulas":
        layout = FormulasPage.get_layout()
        print("Formulas layout created")  # Debug print
        return layout
    elif active_tab == "batch-processing":
        layout = BatchProcessingPage.get_layout()
        print("Batch Processing layout created")  # Debug print
        return layout
    elif active_tab == "batches":
        layout = batches_page.get_layout()
        print("Batches layout created")  # Debug print
        return layout
    elif active_tab == "inventory":
        layout = inventory_page.get_layout()
        print("Inventory layout created")  # Debug print
        return layout
    elif active_tab == "pricing":
        layout = pricing_page.get_layout()
        print("Pricing layout created")  # Debug print
        return layout
    elif active_tab == "packaging":
        layout = packaging_page.get_layout()
        print("Packaging layout created")  # Debug print
        return layout
    elif active_tab == "invoices":
        layout = invoices_page.get_layout()
        print("Invoices layout created")  # Debug print
        return layout
    elif active_tab == "batch-reports":
        layout = BatchReportsPage.get_layout()
        print("Batch Reports layout created")  # Debug print
        return layout
    elif active_tab == "rm-reports":
        layout = RmReportsPage.get_layout()
        print("RM Reports layout created")  # Debug print
        return layout
    elif active_tab == "stocktake":
        layout = StocktakePage.get_layout()
        print("Stocktake layout created")  # Debug print
        return layout
    elif active_tab == "suppliers":
        layout = SuppliersPage.get_layout()
        print("Suppliers layout created")  # Debug print
        return layout
    elif active_tab == "contacts":
        layout = ContactsPage.get_layout()
        print("Contacts layout created")  # Debug print
        return layout
    elif active_tab == "conditions":
        layout = ConditionTypesPage.get_layout()
        print("Conditions layout created")  # Debug print
        return layout
    elif active_tab == "settings":
        from .pages.settings_page import SettingsPage

        layout = SettingsPage.get_layout()
        print("Settings layout created")  # Debug print
        return layout
    elif active_tab == "reports":
        layout = reports_page.get_layout()
        print("Reports layout created")  # Debug print
        return layout
    # Xero integration temporarily disabled - will re-enable later
    # elif active_tab == "accounting":
    #     return accounting_integration_page.layout()
    else:
        return html.Div("Select a tab to view content")


# Products page callbacks - Initial table data load and filter
@app.callback(
    Output("products-table", "data"),
    [Input("main-tabs", "active_tab"), Input("products-refresh", "n_clicks")],
    [
        State("filter-purchase", "value"),
        State("filter-sell", "value"),
        State("filter-assemble", "value"),
    ],
    prevent_initial_call=True,
)
def load_products_table(
    active_tab, refresh_clicks, filter_purchase, filter_sell, filter_assemble
):
    """Load products table when products tab is activated or refresh is clicked."""
    if active_tab != "products":
        return no_update

    print(
        f"[load_products_table] active_tab={active_tab}, filters: purchase={filter_purchase}, sell={filter_sell}, assemble={filter_assemble}"
    )

    # Initialize products list
    all_products = []

    try:
        # Build filter query using capabilities
        filter_params = {}
        if filter_purchase is True:
            filter_params["is_purchase"] = True
        if filter_sell is True:
            filter_params["is_sell"] = True
        if filter_assemble is True:
            filter_params["is_assemble"] = True

        print(f"[load_products_table] Fetching products with filters: {filter_params}")

        # Fetch products with filters
        try:
            response = make_api_request("GET", "/products/", data=filter_params)
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

        # If still no products, try fetching all
        if not all_products:
            print("[load_products_table] No products with filters, trying all...")
            try:
                response = make_api_request("GET", "/products/")
                if isinstance(response, list):
                    all_products = response
                elif isinstance(response, dict):
                    if "products" in response:
                        all_products = response["products"]
                    elif "error" in response:
                        print(
                            f"[load_products_table] Error fetching all: {response.get('error')}"
                        )
                        all_products = []
                    else:
                        print(
                            f"[load_products_table] Unexpected response keys: {list(response.keys())}"
                        )
                        all_products = []
                else:
                    all_products = []
            except Exception as e:
                print(f"[load_products_table] Error fetching all: {e}")
                all_products = []

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
            # Convert datetime objects to strings
            for date_field in ["created_at", "updated_at"]:
                if date_field in product and product[date_field]:
                    product[date_field] = str(product[date_field])
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


# Separate callback for filter changes
@app.callback(
    Output("products-table", "data", allow_duplicate=True),
    [
        Input("filter-purchase", "value"),
        Input("filter-sell", "value"),
        Input("filter-assemble", "value"),
    ],
    [State("main-tabs", "active_tab")],
    prevent_initial_call=True,
)
def update_products_on_filter_change(
    filter_purchase, filter_sell, filter_assemble, active_tab
):
    """Update products table when filters change (only if products tab is active)."""
    if active_tab != "products":
        return no_update

    # Reuse the same logic as the main callback
    try:
        filter_params = {}
        if filter_purchase is True:
            filter_params["is_purchase"] = True
        if filter_sell is True:
            filter_params["is_sell"] = True
        if filter_assemble is True:
            filter_params["is_assemble"] = True

        # Fetch products with filters
        try:
            response = make_api_request("GET", "/products/", data=filter_params)

            if isinstance(response, list):
                all_products = response
            elif isinstance(response, dict):
                if "error" in response:
                    print(
                        f"[update_products_on_filter_change] Error: {response.get('error')}"
                    )
                    all_products = []
                elif "products" in response:
                    all_products = response["products"]
                else:
                    all_products = []
            else:
                all_products = []
        except Exception as e:
            print(f"[update_products_on_filter_change] Error fetching products: {e}")
            all_products = []

        # If still no products, try fetching all
        if not all_products:
            try:
                response = make_api_request("GET", "/products/")
                if isinstance(response, list):
                    all_products = response
                elif isinstance(response, dict) and "products" in response:
                    all_products = response["products"]
            except Exception as e:
                print(f"[update_products_on_filter_change] Error fetching all: {e}")
                all_products = []

        # Remove duplicates and format
        seen_ids = set()
        unique_products = []
        for product in all_products:
            if not isinstance(product, dict):
                continue
            prod_id = product.get("id")
            if prod_id and prod_id not in seen_ids:
                seen_ids.add(prod_id)
                unique_products.append(product)

        # Format for table display
        for product in unique_products:
            # Convert variants to string - ensure no objects/dicts remain
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
                    product["variants"] = str(
                        variants_val.get("variant_name")
                        or variants_val.get("variant_code", "")
                    )
                else:
                    product["variants"] = ""
            else:
                product["variants"] = ""
            product["is_purchase"] = "✓" if product.get("is_purchase") else ""
            product["is_sell"] = "✓" if product.get("is_sell") else ""
            product["is_assemble"] = "✓" if product.get("is_assemble") else ""
            for date_field in ["created_at", "updated_at"]:
                if date_field in product and product[date_field]:
                    product[date_field] = str(product[date_field])
            # Format stock as number without unit
            stock_value = product.get("stock_on_hand", 0.0) or 0.0
            product["stock"] = round(float(stock_value), 3) if stock_value else 0.0
            product["primary_assembly_cost"] = (
                product.get("manufactured_cost_ex_gst")
                or product.get("purchase_cost_ex_gst")
                or product.get("usage_cost_ex_gst")
                or 0.0
            )

        if unique_products:
            try:
                df = pd.DataFrame(unique_products)
                scalar_cols = [
                    col
                    for col in df.columns
                    if not df[col].apply(lambda x: isinstance(x, (list, dict))).any()
                ]
                df = df[scalar_cols] if scalar_cols else df
                return df.to_dict("records")
            except Exception as e:
                print(f"[update_products_on_filter_change] DataFrame error: {e}")
                return unique_products

        return []
    except Exception as e:
        print(f"[update_products_on_filter_change] Fatal error: {e}")
        import traceback

        traceback.print_exc()
        return []


# Batches page callbacks
@app.callback(
    [Output("batches-table", "data"), Output("batches-table", "columns")],
    [Input("main-tabs", "active_tab")],
)
def update_batches_table(active_tab):
    """Update batches table."""
    # Load data when batches tab is active
    if active_tab == "batches":
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
    [Input("main-tabs", "active_tab")],
)
def update_inventory_table(active_tab):
    """Update inventory table."""
    # Load data when inventory tab is active
    if active_tab == "inventory":
        response = make_api_request("GET", "/inventory/lots/")

        if "error" in response:
            return [], []

        # API returns a list directly, not wrapped in a dict
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


# Pricing page callbacks
@app.callback(
    [Output("pricing-table", "data"), Output("pricing-table", "columns")],
    [Input("main-tabs", "active_tab")],
)
def update_pricing_table(active_tab):
    """Update pricing table."""
    # Load data when pricing tab is active
    if active_tab == "pricing":
        response = make_api_request("GET", "/pricing/lists/")

        if "error" in response:
            return [], []

        # API returns a list directly, not wrapped in a dict
        price_lists = (
            response if isinstance(response, list) else response.get("price_lists", [])
        )

        if price_lists:
            df = pd.DataFrame(price_lists)
            columns = [
                {"name": col.replace("_", " ").title(), "id": col} for col in df.columns
            ]
            return df.to_dict("records"), columns
        else:
            return [], []

    return [], []


# Packaging page callbacks
@app.callback(
    [Output("packaging-table", "data"), Output("packaging-table", "columns")],
    [Input("main-tabs", "active_tab")],
)
def update_packaging_table(active_tab):
    """Update packaging table."""
    # Load data when packaging tab is active
    if active_tab == "packaging":
        response = make_api_request("GET", "/pack/units/")

        if "error" in response:
            return [], []

        # API returns a list directly, not wrapped in a dict
        pack_units = (
            response if isinstance(response, list) else response.get("pack_units", [])
        )

        if pack_units:
            df = pd.DataFrame(pack_units)
            columns = [
                {"name": col.replace("_", " ").title(), "id": col} for col in df.columns
            ]
            return df.to_dict("records"), columns
        else:
            return [], []

    return [], []


@app.callback(
    Output("pack-conversion-result", "children"),
    [Input("pack-convert-btn", "n_clicks")],
    [
        State("pack-product-id", "value"),
        State("pack-quantity", "value"),
        State("pack-from-unit", "value"),
        State("pack-to-unit", "value"),
    ],
)
def convert_pack_units(n_clicks, product_id, quantity, from_unit, to_unit):
    """Convert pack units."""
    if not n_clicks or not all([product_id, quantity, from_unit, to_unit]):
        return html.Div("Fill in all fields to convert")

    params = {
        "product_id": product_id,
        "qty": quantity,
        "from_unit": from_unit,
        "to_unit": to_unit,
    }

    response = make_api_request("GET", "/pack/convert", data=params)

    if "error" in response:
        return html.Div(f"Error: {response['error']}")

    result = response.get("result", {})
    converted_qty = result.get("converted_quantity", 0)

    return html.Div(
        [
            html.H5("Conversion Result"),
            html.P(f"{quantity} {from_unit} = {converted_qty} {to_unit}"),
        ]
    )


# Invoices page callbacks
@app.callback(
    [Output("invoices-table", "data"), Output("invoices-table", "columns")],
    [Input("main-tabs", "active_tab")],
)
def update_invoices_table(active_tab):
    """Update invoices table."""
    # Load data when invoices tab is active
    if active_tab == "invoices":
        response = make_api_request("GET", "/invoices/")

        if "error" in response:
            return [], []

        # API returns a list directly, not wrapped in a dict
        invoices = (
            response if isinstance(response, list) else response.get("invoices", [])
        )

        if invoices:
            df = pd.DataFrame(invoices)
            columns = [
                {"name": col.replace("_", " ").title(), "id": col} for col in df.columns
            ]
            return df.to_dict("records"), columns
        else:
            return [], []

    return [], []


@app.callback(
    Output("invoice-print-preview", "children"),
    [Input("invoice-print-btn", "n_clicks")],
    [State("invoices-table", "selected_rows"), State("invoices-table", "data")],
)
def show_invoice_print_preview(n_clicks, selected_rows, data):
    """Show invoice print preview."""
    if not n_clicks or not selected_rows or not data:
        return html.Div("Select an invoice to print")

    invoice_data = data[selected_rows[0]]
    invoice_number = invoice_data.get("invoice_number", "")

    if not invoice_number:
        return html.Div("No invoice number found")

    response = make_api_request(
        "GET", f"/invoices/{invoice_number}/print", {"format": "text"}
    )

    if "error" in response:
        return html.Div(f"Error: {response['error']}")

    print_text = response.get("text", "")

    return html.Div(
        [
            html.H5(f"Invoice: {invoice_number}"),
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
register_formulas_callbacks(app, make_api_request)
register_suppliers_callbacks(app, make_api_request)
register_contacts_callbacks(app, make_api_request)
register_units_callbacks(app, make_api_request)
register_excise_rates_callbacks(app, make_api_request)

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
