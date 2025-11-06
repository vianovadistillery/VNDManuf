"""CRUD callbacks for formulas page."""

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dash_table, html, no_update
from dash.exceptions import PreventUpdate


def register_formulas_callbacks(app, make_api_request):
    """Register all formula CRUD callbacks."""

    # Update formula master table
    @app.callback(
        [
            Output("formula-master-table", "data"),
            Output("formula-master-table", "columns"),
        ],
        [
            Input("main-tabs", "active_tab"),
            Input("formula-search-btn", "n_clicks"),
            Input("formula-refresh-btn", "n_clicks"),
        ],
        [State("formula-search", "value")],
        prevent_initial_call=False,
    )
    def update_formula_table(active_tab, search_clicks, refresh_clicks, search_value):
        """Update formula master table."""
        # Only update when formulas tab is active
        if active_tab != "formulas":
            return no_update, no_update

        # Fetch formulas from API
        try:
            response = make_api_request("GET", "/formulas/")

            # Check for error in response
            if isinstance(response, dict) and "error" in response:
                error_msg = response.get("error", "Unknown error")
                print(f"Error loading formulas: {error_msg}")
                # Try to parse JSON error message
                try:
                    import json

                    error_dict = (
                        json.loads(error_msg)
                        if isinstance(error_msg, str)
                        else error_msg
                    )
                    if isinstance(error_dict, dict):
                        error_msg = error_dict.get("message", error_msg)
                except (KeyError, ValueError, TypeError):
                    pass
                print(f"Error loading formulas: {error_msg}")
                return [], []

            # Handle list response
            if isinstance(response, list):
                formulas = response
            elif isinstance(response, dict):
                formulas = response.get("formulas", [])
            else:
                formulas = []
        except Exception as e:
            print(f"Exception loading formulas: {e}")
            import traceback

            traceback.print_exc()
            return [], []

        if not formulas:
            print("No formulas returned from API")
            return [], []

        print(f"Loaded {len(formulas)} formulas")

        # Flatten and format data for display
        formatted_data = []
        for formula in formulas:
            product_name = formula.get("product_name", "")
            product_sku = formula.get("product_sku", "")
            # Format product display as "SKU - Name" or just "Name" if SKU not available
            if product_sku and product_name:
                product_display = f"{product_sku} - {product_name}"
            elif product_sku:
                product_display = product_sku
            elif product_name:
                product_display = product_name
            else:
                product_display = "-"

            formatted_data.append(
                {
                    "formula_code": formula.get("formula_code", ""),
                    "formula_name": formula.get("formula_name", ""),
                    "version": formula.get("version", 1),
                    "product_name": product_display,
                    "is_active": "✓" if formula.get("is_active", True) else "✗",
                    "id": formula.get("id", ""),
                }
            )

        # Apply search filter
        if search_value:
            search_lower = search_value.lower()
            formatted_data = [
                f
                for f in formatted_data
                if search_lower in f["formula_code"].lower()
                or search_lower in f["formula_name"].lower()
            ]

        # Create columns
        columns = [
            {"name": "Code", "id": "formula_code"},
            {"name": "Name", "id": "formula_name", "presentation": "markdown"},
            {"name": "Version", "id": "version"},
            {"name": "Product", "id": "product_name"},
            {"name": "Active", "id": "is_active"},
        ]

        return formatted_data, columns

    # Update formula detail panel
    @app.callback(
        [
            Output("formula-detail-title", "children"),
            Output("formula-info-code", "children"),
            Output("formula-info-version", "children"),
            Output("formula-info-product", "children"),
            Output("formula-info-status", "children"),
            Output("formula-lines-table-container", "children"),
        ],
        [Input("formula-master-table", "selected_rows")],
        [State("formula-master-table", "data")],
    )
    def update_formula_detail(selected_rows, data):
        """Update formula detail panel - replicate product detail view logic."""
        if not selected_rows or not data:
            return (
                "Select a formula...",
                "-",
                "-",
                "-",
                "-",
                html.Div("Select a formula to view details"),
            )

        formula = data[selected_rows[0]]
        formula_id = formula.get("id")

        if not formula_id:
            return (
                "Select a formula...",
                "-",
                "-",
                "-",
                "-",
                html.Div("Select a formula to view details"),
            )

        # Fetch formula details from API
        formula_response = make_api_request("GET", f"/formulas/{formula_id}")

        if "error" in formula_response:
            return (
                f"{formula.get('formula_code', 'Unknown')}",
                formula.get("formula_code", "-"),
                str(formula.get("version", "-")),
                formula.get("product_name", "-"),
                formula.get("is_active", "-"),
                html.Div("Error loading formula details"),
            )

        formula_data = formula_response

        # Get parent product_id from formula response
        parent_product_id = formula_data.get("product_id")

        # Get parent product density for totals
        parent_density = 0.0
        if parent_product_id:
            try:
                parent_resp = make_api_request("GET", f"/products/{parent_product_id}")
                if isinstance(parent_resp, dict) and "error" not in parent_resp:
                    density_val = parent_resp.get("density_kg_per_l", 0) or 0
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
                    product_resp = make_api_request(
                        "GET", f"/products/{line_product_id}"
                    )
                    if isinstance(product_resp, dict) and "error" not in product_resp:
                        product_sku = product_resp.get("sku", "")
                        product_name = product_resp.get("name", product_name)

                        # Get density
                        density_val = product_resp.get("density_kg_per_l", 0) or 0
                        try:
                            density = float(density_val)
                        except (ValueError, TypeError):
                            density = 0.0

                        # Get product's usage_unit
                        product_usage_unit = (
                            product_resp.get("usage_unit", "").upper()
                            if product_resp.get("usage_unit")
                            else None
                        )

                        # Check if product is an assembly - if so, use primary assembly cost
                        is_assemble = product_resp.get("is_assemble", False)
                        if is_assemble:
                            # Fetch formulas for this assembly product
                            try:
                                formulas_response = make_api_request(
                                    "GET",
                                    f"/formulas/?product_id={line_product_id}&is_active=true",
                                )
                                if (
                                    isinstance(formulas_response, list)
                                    and len(formulas_response) > 0
                                ):
                                    # Find primary assembly (use first active one, or first one if none active)
                                    primary_formula = None
                                    for f in formulas_response:
                                        if f.get("is_active") is True:
                                            primary_formula = f
                                            break

                                    if not primary_formula:
                                        primary_formula = formulas_response[0]

                                    # Calculate primary assembly's cost per kg
                                    if primary_formula:
                                        lines_list = primary_formula.get("lines", [])
                                        assembly_total_cost = 0.0
                                        assembly_total_kg = 0.0

                                        for assembly_line in lines_list:
                                            if isinstance(assembly_line, dict):
                                                assembly_qty_kg = float(
                                                    assembly_line.get(
                                                        "quantity_kg", 0.0
                                                    )
                                                    or 0.0
                                                )
                                                assembly_line_product_id = (
                                                    assembly_line.get("raw_material_id")
                                                )
                                                assembly_line_cost = 0.0

                                                if assembly_line_product_id:
                                                    try:
                                                        assembly_line_product = make_api_request(
                                                            "GET",
                                                            f"/products/{assembly_line_product_id}",
                                                        )
                                                        if isinstance(
                                                            assembly_line_product, dict
                                                        ):
                                                            assembly_cost_val = (
                                                                assembly_line_product.get(
                                                                    "usage_cost_ex_gst"
                                                                )
                                                                or assembly_line_product.get(
                                                                    "purchase_cost_ex_gst"
                                                                )
                                                                or assembly_line_product.get(
                                                                    "usage_cost_inc_gst"
                                                                )
                                                                or assembly_line_product.get(
                                                                    "purchase_cost_inc_gst"
                                                                )
                                                                or 0
                                                            )
                                                            if assembly_cost_val:
                                                                try:
                                                                    assembly_line_unit_cost_raw = float(
                                                                        assembly_cost_val
                                                                    )
                                                                    assembly_line_usage_unit = (
                                                                        assembly_line_product.get(
                                                                            "usage_unit",
                                                                            "",
                                                                        ).upper()
                                                                        if assembly_line_product.get(
                                                                            "usage_unit"
                                                                        )
                                                                        else "KG"
                                                                    )
                                                                    assembly_line_density = float(
                                                                        assembly_line_product.get(
                                                                            "density_kg_per_l",
                                                                            0,
                                                                        )
                                                                        or 0
                                                                    )

                                                                    # Handle "EA" (each) unit
                                                                    if (
                                                                        assembly_line_usage_unit
                                                                        in [
                                                                            "EA",
                                                                            "EACH",
                                                                            "UNIT",
                                                                            "UNITS",
                                                                        ]
                                                                    ):
                                                                        assembly_line_qty_ea = assembly_qty_kg
                                                                        weight_kg_per_item = (
                                                                            assembly_line_product.get(
                                                                                "weight_kg"
                                                                            )
                                                                            or 0.0
                                                                        )
                                                                        if (
                                                                            weight_kg_per_item
                                                                            and weight_kg_per_item
                                                                            > 0
                                                                        ):
                                                                            try:
                                                                                assembly_line_qty_ea = (
                                                                                    assembly_qty_kg
                                                                                    / float(
                                                                                        weight_kg_per_item
                                                                                    )
                                                                                )
                                                                            except (
                                                                                ValueError,
                                                                                TypeError,
                                                                                ZeroDivisionError,
                                                                            ):
                                                                                assembly_line_qty_ea = assembly_qty_kg

                                                                        assembly_line_cost = (
                                                                            assembly_line_qty_ea
                                                                            * assembly_line_unit_cost_raw
                                                                        )
                                                                        if (
                                                                            assembly_qty_kg
                                                                            > 0
                                                                        ):
                                                                            assembly_line_cost_per_kg = (
                                                                                assembly_line_cost
                                                                                / assembly_qty_kg
                                                                            )
                                                                        else:
                                                                            assembly_line_cost_per_kg = 0.0
                                                                    else:
                                                                        # Convert unit cost to $/kg
                                                                        assembly_line_cost_per_kg = assembly_line_unit_cost_raw
                                                                        if (
                                                                            assembly_line_usage_unit
                                                                            in [
                                                                                "G",
                                                                                "GRAM",
                                                                                "GRAMS",
                                                                            ]
                                                                        ):
                                                                            assembly_line_cost_per_kg = (
                                                                                assembly_line_unit_cost_raw
                                                                                * 1000.0
                                                                            )
                                                                        elif (
                                                                            assembly_line_usage_unit
                                                                            in [
                                                                                "L",
                                                                                "LT",
                                                                                "LTR",
                                                                                "LITER",
                                                                                "LITRE",
                                                                            ]
                                                                        ):
                                                                            if (
                                                                                assembly_line_density
                                                                                > 0
                                                                            ):
                                                                                assembly_line_cost_per_kg = (
                                                                                    assembly_line_unit_cost_raw
                                                                                    / assembly_line_density
                                                                                )
                                                                            else:
                                                                                assembly_line_cost_per_kg = assembly_line_unit_cost_raw
                                                                        elif (
                                                                            assembly_line_usage_unit
                                                                            in [
                                                                                "ML",
                                                                                "MILLILITER",
                                                                                "MILLILITRE",
                                                                            ]
                                                                        ):
                                                                            if (
                                                                                assembly_line_density
                                                                                > 0
                                                                            ):
                                                                                assembly_line_cost_per_kg = (
                                                                                    (
                                                                                        assembly_line_unit_cost_raw
                                                                                        * 1000.0
                                                                                    )
                                                                                    / assembly_line_density
                                                                                )
                                                                            else:
                                                                                assembly_line_cost_per_kg = (
                                                                                    assembly_line_unit_cost_raw
                                                                                    * 1000.0
                                                                                )

                                                                        assembly_line_cost = (
                                                                            assembly_qty_kg
                                                                            * assembly_line_cost_per_kg
                                                                        )
                                                                except (
                                                                    ValueError,
                                                                    TypeError,
                                                                ):
                                                                    pass
                                                    except Exception:
                                                        pass

                                                assembly_total_cost += (
                                                    assembly_line_cost
                                                )
                                                assembly_total_kg += assembly_qty_kg

                                        # Calculate cost per kg for the assembly
                                        if assembly_total_kg > 0:
                                            assembly_cost_per_kg = (
                                                assembly_total_cost / assembly_total_kg
                                            )
                                            product_usage_cost = round(
                                                assembly_cost_per_kg, 4
                                            )
                                            product_usage_unit = "KG"
                                        else:
                                            # Fallback to usage/purchase cost
                                            cost_val = (
                                                product_resp.get("usage_cost_ex_gst")
                                                or product_resp.get(
                                                    "purchase_cost_ex_gst"
                                                )
                                                or product_resp.get(
                                                    "usage_cost_inc_gst"
                                                )
                                                or product_resp.get(
                                                    "purchase_cost_inc_gst"
                                                )
                                                or 0
                                            )
                                            if cost_val:
                                                try:
                                                    product_usage_cost = round(
                                                        float(cost_val), 4
                                                    )
                                                except (ValueError, TypeError):
                                                    product_usage_cost = 0.0
                            except Exception as e:
                                print(f"Error fetching assembly cost: {e}")
                                # Fallback to usage/purchase cost
                                cost_val = (
                                    product_resp.get("usage_cost_ex_gst")
                                    or product_resp.get("purchase_cost_ex_gst")
                                    or product_resp.get("usage_cost_inc_gst")
                                    or product_resp.get("purchase_cost_inc_gst")
                                    or 0
                                )
                                if cost_val:
                                    try:
                                        product_usage_cost = round(float(cost_val), 4)
                                    except (ValueError, TypeError):
                                        product_usage_cost = 0.0
                        else:
                            # Not an assembly - use usage/purchase cost
                            cost_val = (
                                product_resp.get("usage_cost_ex_gst")
                                or product_resp.get("purchase_cost_ex_gst")
                                or product_resp.get("usage_cost_inc_gst")
                                or product_resp.get("purchase_cost_inc_gst")
                                or 0
                            )
                            if cost_val:
                                try:
                                    product_usage_cost = round(float(cost_val), 4)
                                except (ValueError, TypeError):
                                    product_usage_cost = 0.0
                except Exception:
                    pass

            # Get quantity_kg from line (this is the canonical stored value)
            quantity_kg = float(line.get("quantity_kg", 0.0) or 0.0)
            unit = line.get("unit", "kg")

            # Convert quantity_kg back to display unit (reverse conversion)
            unit_upper = unit.upper() if unit else "KG"
            quantity_display = quantity_kg

            if unit_upper in ["G", "GRAM", "GRAMS"]:
                quantity_display = quantity_kg * 1000.0
            elif unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                if density > 0:
                    quantity_display = quantity_kg / density
                else:
                    quantity_display = quantity_kg
            elif unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                if density > 0:
                    quantity_l = quantity_kg / density
                    quantity_display = quantity_l * 1000.0
                else:
                    quantity_display = quantity_kg * 1000.0

            # Calculate quantity_l using the line item product's density
            quantity_l = quantity_kg / density if density > 0 else 0.0

            # Calculate line cost with proper unit conversions
            line_cost = 0.0
            if product_usage_cost > 0 and product_usage_unit:
                quantity_in_usage_unit = 0.0
                assembly_unit_upper = unit.upper() if unit else "KG"

                # If units match, no conversion needed
                if assembly_unit_upper == product_usage_unit:
                    quantity_in_usage_unit = quantity_display
                # Mass conversions
                elif assembly_unit_upper in [
                    "G",
                    "GRAM",
                    "GRAMS",
                ] and product_usage_unit in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    quantity_in_usage_unit = quantity_kg
                elif assembly_unit_upper in [
                    "KG",
                    "KILOGRAM",
                    "KILOGRAMS",
                ] and product_usage_unit in ["G", "GRAM", "GRAMS"]:
                    quantity_in_usage_unit = quantity_kg * 1000.0
                elif assembly_unit_upper in [
                    "KG",
                    "KILOGRAM",
                    "KILOGRAMS",
                ] and product_usage_unit in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    quantity_in_usage_unit = quantity_kg
                # Volume conversions
                elif assembly_unit_upper in [
                    "ML",
                    "MILLILITER",
                    "MILLILITRE",
                ] and product_usage_unit in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    quantity_in_usage_unit = quantity_l
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit in ["ML", "MILLILITER", "MILLILITRE"]:
                    quantity_in_usage_unit = quantity_l * 1000.0
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    quantity_in_usage_unit = quantity_l
                # Volume to mass (using density)
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    quantity_in_usage_unit = quantity_kg if density > 0 else quantity_l
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit in ["G", "GRAM", "GRAMS"]:
                    quantity_in_usage_unit = (
                        quantity_kg * 1000.0 if density > 0 else quantity_l * 1000.0
                    )
                elif assembly_unit_upper in [
                    "ML",
                    "MILLILITER",
                    "MILLILITRE",
                ] and product_usage_unit in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    quantity_in_usage_unit = quantity_kg if density > 0 else quantity_l
                elif assembly_unit_upper in [
                    "ML",
                    "MILLILITER",
                    "MILLILITRE",
                ] and product_usage_unit in ["G", "GRAM", "GRAMS"]:
                    quantity_in_usage_unit = (
                        quantity_kg * 1000.0 if density > 0 else quantity_l * 1000.0
                    )
                # Mass to volume (using density)
                elif assembly_unit_upper in [
                    "KG",
                    "KILOGRAM",
                    "KILOGRAMS",
                ] and product_usage_unit in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    quantity_in_usage_unit = quantity_l if density > 0 else quantity_kg
                elif assembly_unit_upper in [
                    "G",
                    "GRAM",
                    "GRAMS",
                ] and product_usage_unit in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    quantity_in_usage_unit = quantity_l if density > 0 else quantity_kg
                elif assembly_unit_upper in [
                    "KG",
                    "KILOGRAM",
                    "KILOGRAMS",
                ] and product_usage_unit in ["ML", "MILLILITER", "MILLILITRE"]:
                    quantity_in_usage_unit = (
                        quantity_l * 1000.0 if density > 0 else quantity_kg * 1000.0
                    )
                elif assembly_unit_upper in [
                    "G",
                    "GRAM",
                    "GRAMS",
                ] and product_usage_unit in ["ML", "MILLILITER", "MILLILITRE"]:
                    quantity_in_usage_unit = (
                        quantity_l * 1000.0 if density > 0 else quantity_kg * 1000.0
                    )
                # Handle "EA" (each) units
                elif assembly_unit_upper in [
                    "EA",
                    "EACH",
                    "UNIT",
                    "UNITS",
                ] and product_usage_unit.upper() in ["EA", "EACH", "UNIT", "UNITS"]:
                    quantity_in_usage_unit = quantity_display
                elif assembly_unit_upper in ["EA", "EACH", "UNIT", "UNITS"]:
                    quantity_in_usage_unit = quantity_display
                elif product_usage_unit.upper() in ["EA", "EACH", "UNIT", "UNITS"]:
                    quantity_in_usage_unit = quantity_display
                else:
                    quantity_in_usage_unit = quantity_kg

                line_cost = quantity_in_usage_unit * product_usage_cost
            elif product_usage_cost > 0:
                # If no usage_unit, assume it's per kg
                line_cost = quantity_kg * product_usage_cost

            # Calculate display unit_cost (cost per assembly line unit)
            display_unit_cost = 0.0
            if product_usage_cost > 0 and product_usage_unit and quantity_display > 0:
                assembly_unit_upper = unit.upper() if unit else "KG"

                if assembly_unit_upper == product_usage_unit:
                    display_unit_cost = product_usage_cost
                elif assembly_unit_upper in [
                    "G",
                    "GRAM",
                    "GRAMS",
                ] and product_usage_unit in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    display_unit_cost = product_usage_cost / 1000.0
                elif assembly_unit_upper in [
                    "KG",
                    "KILOGRAM",
                    "KILOGRAMS",
                ] and product_usage_unit in ["G", "GRAM", "GRAMS"]:
                    display_unit_cost = product_usage_cost * 1000.0
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    display_unit_cost = (
                        product_usage_cost / density
                        if density > 0
                        else product_usage_cost
                    )
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit in ["G", "GRAM", "GRAMS"]:
                    display_unit_cost = (
                        (product_usage_cost / density) / 1000.0
                        if density > 0
                        else product_usage_cost / 1000.0
                    )
                elif assembly_unit_upper in [
                    "ML",
                    "MILLILITER",
                    "MILLILITRE",
                ] and product_usage_unit in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    display_unit_cost = product_usage_cost / 1000.0
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit in ["ML", "MILLILITER", "MILLILITRE"]:
                    display_unit_cost = product_usage_cost * 1000.0
                # Handle "EA" (each) units for display unit cost
                elif assembly_unit_upper in [
                    "EA",
                    "EACH",
                    "UNIT",
                    "UNITS",
                ] and product_usage_unit.upper() in ["EA", "EACH", "UNIT", "UNITS"]:
                    display_unit_cost = product_usage_cost
                elif assembly_unit_upper in [
                    "EA",
                    "EACH",
                    "UNIT",
                    "UNITS",
                ] or product_usage_unit.upper() in ["EA", "EACH", "UNIT", "UNITS"]:
                    display_unit_cost = product_usage_cost
                else:
                    display_unit_cost = (
                        line_cost / quantity_display if quantity_display > 0 else 0.0
                    )
            elif product_usage_cost > 0:
                display_unit_cost = (
                    line_cost / quantity_display if quantity_display > 0 else 0.0
                )

            total_cost += line_cost
            total_quantity_kg += quantity_kg
            total_quantity_l += quantity_l

            lines_data.append(
                {
                    "product_sku": product_sku,
                    "product_name": product_name,
                    "quantity": round(quantity_display, 3),
                    "unit": unit,
                    "quantity_kg": round(quantity_kg, 3),
                    "unit_cost": round(display_unit_cost, 4),
                    "line_cost": round(line_cost, 4),
                }
            )

        if lines_data:
            # Calculate totals - use parent product density for total_quantity_l (same as product detail view)
            if parent_density > 0 and total_quantity_kg > 0:
                total_quantity_l = total_quantity_kg / parent_density
            # Otherwise total_quantity_l is already the sum of individual line quantities

            cost_per_kg = (
                total_cost / total_quantity_kg if total_quantity_kg > 0 else 0.0
            )
            cost_per_l = total_cost / total_quantity_l if total_quantity_l > 0 else 0.0

            # Create table with same format as product detail view
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
            )

            # Create summary totals (same format as product detail view)
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
                f"{formula_data.get('formula_name', formula.get('formula_code', 'Unknown'))}",
                formula_data.get("formula_code", "-"),
                str(formula_data.get("version", "-")),
                formula_data.get("product_name", "-"),
                "Active" if formula_data.get("is_active", True) else "Inactive",
                html.Div([lines_table, summary]),
            )
        else:
            return (
                f"{formula_data.get('formula_name', formula.get('formula_code', 'Unknown'))}",
                formula_data.get("formula_code", "-"),
                str(formula_data.get("version", "-")),
                formula_data.get("product_name", "-"),
                "Active" if formula_data.get("is_active", True) else "Inactive",
                html.Div("No line items in this assembly"),
            )

    # Open formula editor modal
    @app.callback(
        [
            Output("formula-editor-modal", "is_open", allow_duplicate=True),
            Output("formula-editor-title", "children", allow_duplicate=True),
            Output("formula-input-name", "value", allow_duplicate=True),
            Output("formula-input-version", "value", allow_duplicate=True),
            Output("formula-input-product", "options", allow_duplicate=True),
            Output("formula-input-product", "value", allow_duplicate=True),
            Output("formula-input-yield-factor", "value", allow_duplicate=True),
            Output("formula-input-active", "value", allow_duplicate=True),
            Output("formula-editor-lines", "data", allow_duplicate=True),
        ],
        [Input("formula-add-btn", "n_clicks"), Input("formula-edit-btn", "n_clicks")],
        [
            State("formula-master-table", "selected_rows"),
            State("formula-master-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def open_formula_editor(add_clicks, edit_clicks, selected_rows, data):
        """Open formula editor modal."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Get products for dropdown
        products_response = make_api_request("GET", "/products/")
        products = (
            products_response
            if isinstance(products_response, list)
            else products_response.get("products", [])
        )

        product_options = [
            {
                "label": f"{p.get('sku', '')} - {p.get('name', '')}",
                "value": p.get("id", ""),
            }
            for p in products
        ]

        if button_id == "formula-add-btn":
            # Add mode - clear form
            return (
                True,  # is_open
                "New Formula",  # title
                "",  # name
                1,  # version
                product_options,  # products
                None,  # selected product
                1.0,  # yield_factor (default)
                True,  # is_active
                [],  # empty lines
            )

        elif button_id == "formula-edit-btn":
            if not selected_rows or not data:
                raise PreventUpdate

            formula = data[selected_rows[0]]
            formula_id = formula.get("id")

            # Fetch full formula data
            formula_response = make_api_request("GET", f"/formulas/{formula_id}")

            if "error" in formula_response:
                raise PreventUpdate

            formula_data = formula_response

            # Format lines data for editor
            lines_data = []
            for line in formula_data.get("lines", []):
                # Get the quantity in the display unit
                qty_kg = float(line.get("quantity_kg", 0))
                unit = line.get("unit", "kg")

                # Convert from kg to display unit if needed
                if unit == "kg":
                    display_qty = qty_kg
                elif unit == "g":
                    display_qty = qty_kg * 1000
                elif unit == "oz":
                    display_qty = qty_kg / 0.0283495
                elif unit == "lb":
                    display_qty = qty_kg / 0.453592
                elif unit == "mL":
                    display_qty = qty_kg * 1000
                else:
                    display_qty = qty_kg

                lines_data.append(
                    {
                        "sequence": str(line.get("sequence", "")),
                        "ingredient_name": line.get("ingredient_name", ""),
                        "raw_material_id": line.get("raw_material_id", ""),
                        "quantity": f"{display_qty:.3f}",
                        "unit": unit,  # Use saved unit
                        "notes": line.get("notes", ""),
                    }
                )

            # Get yield_factor from formula or default to 1.0
            yield_factor = formula_data.get("yield_factor", 1.0)
            if yield_factor is None:
                yield_factor = 1.0
            try:
                yield_factor = float(yield_factor)
            except (ValueError, TypeError):
                yield_factor = 1.0

            return (
                True,  # is_open
                "Edit Formula",  # title
                formula_data.get("formula_name", ""),
                formula_data.get("version", 1),
                product_options,
                formula_data.get("product_id", ""),
                yield_factor,  # yield_factor
                formula_data.get("is_active", True),
                lines_data,  # lines data
            )

        raise PreventUpdate

    # Save formula
    @app.callback(
        [
            Output("formula-editor-modal", "is_open", allow_duplicate=True),
            Output("formula-master-table", "data", allow_duplicate=True),
            Output("formula-master-table", "columns", allow_duplicate=True),
        ],
        [Input("formula-editor-save-btn", "n_clicks")],
        [
            State("formula-input-name", "value"),
            State("formula-input-version", "value"),
            State("formula-input-product", "value"),
            State("formula-input-yield-factor", "value"),
            State("formula-input-active", "value"),
            State("formula-editor-title", "children"),
            State("formula-editor-lines", "data"),
            State("formula-master-table", "selected_rows"),
            State("formula-master-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_formula(
        n_clicks,
        name,
        version,
        product_id,
        yield_factor,
        is_active,
        title,
        lines_data,
        selected_rows,
        current_data,
    ):
        """Save formula."""
        if not n_clicks:
            raise PreventUpdate

        if not all([name, product_id]):
            return False, no_update, no_update

        # Determine if this is edit mode
        is_edit = title == "Edit Formula" and selected_rows and len(selected_rows) > 0
        formula_id = None

        if is_edit:
            # Get the selected formula to get its ID
            selected_formula = current_data[selected_rows[0]]
            formula_id = selected_formula.get("id")
            if not formula_id:
                print("No ID found for selected formula")
                return False, no_update, no_update

        # Prepare payload
        if is_edit:
            # Update existing formula header
            # Convert yield_factor to float if provided
            yield_factor_float = 1.0
            if yield_factor is not None:
                try:
                    yield_factor_float = float(yield_factor)
                except (ValueError, TypeError):
                    yield_factor_float = 1.0

            payload = {
                "formula_name": name,
                "yield_factor": yield_factor_float,
                "is_active": is_active,
            }
            response = make_api_request("PUT", f"/formulas/{formula_id}", payload)

            # Also update the lines if they exist
            if lines_data:
                # Convert lines data to API format
                lines = []
                for line in lines_data:
                    raw_material_id = line.get("raw_material_id", "")
                    if not raw_material_id:
                        # Also check old field name for backwards compatibility
                        raw_material_id = line.get("ingredient_id", "")
                        if not raw_material_id:
                            continue

                    quantity = float(line.get("quantity", 0))
                    unit = line.get("unit", "kg")

                    # Convert to kg if needed
                    quantity_kg = quantity
                    if unit == "g":
                        quantity_kg = quantity / 1000
                    elif unit == "oz":
                        quantity_kg = quantity * 0.0283495
                    elif unit == "lb":
                        quantity_kg = quantity * 0.453592
                    elif unit == "mL":
                        quantity_kg = quantity / 1000

                    lines.append(
                        {
                            "raw_material_id": raw_material_id,
                            "quantity_kg": quantity_kg,
                            "sequence": int(line.get("sequence", 0)),
                            "notes": line.get("notes", ""),
                            "unit": line.get("unit", "kg"),  # Save the display unit
                        }
                    )

                # Update lines
                if lines:
                    lines_response = make_api_request(
                        "PUT", f"/formulas/{formula_id}/lines", lines
                    )
                    if "error" in lines_response:
                        print(
                            f"Error saving formula lines: {lines_response.get('error')}"
                        )
                        return False, no_update, no_update
        else:
            # Create new formula - need to get next available code
            # Fetch all formulas to generate next code
            all_formulas = make_api_request("GET", "/formulas/")
            if "error" in all_formulas:
                print("Error fetching existing formulas")
                return False, no_update, no_update

            # Generate next formula code
            existing_codes = []
            if isinstance(all_formulas, list):
                for f in all_formulas:
                    code = f.get("formula_code", "")
                    if code and str(code).isdigit():
                        existing_codes.append(int(code))
            elif isinstance(all_formulas, dict) and "formulas" in all_formulas:
                for f in all_formulas.get("formulas", []):
                    code = f.get("formula_code", "")
                    if code and str(code).isdigit():
                        existing_codes.append(int(code))

            next_code = max(existing_codes, default=0) + 1 if existing_codes else 1

            # Convert lines data to API format
            lines = []
            if lines_data:
                for line in lines_data:
                    raw_material_id = line.get("raw_material_id", "")
                    if not raw_material_id:
                        # Also check old field name for backwards compatibility
                        raw_material_id = line.get("ingredient_id", "")
                        if not raw_material_id:
                            continue

                    quantity = float(line.get("quantity", 0))
                    unit = line.get("unit", "kg")

                    # Convert to kg if needed
                    quantity_kg = quantity
                    if unit == "g":
                        quantity_kg = quantity / 1000
                    elif unit == "oz":
                        quantity_kg = quantity * 0.0283495
                    elif unit == "lb":
                        quantity_kg = quantity * 0.453592
                    elif unit == "mL":
                        quantity_kg = quantity / 1000

                    lines.append(
                        {
                            "raw_material_id": raw_material_id,
                            "quantity_kg": quantity_kg,
                            "sequence": int(line.get("sequence", 0)),
                            "notes": line.get("notes", ""),
                            "unit": line.get("unit", "kg"),  # Save the display unit
                        }
                    )

            # Convert yield_factor to float if provided
            yield_factor_float = 1.0
            if yield_factor is not None:
                try:
                    yield_factor_float = float(yield_factor)
                except (ValueError, TypeError):
                    yield_factor_float = 1.0

            payload = {
                "formula_code": str(next_code),
                "formula_name": name,
                "version": version or 1,
                "product_id": product_id,
                "yield_factor": yield_factor_float,
                "is_active": is_active,
                "lines": lines,
            }
            response = make_api_request("POST", "/formulas/", payload)

        if "error" in response:
            print(f"Error saving formula: {response.get('error')}")
            return False, no_update, no_update

        print("Formula saved successfully")

        # Reload formulas to refresh table
        reload_response = make_api_request("GET", "/formulas/")
        if "error" in reload_response:
            print(f"Error reloading formulas: {reload_response.get('error')}")
            return False, [], []

        formulas = (
            reload_response
            if isinstance(reload_response, list)
            else reload_response.get("formulas", [])
        )

        if not formulas:
            print("No formulas in reload")
            return False, [], []

        # Format data for display
        formatted_data = []
        for formula in formulas:
            product_name = formula.get("product_name", "")
            product_sku = formula.get("product_sku", "")
            # Format product display as "SKU - Name" or just "Name" if SKU not available
            if product_sku and product_name:
                product_display = f"{product_sku} - {product_name}"
            elif product_sku:
                product_display = product_sku
            elif product_name:
                product_display = product_name
            else:
                product_display = "-"

            formatted_data.append(
                {
                    "formula_code": formula.get("formula_code", ""),
                    "formula_name": formula.get("formula_name", ""),
                    "version": formula.get("version", 1),
                    "product_name": product_display,
                    "is_active": "✓" if formula.get("is_active", True) else "✗",
                    "id": formula.get("id", ""),
                }
            )

        # Create columns
        columns = [
            {"name": "Code", "id": "formula_code"},
            {"name": "Name", "id": "formula_name", "presentation": "markdown"},
            {"name": "Version", "id": "version"},
            {"name": "Product", "id": "product_name"},
            {"name": "Active", "id": "is_active"},
        ]

        return False, formatted_data, columns

    # Close modal
    @app.callback(
        Output("formula-editor-modal", "is_open", allow_duplicate=True),
        [Input("formula-editor-cancel-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def close_modal(n_clicks):
        """Close formula editor modal."""
        return False

    # Clear search
    @app.callback(
        Output("formula-search", "value"),
        [Input("formula-clear-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def clear_search(n_clicks):
        """Clear search input."""
        return ""

    # Add line to formula editor
    @app.callback(
        Output("formula-editor-lines", "data", allow_duplicate=True),
        [Input("formula-add-line-btn", "n_clicks")],
        [State("formula-editor-lines", "data")],
        prevent_initial_call=True,
    )
    def add_formula_line(n_clicks, current_data):
        """Add a new line to the formula."""
        if not n_clicks:
            raise PreventUpdate

        if current_data is None:
            current_data = []

        # Find next sequence number
        existing_sequences = [
            int(line.get("sequence", 0))
            for line in current_data
            if line.get("sequence")
        ]
        next_seq = max(existing_sequences, default=0) + 1 if existing_sequences else 1

        # Add new line
        new_line = {
            "sequence": str(next_seq),
            "ingredient_name": "[Click to select ingredient]",  # Placeholder
            "raw_material_id": "",  # To be filled when ingredient is selected
            "quantity": "0.000",
            "unit": "kg",  # Default unit
            "notes": "",
        }

        return current_data + [new_line]

    # Edit line - open ingredient selection modal for selected line
    @app.callback(
        [
            Output("ingredient-selection-modal", "is_open", allow_duplicate=True),
            Output("current-line-index-store", "children", allow_duplicate=True),
        ],
        [Input("formula-edit-line-btn", "n_clicks")],
        [
            State("formula-editor-lines", "selected_rows"),
            State("formula-editor-lines", "data"),
        ],
        prevent_initial_call=True,
    )
    def edit_formula_line_ingredient(n_clicks, selected_rows, current_data):
        """Open ingredient selection modal for selected line."""
        if not n_clicks or not selected_rows or not current_data:
            return False, no_update

        # Open modal and store which line we're editing
        return True, str(selected_rows[0])

    # Delete line from formula editor
    @app.callback(
        Output("formula-editor-lines", "data", allow_duplicate=True),
        [Input("formula-delete-line-btn", "n_clicks")],
        [
            State("formula-editor-lines", "selected_rows"),
            State("formula-editor-lines", "data"),
        ],
        prevent_initial_call=True,
    )
    def delete_formula_line(n_clicks, selected_rows, current_data):
        """Delete selected line from formula."""
        if not n_clicks or not selected_rows or not current_data:
            raise PreventUpdate

        # Remove selected rows
        new_data = [row for i, row in enumerate(current_data) if i not in selected_rows]

        return new_data

    # Open ingredient selection modal when clicking on ingredient cell
    @app.callback(
        [
            Output("ingredient-selection-modal", "is_open"),
            Output("current-line-index-store", "children"),
        ],
        [
            Input("formula-editor-lines", "active_cell"),
            Input("ingredient-modal-cancel", "n_clicks"),
        ],
        [State("formula-editor-lines", "data")],
        prevent_initial_call=True,
    )
    def open_ingredient_modal(active_cell, cancel_clicks, lines_data):
        """Open ingredient selection modal when clicking on ingredient column."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # If cancel button clicked, close modal
        if trigger_id == "ingredient-modal-cancel":
            return False, no_update

        # If clicking on table
        if active_cell and lines_data:
            col_id = active_cell.get("column_id")
            row_idx = active_cell.get("row")

            # Only open modal if clicking on ingredient column
            if col_id == "ingredient_name" and row_idx is not None:
                # Store which line we're editing
                return True, str(row_idx)

        return False, no_update

    # Search ingredients and populate results
    @app.callback(
        [
            Output("ingredient-search-results", "children"),
            Output("ingredient-search-message", "children"),
        ],
        [Input("ingredient-search-input", "value")],
        prevent_initial_call=False,
    )
    def search_ingredients(search_term):
        """Search raw materials for ingredients."""
        # If no search term, show all raw materials
        params = {}
        if search_term and len(search_term) >= 1:
            params["search"] = search_term

        # Fetch raw materials
        response = make_api_request("GET", "/raw-materials/", data=params)

        if "error" in response:
            return html.Div("Error loading raw materials"), ""

        raw_materials = response if isinstance(response, list) else []

        message = f"Showing {len(raw_materials)} raw materials"

        if not raw_materials:
            return html.Div(dbc.Alert("No raw materials found", color="warning")), ""

        # Create table of results
        results = []
        for rm in raw_materials[:100]:  # Limit to 100 results for performance
            code = str(rm.get("code", "")).strip()
            desc1 = str(rm.get("desc1", "")).strip()
            desc2 = str(rm.get("desc2", "")).strip()
            desc = f"{code} - {desc1} {desc2}".strip()

            results.append(
                {
                    "id": rm.get("id", ""),
                    "code": code,
                    "description": desc,
                }
            )

        return (
            html.Div(
                [
                    dash_table.DataTable(
                        id="ingredient-results-table",
                        columns=[
                            {"name": "Code", "id": "code"},
                            {"name": "Description", "id": "description"},
                        ],
                        data=results,
                        row_selectable="single",
                        page_action="native",
                        page_current=0,
                        page_size=20,
                        style_cell={
                            "textAlign": "left",
                            "fontSize": "11px",
                            "padding": "8px",
                        },
                        style_header={
                            "backgroundColor": "rgb(220, 220, 220)",
                            "fontWeight": "bold",
                        },
                        style_data_conditional=[
                            {
                                "if": {"row_index": "odd"},
                                "backgroundColor": "rgb(248, 248, 248)",
                            }
                        ],
                    )
                ]
            ),
            message,
        )

    # Handle ingredient selection from results table
    @app.callback(
        [
            Output("formula-editor-lines", "data", allow_duplicate=True),
            Output("ingredient-selection-modal", "is_open", allow_duplicate=True),
            Output("ingredient-results-table", "selected_rows"),
        ],
        [
            Input("ingredient-results-table", "selected_rows"),
            Input("ingredient-modal-cancel", "n_clicks"),
        ],
        [
            State("ingredient-results-table", "data"),
            State("current-line-index-store", "children"),
            State("formula-editor-lines", "data"),
        ],
        prevent_initial_call=True,
    )
    def handle_ingredient_selection(
        selected_rows, cancel_clicks, results_data, line_index, current_lines
    ):
        """Handle selection of ingredient from results."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # If cancel clicked, just close modal
        if trigger_id == "ingredient-modal-cancel":
            return no_update, False, []

        # If ingredient selected
        if selected_rows and results_data and current_lines and line_index:
            selected_row = results_data[selected_rows[0]]
            ingredient_id = selected_row.get("id")
            ingredient_name = selected_row.get("description", "")

            # Update the line in formula editor
            line_idx = int(line_index)
            if 0 <= line_idx < len(current_lines):
                new_lines = current_lines.copy()
                new_lines[line_idx]["raw_material_id"] = ingredient_id
                new_lines[line_idx]["ingredient_name"] = ingredient_name

                # Close modal and clear selection
                return new_lines, False, []

        return no_update, False, []
