# app/ui/work_orders_callbacks.py
"""Callbacks for Work Orders page."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

import dash
import dash_bootstrap_components as dbc
import requests
from dash import Input, Output, State, dash_table, dcc, html, no_update
from dash.dash_table.Format import Format, Scheme
from dash.exceptions import PreventUpdate


def safe_float(value: Optional[Any], default: Optional[float] = 0.0) -> Optional[float]:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def get_product_details(
    product_id: Optional[str], api_base_url: str, cache: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    if not product_id:
        return {
            "label": "",
            "density": None,
            "base_unit": None,
            "default_uom": None,
            "data": {},
        }

    if product_id in cache:
        return cache[product_id]

    details = {
        "label": product_id,
        "density": None,
        "base_unit": None,
        "default_uom": None,
        "data": {},
    }

    try:
        prod_url = f"{api_base_url}/products/{product_id}"
        prod_response = requests.get(prod_url, timeout=5)
        if prod_response.status_code == 200:
            product = prod_response.json()
            sku = product.get("sku", "")
            name = product.get("name", "")
            if sku and name:
                details["label"] = f"{sku} - {name}"
            elif name:
                details["label"] = name
            elif sku:
                details["label"] = sku

            details["density"] = safe_float(product.get("density_kg_per_l"), None)
            details["base_unit"] = product.get("base_unit")
            details["default_uom"] = (
                product.get("usage_unit")
                or product.get("base_unit")
                or product.get("purchase_unit")
            )
            details["data"] = product
    except Exception:
        details["label"] = product_id

    cache[product_id] = details
    return details


MASS_FACTORS = {
    "KG": 1,
    "KILOGRAM": 1,
    "KILOGRAMS": 1,
    "G": 1000,
    "GRAM": 1000,
    "GRAMS": 1000,
    "MG": 1_000_000,
    "LB": 2.20462262185,
    "LBS": 2.20462262185,
    "POUND": 2.20462262185,
    "POUNDS": 2.20462262185,
}

VOLUME_UOMS = {
    "L": ("L", 1),
    "LITER": ("L", 1),
    "LITRE": ("L", 1),
    "ML": ("ML", 1000),
    "MILLILITER": ("ML", 1000),
    "MILLILITRE": ("ML", 1000),
}


def convert_from_kg(
    value_kg: Optional[float], uom: Optional[str], product_details: Dict[str, Any]
) -> Optional[float]:
    if value_kg is None:
        return None

    numeric = safe_float(value_kg, default=None)
    if numeric is None:
        return None

    uom_clean = (uom or "").strip().upper()
    if not uom_clean:
        return round(numeric, 3)

    if uom_clean in MASS_FACTORS:
        return round(numeric * MASS_FACTORS[uom_clean], 3)

    if uom_clean in VOLUME_UOMS:
        density = product_details.get("density")
        if not density or density == 0:
            return round(numeric, 3)
        base_unit, multiplier = VOLUME_UOMS[uom_clean]
        litres = numeric / density
        if base_unit == "ML":
            return round(litres * multiplier, 3)
        return round(litres * multiplier, 3)

    return round(numeric, 3)


def build_input_rows(
    wo: Dict[str, Any],
    api_base_url: str,
    product_cache: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    cache = product_cache if product_cache is not None else {}
    inputs = wo.get("inputs", []) or []
    rows: List[Dict[str, Any]] = []
    options: List[Dict[str, str]] = []
    option_ids: Set[str] = set()

    sorted_inputs = sorted(
        inputs,
        key=lambda item: (
            item.get("sequence") is None,
            safe_float(item.get("sequence")),
        ),
    )

    for idx, inp in enumerate(sorted_inputs):
        component_id = inp.get("component_product_id")
        details = get_product_details(component_id, api_base_url, cache)
        label = details["label"]

        planned_display = safe_float(inp.get("planned_qty"))
        planned_canonical = safe_float(inp.get("required_quantity_kg"))
        actual_canonical = safe_float(inp.get("actual_qty"))
        if actual_canonical is None:
            actual_canonical = safe_float(inp.get("allocated_quantity_kg"))
        if actual_canonical is None:
            actual_canonical = 0.0

        uom = (
            inp.get("uom")
            or details.get("default_uom")
            or details.get("base_unit")
            or ""
        ).strip()

        planned_qty_display = planned_display
        if planned_qty_display is None and planned_canonical is not None:
            converted_planned = convert_from_kg(planned_canonical, uom, details)
            planned_qty_display = (
                converted_planned
                if converted_planned is not None
                else planned_canonical
            )

        actual_qty_display = convert_from_kg(actual_canonical, uom, details)
        if actual_qty_display is None:
            actual_qty_display = actual_canonical

        remaining_canonical = None
        if planned_canonical is not None:
            remaining_canonical = max(planned_canonical - actual_canonical, 0.0)
        remaining_qty_display = (
            convert_from_kg(remaining_canonical, uom, details)
            if remaining_canonical is not None
            else None
        )
        if remaining_qty_display is None and remaining_canonical is not None:
            remaining_qty_display = remaining_canonical

        rows.append(
            {
                "id": inp.get("id") or f"input-{idx}",
                "component_label": label or component_id or "",
                "component_product_id": component_id,
                "planned_qty": planned_qty_display,
                "planned_qty_canonical": planned_canonical,
                "uom": uom,
                "actual_qty": actual_qty_display,
                "actual_qty_canonical": actual_canonical,
                "remaining_qty": remaining_qty_display,
                "remaining_qty_canonical": remaining_canonical,
                "batch": inp.get("source_batch_id", "") or "",
            }
        )

        if component_id and component_id not in option_ids:
            option_ids.add(component_id)
            options.append({"label": label or component_id, "value": component_id})

    return rows, options


def build_output_rows(
    wo: Dict[str, Any],
    api_base_url: str,
    product_cache: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    cache = product_cache if product_cache is not None else {}
    outputs = wo.get("outputs", []) or []
    rows: List[Dict[str, Any]] = []
    planned_total_display = safe_float(wo.get("planned_qty"))
    planned_total_canonical = safe_float(wo.get("quantity_kg"))
    primary_product_id = wo.get("product_id")
    wo_uom = (wo.get("uom") or "").strip()

    if not outputs and primary_product_id:
        details = get_product_details(primary_product_id, api_base_url, cache)
        label = details["label"]
        if planned_total_display is not None:
            planned_display = planned_total_display
        elif planned_total_canonical is not None:
            converted = convert_from_kg(planned_total_canonical, wo_uom, details)
            planned_display = (
                converted if converted is not None else planned_total_canonical
            )
        else:
            planned_display = 0.0
        rows.append(
            {
                "id": "planned-output",
                "product_label": label or primary_product_id,
                "product_id": primary_product_id,
                "planned_qty": planned_display,
                "planned_qty_canonical": planned_total_canonical
                if planned_total_canonical is not None
                else planned_display,
                "actual_qty": 0.0,
                "uom": wo_uom,
                "batch": "",
            }
        )
        return rows

    for idx, out in enumerate(outputs):
        product_id = out.get("product_id")
        details = get_product_details(product_id, api_base_url, cache)
        label = details["label"]
        actual_display = safe_float(out.get("qty_produced"))
        uom = (
            out.get("uom")
            or wo_uom
            or details.get("default_uom")
            or details.get("base_unit")
            or ""
        )

        if product_id == primary_product_id:
            planned_canonical = planned_total_canonical
            planned_display = planned_total_display
        else:
            planned_canonical = None
            planned_display = None

        if planned_display is None and planned_canonical is not None:
            converted = convert_from_kg(planned_canonical, uom, details)
            planned_display = converted if converted is not None else planned_canonical
        if planned_display is None:
            planned_display = 0.0

        if actual_display is None:
            actual_display = 0.0

        actual_canonical = None

        rows.append(
            {
                "id": out.get("id") or f"output-{idx}",
                "product_label": label or product_id or "",
                "product_id": product_id,
                "planned_qty": planned_display,
                "planned_qty_canonical": planned_canonical
                if planned_canonical is not None
                else planned_display,
                "actual_qty": actual_display,
                "actual_qty_canonical": actual_canonical,
                "uom": uom,
                "batch": out.get("batch_id", "") or "",
            }
        )

    return rows


def register_work_orders_callbacks(
    app, api_base_url: str = "http://127.0.0.1:8000/api/v1"
):
    """Register all work order callbacks."""

    # Load work orders list
    @app.callback(
        [
            Output("wo-list-table", "data"),
            Output("wo-list-table", "columns"),
        ],
        [
            Input("wo-status-filter", "value"),
            Input("wo-product-filter", "value"),
            Input("wo-date-from", "value"),
            Input("wo-date-to", "value"),
            Input("main-tabs", "active_tab"),
        ],
        prevent_initial_call=False,
    )
    def load_work_orders_list(
        status_filter, product_filter, date_from, date_to, active_tab
    ):
        """Load work orders list with filters."""
        if active_tab != "work-orders":
            return [], []

        try:
            params = {}
            if status_filter:
                params["status"] = status_filter
            if product_filter:
                params["product_id"] = product_filter
            if date_from:
                params["date_from"] = date_from
            if date_to:
                params["date_to"] = date_to

            url = f"{api_base_url}/work-orders/"
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                work_orders = response.json()

                # Format data for table
                table_data = []
                for wo in work_orders:
                    # Get QC status
                    qc_status = "N/A"
                    if wo.get("qc_tests"):
                        qc_tests = wo.get("qc_tests", [])
                        pending = [t for t in qc_tests if t.get("status") == "pending"]
                        failed = [t for t in qc_tests if t.get("status") == "fail"]
                        if failed:
                            qc_status = "Failed"
                        elif pending:
                            qc_status = "Pending"
                        else:
                            qc_status = "Passed"

                    # Get unit cost
                    unit_cost = None
                    outputs = wo.get("outputs", [])
                    if outputs:
                        unit_cost = outputs[0].get("unit_cost")

                    # Format planned_qty - convert to float first
                    planned_qty_val = wo.get("planned_qty")
                    if planned_qty_val is not None:
                        try:
                            planned_qty_str = f"{float(planned_qty_val):.3f}"
                        except (ValueError, TypeError):
                            planned_qty_str = "0"
                    else:
                        planned_qty_str = "0"

                    # Format unit_cost - convert to float first
                    if unit_cost is not None:
                        try:
                            unit_cost_str = f"${float(unit_cost):.2f}"
                        except (ValueError, TypeError):
                            unit_cost_str = "N/A"
                    else:
                        unit_cost_str = "N/A"

                    # Get product name
                    product_id = wo.get("product_id", "")
                    product_name = product_id  # Default to ID if fetch fails
                    if product_id:
                        try:
                            product_url = f"{api_base_url}/products/{product_id}"
                            product_response = requests.get(product_url, timeout=5)
                            if product_response.status_code == 200:
                                product_data = product_response.json()
                                product_name = f"{product_data.get('sku', '')} - {product_data.get('name', product_id)}"
                        except Exception:
                            pass  # Keep default product_id if fetch fails

                    # Format dates
                    from datetime import datetime

                    released_at = wo.get("released_at")
                    released_at_str = ""
                    if released_at:
                        try:
                            if isinstance(released_at, str):
                                dt = datetime.fromisoformat(
                                    released_at.replace("Z", "+00:00")
                                )
                            else:
                                dt = released_at
                            released_at_str = dt.strftime("%Y-%m-%d")
                        except Exception:
                            released_at_str = ""

                    completed_at = wo.get("completed_at")
                    completed_at_str = ""
                    if completed_at:
                        try:
                            if isinstance(completed_at, str):
                                dt = datetime.fromisoformat(
                                    completed_at.replace("Z", "+00:00")
                                )
                            else:
                                dt = completed_at
                            completed_at_str = dt.strftime("%Y-%m-%d")
                        except Exception:
                            completed_at_str = ""

                    # Format actual_qty
                    actual_qty_val = wo.get("actual_qty")
                    actual_qty_str = ""
                    if actual_qty_val is not None:
                        try:
                            actual_qty_str = f"{float(actual_qty_val):.3f}"
                        except (ValueError, TypeError):
                            actual_qty_str = ""

                    # Format estimated_cost
                    estimated_cost_val = wo.get("estimated_cost")
                    estimated_cost_str = ""
                    if estimated_cost_val is not None:
                        try:
                            estimated_cost_str = f"${float(estimated_cost_val):.2f}"
                        except (ValueError, TypeError):
                            estimated_cost_str = ""

                    # Format actual_cost
                    actual_cost_val = wo.get("actual_cost")
                    actual_cost_str = ""
                    if actual_cost_val is not None:
                        try:
                            actual_cost_str = f"${float(actual_cost_val):.2f}"
                        except (ValueError, TypeError):
                            actual_cost_str = ""

                    table_data.append(
                        {
                            "id": wo.get("id"),
                            "code": wo.get("code", ""),
                            "product": product_name,
                            "planned_qty": planned_qty_str,
                            "uom": wo.get("uom", "KG"),
                            "status": wo.get("status", "").title(),
                            "released_at": released_at_str,
                            "completed_at": completed_at_str,
                            "actual_qty": actual_qty_str,
                            "estimated_cost": estimated_cost_str,
                            "actual_cost": actual_cost_str,
                            "qc_status": qc_status,
                            "unit_cost": unit_cost_str,
                        }
                    )

                columns = [
                    {"name": "WO Number", "id": "code"},
                    {"name": "Product", "id": "product"},
                    {"name": "Planned Qty", "id": "planned_qty"},
                    {"name": "UOM", "id": "uom"},
                    {"name": "Status", "id": "status"},
                    {"name": "Issued Date", "id": "released_at"},
                    {"name": "Completed Date", "id": "completed_at"},
                    {"name": "Actual Qty", "id": "actual_qty"},
                    {"name": "Est. Cost", "id": "estimated_cost"},
                    {"name": "Act Cost", "id": "actual_cost"},
                    {"name": "QC Status", "id": "qc_status"},
                    {"name": "Cost/Unit", "id": "unit_cost"},
                ]

                return table_data, columns
            else:
                print(f"Error loading work orders: {response.status_code}")
                return [], []
        except Exception as e:
            print(f"Error in load_work_orders_list: {e}")
            return [], []

    # Load products for filter dropdown
    @app.callback(
        Output("wo-product-filter", "options"),
        [Input("main-tabs", "active_tab")],
        prevent_initial_call=False,
    )
    def load_products_for_filter(active_tab):
        """Load products for filter dropdown."""
        if active_tab != "work-orders":
            return no_update

        try:
            url = f"{api_base_url}/products/?is_active=true"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                products_data = response.json()
                products = (
                    products_data
                    if isinstance(products_data, list)
                    else products_data.get("products", [])
                )
                options = [
                    {
                        "label": f"{p.get('sku', '')} - {p.get('name', '')}",
                        "value": p.get("id", ""),
                    }
                    for p in products
                ]
                return [{"label": "All", "value": ""}] + options
            else:
                return []
        except Exception as e:
            print(f"Error loading products: {e}")
            return []

    # Load components for issue material dropdown
    @app.callback(
        Output("wo-issue-component-dropdown", "options"),
        [Input("wo-detail-wo-id", "data")],
        prevent_initial_call=True,
    )
    def load_components_for_issue(wo_id):
        """Load components for issue material dropdown."""
        if not wo_id:
            return []

        try:
            url = f"{api_base_url}/work-orders/{wo_id}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                wo = response.json()
                _, options = build_input_rows(wo, api_base_url)
                return options
            else:
                return []
        except Exception as e:
            print(f"Error loading components: {e}")
            return []

    # Refresh work orders list after actions
    @app.callback(
        Output("wo-list-table", "data", allow_duplicate=True),
        [
            Input("wo-create-submit-btn", "n_clicks"),
            Input("wo-issue-submit-btn", "n_clicks"),
            Input("wo-qc-submit-btn", "n_clicks"),
            Input("wo-complete-submit-btn", "n_clicks"),
            Input("wo-release-btn", "n_clicks"),
            Input("wo-start-btn", "n_clicks"),
            Input("wo-void-btn", "n_clicks"),
        ],
        [
            State("wo-status-filter", "value"),
            State("wo-product-filter", "value"),
            State("wo-date-from", "value"),
            State("wo-date-to", "value"),
        ],
        prevent_initial_call=True,
    )
    def refresh_work_orders_list(
        create_clicks,
        issue_clicks,
        qc_clicks,
        complete_clicks,
        release_clicks,
        start_clicks,
        void_clicks,
        status_filter,
        product_filter,
        date_from,
        date_to,
    ):
        """Refresh work orders list after any action."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        try:
            params = {}
            if status_filter:
                params["status"] = status_filter
            if product_filter:
                params["product_id"] = product_filter
            if date_from:
                params["date_from"] = date_from
            if date_to:
                params["date_to"] = date_to

            url = f"{api_base_url}/work-orders/"
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                work_orders = response.json()

                table_data = []
                for wo in work_orders:
                    qc_status = "N/A"
                    if wo.get("qc_tests"):
                        qc_tests = wo.get("qc_tests", [])
                        pending = [t for t in qc_tests if t.get("status") == "pending"]
                        failed = [t for t in qc_tests if t.get("status") == "fail"]
                        if failed:
                            qc_status = "Failed"
                        elif pending:
                            qc_status = "Pending"
                        else:
                            qc_status = "Passed"

                    unit_cost = None
                    outputs = wo.get("outputs", [])
                    if outputs:
                        unit_cost = outputs[0].get("unit_cost")

                    # Format planned_qty - convert to float first
                    planned_qty_val = wo.get("planned_qty")
                    if planned_qty_val is not None:
                        try:
                            planned_qty_str = f"{float(planned_qty_val):.3f}"
                        except (ValueError, TypeError):
                            planned_qty_str = "0"
                    else:
                        planned_qty_str = "0"

                    # Format unit_cost - convert to float first
                    if unit_cost is not None:
                        try:
                            unit_cost_str = f"${float(unit_cost):.2f}"
                        except (ValueError, TypeError):
                            unit_cost_str = "N/A"
                    else:
                        unit_cost_str = "N/A"

                    # Get product name
                    product_id = wo.get("product_id", "")
                    product_name = product_id  # Default to ID if fetch fails
                    if product_id:
                        try:
                            product_url = f"{api_base_url}/products/{product_id}"
                            product_response = requests.get(product_url, timeout=5)
                            if product_response.status_code == 200:
                                product_data = product_response.json()
                                product_name = f"{product_data.get('sku', '')} - {product_data.get('name', product_id)}"
                        except Exception:
                            pass  # Keep default product_id if fetch fails

                    # Format dates
                    from datetime import datetime

                    released_at = wo.get("released_at")
                    released_at_str = ""
                    if released_at:
                        try:
                            if isinstance(released_at, str):
                                dt = datetime.fromisoformat(
                                    released_at.replace("Z", "+00:00")
                                )
                            else:
                                dt = released_at
                            released_at_str = dt.strftime("%Y-%m-%d")
                        except Exception:
                            released_at_str = ""

                    completed_at = wo.get("completed_at")
                    completed_at_str = ""
                    if completed_at:
                        try:
                            if isinstance(completed_at, str):
                                dt = datetime.fromisoformat(
                                    completed_at.replace("Z", "+00:00")
                                )
                            else:
                                dt = completed_at
                            completed_at_str = dt.strftime("%Y-%m-%d")
                        except Exception:
                            completed_at_str = ""

                    # Format actual_qty
                    actual_qty_val = wo.get("actual_qty")
                    actual_qty_str = ""
                    if actual_qty_val is not None:
                        try:
                            actual_qty_str = f"{float(actual_qty_val):.3f}"
                        except (ValueError, TypeError):
                            actual_qty_str = ""

                    # Format estimated_cost
                    estimated_cost_val = wo.get("estimated_cost")
                    estimated_cost_str = ""
                    if estimated_cost_val is not None:
                        try:
                            estimated_cost_str = f"${float(estimated_cost_val):.2f}"
                        except (ValueError, TypeError):
                            estimated_cost_str = ""

                    # Format actual_cost
                    actual_cost_val = wo.get("actual_cost")
                    actual_cost_str = ""
                    if actual_cost_val is not None:
                        try:
                            actual_cost_str = f"${float(actual_cost_val):.2f}"
                        except (ValueError, TypeError):
                            actual_cost_str = ""

                    table_data.append(
                        {
                            "id": wo.get("id"),
                            "code": wo.get("code", ""),
                            "product": product_name,
                            "planned_qty": planned_qty_str,
                            "uom": wo.get("uom", "KG"),
                            "status": wo.get("status", "").title(),
                            "released_at": released_at_str,
                            "completed_at": completed_at_str,
                            "actual_qty": actual_qty_str,
                            "estimated_cost": estimated_cost_str,
                            "actual_cost": actual_cost_str,
                            "qc_status": qc_status,
                            "unit_cost": unit_cost_str,
                        }
                    )

                return table_data
            else:
                return no_update
        except Exception as e:
            print(f"Error refreshing work orders: {e}")
            return no_update

    # Load products and assemblies for create modal
    @app.callback(
        [
            Output("wo-create-product-dropdown", "options"),
            Output("wo-create-product-dropdown", "value"),
            Output("wo-create-assembly-dropdown", "options"),
            Output("wo-create-assembly-dropdown", "value"),
            Output("wo-create-work-center", "options"),
            Output("wo-create-uom", "options"),
            Output("wo-create-batch-code", "value"),
        ],
        [Input("wo-create-modal", "is_open")],
        prevent_initial_call=True,
    )
    def load_create_modal_dropdowns(modal_is_open):
        """Load products and assemblies for create modal, and generate batch code."""
        if not modal_is_open:
            raise PreventUpdate

        try:
            # Load products that have assembly capability (is_assemble=True)
            products_url = f"{api_base_url}/products/?is_active=true&is_assemble=true"
            products_response = requests.get(products_url, timeout=5)
            products = []
            if products_response.status_code == 200:
                products_data = products_response.json()
                products = (
                    products_data
                    if isinstance(products_data, list)
                    else products_data.get("products", [])
                )

            # Filter to only include products with is_assemble=True
            products = [p for p in products if p.get("is_assemble", False)]

            product_options = [
                {
                    "label": f"{p.get('sku', '')} - {p.get('name', '')}",
                    "value": p.get("id", ""),
                }
                for p in products
            ]

            # Generate batch code (client-side generation matching server logic)
            # This is a preview - actual code will be generated server-side on save
            today = datetime.utcnow()
            year_2digit = today.strftime("%y")  # e.g., "25" for 2025

            # Get existing batch codes from work orders to find max sequence
            # Note: This is a preview - actual code will be generated server-side on save
            # But we can generate a likely next code for display
            try:
                work_orders_response = requests.get(
                    f"{api_base_url}/work-orders/", timeout=5
                )

                max_seq = 0
                year_prefix = f"B{year_2digit}"

                # Check work orders for batch codes
                if work_orders_response.status_code == 200:
                    work_orders = work_orders_response.json()
                    for wo in work_orders:
                        batch_code = wo.get("batch_code", "")
                        if batch_code and batch_code.startswith(year_prefix):
                            try:
                                seq_part = batch_code[-4:]
                                seq_num = int(seq_part)
                                max_seq = max(max_seq, seq_num)
                            except (ValueError, IndexError):
                                pass

                seq = max_seq + 1
                batch_code = f"B{year_2digit}{seq:04d}"
            except Exception:
                # Fallback: generate a simple code
                batch_code = f"B{year_2digit}0001"

            # Load work areas/centers (for now, use a simple list or API endpoint)
            # TODO: Create work_areas API endpoint
            work_area_options = [
                {"label": "Still01", "value": "Still01"},
                {"label": "Canning01", "value": "Canning01"},
                {"label": "Bottling01", "value": "Bottling01"},
                {"label": "Packaging01", "value": "Packaging01"},
            ]

            # Try to load from API if endpoint exists
            try:
                work_areas_url = f"{api_base_url}/work-areas/"
                work_areas_response = requests.get(work_areas_url, timeout=5)
                if work_areas_response.status_code == 200:
                    work_areas_data = work_areas_response.json()
                    work_areas = (
                        work_areas_data
                        if isinstance(work_areas_data, list)
                        else work_areas_data.get("work_areas", [])
                    )
                    work_area_options = [
                        {
                            "label": f"{wa.get('code', '')} - {wa.get('name', '')}",
                            "value": wa.get("code", ""),
                        }
                        for wa in work_areas
                        if wa.get("is_active", True)
                    ]
            except Exception:
                # If API doesn't exist yet, use default list
                pass

            # Load units from units API
            unit_options = [{"label": "KG", "value": "KG"}]  # Default
            try:
                units_url = f"{api_base_url}/units/?is_active=true"
                units_response = requests.get(units_url, timeout=5)
                if units_response.status_code == 200:
                    units_data = units_response.json()
                    units = (
                        units_data
                        if isinstance(units_data, list)
                        else units_data.get("units", [])
                    )
                    unit_options = [
                        {
                            "label": f"{u.get('code', '')} - {u.get('name', '')}",
                            "value": u.get("code", ""),
                        }
                        for u in units
                        if u.get("is_active", True)
                    ]
                    # Ensure KG is in the list
                    if not any(
                        u.get("code") == "KG" for u in units if u.get("is_active", True)
                    ):
                        unit_options.insert(
                            0, {"label": "KG - Kilogram", "value": "KG"}
                        )
            except Exception:
                # If API doesn't exist yet, use default list
                pass

            # Reset both dropdowns when modal opens
            return (
                product_options,
                None,
                [],
                None,
                work_area_options,
                unit_options,
                batch_code,
            )
        except Exception as e:
            print(f"Error loading dropdowns: {e}")
            return [], None, [], None, [], [{"label": "KG", "value": "KG"}], ""

    # Update assembly dropdown when product is selected
    @app.callback(
        [
            Output("wo-create-assembly-dropdown", "options", allow_duplicate=True),
            Output("wo-create-assembly-dropdown", "value", allow_duplicate=True),
            Output("wo-create-assembly-details", "children"),
        ],
        [
            Input("wo-create-product-dropdown", "value"),
            Input("wo-create-assembly-dropdown", "value"),
            Input("wo-create-planned-qty", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_assembly_dropdown(product_id, assembly_id, planned_qty):
        """Update assembly dropdown based on selected product and show assembly details."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # If product changed, update dropdown options
        if trigger_id == "wo-create-product-dropdown":
            if not product_id:
                return [], None, html.Div()

            try:
                # Load formulas (assemblies) filtered by product_id
                formulas_url = (
                    f"{api_base_url}/formulas/?product_id={product_id}&is_active=true"
                )
                formulas_response = requests.get(formulas_url, timeout=5)
                formulas = []
                if formulas_response.status_code == 200:
                    formulas_data = formulas_response.json()
                    # Handle both list and dict responses
                    if isinstance(formulas_data, list):
                        formulas = formulas_data
                    elif isinstance(formulas_data, dict):
                        formulas = formulas_data.get("formulas", [])

                assembly_options = [
                    {
                        "label": f"{f.get('formula_code', '')} - {f.get('formula_name', '')}",
                        "value": f.get("id", ""),
                    }
                    for f in formulas
                ]

                # Clear the selected value if assemblies changed
                return assembly_options, None, html.Div()
            except Exception as e:
                print(f"Error loading formulas for product {product_id}: {e}")
                return [], None, html.Div()

        # If assembly selected or planned_qty changed, show/update details
        elif (trigger_id == "wo-create-assembly-dropdown" and assembly_id) or (
            trigger_id == "wo-create-planned-qty" and assembly_id
        ):
            try:
                # Fetch formula details
                formula_url = f"{api_base_url}/formulas/{assembly_id}"
                formula_response = requests.get(formula_url, timeout=5)

                if formula_response.status_code != 200:
                    return no_update, no_update, html.Div()

                formula_data = formula_response.json()

                # Get yield factor and planned quantity for scaling
                yield_factor = float(formula_data.get("yield_factor", 1.0) or 1.0)
                planned_qty_float = 0.0
                if planned_qty:
                    try:
                        planned_qty_float = float(planned_qty)
                    except (ValueError, TypeError):
                        planned_qty_float = 0.0
                scale_factor = (
                    planned_qty_float * yield_factor if planned_qty_float > 0 else 1.0
                )

                # Get parent product for density
                parent_product_id = formula_data.get("product_id")
                parent_density = 0.0
                if parent_product_id:
                    try:
                        parent_resp = requests.get(
                            f"{api_base_url}/products/{parent_product_id}", timeout=5
                        )
                        if parent_resp.status_code == 200:
                            parent_data = parent_resp.json()
                            density_val = parent_data.get("density_kg_per_l", 0) or 0
                            try:
                                parent_density = float(density_val)
                            except (ValueError, TypeError):
                                pass
                    except Exception:
                        pass

                lines_data = []
                total_cost = 0.0
                total_quantity_kg = 0.0
                total_quantity_l = 0.0

                for line in formula_data.get("lines", []):
                    line_product_id = line.get("raw_material_id")
                    product_sku = ""
                    product_name = line.get("ingredient_name", "")
                    density = 0.0
                    product_usage_unit = None
                    product_usage_cost = 0.0

                    if line_product_id:
                        try:
                            product_resp = requests.get(
                                f"{api_base_url}/products/{line_product_id}", timeout=5
                            )
                            if product_resp.status_code == 200:
                                product_data = product_resp.json()
                                product_sku = product_data.get("sku", "")
                                product_name = product_data.get("name", product_name)

                                density_val = (
                                    product_data.get("density_kg_per_l", 0) or 0
                                )
                                try:
                                    density = float(density_val)
                                except (ValueError, TypeError):
                                    density = 0.0

                                product_usage_unit = (
                                    product_data.get("usage_unit", "").upper()
                                    if product_data.get("usage_unit")
                                    else None
                                )

                                # Get cost (use same logic as formulas page)
                                cost_val = (
                                    product_data.get("usage_cost_ex_gst")
                                    or product_data.get("purchase_cost_ex_gst")
                                    or product_data.get("usage_cost_inc_gst")
                                    or product_data.get("purchase_cost_inc_gst")
                                    or 0
                                )
                                if cost_val:
                                    try:
                                        product_usage_cost = round(float(cost_val), 4)
                                    except (ValueError, TypeError):
                                        product_usage_cost = 0.0
                        except Exception:
                            pass

                    quantity_kg = float(line.get("quantity_kg", 0.0) or 0.0)
                    unit = line.get("unit", "kg")

                    # Convert quantity_kg back to display unit
                    unit_upper = unit.upper() if unit else "KG"
                    quantity_display = quantity_kg

                    if unit_upper in ["G", "GRAM", "GRAMS"]:
                        quantity_display = quantity_kg * 1000.0
                    elif unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                        if density > 0:
                            quantity_display = quantity_kg / density
                    elif unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                        if density > 0:
                            quantity_l = quantity_kg / density
                            quantity_display = quantity_l * 1000.0

                    quantity_l = quantity_kg / density if density > 0 else 0.0

                    # Calculate line cost
                    line_cost = 0.0
                    if product_usage_cost > 0:
                        if product_usage_unit and product_usage_unit in [
                            "KG",
                            "KILOGRAM",
                            "KILOGRAMS",
                        ]:
                            line_cost = quantity_kg * product_usage_cost
                        elif product_usage_unit and product_usage_unit in [
                            "G",
                            "GRAM",
                            "GRAMS",
                        ]:
                            line_cost = quantity_kg * product_usage_cost * 1000.0
                        elif product_usage_unit and product_usage_unit in [
                            "L",
                            "LT",
                            "LTR",
                            "LITER",
                            "LITRE",
                        ]:
                            if density > 0:
                                line_cost = quantity_kg * product_usage_cost / density
                            else:
                                line_cost = quantity_l * product_usage_cost
                        else:
                            line_cost = quantity_kg * product_usage_cost

                    # Calculate display unit cost
                    display_unit_cost = 0.0
                    if product_usage_cost > 0 and quantity_display > 0:
                        if unit_upper == product_usage_unit:
                            display_unit_cost = product_usage_cost
                        elif unit_upper in [
                            "G",
                            "GRAM",
                            "GRAMS",
                        ] and product_usage_unit in ["KG", "KILOGRAM", "KILOGRAMS"]:
                            display_unit_cost = product_usage_cost / 1000.0
                        elif unit_upper in [
                            "KG",
                            "KILOGRAM",
                            "KILOGRAMS",
                        ] and product_usage_unit in ["G", "GRAM", "GRAMS"]:
                            display_unit_cost = product_usage_cost * 1000.0
                        else:
                            display_unit_cost = (
                                line_cost / quantity_display
                                if quantity_display > 0
                                else 0.0
                            )

                    # Calculate quantity required (scaled by planned quantity and yield factor)
                    quantity_required = quantity_display * scale_factor
                    quantity_required_kg = quantity_kg * scale_factor

                    # Calculate scaled line cost
                    scaled_line_cost = line_cost * scale_factor

                    total_cost += scaled_line_cost
                    total_quantity_kg += quantity_required_kg
                    total_quantity_l += quantity_l * scale_factor

                    lines_data.append(
                        {
                            "product_sku": product_sku,
                            "product_name": product_name,
                            "quantity": round(quantity_display, 3),
                            "unit": unit,
                            "quantity_kg": round(quantity_kg, 3),
                            "quantity_required": round(quantity_required, 3),
                            "quantity_required_kg": round(quantity_required_kg, 3),
                            "unit_cost": round(display_unit_cost, 4),
                            "line_cost": round(scaled_line_cost, 4),
                        }
                    )

                if lines_data:
                    # Calculate totals
                    if parent_density > 0 and total_quantity_kg > 0:
                        total_quantity_l = total_quantity_kg / parent_density

                    cost_per_kg = (
                        total_cost / total_quantity_kg if total_quantity_kg > 0 else 0.0
                    )
                    cost_per_l = (
                        total_cost / total_quantity_l if total_quantity_l > 0 else 0.0
                    )

                    # Create table
                    lines_table = dash_table.DataTable(
                        data=lines_data,
                        columns=[
                            {"name": "SKU", "id": "product_sku"},
                            {"name": "Product", "id": "product_name"},
                            {
                                "name": "Quantity",
                                "id": "quantity",
                                "type": "numeric",
                                "format": {"specifier": ".3f"},
                            },
                            {"name": "Unit", "id": "unit"},
                            {
                                "name": "Qty (kg)",
                                "id": "quantity_kg",
                                "type": "numeric",
                                "format": {"specifier": ".3f"},
                            },
                            {
                                "name": "Qty Required",
                                "id": "quantity_required",
                                "type": "numeric",
                                "format": {"specifier": ".3f"},
                            },
                            {
                                "name": "Qty Req (kg)",
                                "id": "quantity_required_kg",
                                "type": "numeric",
                                "format": {"specifier": ".3f"},
                            },
                            {
                                "name": "Unit Cost",
                                "id": "unit_cost",
                                "type": "numeric",
                                "format": {"specifier": ".4f"},
                            },
                            {
                                "name": "Line Cost",
                                "id": "line_cost",
                                "type": "numeric",
                                "format": {"specifier": ".4f"},
                            },
                        ],
                        style_cell={
                            "textAlign": "left",
                            "fontSize": "11px",
                            "padding": "4px",
                        },
                        style_header={
                            "backgroundColor": "rgb(230, 230, 230)",
                            "fontWeight": "bold",
                        },
                        style_cell_conditional=[
                            {
                                "if": {"column_id": "quantity_required"},
                                "backgroundColor": "rgb(230, 250, 230)",
                                "fontWeight": "bold",
                            },
                            {
                                "if": {"column_id": "quantity_required_kg"},
                                "backgroundColor": "rgb(230, 250, 230)",
                                "fontWeight": "bold",
                            },
                        ],
                    )

                    # Create summary
                    summary = html.Div(
                        [
                            html.Hr(),
                            html.Div(
                                [
                                    html.Strong("Totals: "),
                                    f"Total Cost: ${total_cost:.2f} | ",
                                    f"Total kg: {total_quantity_kg:.3f} | ",
                                    f"Total L: {total_quantity_l:.3f} | ",
                                    f"Cost/kg: ${cost_per_kg:.4f} | ",
                                    f"$/L: ${cost_per_l:.4f}",
                                ],
                                style={
                                    "fontSize": "12px",
                                    "fontWeight": "bold",
                                    "marginTop": "10px",
                                },
                            ),
                        ]
                    )

                    return (
                        no_update,
                        no_update,
                        html.Div(
                            [
                                html.H5("Assembly Details", className="mb-2"),
                                lines_table,
                                summary,
                            ]
                        ),
                    )
                else:
                    return no_update, no_update, html.Div()
            except Exception as e:
                print(f"Error loading assembly details: {e}")
                return no_update, no_update, html.Div()

        # If assembly cleared, clear details
        elif trigger_id == "wo-create-assembly-dropdown" and not assembly_id:
            return no_update, no_update, html.Div()

        # If planned_qty changed but no assembly selected, do nothing
        elif trigger_id == "wo-create-planned-qty" and not assembly_id:
            return no_update, no_update, html.Div()

        return no_update, no_update, html.Div()

    # Create work order
    @app.callback(
        [
            Output("wo-create-modal", "is_open", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
            Output("toast", "icon", allow_duplicate=True),
        ],
        [Input("wo-create-submit-btn", "n_clicks")],
        [
            State("wo-create-product-dropdown", "value"),
            State("wo-create-planned-qty", "value"),
            State("wo-create-uom", "value"),
            State("wo-create-work-center", "value"),
            State("wo-create-assembly-dropdown", "value"),
            State("wo-create-batch-code", "value"),
            State("wo-create-notes", "value"),
        ],
        prevent_initial_call=True,
    )
    def create_work_order(
        n_clicks,
        product_id,
        planned_qty,
        uom,
        work_center,
        assembly_id,
        batch_code,
        notes,
    ):
        """Create a new work order."""
        if not n_clicks:
            raise PreventUpdate

        if not product_id or not planned_qty:
            return (
                no_update,
                True,
                "Error",
                "Product and planned quantity are required",
                "danger",
            )

        try:
            # Only include assembly_id if it's provided and not empty
            data = {
                "product_id": product_id,
                "planned_qty": float(planned_qty),
                "uom": uom or "KG",
                "work_center": work_center,
                "notes": notes,
            }
            # Only add assembly_id if it's provided and not empty
            # Also validate that the assembly_id is not just whitespace or "None"
            if (
                assembly_id
                and str(assembly_id).strip()
                and str(assembly_id).strip().lower() != "none"
            ):
                # Verify the formula exists before sending
                try:
                    # Quick validation - check if formula exists in the formulas list for this product
                    formulas_check = requests.get(
                        f"{api_base_url}/formulas/?product_id={product_id}&is_active=true",
                        timeout=5,
                    )
                    if formulas_check.status_code == 200:
                        formulas_list_data = formulas_check.json()
                        # Handle both list and dict responses
                        if isinstance(formulas_list_data, list):
                            formulas_list = formulas_list_data
                        elif isinstance(formulas_list_data, dict):
                            formulas_list = formulas_list_data.get("formulas", [])
                        else:
                            formulas_list = []
                        assembly_ids = [f.get("id") for f in formulas_list]
                        if assembly_id in assembly_ids:
                            data["assembly_id"] = assembly_id
                        else:
                            # Assembly doesn't exist or doesn't belong to this product, don't send it
                            print(
                                f"Warning: Assembly {assembly_id} not found for product {product_id}, skipping"
                            )
                    else:
                        # Can't validate, skip sending assembly_id
                        print(
                            f"Warning: Could not validate assembly {assembly_id}: API error"
                        )
                except Exception as e:
                    # If validation fails, skip sending assembly_id
                    print(f"Warning: Could not validate assembly {assembly_id}: {e}")
            # Note: batch_code is generated server-side, so we don't send it here
            # The server will generate it using BatchCodeGenerator

            url = f"{api_base_url}/work-orders/"
            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 201:
                return (
                    False,  # Close modal
                    True,  # Show toast
                    "Success",
                    f"Work order created successfully: {response.json().get('code', '')}",
                    "success",
                )
            else:
                error_msg = response.json().get("detail", "Unknown error")
                return (
                    no_update,
                    True,
                    "Error",
                    f"Failed to create work order: {error_msg}",
                    "danger",
                )
        except Exception as e:
            return (
                no_update,
                True,
                "Error",
                f"Failed to create work order: {str(e)}",
                "danger",
            )

    # Load work order detail when row selected or detail tab active
    @app.callback(
        [
            Output("wo-detail-content", "children"),
            Output("wo-detail-content", "style"),
            Output("wo-detail-wo-id", "data"),
            Output("wo-main-tabs", "active_tab", allow_duplicate=True),
            Output("wo-detail-active-tab", "data", allow_duplicate=True),
        ],
        [
            Input("wo-list-table", "selected_rows"),
            Input("wo-main-tabs", "active_tab"),
        ],
        [
            State("wo-list-table", "data"),
            State("wo-detail-wo-id", "data"),
            State("wo-detail-active-tab", "data"),
        ],
        prevent_initial_call="initial_duplicate",
    )
    def load_work_order_detail(
        selected_rows, active_tab, table_data, current_wo_id, current_detail_tab
    ):
        """Load work order detail when selected or detail tab is active."""
        ctx = dash.callback_context
        if not ctx.triggered:
            # Initial load - don't do anything
            raise PreventUpdate

        triggered = ctx.triggered[0]["prop_id"] if ctx.triggered else None

        # Handle case where table_data might not exist (component not in DOM yet)
        if table_data is None:
            table_data = []

        # If a row was selected, switch to detail tab and load the work order
        if triggered == "wo-list-table.selected_rows":
            if selected_rows and table_data and len(selected_rows) > 0:
                wo_id = table_data[selected_rows[0]].get("id")
                if wo_id:
                    try:
                        url = f"{api_base_url}/work-orders/{wo_id}"
                        response = requests.get(url, timeout=5)
                        if response.status_code == 200:
                            wo = response.json()
                            return (
                                create_work_order_detail_layout(
                                    wo, api_base_url, active_tab="wo-detail-inputs"
                                ),
                                {"display": "block"},
                                wo_id,
                                "detail",
                                "wo-detail-inputs",
                            )
                        else:
                            return (
                                html.Div(
                                    [
                                        html.P(
                                            f"Error loading work order: {response.status_code}"
                                        ),
                                        build_detail_tab_content(
                                            {},
                                            api_base_url,
                                            "wo-detail-inputs",
                                        ),
                                    ]
                                ),
                                {"display": "block"},
                                wo_id,
                                "detail",
                                "wo-detail-inputs",
                            )
                    except Exception as e:
                        return (
                            html.Div(
                                [
                                    html.P(f"Error: {str(e)}"),
                                    build_detail_tab_content(
                                        {},
                                        api_base_url,
                                        "wo-detail-inputs",
                                    ),
                                ]
                            ),
                            {"display": "block"},
                            wo_id,
                            "detail",
                            "wo-detail-inputs",
                        )
            # No row selected - show message
            return (
                html.Div(
                    [
                        html.P("Select a work order from the list to view details"),
                        build_detail_tab_content(
                            {},
                            api_base_url,
                            current_detail_tab or "wo-detail-inputs",
                        ),
                    ]
                ),
                {"display": "block"},
                None,
                "detail",
                current_detail_tab or "wo-detail-inputs",
            )

        # If detail tab was activated, try to load current work order or selected one
        elif triggered == "wo-main-tabs.active_tab":
            if active_tab == "detail":
                # Try to get work order from selected row first
                if selected_rows and table_data and len(selected_rows) > 0:
                    wo_id = table_data[selected_rows[0]].get("id")
                    if wo_id:
                        try:
                            url = f"{api_base_url}/work-orders/{wo_id}"
                            response = requests.get(url, timeout=5)
                            if response.status_code == 200:
                                wo = response.json()
                                return (
                                    create_work_order_detail_layout(
                                        wo,
                                        api_base_url,
                                        active_tab=current_detail_tab
                                        or "wo-detail-inputs",
                                    ),
                                    {"display": "block"},
                                    wo_id,
                                    no_update,
                                    no_update,
                                )
                        except Exception as e:
                            return (
                                html.Div(
                                    [
                                        html.P(f"Error: {str(e)}"),
                                        build_detail_tab_content(
                                            {},
                                            api_base_url,
                                            current_detail_tab or "wo-detail-inputs",
                                        ),
                                    ]
                                ),
                                {"display": "block"},
                                wo_id,
                                no_update,
                                no_update,
                            )
                # Otherwise try current_wo_id
                elif current_wo_id:
                    try:
                        url = f"{api_base_url}/work-orders/{current_wo_id}"
                        response = requests.get(url, timeout=5)
                        if response.status_code == 200:
                            wo = response.json()
                            return (
                                create_work_order_detail_layout(
                                    wo,
                                    api_base_url,
                                    active_tab=current_detail_tab or "wo-detail-inputs",
                                ),
                                {"display": "block"},
                                current_wo_id,
                                no_update,
                                no_update,
                            )
                    except (ValueError, TypeError, AttributeError):
                        pass
                # Default: show message
                return (
                    html.Div(
                        [
                            html.P("Select a work order from the list to view details"),
                            build_detail_tab_content(
                                {},
                                api_base_url,
                                current_detail_tab or "wo-detail-inputs",
                            ),
                        ]
                    ),
                    {"display": "block"},
                    None,
                    no_update,
                    no_update,
                )
            else:
                # Hide detail content when not on detail tab
                return no_update, {"display": "none"}, no_update, no_update, no_update

        # Default: prevent update
        raise PreventUpdate

    # Issue material
    @app.callback(
        [
            Output("wo-issue-toast", "is_open", allow_duplicate=True),
            Output("wo-issue-toast", "header", allow_duplicate=True),
            Output("wo-issue-toast", "children", allow_duplicate=True),
        ],
        [Input("wo-issue-submit-btn", "n_clicks")],
        [
            State("wo-detail-wo-id", "data"),
            State("wo-issue-component-dropdown", "value"),
            State("wo-issue-qty", "value"),
            State("wo-issue-batch-dropdown", "value"),
        ],
        prevent_initial_call=True,
    )
    def issue_material(n_clicks, wo_id, component_id, qty, batch_id):
        """Issue material for work order."""
        if not n_clicks or not wo_id:
            raise PreventUpdate

        if not component_id or not qty:
            return (
                True,
                "Error",
                "Component and quantity are required",
            )

        try:
            data = {
                "component_product_id": component_id,
                "qty": float(qty),
                "source_batch_id": batch_id,
                "uom": None,
            }

            url = f"{api_base_url}/work-orders/{wo_id}/issues"
            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 201:
                return (
                    True,
                    "Success",
                    "Material issued successfully",
                )
            else:
                error_msg = response.json().get("detail", "Unknown error")
                return (
                    True,
                    "Error",
                    f"Failed to issue material: {error_msg}",
                )
        except Exception as e:
            return (
                True,
                "Error",
                f"Failed to issue material: {str(e)}",
            )

    @app.callback(
        [
            Output("wo-issue-component-dropdown", "value", allow_duplicate=True),
            Output("wo-issue-qty", "value", allow_duplicate=True),
            Output("wo-issue-batch-dropdown", "value", allow_duplicate=True),
        ],
        Input("wo-inputs-edit-btn", "n_clicks"),
        State("wo-inputs-table", "selected_rows"),
        State("wo-inputs-table", "data"),
        prevent_initial_call=True,
    )
    def prefill_issue_form(edit_clicks, selected_rows, table_data):
        """Prefill the issue material form from the selected input line."""
        if not edit_clicks:
            raise PreventUpdate

        if not table_data or not selected_rows:
            return no_update, no_update, no_update

        row_index = selected_rows[0]
        if row_index >= len(table_data):
            return no_update, no_update, no_update

        row = table_data[row_index]
        component_id = row.get("component_product_id")
        remaining_display = row.get("remaining_qty")
        if remaining_display is not None:
            remaining_display = round(safe_float(remaining_display), 3)
            if remaining_display <= 0:
                remaining_display = None

        return (
            component_id,
            remaining_display,
            row.get("batch") or None,
        )

    # Record QC
    @app.callback(
        Output("wo-qc-type-options", "data"),
        Input("wo-main-tabs", "active_tab"),
        prevent_initial_call=True,
    )
    def load_qc_types(active_tab):
        """Load QC test type settings when entering detail view."""
        if active_tab != "detail":
            raise PreventUpdate

        try:
            url = f"{api_base_url}/work-orders/qc-test-types"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return dash.no_update
        except Exception as e:
            print(f"Error loading QC test types: {e}")
            return dash.no_update

    @app.callback(
        Output("wo-qc-test-type", "options"),
        Input("wo-qc-type-options", "data"),
        prevent_initial_call=True,
    )
    def set_qc_type_options(type_data):
        """Populate QC test type dropdown options."""
        if not type_data:
            return []

        options = []
        for item in type_data:
            label = item.get("code") or item.get("name") or "Unknown"
            unit = item.get("unit")
            if unit:
                label = f"{label} ({unit})"
            options.append({"label": label, "value": item.get("id")})
        return options

    @app.callback(
        Output("wo-qc-unit-display", "children"),
        Input("wo-qc-test-type", "value"),
        State("wo-qc-type-options", "data"),
        prevent_initial_call=True,
    )
    def update_qc_unit_display(selected_type_id, type_data):
        """Display the unit for the selected QC test type."""
        if not selected_type_id or not type_data:
            return "—"
        for item in type_data:
            if item.get("id") == selected_type_id:
                unit = item.get("unit")
                return unit if unit else "—"
        return "—"

    @app.callback(
        [
            Output("wo-qc-edit-btn", "disabled"),
            Output("wo-qc-delete-btn", "disabled"),
        ],
        Input("wo-qc-table", "selected_rows"),
        prevent_initial_call=True,
    )
    def toggle_qc_action_buttons(selected_rows):
        """Enable QC edit/delete buttons when a row is selected."""
        has_selection = bool(selected_rows)
        disabled = not has_selection
        return disabled, disabled

    @app.callback(
        [
            Output("wo-qc-test-type", "value", allow_duplicate=True),
            Output("wo-qc-result-value", "value", allow_duplicate=True),
            Output("wo-qc-result-text", "value", allow_duplicate=True),
            Output("wo-qc-status", "value", allow_duplicate=True),
            Output("wo-qc-tester", "value", allow_duplicate=True),
            Output("wo-qc-note", "value", allow_duplicate=True),
            Output("wo-qc-current-id", "data", allow_duplicate=True),
        ],
        Input("wo-qc-edit-btn", "n_clicks"),
        State("wo-qc-table", "selected_rows"),
        State("wo-qc-table", "data"),
        State("wo-qc-type-options", "data"),
        prevent_initial_call=True,
    )
    def prefill_qc_form(edit_clicks, selected_rows, table_data, type_data):
        """Prefill QC form for editing."""
        if not edit_clicks:
            raise PreventUpdate

        if not selected_rows:
            raise PreventUpdate

        row_index = selected_rows[0]
        if table_data is None or row_index >= len(table_data):
            raise PreventUpdate

        row = table_data[row_index]
        type_id = row.get("test_type_id")

        if not type_id and type_data:
            row_test_type = (row.get("test_type") or "").upper()
            for item in type_data:
                if (item.get("code") or "").upper() == row_test_type:
                    type_id = item.get("id")
                    break

        return (
            type_id,
            row.get("result_value"),
            row.get("result_text"),
            (row.get("status_raw") or "pending").lower() or "pending",
            row.get("tester"),
            row.get("note"),
            row.get("id"),
        )

    @app.callback(
        [
            Output("wo-qc-toast", "is_open", allow_duplicate=True),
            Output("wo-qc-toast", "header", allow_duplicate=True),
            Output("wo-qc-toast", "children", allow_duplicate=True),
            Output("wo-qc-current-id", "data", allow_duplicate=True),
        ],
        Input("wo-qc-delete-btn", "n_clicks"),
        [
            State("wo-detail-wo-id", "data"),
            State("wo-qc-table", "selected_rows"),
            State("wo-qc-table", "data"),
            State("wo-qc-current-id", "data"),
        ],
        prevent_initial_call=True,
    )
    def delete_qc_result(
        delete_clicks, wo_id, selected_rows, table_data, current_qc_id
    ):
        """Soft delete a QC test result."""
        if not delete_clicks or not wo_id:
            raise PreventUpdate

        if not selected_rows:
            return (
                True,
                "Error",
                "Select a QC result to delete",
                current_qc_id,
            )

        row_index = selected_rows[0]
        if table_data is None or row_index >= len(table_data):
            raise PreventUpdate

        qc_id = table_data[row_index].get("id")
        if not qc_id:
            return (
                True,
                "Error",
                "Invalid QC result selected",
                current_qc_id,
            )

        try:
            url = f"{api_base_url}/work-orders/{wo_id}/qc/{qc_id}"
            response = requests.delete(url, timeout=10)
            if response.status_code == 204:
                return (
                    True,
                    "Success",
                    "QC result deleted",
                    None if current_qc_id == qc_id else current_qc_id,
                )
            else:
                error_msg = response.json().get("detail", "Unknown error")
                return (
                    True,
                    "Error",
                    f"Failed to delete QC result: {error_msg}",
                    current_qc_id,
                )
        except Exception as e:
            return (
                True,
                "Error",
                f"Failed to delete QC result: {str(e)}",
                current_qc_id,
            )

    @app.callback(
        [
            Output("wo-qc-toast", "is_open", allow_duplicate=True),
            Output("wo-qc-toast", "header", allow_duplicate=True),
            Output("wo-qc-toast", "children", allow_duplicate=True),
            Output("wo-qc-current-id", "data", allow_duplicate=True),
        ],
        [Input("wo-qc-submit-btn", "n_clicks")],
        [
            State("wo-detail-wo-id", "data"),
            State("wo-qc-test-type", "value"),
            State("wo-qc-result-value", "value"),
            State("wo-qc-result-text", "value"),
            State("wo-qc-status", "value"),
            State("wo-qc-tester", "value"),
            State("wo-qc-note", "value"),
            State("wo-qc-current-id", "data"),
        ],
        prevent_initial_call=True,
    )
    def record_qc(
        n_clicks,
        wo_id,
        test_type_id,
        result_value,
        result_text,
        qc_status,
        tester,
        note,
        current_qc_id,
    ):
        """Create or update a QC test result."""
        if not n_clicks or not wo_id:
            raise PreventUpdate

        if not test_type_id:
            return (
                True,
                "Error",
                "Test type is required",
                dash.no_update,
            )

        payload = {
            "test_type_id": test_type_id,
            "result_value": float(result_value)
            if result_value not in (None, "")
            else None,
            "result_text": result_text,
            "status": qc_status or "pending",
            "tester": tester,
            "note": note,
        }

        try:
            if current_qc_id:
                url = f"{api_base_url}/work-orders/{wo_id}/qc/{current_qc_id}"
                response = requests.patch(url, json=payload, timeout=10)
                success_code = 200
                success_message = "QC test updated successfully"
            else:
                url = f"{api_base_url}/work-orders/{wo_id}/qc"
                response = requests.post(url, json=payload, timeout=10)
                success_code = 201
                success_message = "QC test recorded successfully"

            if response.status_code == success_code:
                return (
                    True,
                    "Success",
                    success_message,
                    None,
                )
            else:
                error_msg = response.json().get("detail", "Unknown error")
                return (
                    True,
                    "Error",
                    f"Failed to save QC result: {error_msg}",
                    current_qc_id,
                )
        except Exception as e:
            return (
                True,
                "Error",
                f"Failed to save QC result: {str(e)}",
                current_qc_id,
            )

    # Complete work order
    @app.callback(
        [
            Output("wo-complete-toast", "is_open", allow_duplicate=True),
            Output("wo-complete-toast", "header", allow_duplicate=True),
            Output("wo-complete-toast", "children", allow_duplicate=True),
        ],
        [Input("wo-complete-submit-btn", "n_clicks")],
        [
            State("wo-detail-wo-id", "data"),
            State("wo-complete-qty", "value"),
        ],
        prevent_initial_call=True,
    )
    def complete_work_order(n_clicks, wo_id, qty_produced):
        """Complete work order."""
        if not n_clicks or not wo_id:
            raise PreventUpdate

        if not qty_produced:
            return (
                True,
                "Error",
                "Quantity produced is required",
            )

        try:
            data = {
                "qty_produced": float(qty_produced),
                "batch_attrs": {},
            }

            url = f"{api_base_url}/work-orders/{wo_id}/complete"
            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 200:
                return (
                    True,
                    "Success",
                    "Work order completed successfully",
                )
            else:
                error_msg = response.json().get("detail", "Unknown error")
                return (
                    True,
                    "Error",
                    f"Failed to complete work order: {error_msg}",
                )
        except Exception as e:
            return (
                True,
                "Error",
                f"Failed to complete work order: {str(e)}",
            )

    # Load costs
    @app.callback(
        Output("wo-costs-content", "children"),
        [Input("wo-detail-wo-id", "data")],
        prevent_initial_call=True,
    )
    def load_work_order_costs(wo_id):
        """Load work order cost breakdown."""
        if not wo_id:
            return html.Div("No work order selected")

        try:
            url = f"{api_base_url}/work-orders/{wo_id}/costs"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                costs = response.json()
                return dbc.Card(
                    [
                        dbc.CardHeader("Cost Breakdown"),
                        dbc.CardBody(
                            [
                                html.P(
                                    f"Material Cost: ${costs.get('material_cost', 0):.2f}"
                                ),
                                html.P(
                                    f"Overhead Cost: ${costs.get('overhead_cost', 0):.2f}"
                                ),
                                html.P(
                                    f"Total Cost: ${costs.get('total_cost', 0):.2f}"
                                ),
                                html.P(
                                    f"Quantity Produced: {costs.get('qty_produced', 0):.3f}"
                                ),
                                html.P(
                                    f"Unit Cost: ${costs.get('unit_cost', 0):.2f}"
                                    if costs.get("unit_cost")
                                    else "N/A"
                                ),
                            ]
                        ),
                    ]
                )
            else:
                return html.Div(f"Error loading costs: {response.status_code}")
        except Exception as e:
            return html.Div(f"Error: {str(e)}")

    # Load genealogy
    @app.callback(
        Output("wo-genealogy-content", "children"),
        [Input("wo-detail-wo-id", "data")],
        prevent_initial_call=True,
    )
    def load_genealogy(wo_id):
        """Load batch genealogy."""
        if not wo_id:
            return html.Div("No work order selected")

        try:
            url = f"{api_base_url}/work-orders/{wo_id}/genealogy"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                genealogy = response.json()
                return dbc.Card(
                    [
                        dbc.CardHeader("Batch Genealogy"),
                        dbc.CardBody(
                            [
                                html.P(
                                    f"Batch Code: {genealogy.get('batch_code', '')}"
                                ),
                                html.P(
                                    f"Input Batch IDs: {', '.join(genealogy.get('input_batch_ids', []))}"
                                ),
                                html.Pre(
                                    json.dumps(genealogy.get("genealogy", {}), indent=2)
                                ),
                            ]
                        ),
                    ]
                )
            else:
                return html.Div(f"Error loading genealogy: {response.status_code}")
        except Exception as e:
            return html.Div(f"Error: {str(e)}")

    # Work order actions (release, start, void)
    @app.callback(
        [
            Output("wo-action-toast", "is_open", allow_duplicate=True),
            Output("wo-action-toast", "header", allow_duplicate=True),
            Output("wo-action-toast", "children", allow_duplicate=True),
        ],
        [
            Input("wo-release-btn", "n_clicks"),
            Input("wo-start-btn", "n_clicks"),
            Input("wo-void-btn", "n_clicks"),
        ],
        [State("wo-detail-wo-id", "data")],
        prevent_initial_call=True,
    )
    def work_order_actions(release_clicks, start_clicks, void_clicks, wo_id):
        """Handle work order actions (release, start, void)."""
        ctx = dash.callback_context
        if not ctx.triggered or not wo_id:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        try:
            if button_id == "wo-release-btn":
                if not release_clicks:
                    raise PreventUpdate
                url = f"{api_base_url}/work-orders/{wo_id}/release"
                action = "released"
                data = {}
            elif button_id == "wo-start-btn":
                if not start_clicks:
                    raise PreventUpdate
                url = f"{api_base_url}/work-orders/{wo_id}/start"
                action = "started"
                data = {}
            elif button_id == "wo-void-btn":
                if not void_clicks:
                    raise PreventUpdate
                url = f"{api_base_url}/work-orders/{wo_id}/void"
                action = "voided"
                data = {"reason": "Voided from UI"}
            else:
                raise PreventUpdate

            response = requests.post(url, json=data, timeout=10)

            if response.status_code in [200, 201]:
                return (
                    True,
                    "Success",
                    f"Work order {action} successfully",
                )
            else:
                error_msg = response.json().get("detail", "Unknown error")
                return (
                    True,
                    "Error",
                    f"Failed to {action} work order: {error_msg}",
                )
        except Exception as e:
            return (
                True,
                "Error",
                f"Failed to perform action: {str(e)}",
            )

    # Tab switching for main tabs - control visibility of table and create button
    @app.callback(
        [
            Output("wo-main-tab-content", "children"),
            Output("wo-list-table-wrapper", "style"),
            Output("wo-create-btn-wrapper", "style"),
            Output("wo-detail-content", "style", allow_duplicate=True),
        ],
        [Input("wo-main-tabs", "active_tab")],
        [State("wo-detail-wo-id", "data")],
        prevent_initial_call="initial_duplicate",
    )
    def switch_main_tabs(active_tab, current_wo_id):
        """Switch between main tabs (list, detail, rates, batch-lookup)."""
        # Default to "list" if active_tab is None or empty
        if not active_tab:
            active_tab = "list"

        if active_tab == "list":
            # Show table and create button, hide detail content
            return (
                html.Div("Work Orders", className="h4 mb-3"),
                {"display": "block"},  # Show table wrapper
                {"display": "block"},  # Show create button wrapper
                {"display": "none"},  # Hide detail content
            )
        elif active_tab == "detail":
            # Hide table and create button, show detail content
            # Note: wo-detail-content is always in layout, we just need to show it
            return (
                html.Div("Work Order Detail", className="h4 mb-3"),
                {"display": "none"},  # Hide table wrapper
                {"display": "none"},  # Hide create button wrapper
                {"display": "block"},  # Show detail content
            )
        elif active_tab == "rates":
            return (
                dbc.Card(
                    [
                        dbc.CardHeader("Cost Rate Manager"),
                        dbc.CardBody(html.P("Cost rate management coming soon...")),
                    ]
                ),
                {"display": "none"},  # Hide table wrapper
                {"display": "none"},  # Hide create button wrapper
                {"display": "none"},  # Hide detail content
            )
        elif active_tab == "batch-lookup":
            return (
                dbc.Card(
                    [
                        dbc.CardHeader("Batch Lookup"),
                        dbc.CardBody(
                            html.P("Batch lookup and traceability coming soon...")
                        ),
                    ]
                ),
                {"display": "none"},  # Hide table wrapper
                {"display": "none"},  # Hide create button wrapper
                {"display": "none"},  # Hide detail content
            )
        return (
            html.Div(),
            {"display": "none"},  # Hide table wrapper
            {"display": "none"},  # Hide create button wrapper
            {"display": "none"},  # Hide detail content
        )

    # Open create modal
    @app.callback(
        Output("wo-create-modal", "is_open", allow_duplicate=True),
        [Input("wo-create-btn", "n_clicks"), Input("wo-create-cancel-btn", "n_clicks")],
        [State("wo-create-modal", "is_open")],
        prevent_initial_call=True,
    )
    def toggle_create_modal(create_clicks, cancel_clicks, is_open):
        """Toggle create work order modal."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        return not is_open

    # Refresh detail view after actions
    @app.callback(
        [
            Output("wo-detail-content", "children", allow_duplicate=True),
            Output("wo-detail-content", "style", allow_duplicate=True),
            Output("wo-detail-wo-id", "data", allow_duplicate=True),
        ],
        [
            Input("wo-issue-submit-btn", "n_clicks"),
            Input("wo-qc-submit-btn", "n_clicks"),
            Input("wo-qc-delete-btn", "n_clicks"),
            Input("wo-complete-submit-btn", "n_clicks"),
            Input("wo-release-btn", "n_clicks"),
            Input("wo-start-btn", "n_clicks"),
            Input("wo-void-btn", "n_clicks"),
        ],
        [State("wo-detail-wo-id", "data"), State("wo-detail-active-tab", "data")],
        prevent_initial_call="initial_duplicate",
    )
    def refresh_detail_view(
        issue_clicks,
        qc_clicks,
        _delete_qc_clicks,
        complete_clicks,
        release_clicks,
        start_clicks,
        void_clicks,
        wo_id,
        current_detail_tab,
    ):
        """Refresh detail view after actions."""
        ctx = dash.callback_context
        if not ctx.triggered or not wo_id:
            raise PreventUpdate

        try:
            url = f"{api_base_url}/work-orders/{wo_id}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                wo = response.json()
                return (
                    create_work_order_detail_layout(
                        wo,
                        api_base_url,
                        active_tab=current_detail_tab or "wo-detail-inputs",
                    ),
                    {"display": "block"},
                    wo_id,
                )
            else:
                return no_update, no_update, no_update
        except Exception as e:
            print(f"Error refreshing detail: {e}")
            return no_update, no_update, no_update

    # Detail tab content switching
    @app.callback(
        [
            Output("wo-detail-tab-content", "children"),
            Output("wo-detail-active-tab", "data"),
        ],
        [Input("wo-detail-tabs", "active_tab")],
        [State("wo-detail-wo-id", "data")],
        prevent_initial_call=True,
    )
    def switch_detail_tabs(active_tab, wo_id):
        """Switch between detail view tabs."""
        if not wo_id:
            return build_detail_tab_content({}, api_base_url, active_tab), active_tab

        try:
            url = f"{api_base_url}/work-orders/{wo_id}"
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                return (
                    html.Div(f"Error loading work order: {response.status_code}"),
                    no_update,
                )

            wo = response.json()
            return build_detail_tab_content(wo, api_base_url, active_tab), active_tab
        except Exception as e:
            return (
                html.Div(
                    [
                        html.P(f"Error: {str(e)}"),
                        build_detail_tab_content({}, api_base_url, active_tab),
                    ]
                ),
                no_update,
            )


def create_complete_form(visible: bool = False, uom: Optional[str] = None) -> html.Div:
    """Create the work order completion form."""

    uom_display = f" ({uom})" if uom else ""

    return html.Div(
        [
            html.Hr(),
            html.H5("Complete Work Order"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label(f"Quantity Produced{uom_display} *"),
                            dbc.Input(
                                id="wo-complete-qty",
                                type="number",
                                step=0.001,
                                min=0,
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Button(
                "Complete Work Order",
                id="wo-complete-submit-btn",
                color="success",
            ),
        ],
        style={"display": "block"} if visible else {"display": "none"},
    )


def create_qc_section(
    table_data: Optional[List[Dict[str, Any]]] = None, visible: bool = False
) -> html.Div:
    """Create the QC section, optionally hidden when not on the QC tab."""

    table_data = table_data or []
    qty_format = Format(precision=4, scheme=Scheme.fixed)

    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardHeader("QC Tests"),
                    dbc.CardBody(
                        [
                            dash_table.DataTable(
                                id="wo-qc-table",
                                columns=[
                                    {"name": "Test Type", "id": "test_type"},
                                    {
                                        "name": "Result Value",
                                        "id": "result_value",
                                        "type": "numeric",
                                        "format": qty_format,
                                    },
                                    {"name": "Result Text", "id": "result_text"},
                                    {"name": "Unit", "id": "unit"},
                                    {"name": "Status", "id": "status"},
                                    {"name": "Tested At", "id": "tested_at"},
                                    {"name": "Tester", "id": "tester"},
                                    {"name": "Note", "id": "note"},
                                ],
                                data=table_data,
                                row_selectable="single",
                                style_table={"overflowX": "auto"},
                                style_cell={"padding": "0.5rem"},
                                hidden_columns=[
                                    "id",
                                    "test_type_id",
                                    "status_raw",
                                    "tested_at_raw",
                                ],
                                sort_action="native",
                            ),
                            html.Div(
                                [
                                    dbc.Button(
                                        "Edit Selected",
                                        id="wo-qc-edit-btn",
                                        outline=True,
                                        color="secondary",
                                        size="sm",
                                        className="me-2 mt-3",
                                        disabled=True,
                                    ),
                                    dbc.Button(
                                        "Delete Selected",
                                        id="wo-qc-delete-btn",
                                        outline=True,
                                        color="danger",
                                        size="sm",
                                        className="mt-3",
                                        disabled=True,
                                    ),
                                ]
                            ),
                            html.Hr(),
                            html.H5("Record QC Test"),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label("Test Type *"),
                                            dcc.Dropdown(
                                                id="wo-qc-test-type",
                                                options=[],
                                                placeholder="Select test type",
                                            ),
                                        ],
                                        md=4,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Unit"),
                                            html.Div(
                                                id="wo-qc-unit-display",
                                                className="mt-2 text-muted",
                                                children="—",
                                            ),
                                        ],
                                        md=2,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Result Value"),
                                            dbc.Input(
                                                id="wo-qc-result-value",
                                                type="number",
                                                step=0.01,
                                            ),
                                        ],
                                        md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Result Text"),
                                            dbc.Input(
                                                id="wo-qc-result-text",
                                                type="text",
                                            ),
                                        ],
                                        md=3,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label("Status"),
                                            dcc.Dropdown(
                                                id="wo-qc-status",
                                                options=[
                                                    {
                                                        "label": "Pending",
                                                        "value": "pending",
                                                    },
                                                    {"label": "Pass", "value": "pass"},
                                                    {"label": "Fail", "value": "fail"},
                                                ],
                                                value="pending",
                                            ),
                                        ],
                                        md=4,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Tester"),
                                            dbc.Input(id="wo-qc-tester", type="text"),
                                        ],
                                        md=4,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Note"),
                                            dbc.Input(id="wo-qc-note", type="text"),
                                        ],
                                        md=4,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            dbc.Button(
                                "Save QC Result",
                                id="wo-qc-submit-btn",
                                color="primary",
                            ),
                        ]
                    ),
                ]
            )
        ],
        style={"display": "block"} if visible else {"display": "none"},
    )


def create_costs_section(
    visible: bool = False,
) -> html.Div:
    """Render the costs section (placeholder until detailed data is available)."""

    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardHeader("Costs"),
                    dbc.CardBody(
                        [
                            html.P(
                                "Cost summary will appear here once calculations are implemented.",
                                className="text-muted",
                            )
                        ]
                    ),
                ]
            )
        ],
        style={"display": "block"} if visible else {"display": "none"},
    )


def create_genealogy_section(
    visible: bool = False,
) -> html.Div:
    """Render the genealogy section (placeholder until data is wired in)."""

    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardHeader("Genealogy"),
                    dbc.CardBody(
                        [
                            html.P(
                                "Genealogy details will be shown here once tracking is available.",
                                className="text-muted",
                            )
                        ]
                    ),
                ]
            )
        ],
        style={"display": "block"} if visible else {"display": "none"},
    )


def build_detail_tab_content(
    wo: Optional[Dict[str, Any]],
    api_base_url: str,
    active_tab: str,
    raw_status: Optional[str] = None,
) -> html.Div:
    """Compose the detail tab content with appropriate visibility and data."""

    wo = wo or {}
    product_cache: Dict[str, Dict[str, Any]] = {}
    inputs_data, _ = build_input_rows(wo, api_base_url, product_cache)
    outputs_data = build_output_rows(wo, api_base_url, product_cache)

    status = raw_status if raw_status is not None else (wo.get("status") or "").lower()
    allow_issue_edit = status not in {"complete", "void"}
    allow_complete = status not in {"draft", "void", "complete"}
    output_uom = wo.get("uom") or ""

    qc_tests = wo.get("qc_tests", []) or []
    qc_table_data: List[Dict[str, Any]] = []
    for qc in qc_tests:
        tested_at_raw = qc.get("tested_at")
        if tested_at_raw:
            try:
                tested_at_display = datetime.fromisoformat(
                    tested_at_raw.rstrip("Z")
                ).strftime("%Y-%m-%d %H:%M")
            except Exception:
                tested_at_display = tested_at_raw
        else:
            tested_at_display = ""

        qc_table_data.append(
            {
                "id": qc.get("id"),
                "test_type": qc.get("test_type", ""),
                "test_type_id": qc.get("test_type_id"),
                "result_value": safe_float(qc.get("result_value")),
                "result_text": qc.get("result_text", ""),
                "unit": qc.get("unit", "") or "",
                "status": (qc.get("status") or "").title(),
                "status_raw": qc.get("status", ""),
                "tested_at": tested_at_display,
                "tested_at_raw": tested_at_raw,
                "tester": qc.get("tester", "") or "",
                "note": qc.get("note", "") or "",
            }
        )

    return html.Div(
        [
            create_issue_section(
                table_data=inputs_data,
                visible=active_tab == "wo-detail-inputs",
                allow_edit=allow_issue_edit,
            ),
            create_outputs_section(
                table_data=outputs_data,
                visible=active_tab == "wo-detail-outputs",
            ),
            create_qc_section(
                table_data=qc_table_data,
                visible=active_tab == "wo-detail-qc",
            ),
            create_costs_section(visible=active_tab == "wo-detail-costs"),
            create_genealogy_section(visible=active_tab == "wo-detail-genealogy"),
            create_complete_form(
                visible=active_tab == "wo-detail-outputs" and allow_complete,
                uom=output_uom,
            ),
        ],
        id="wo-detail-tab-panels",
    )


def create_issue_section(
    table_data: Optional[List[Dict[str, Any]]] = None,
    visible: bool = False,
    allow_edit: bool = True,
) -> html.Div:
    """Create the inputs/issue material section with planned vs actual visibility."""

    table_data = table_data or []
    qty_format = Format(precision=3, scheme=Scheme.fixed)

    header_row = dbc.Row(
        [
            dbc.Col(html.H5("Input Materials"), md=6),
            dbc.Col(
                dbc.Button(
                    "Edit Selected",
                    id="wo-inputs-edit-btn",
                    outline=True,
                    color="secondary",
                    size="sm",
                    className="float-end",
                    disabled=not allow_edit,
                ),
                md=6,
            ),
        ],
        align="center",
        className="mb-3",
    )

    table = dash_table.DataTable(
        id="wo-inputs-table",
        columns=[
            {"name": "Component", "id": "component_label"},
            {
                "name": "Planned Qty",
                "id": "planned_qty",
                "type": "numeric",
                "format": qty_format,
                "editable": False,
            },
            {
                "name": "Actual Issued",
                "id": "actual_qty",
                "type": "numeric",
                "format": qty_format,
                "editable": False,
            },
            {
                "name": "Remaining",
                "id": "remaining_qty",
                "type": "numeric",
                "format": qty_format,
                "editable": False,
            },
            {"name": "UOM", "id": "uom", "editable": False},
            {"name": "Batch", "id": "batch", "editable": False},
        ],
        data=table_data,
        hidden_columns=[
            "component_product_id",
            "planned_qty_canonical",
            "actual_qty_canonical",
            "remaining_qty_canonical",
        ],
        row_selectable="single",
        style_table={"overflowX": "auto"},
        style_cell={"padding": "0.5rem"},
        sort_action="native",
    )

    body_children: List[Any] = [header_row]

    if not table_data:
        body_children.append(
            dbc.Alert(
                "No input components defined for this work order.",
                color="info",
                className="mb-3",
            )
        )

    body_children.extend(
        [
            table,
            html.Hr(className="my-3"),
            html.H6("Add Additional Material"),
            html.P(
                "Record extra material usage or top up planned quantities. "
                "Select a component to prefill the form, then issue the additional amount.",
                className="text-muted",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Component"),
                            dcc.Dropdown(
                                id="wo-issue-component-dropdown",
                                options=[],
                                placeholder="Select component",
                                disabled=not allow_edit,
                            ),
                        ],
                        md=5,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Quantity"),
                            dbc.Input(
                                id="wo-issue-qty",
                                type="number",
                                step=0.001,
                                min=0,
                                disabled=not allow_edit,
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Batch (optional)"),
                            dcc.Dropdown(
                                id="wo-issue-batch-dropdown",
                                options=[],
                                placeholder="Select batch",
                                disabled=not allow_edit,
                                clearable=True,
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Button(
                "Issue Material",
                id="wo-issue-submit-btn",
                color="primary",
                disabled=not allow_edit,
            ),
        ]
    )

    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardBody(body_children),
                ]
            )
        ],
        style={"display": "block"} if visible else {"display": "none"},
    )


def create_outputs_section(
    table_data: Optional[List[Dict[str, Any]]] = None,
    visible: bool = False,
) -> html.Div:
    """Render the outputs table for the work order."""

    table_data = table_data or []
    qty_format = Format(precision=3, scheme=Scheme.fixed)

    outputs_table = dash_table.DataTable(
        id="wo-outputs-table",
        columns=[
            {"name": "Product", "id": "product_label"},
            {
                "name": "Planned Qty",
                "id": "planned_qty",
                "type": "numeric",
                "format": qty_format,
            },
            {
                "name": "Actual Qty",
                "id": "actual_qty",
                "type": "numeric",
                "format": qty_format,
            },
            {"name": "UOM", "id": "uom"},
            {"name": "Batch", "id": "batch"},
        ],
        data=table_data,
        hidden_columns=[
            "product_id",
            "planned_qty_canonical",
            "actual_qty_canonical",
        ],
        style_table={"overflowX": "auto"},
        style_cell={"padding": "0.5rem"},
        sort_action="native",
    )

    body_children: List[Any] = []
    if not table_data:
        body_children.append(
            dbc.Alert(
                "No outputs recorded yet. Complete the work order to add outputs.",
                color="info",
                className="mb-3",
            )
        )

    body_children.append(outputs_table)

    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardHeader("Outputs"),
                    dbc.CardBody(body_children),
                ]
            )
        ],
        style={"display": "block"} if visible else {"display": "none"},
    )


def create_work_order_detail_layout(
    wo: dict, api_base_url: str, active_tab: str = "wo-detail-inputs"
) -> html.Div:
    """Create detailed layout for work order."""
    status_colors = {
        "draft": "secondary",
        "released": "info",
        "in_progress": "warning",
        "hold": "danger",
        "complete": "success",
        "void": "dark",
    }

    raw_status = (wo.get("status") or "").lower()
    badge_color = status_colors.get(raw_status, "secondary")
    status_display = (wo.get("status") or "").replace("_", " ").title()

    tab_content = build_detail_tab_content(
        wo, api_base_url, active_tab, raw_status=raw_status
    )

    return dbc.Container(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4(f"Work Order: {wo.get('code', '')}"),
                            dbc.Badge(
                                status_display,
                                color=badge_color,
                                className="ms-2",
                            ),
                        ]
                    )
                ],
                className="mb-3",
            ),
            # Info cards
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Product"),
                                dbc.CardBody(html.P(wo.get("product_id", ""))),
                            ]
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Planned Qty"),
                                dbc.CardBody(
                                    html.P(
                                        f"{float(wo.get('planned_qty', 0) or 0):.3f} {wo.get('uom', 'KG')}"
                                    )
                                ),
                            ]
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Work Center"),
                                dbc.CardBody(html.P(wo.get("work_center", "N/A"))),
                            ]
                        ),
                        md=4,
                    ),
                ],
                className="mb-3",
            ),
            # Action buttons
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button(
                                "Release Work Order",
                                id="wo-release-btn",
                                color="primary",
                                className="me-2",
                                disabled=raw_status not in {"draft", "hold"},
                            ),
                            dbc.Button(
                                "Start Work Order",
                                id="wo-start-btn",
                                color="success",
                                className="me-2",
                                disabled=raw_status not in ["released"],
                            ),
                            dbc.Button(
                                "Void Work Order",
                                id="wo-void-btn",
                                color="danger",
                                className="me-2",
                                disabled=raw_status in ["complete", "void"],
                            ),
                        ]
                    )
                ],
                className="mb-3",
            ),
            # Tabs for detail views
            dbc.Tabs(
                [
                    dbc.Tab(label="Inputs", tab_id="wo-detail-inputs"),
                    dbc.Tab(label="Outputs", tab_id="wo-detail-outputs"),
                    dbc.Tab(label="QC Tests", tab_id="wo-detail-qc"),
                    dbc.Tab(label="Costs", tab_id="wo-detail-costs"),
                    dbc.Tab(label="Genealogy", tab_id="wo-detail-genealogy"),
                ],
                id="wo-detail-tabs",
                active_tab=active_tab,
                className="mb-3",
            ),
            html.Div(tab_content, id="wo-detail-tab-content"),
        ],
        fluid=True,
    )
