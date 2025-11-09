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
    app,
    api_base_url: str = "http://127.0.0.1:8000/api/v1",
    make_api_request=None,
):
    """Register all work order callbacks."""

    def _fetch_qc_test_types() -> Optional[List[Dict[str, Any]]]:
        """Fetch QC test type definitions from settings."""
        try:
            if make_api_request:
                response = make_api_request("GET", "/work-orders/qc-test-types")
                if isinstance(response, dict) and response.get("error"):
                    return None
            else:
                url = f"{api_base_url}/work-orders/qc-test-types"
                response = requests.get(url, timeout=5)
                if response.status_code != 200:
                    return None
                response = response.json()

            if isinstance(response, dict):
                if response.get("error"):
                    return None
                raw_items = (
                    response.get("qc_test_types")
                    or response.get("items")
                    or response.get("data")
                    or []
                )
            elif isinstance(response, list):
                raw_items = response
            else:
                raw_items = []

            results: List[Dict[str, Any]] = []
            for item in raw_items:
                if not isinstance(item, dict):
                    continue
                if item.get("is_active") is False:
                    continue
                results.append(item)
            return results
        except Exception as exc:  # pragma: no cover - defensive logging
            print(f"Error fetching QC test types: {exc}")
            return None

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
                            estimated_cost_str = "N/A"
                    else:
                        estimated_cost_str = "N/A"

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
        [
            Input("wo-detail-wo-id", "data"),
            Input("wo-inputs-table", "data"),
            Input("wo-add-input-submit-btn", "n_clicks"),
        ],
        prevent_initial_call=False,
    )
    def load_components_for_issue(wo_id, inputs_data, _add_input_clicks):
        """Load components for issue material dropdown."""
        if not wo_id:
            return []

        options: List[Dict[str, str]] = []
        seen: Set[str] = set()

        for row in inputs_data or []:
            component_id = row.get("component_product_id")
            if not component_id or component_id in seen:
                continue
            label = row.get("component_label") or component_id
            options.append({"label": label, "value": component_id})
            seen.add(component_id)

        if options:
            return options

        try:
            url = f"{api_base_url}/work-orders/{wo_id}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                wo = response.json()
                _, api_options = build_input_rows(wo, api_base_url)
                return api_options
            return []
        except Exception as e:
            print(f"Error loading components: {e}")
            return []

    @app.callback(
        Output("wo-add-input-component-dropdown", "options"),
        Input("wo-add-input-modal", "is_open"),
        prevent_initial_call=True,
    )
    def load_add_input_components(is_open):
        """Load component options for adding input lines."""
        if not is_open:
            raise PreventUpdate

        try:
            response = requests.get(
                f"{api_base_url}/products/?is_active=true", timeout=5
            )
            if response.status_code != 200:
                return []

            products_data = response.json()
            products = (
                products_data
                if isinstance(products_data, list)
                else products_data.get("products", [])
            )

            options = []
            for prod in products:
                product_id = prod.get("id")
                if not product_id:
                    continue
                sku = (prod.get("sku") or "").strip()
                name = (prod.get("name") or "").strip()
                label_parts = [part for part in (sku, name) if part]
                label = " - ".join(label_parts) if label_parts else product_id
                options.append({"label": label, "value": product_id})
            return options
        except Exception as e:
            print(f"Error loading product options: {e}")
            return []

    @app.callback(
        Output("wo-add-input-uom", "value", allow_duplicate=True),
        Input("wo-add-input-component-dropdown", "value"),
        prevent_initial_call=True,
    )
    def set_add_input_default_uom(component_id):
        """Prefill UOM based on selected component."""
        if not component_id:
            raise PreventUpdate

        details = get_product_details(component_id, api_base_url, {})
        return (
            details.get("default_uom") or details.get("base_unit") or ""
        ).strip() or "KG"

    @app.callback(
        [
            Output("wo-add-input-modal", "is_open", allow_duplicate=True),
            Output("wo-action-toast", "is_open", allow_duplicate=True),
            Output("wo-action-toast", "header", allow_duplicate=True),
            Output("wo-action-toast", "children", allow_duplicate=True),
        ],
        [
            Input("wo-inputs-add-btn", "n_clicks"),
            Input("wo-add-input-cancel-btn", "n_clicks"),
        ],
        [State("wo-add-input-modal", "is_open"), State("wo-detail-wo-id", "data")],
        prevent_initial_call="initial_duplicate",
    )
    def toggle_add_input_modal(add_clicks, cancel_clicks, is_open, wo_id):
        """Open/close the add input modal."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "wo-inputs-add-btn":
            if not add_clicks:
                raise PreventUpdate
            if not wo_id:
                return (
                    is_open,
                    True,
                    "Error",
                    "Select a work order before adding input lines.",
                )
            return True, False, no_update, no_update

        if button_id == "wo-add-input-cancel-btn" and is_open:
            if not cancel_clicks:
                raise PreventUpdate
            return False, False, no_update, no_update

        raise PreventUpdate

    @app.callback(
        Output("wo-inputs-add-btn", "disabled", allow_duplicate=True),
        Input("wo-detail-wo-id", "data"),
        State("wo-detail-allow-input-edit", "data"),
        prevent_initial_call="initial_duplicate",
    )
    def sync_add_button_state(wo_id, allow_edit):
        """Disable add button when editing isn't allowed or no work order is selected."""
        if allow_edit is False:
            return True
        return not bool(wo_id)

    @app.callback(
        Output("wo-inputs-edit-btn", "disabled", allow_duplicate=True),
        Input("wo-inputs-table", "selected_rows"),
        State("wo-detail-wo-id", "data"),
        State("wo-detail-allow-input-edit", "data"),
        prevent_initial_call="initial_duplicate",
    )
    def sync_edit_button_state(selected_rows, wo_id, allow_edit):
        """Enable edit button only when editing is allowed and a row is selected."""
        if allow_edit is False:
            return True
        if not wo_id:
            return True
        if not selected_rows:
            return True
        return False

    @app.callback(
        [
            Output("wo-action-toast", "is_open", allow_duplicate=True),
            Output("wo-action-toast", "header", allow_duplicate=True),
            Output("wo-action-toast", "children", allow_duplicate=True),
            Output("wo-add-input-modal", "is_open", allow_duplicate=True),
            Output("wo-add-input-component-dropdown", "value", allow_duplicate=True),
            Output("wo-add-input-planned-qty", "value", allow_duplicate=True),
            Output("wo-add-input-uom", "value", allow_duplicate=True),
            Output("wo-add-input-note", "value", allow_duplicate=True),
        ],
        Input("wo-add-input-submit-btn", "n_clicks"),
        [
            State("wo-detail-wo-id", "data"),
            State("wo-add-input-component-dropdown", "value"),
            State("wo-add-input-planned-qty", "value"),
            State("wo-add-input-uom", "value"),
            State("wo-add-input-note", "value"),
        ],
        prevent_initial_call=True,
    )
    def submit_add_input_line(
        submit_clicks, wo_id, component_id, planned_qty, uom, note
    ):
        """Submit a new input line for the work order."""
        if not submit_clicks:
            raise PreventUpdate

        if not wo_id:
            return (
                True,
                "Error",
                "Select a work order before adding input lines.",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        if not component_id:
            return (
                True,
                "Error",
                "Component is required.",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        payload = {"component_product_id": component_id}
        if planned_qty is not None:
            payload["planned_qty"] = float(planned_qty)
        if uom:
            payload["uom"] = uom
        if note:
            payload["note"] = note

        try:
            url = f"{api_base_url}/work-orders/{wo_id}/inputs"
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 201:
                return (
                    True,
                    "Success",
                    "Input line added successfully.",
                    False,
                    None,
                    None,
                    None,
                    None,
                )

            try:
                detail = response.json().get("detail", "Unknown error")
            except Exception:
                detail = response.text or "Unknown error"
            return (
                True,
                "Error",
                f"Failed to add input line: {detail}",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        except Exception as e:
            return (
                True,
                "Error",
                f"Failed to add input line: {str(e)}",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

    # Refresh work orders list after actions
    @app.callback(
        [
            Output("wo-action-toast", "is_open", allow_duplicate=True),
            Output("wo-action-toast", "header", allow_duplicate=True),
            Output("wo-action-toast", "children", allow_duplicate=True),
            Output("wo-detail-refresh-trigger", "data", allow_duplicate=True),
            Output("wo-planned-qty-refresh", "data", allow_duplicate=True),
        ],
        Input("wo-planned-qty-save", "n_clicks"),
        [
            State("wo-detail-wo-id", "data"),
            State("wo-planned-qty-input", "value"),
            State("wo-detail-refresh-trigger", "data"),
            State("wo-planned-qty-refresh", "data"),
        ],
        prevent_initial_call=True,
    )
    def update_planned_quantity(
        save_clicks, wo_id, planned_qty_value, current_refresh, planned_refresh
    ):
        """Update planned quantity for draft work order."""
        if not save_clicks:
            raise PreventUpdate

        if not wo_id:
            return (
                True,
                "Error",
                "Select a work order first.",
                dash.no_update,
                dash.no_update,
            )

        if planned_qty_value in (None, ""):
            return (
                True,
                "Error",
                "Enter a planned quantity before saving.",
                dash.no_update,
                dash.no_update,
            )

        try:
            data = {"planned_qty": float(planned_qty_value)}
            url = f"{api_base_url}/work-orders/{wo_id}"
            response = requests.patch(url, json=data, timeout=10)

            if response.status_code == 200:
                return (
                    True,
                    "Success",
                    "Planned quantity updated successfully.",
                    (current_refresh or 0) + 1,
                    (planned_refresh or 0) + 1,
                )

            try:
                error_payload = response.json()
            except ValueError:
                error_payload = {}

            detail = (
                error_payload.get("detail")
                if isinstance(error_payload, dict)
                else error_payload
            )

            if isinstance(detail, list):
                detail_msg = "; ".join(
                    item.get("msg", json.dumps(item))
                    if isinstance(item, dict)
                    else str(item)
                    for item in detail
                )
            elif isinstance(detail, dict):
                detail_msg = detail.get("message") or json.dumps(detail)
            elif detail:
                detail_msg = str(detail)
            else:
                detail_msg = "Unknown error"

            return (
                True,
                "Error",
                f"Failed to update planned quantity: {detail_msg}",
                dash.no_update,
                dash.no_update,
            )
        except Exception as exc:
            return (
                True,
                "Error",
                f"Failed to update planned quantity: {str(exc)}",
                dash.no_update,
                dash.no_update,
            )

    # Load work order detail when row selected or detail tab active
    @app.callback(
        [
            Output("wo-detail-content", "children"),
            Output("wo-detail-content", "style"),
            Output("wo-detail-wo-id", "data"),
            Output("wo-main-tabs", "active_tab", allow_duplicate=True),
            Output("wo-detail-active-tab", "data", allow_duplicate=True),
            Output("wo-qc-type-options", "data", allow_duplicate=True),
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

        _QC_SENTINEL = object()

        def build_return(
            children,
            style,
            wo_id_val,
            main_tab_val,
            detail_tab_val,
            qc_data=_QC_SENTINEL,
        ):
            if qc_data is _QC_SENTINEL:
                fetched_types = _fetch_qc_test_types()
                qc_payload = (
                    fetched_types if fetched_types is not None else dash.no_update
                )
            else:
                fetched_types = qc_data
                qc_payload = (
                    fetched_types if fetched_types is not None else dash.no_update
                )
            return (
                children,
                style,
                wo_id_val,
                main_tab_val,
                detail_tab_val,
                qc_payload,
            )

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
                            return build_return(
                                create_work_order_detail_layout(
                                    wo, api_base_url, active_tab="wo-detail-inputs"
                                ),
                                {"display": "block"},
                                wo_id,
                                "detail",
                                "wo-detail-inputs",
                            )
                        else:
                            return build_return(
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
                        return build_return(
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
            return build_return(
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
                                return build_return(
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
                            return build_return(
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
                            return build_return(
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
                return build_return(
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
                return build_return(
                    no_update,
                    {"display": "none"},
                    no_update,
                    no_update,
                    no_update,
                    qc_data=dash.no_update,
                )

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
                payload = response.json()
                message = payload.get("message")
                if not message:
                    message = (
                        "Material returned successfully"
                        if qty and float(qty) < 0
                        else "Material issued successfully"
                    )
                return True, "Success", message

            try:
                error_payload = response.json()
            except ValueError:
                error_payload = {}

            detail = error_payload.get("detail", "Unknown error")
            if isinstance(detail, list):
                detail = "; ".join(
                    item.get("msg", json.dumps(item))
                    if isinstance(item, dict)
                    else str(item)
                    for item in detail
                )
            elif isinstance(detail, dict):
                detail = detail.get("message") or json.dumps(detail)

            return True, "Error", f"Failed to issue material: {detail}"
        except Exception as exc:
            return True, "Error", f"Failed to issue material: {str(exc)}"

    @app.callback(
        [
            Output("wo-issue-component-dropdown", "value", allow_duplicate=True),
            Output("wo-issue-qty", "value", allow_duplicate=True),
            Output("wo-issue-batch-dropdown", "value", allow_duplicate=True),
            Output("wo-issue-toast", "is_open", allow_duplicate=True),
            Output("wo-issue-toast", "header", allow_duplicate=True),
            Output("wo-issue-toast", "children", allow_duplicate=True),
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
            return (
                no_update,
                no_update,
                no_update,
                True,
                "Error",
                "Select an input line to edit.",
            )

        row_index = selected_rows[0]
        if row_index >= len(table_data):
            return (
                no_update,
                no_update,
                no_update,
                True,
                "Error",
                "Selected row is out of range.",
            )

        row = table_data[row_index]
        component_id = row.get("component_product_id")
        qty_value = safe_float(row.get("remaining_qty"))
        if qty_value is None:
            qty_value = safe_float(row.get("planned_qty"))
        if qty_value is None:
            qty_value = safe_float(row.get("remaining_qty_canonical"))
        if qty_value is not None:
            qty_value = round(qty_value, 3)
        return (
            component_id,
            qty_value,
            row.get("batch") or None,
            True,
            "Info",
            "Line details loaded below. Adjust quantity and issue material.",
        )

    @app.callback(
        Output("wo-qc-test-type", "options"),
        Input("wo-qc-type-options", "data"),
        prevent_initial_call=True,
    )
    def set_qc_type_options(type_data):
        """Populate QC test type dropdown options."""
        if type_data in (None, dash.no_update):
            raise PreventUpdate

        if not type_data:
            return []

        options = []
        for item in type_data:
            code = (item.get("code") or "").strip()
            name = (item.get("name") or "").strip()
            unit = (item.get("unit") or "").strip()

            label_parts: List[str] = []
            if code:
                label_parts.append(code.upper())
            if name and name.upper() != code.upper():
                label_parts.append(name)
            label = " — ".join(part for part in label_parts if part) or "Unknown"
            if unit:
                label = f"{label} ({unit})"

            option = {
                "label": label,
                "value": item.get("id"),
            }
            options.append(option)
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
            Output("wo-qc-test-type", "value", allow_duplicate=True),
            Output("wo-qc-result-value", "value", allow_duplicate=True),
            Output("wo-qc-result-text", "value", allow_duplicate=True),
            Output("wo-qc-status", "value", allow_duplicate=True),
            Output("wo-qc-tester", "value", allow_duplicate=True),
            Output("wo-qc-note", "value", allow_duplicate=True),
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
            Output("wo-qc-test-type", "value", allow_duplicate=True),
            Output("wo-qc-result-value", "value", allow_duplicate=True),
            Output("wo-qc-result-text", "value", allow_duplicate=True),
            Output("wo-qc-status", "value", allow_duplicate=True),
            Output("wo-qc-tester", "value", allow_duplicate=True),
            Output("wo-qc-note", "value", allow_duplicate=True),
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
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
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
                    None,
                    None,
                    "",
                    "pending",
                    "",
                    "",
                )

            error_msg = response.json().get("detail", "Unknown error")
            return (
                True,
                "Error",
                f"Failed to save QC result: {error_msg}",
                current_qc_id,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )
        except Exception as exc:
            return (
                True,
                "Error",
                f"Failed to save QC result: {str(exc)}",
                current_qc_id,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
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

        if qty_produced in (None, ""):
            return (
                True,
                "Error",
                "Quantity produced is required",
            )

        try:
            qty_value = float(qty_produced)

            data = {
                "qty_produced": qty_value,
                "batch_attrs": {},
            }

            url = f"{api_base_url}/work-orders/{wo_id}/complete"
            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 200:
                payload = response.json()
                message_body = payload.get("message") or (
                    "Work order completion recorded"
                    if qty_value < 0
                    else "Work order completed successfully"
                )
                header = "Warning" if qty_value < 0 else "Success"
                return (
                    True,
                    header,
                    message_body,
                )
            else:
                try:
                    error_payload = response.json()
                except ValueError:
                    error_payload = {}

                detail = (
                    error_payload.get("detail")
                    if isinstance(error_payload, dict)
                    else error_payload
                )

                if isinstance(detail, list):
                    error_msg = "; ".join(
                        item.get("msg", json.dumps(item))
                        if isinstance(item, dict)
                        else str(item)
                        for item in detail
                    )
                elif isinstance(detail, dict):
                    error_msg = detail.get("message") or json.dumps(detail)
                elif detail:
                    error_msg = str(detail)
                else:
                    error_msg = "Unknown error"

                return (True, "Error", f"Failed to complete work order: {error_msg}")
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
            Input("wo-reopen-btn", "n_clicks"),
        ],
        [State("wo-detail-wo-id", "data")],
        prevent_initial_call=True,
    )
    def work_order_actions(
        release_clicks, start_clicks, void_clicks, reopen_clicks, wo_id
    ):
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
            elif button_id == "wo-reopen-btn":
                if not reopen_clicks:
                    raise PreventUpdate
                url = f"{api_base_url}/work-orders/{wo_id}/reopen"
                action = "reopened"
                data = {"reason": "Reopened from UI"}
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
        except PreventUpdate:
            raise
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
            Output("wo-qc-type-options", "data", allow_duplicate=True),
        ],
        [
            Input("wo-issue-submit-btn", "n_clicks"),
            Input("wo-add-input-submit-btn", "n_clicks"),
            Input("wo-qc-submit-btn", "n_clicks"),
            Input("wo-qc-delete-btn", "n_clicks"),
            Input("wo-complete-submit-btn", "n_clicks"),
            Input("wo-release-btn", "n_clicks"),
            Input("wo-start-btn", "n_clicks"),
            Input("wo-void-btn", "n_clicks"),
            Input("wo-reopen-btn", "n_clicks"),
            Input("wo-detail-refresh-trigger", "data"),
        ],
        [State("wo-detail-wo-id", "data"), State("wo-detail-active-tab", "data")],
        prevent_initial_call="initial_duplicate",
    )
    def refresh_detail_view(
        issue_clicks,
        add_input_clicks,
        qc_clicks,
        _delete_qc_clicks,
        complete_clicks,
        release_clicks,
        start_clicks,
        void_clicks,
        reopen_clicks,
        _refresh_trigger,
        wo_id,
        current_detail_tab=None,
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
                fetched_types = _fetch_qc_test_types()
                qc_type_options = (
                    fetched_types if fetched_types is not None else dash.no_update
                )
                return (
                    create_work_order_detail_layout(
                        wo,
                        api_base_url,
                        active_tab=current_detail_tab or "wo-detail-inputs",
                    ),
                    {"display": "block"},
                    wo_id,
                    qc_type_options,
                )
            else:
                return no_update, no_update, no_update, dash.no_update
        except Exception as e:
            print(f"Error refreshing detail: {e}")
            return no_update, no_update, no_update, dash.no_update

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
                                placeholder="Enter quantity (negative allowed)",
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
                                    {"name": "Test Type", "id": "test_type_display"},
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
                                    "test_type",
                                    "test_type_id",
                                    "status_raw",
                                    "tested_at_raw",
                                    "sequence_index",
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
    cost_data: Optional[Dict[str, Any]], visible: bool = False
) -> html.Div:
    """Render the costs section with actual material and overhead details."""

    cost_data = cost_data or {}
    material_lines = cost_data.get("material_lines") or []
    material_cost = cost_data.get("material_cost")
    overhead_cost = cost_data.get("overhead_cost")
    total_cost = cost_data.get("total_cost")
    qty_produced = cost_data.get("qty_produced")
    unit_cost = cost_data.get("unit_cost")

    material_table = dash_table.DataTable(
        columns=[
            {"name": "Component", "id": "component_label"},
            {"name": "Product ID", "id": "component_product_id"},
            {"name": "Actual Qty", "id": "actual_qty", "type": "numeric"},
            {"name": "UOM", "id": "uom"},
            {
                "name": "Unit Cost",
                "id": "unit_cost",
                "type": "numeric",
                "format": {"specifier": ".2f"},
            },
            {
                "name": "Cost",
                "id": "cost",
                "type": "numeric",
                "format": {"specifier": ".2f"},
            },
        ],
        data=[
            {
                "component_label": line.get("component_label", ""),
                "component_product_id": line.get("component_product_id", ""),
                "actual_qty": line.get("actual_qty", 0),
                "uom": line.get("uom", ""),
                "unit_cost": float(line.get("unit_cost" or 0)),
                "cost": float(line.get("cost" or 0)),
            }
            for line in material_lines
        ],
        style_table={"overflowX": "auto"},
        style_cell={"padding": "0.5rem"},
        sort_action="native",
    )

    summary_items = []
    if material_cost is not None:
        summary_items.append(html.Li(f"Material Cost: ${float(material_cost):.2f}"))
    if overhead_cost is not None:
        summary_items.append(html.Li(f"Overhead Cost: ${float(overhead_cost):.2f}"))
    if total_cost is not None:
        summary_items.append(html.Li(f"Total Cost: ${float(total_cost):.2f}"))
    if qty_produced is not None:
        summary_items.append(html.Li(f"Quantity Produced: {float(qty_produced):.3f}"))
    if unit_cost is not None:
        summary_items.append(html.Li(f"Unit Cost: ${float(unit_cost):.2f}"))

    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardHeader("Costs"),
                    dbc.CardBody(
                        [
                            html.H6("Materials", className="fw-bold"),
                            material_table
                            if material_lines
                            else html.P("No material usage recorded."),
                            html.Hr(),
                            html.H6("Summary", className="fw-bold"),
                            html.Ul(summary_items)
                            if summary_items
                            else html.P("No cost summary available."),
                        ]
                    ),
                ]
            )
        ],
        style={"display": "block"} if visible else {"display": "none"},
    )


def create_genealogy_section(
    genealogy_data: Optional[Dict[str, Any]], visible: bool = False
) -> html.Div:
    """Render genealogy section with inventory movements."""

    genealogy_data = genealogy_data or {}
    movements = genealogy_data.get("movements") or []

    movement_table = dash_table.DataTable(
        columns=[
            {"name": "Product", "id": "product_name"},
            {"name": "Product ID", "id": "product_id"},
            {
                "name": "Quantity",
                "id": "qty",
                "type": "numeric",
                "format": {"specifier": ".4f"},
            },
            {"name": "UOM", "id": "unit"},
            {
                "name": "Unit Cost",
                "id": "unit_cost",
                "type": "numeric",
                "format": {"specifier": ".4f"},
            },
            {
                "name": "Cost",
                "id": "line_cost",
                "type": "numeric",
                "format": {"specifier": ".4f"},
            },
            {"name": "Direction", "id": "direction"},
            {"name": "Type", "id": "move_type"},
            {"name": "Timestamp", "id": "timestamp"},
            {"name": "Note", "id": "note"},
        ],
        data=[
            {
                "product_name": move.get("product_name")
                or move.get("product_id")
                or "",
                "product_id": move.get("product_id", ""),
                "qty": abs(float(move.get("qty", 0))),
                "unit": move.get("unit", ""),
                "unit_cost": float(move.get("unit_cost", 0)),
                "line_cost": abs(float(move.get("qty", 0)))
                * float(move.get("unit_cost", 0)),
                "direction": move.get("direction", ""),
                "move_type": move.get("move_type", ""),
                "timestamp": move.get("timestamp", ""),
                "note": move.get("note", ""),
            }
            for move in movements
        ],
        style_table={"overflowX": "auto"},
        style_cell={"padding": "0.5rem"},
        sort_action="native",
    )

    style = {"display": "block" if visible else "none"}

    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardHeader("Genealogy"),
                    dbc.CardBody(
                        [
                            html.H6("Inventory Movements", className="fw-bold"),
                            movement_table
                            if movements
                            else html.P("No inventory movements recorded."),
                        ]
                    ),
                ]
            )
        ],
        style=style,
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
    allow_complete = status not in {"draft", "void"}  # allow complete when reopened
    output_uom = wo.get("uom") or ""

    qc_tests = wo.get("qc_tests", []) or []
    qc_table_data: List[Dict[str, Any]] = []
    type_instances: Dict[str, int] = {}
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

        type_key = f"{qc.get('test_type_id') or ''}__{(qc.get('test_type') or '').strip().lower()}"
        instance_index = type_instances.get(type_key, 0) + 1
        type_instances[type_key] = instance_index

        raw_test_type = qc.get("test_type", "") or ""
        display_test_type = raw_test_type
        if instance_index > 1:
            display_test_type = f"{raw_test_type} #{instance_index}".strip()

        qc_table_data.append(
            {
                "id": qc.get("id"),
                "test_type_display": display_test_type,
                "test_type": raw_test_type,
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
                "sequence_index": instance_index,
            }
        )

    cost_data = None
    genealogy_data = None
    wo_id = wo.get("id")
    if wo_id:
        try:
            cost_url = f"{api_base_url}/work-orders/{wo_id}/costs"
            cost_response = requests.get(cost_url, timeout=5)
            if cost_response.status_code == 200:
                cost_data = cost_response.json()
        except Exception:
            cost_data = None

        try:
            genealogy_url = f"{api_base_url}/work-orders/{wo_id}/genealogy"
            genealogy_response = requests.get(genealogy_url, timeout=5)
            if genealogy_response.status_code == 200:
                genealogy_data = genealogy_response.json()
        except Exception:
            genealogy_data = None

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
            create_costs_section(
                cost_data=cost_data, visible=active_tab == "wo-detail-costs"
            ),
            create_genealogy_section(
                genealogy_data=genealogy_data,
                visible=active_tab == "wo-detail-genealogy",
            ),
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
                html.Div(
                    [
                        dbc.Button(
                            "Add Line",
                            id="wo-inputs-add-btn",
                            color="info",
                            size="sm",
                            className="me-2",
                            disabled=not allow_edit,
                        ),
                        dbc.Button(
                            "Edit Selected",
                            id="wo-inputs-edit-btn",
                            outline=True,
                            color="secondary",
                            size="sm",
                            disabled=not allow_edit,
                        ),
                    ],
                    className="d-flex justify-content-end",
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
            html.Div(
                [
                    html.Strong("Totals:"),
                    html.Span(
                        f" Planned {sum(safe_float(row.get('planned_qty')) or 0 for row in table_data):.3f}"
                    ),
                    html.Span(
                        f" Actual {sum(safe_float(row.get('actual_qty')) or 0 for row in table_data):.3f}"
                    ),
                    html.Span(
                        f" Remaining {sum(safe_float(row.get('remaining_qty')) or 0 for row in table_data):.3f}"
                    ),
                ],
                className="d-flex gap-3 mb-2 fw-semibold",
            ),
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
                                placeholder="Use negative to reduce issued qty",
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
    allow_issue_edit = raw_status not in {"complete", "void"}

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
                                dbc.CardBody(
                                    html.P(
                                        wo.get("product_name")
                                        or wo.get("product_id", "")
                                    )
                                ),
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
                                "Reopen Work Order",
                                id="wo-reopen-btn",
                                color="warning",
                                className="me-2",
                                disabled=raw_status != "complete",
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
            dcc.Store(id="wo-detail-allow-input-edit", data=allow_issue_edit),
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label(
                                        "Adjust Planned Quantity", className="fw-bold"
                                    ),
                                    dbc.Input(
                                        id="wo-planned-qty-input",
                                        type="number",
                                        step=0.001,
                                        value=float(wo.get("planned_qty", 0) or 0),
                                        disabled=raw_status != "draft",
                                    ),
                                    dbc.FormText(f"UOM: {wo.get('uom', 'KG')}"),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Save Planned Quantity",
                                    id="wo-planned-qty-save",
                                    color="primary",
                                    className="mt-4",
                                    disabled=raw_status != "draft",
                                ),
                                md=3,
                            ),
                        ],
                        className="mb-3",
                        style={"display": "flex" if raw_status == "draft" else "none"},
                    ),
                ],
                id="wo-planned-qty-wrapper",
                style={"display": "block" if raw_status == "draft" else "none"},
            ),
        ],
        fluid=True,
    )
