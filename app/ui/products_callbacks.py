"""CRUD callbacks for products page."""

import json

import dash
from dash import Input, Output, State, dash_table, html, no_update
from dash.exceptions import PreventUpdate


def register_product_callbacks(app, make_api_request):
    """Register all product CRUD callbacks."""

    # Load units, purchase formats, and suppliers for dropdowns
    @app.callback(
        [
            Output("product-base-unit", "options"),
            Output("product-purchase-unit-dropdown", "options"),
            Output("product-usage-unit-dropdown", "options"),
            Output("product-purchase-format-dropdown", "options"),
            Output("product-supplier-dropdown", "options"),
        ],
        [Input("product-form-modal", "is_open")],
    )
    def load_dropdowns(modal_is_open):
        """Load units, purchase formats, and suppliers from API for dropdown options."""
        if not modal_is_open:
            raise PreventUpdate

        try:
            # Load units
            units_response = make_api_request("GET", "/units/?is_active=true")
            units = units_response if isinstance(units_response, list) else []

            # Create options list for base_unit (store code, not ID)
            base_unit_options = [
                {
                    "label": f"{u.get('code', '')} - {u.get('name', '')}",
                    "value": u.get("code", ""),
                }
                for u in units
            ]

            # Create options list for purchase_unit and usage_unit (store ID)
            unit_id_options = [
                {
                    "label": f"{u.get('code', '')} - {u.get('name', '')}",
                    "value": str(u.get("id", "")),
                }
                for u in units
            ]

            # Load purchase formats
            formats_response = make_api_request(
                "GET", "/purchase-formats/?is_active=true"
            )
            formats = formats_response if isinstance(formats_response, list) else []
            purchase_format_options = [
                {
                    "label": f"{f.get('code', '')} - {f.get('name', '')}",
                    "value": str(f.get("id", "")),
                }
                for f in formats
            ]

            # Load suppliers (contacts who are suppliers)
            contacts_response = make_api_request(
                "GET", "/contacts/?is_supplier=true&is_active=true"
            )
            contacts = contacts_response if isinstance(contacts_response, list) else []
            supplier_options = [
                {
                    "label": f"{c.get('code', '')} - {c.get('name', '')}",
                    "value": str(c.get("id", "")),
                }
                for c in contacts
            ]

            return (
                base_unit_options,
                unit_id_options,
                base_unit_options,
                purchase_format_options,
                supplier_options,
            )
        except Exception as e:
            print(f"Error loading dropdowns: {e}")
            return [], [], [], [], []

    # Toggle edit/delete buttons based on selection
    @app.callback(
        [
            Output("edit-product-btn", "disabled"),
            Output("duplicate-product-btn", "disabled"),
            Output("delete-product-btn", "disabled"),
        ],
        [Input("products-table", "selected_rows")],
    )
    def toggle_action_buttons(selected_rows):
        disabled = not selected_rows or len(selected_rows) == 0
        return disabled, disabled, disabled  # Edit, Duplicate, Delete

    # Open modal for add/edit and populate form
    @app.callback(
        [
            Output("product-form-modal", "is_open", allow_duplicate=True),
            Output("product-modal-title", "children", allow_duplicate=True),
            Output("product-sku", "value", allow_duplicate=True),
            Output("product-name", "value", allow_duplicate=True),
            Output("product-description", "value", allow_duplicate=True),
            Output("product-ean13", "value", allow_duplicate=True),
            Output("product-supplier-dropdown", "value", allow_duplicate=True),
            Output("product-base-unit", "value", allow_duplicate=True),
            Output("product-is-active", "value", allow_duplicate=True),
            Output("product-is-purchase", "value", allow_duplicate=True),
            Output("product-is-sell", "value", allow_duplicate=True),
            Output("product-is-assemble", "value", allow_duplicate=True),
            Output("product-allow-negative", "value", allow_duplicate=True),
            Output("product-pricing-table", "data", allow_duplicate=True),
            Output("product-cost-table", "data", allow_duplicate=True),
            Output("product-size", "value", allow_duplicate=True),
            Output("product-density", "value", allow_duplicate=True),
            Output("product-abv", "value", allow_duplicate=True),
            Output("product-dgflag", "value", allow_duplicate=True),
            Output("product-purchase-unit-dropdown", "value", allow_duplicate=True),
            Output("product-purchase-quantity", "value", allow_duplicate=True),
            Output("product-purchase-cost-ex-gst", "value", allow_duplicate=True),
            Output("product-purchase-cost-inc-gst", "value", allow_duplicate=True),
            Output("product-usage-unit-dropdown", "value", allow_duplicate=True),
            Output("product-usage-quantity", "value", allow_duplicate=True),
            Output("product-purchase-format-dropdown", "value", allow_duplicate=True),
            Output("product-form-hidden", "children", allow_duplicate=True),
        ],
        [
            Input("add-product-btn", "n_clicks"),
            Input("edit-product-btn", "n_clicks"),
            Input("duplicate-product-btn", "n_clicks"),
        ],
        [State("products-table", "selected_rows"), State("products-table", "data")],
        prevent_initial_call=True,
    )
    def open_product_modal(
        add_clicks, edit_clicks, duplicate_clicks, selected_rows, data
    ):
        """Open modal for add, edit, or duplicate and populate form data."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "add-product-btn":
            # Add mode - clear form
            pricing_data = [
                {
                    "price_level": "Retail",
                    "inc_gst": None,
                    "ex_gst": None,
                    "excise": None,
                },
                {
                    "price_level": "Wholesale",
                    "use_unit": "",
                    "inc_gst": None,
                    "ex_gst": None,
                    "excise": None,
                },
                {
                    "price_level": "Distributor",
                    "use_unit": "",
                    "inc_gst": None,
                    "ex_gst": None,
                    "excise": None,
                },
                {
                    "price_level": "Counter",
                    "use_unit": "",
                    "inc_gst": None,
                    "ex_gst": None,
                    "excise": None,
                },
                {
                    "price_level": "Trade",
                    "use_unit": "",
                    "inc_gst": None,
                    "ex_gst": None,
                    "excise": None,
                },
                {
                    "price_level": "Contract",
                    "use_unit": "",
                    "inc_gst": None,
                    "ex_gst": None,
                    "excise": None,
                },
                {
                    "price_level": "Industrial",
                    "use_unit": "",
                    "inc_gst": None,
                    "ex_gst": None,
                    "excise": None,
                },
            ]
            cost_data = [
                {
                    "cost_type": "Purchase",
                    "is_primary": "[Set Primary]",
                    "is_primary_bool": False,
                    "qty": None,
                    "unit": None,
                    "ex_gst": None,
                    "inc_gst": None,
                    "tax_included": "✗",
                    "tax_included_bool": False,
                },
                {
                    "cost_type": "Assembly",
                    "is_primary": "[Set Primary]",
                    "is_primary_bool": False,
                    "qty": None,
                    "unit": None,
                    "ex_gst": None,
                    "inc_gst": None,
                    "tax_included": "✗",
                    "tax_included_bool": False,
                },
                {
                    "cost_type": "Usage",
                    "is_primary": "[Set Primary]",
                    "is_primary_bool": False,
                    "qty": None,
                    "unit": None,
                    "ex_gst": None,
                    "inc_gst": None,
                    "tax_included": "✗",
                    "tax_included_bool": False,
                },
                {
                    "cost_type": "Manufactured Cost",
                    "is_primary": "",
                    "is_primary_bool": False,
                    "qty": None,
                    "unit": None,
                    "ex_gst": None,
                    "inc_gst": None,
                    "tax_included": "N/A",
                    "tax_included_bool": False,
                },
            ]
            return (
                True,  # is_open
                "Add Product",  # title
                None,  # sku
                None,  # name
                None,  # description
                None,  # ean13
                None,  # supplier_id
                None,  # base_unit
                "true",  # is_active
                False,  # is_purchase
                False,  # is_sell
                False,  # is_assemble
                True,  # allow_negative_inventory
                pricing_data,  # pricing_table
                cost_data,  # cost_table
                None,  # size
                None,  # density
                None,  # abv
                None,  # dgflag
                None,  # purchase-unit
                None,  # purchase-quantity
                None,  # purchase-cost-ex-gst
                None,  # purchase-cost-inc-gst
                None,  # usage-unit
                None,  # usage-quantity
                None,  # purchase-format
                "",  # product-form-hidden (product_id)
            )

        elif button_id == "edit-product-btn" or button_id == "duplicate-product-btn":
            if not selected_rows or not data:
                raise PreventUpdate

            # Get product from table data
            product_table_row = data[selected_rows[0]]
            product_id = product_table_row.get("id")
            is_duplicate = button_id == "duplicate-product-btn"

            # Fetch full product record from API to ensure we have all fields
            product = product_table_row  # Default to table data
            if product_id and not is_duplicate:
                try:
                    full_product = make_api_request("GET", f"/products/{product_id}")
                    if isinstance(full_product, dict):
                        product = full_product  # Use full API response
                except Exception as e:
                    print(f"Error fetching full product: {e}")
                    # Fall back to table data
                    product = product_table_row

            # Helper function to safely convert to float
            def safe_float(value, default=None):
                if value is None or value == "":
                    return default
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default

            # Helper function to safely convert to int
            def safe_int(value, default=None):
                if value is None or value == "":
                    return default
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return default

            # Handle is_active - ensure it's "true" or "false" string
            is_active = product.get("is_active")
            if is_active is None:
                is_active_str = "true"
            elif isinstance(is_active, bool):
                is_active_str = "true" if is_active else "false"
            elif isinstance(is_active, str):
                is_active_str = (
                    "true"
                    if is_active.lower() in ("true", "1", "yes", "y")
                    else "false"
                )
            else:
                is_active_str = "true" if bool(is_active) else "false"

            # Handle purchase_unit_id - ensure it's a string or None (for dropdown)
            purchase_unit_id = product.get("purchase_unit_id")
            if purchase_unit_id is None or purchase_unit_id == "":
                purchase_unit_id = None
            else:
                purchase_unit_id = str(purchase_unit_id)

            # Handle purchase_format_id - ensure it's a string or None (for dropdown)
            purchase_format_id = product.get("purchase_format_id")
            if purchase_format_id is None or purchase_format_id == "":
                purchase_format_id = None
            else:
                purchase_format_id = str(purchase_format_id)

            # Handle boolean fields - ensure they're explicit booleans
            # Note: Table data may have checkmarks ("✓") or empty strings, so handle both
            def to_bool(value):
                """Convert various formats to boolean for checkbox values."""
                if value is None:
                    return False
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    # Handle checkmark, empty string, or text representations
                    value_clean = value.strip()
                    if value_clean == "✓" or value_clean == "":
                        return value_clean == "✓"
                    return value_clean.lower() in ("true", "1", "yes", "y")
                # For any other type, convert to bool
                return bool(value)

            is_purchase = to_bool(product.get("is_purchase"))
            is_sell = to_bool(product.get("is_sell"))
            is_assemble = to_bool(product.get("is_assemble"))
            allow_negative_flag = to_bool(product.get("allow_negative_inventory", True))

            # Get usage costs for COGS calculations
            usage_cost_ex_gst = safe_float(product.get("usage_cost_ex_gst"), 0.0)
            usage_cost_inc_gst = safe_float(product.get("usage_cost_inc_gst"), 0.0)

            # If usage_cost_inc_gst is not available, calculate from ex_gst
            if not usage_cost_inc_gst and usage_cost_ex_gst:
                usage_cost_inc_gst = usage_cost_ex_gst * 1.1

            # Build pricing table data with COGS columns
            pricing_data = []
            price_levels = [
                (
                    "Retail",
                    "retail_price_inc_gst",
                    "retail_price_ex_gst",
                    "retail_excise",
                ),
                (
                    "Wholesale",
                    "wholesale_price_inc_gst",
                    "wholesale_price_ex_gst",
                    "wholesale_excise",
                ),
                (
                    "Distributor",
                    "distributor_price_inc_gst",
                    "distributor_price_ex_gst",
                    "distributor_excise",
                ),
                (
                    "Counter",
                    "counter_price_inc_gst",
                    "counter_price_ex_gst",
                    "counter_excise",
                ),
                ("Trade", "trade_price_inc_gst", "trade_price_ex_gst", "trade_excise"),
                (
                    "Contract",
                    "contract_price_inc_gst",
                    "contract_price_ex_gst",
                    "contract_excise",
                ),
                (
                    "Industrial",
                    "industrial_price_inc_gst",
                    "industrial_price_ex_gst",
                    "industrial_excise",
                ),
            ]

            for level, inc_field, ex_field, excise_field in price_levels:
                inc_gst = safe_float(product.get(inc_field))
                ex_gst = safe_float(product.get(ex_field))
                excise = safe_float(product.get(excise_field), 0.0)

                # Populate Inc GST COGS with usage cost inc GST (including tax use cost)
                inc_gst_cogs = usage_cost_inc_gst if usage_cost_inc_gst else None

                # Populate Inc Excise COGS = (ex-GST use cost + excise) * 1.1
                inc_excise_cogs = None
                if usage_cost_ex_gst is not None and excise is not None:
                    inc_excise_cogs = (usage_cost_ex_gst + excise) * 1.1
                elif usage_cost_ex_gst is not None:
                    inc_excise_cogs = usage_cost_ex_gst * 1.1

                pricing_data.append(
                    {
                        "price_level": level,
                        "inc_gst": inc_gst,
                        "ex_gst": ex_gst,
                        "excise": excise,
                        "inc_gst_cogs": round(inc_gst_cogs, 2)
                        if inc_gst_cogs is not None
                        else None,
                        "inc_excise_cogs": round(inc_excise_cogs, 2)
                        if inc_excise_cogs is not None
                        else None,
                    }
                )

            # Build cost table data with row-based structure
            # Get purchase unit code for display
            purchase_unit_display = ""
            if purchase_unit_id:
                try:
                    units_response = make_api_request("GET", "/units/?is_active=true")
                    units = units_response if isinstance(units_response, list) else []
                    for unit in units:
                        if str(unit.get("id")) == str(purchase_unit_id):
                            purchase_unit_display = unit.get("code", "").upper()
                            break
                except Exception:
                    pass

            # Calculate per unit costs from purchase_cost_ex_gst
            purchase_per_unit = None
            purchase_cost_ex_gst = safe_float(product.get("purchase_cost_ex_gst"))
            purchase_qty_val = safe_float(product.get("purchase_quantity"))
            if (
                purchase_qty_val
                and purchase_qty_val > 0
                and purchase_cost_ex_gst is not None
            ):
                purchase_per_unit = purchase_cost_ex_gst / purchase_qty_val

            safe_float(product.get("usage_cost_ex_gst"))

            # product_id already extracted above
            if is_duplicate:
                product_id = None  # Clear ID for duplicate

            # Check if product has assembly (formulas)
            has_assembly = False
            assembly_cost_per_kg = None
            assembly_total_kg = None
            assembly_total_cost = None  # Store total assembly cost
            if product_id:
                try:
                    formulas_response = make_api_request(
                        "GET", f"/formulas/?product_id={product_id}&is_active=true"
                    )
                    if (
                        isinstance(formulas_response, list)
                        and len(formulas_response) > 0
                    ):
                        # Get the first active formula and calculate its cost
                        formula = formulas_response[0]
                        lines_list = formula.get("lines", [])
                        if lines_list:
                            has_assembly = True
                            # Calculate assembly cost (similar to calculate_assembly_line_costs)
                            total_cost = 0.0
                            total_quantity_kg = 0.0
                            total_quantity_l = 0.0
                            for line in lines_list:
                                if isinstance(line, dict):
                                    qty_kg = float(line.get("quantity_kg", 0.0) or 0.0)
                                    unit_cost = float(line.get("unit_cost", 0.0) or 0.0)
                                    if unit_cost == 0:
                                        # Try to get cost from product
                                        line_product_id = line.get(
                                            "raw_material_id"
                                        ) or line.get("product_id")
                                        if line_product_id:
                                            try:
                                                line_product = make_api_request(
                                                    "GET",
                                                    f"/products/{line_product_id}",
                                                )
                                                if isinstance(line_product, dict):
                                                    # Preserve 4 decimal places
                                                    cost_val = (
                                                        line_product.get(
                                                            "usage_cost_ex_gst"
                                                        )
                                                        or line_product.get(
                                                            "purchase_cost_ex_gst"
                                                        )
                                                        or 0
                                                    )
                                                    if cost_val:
                                                        try:
                                                            unit_cost = round(
                                                                float(cost_val), 4
                                                            )
                                                        except (ValueError, TypeError):
                                                            unit_cost = 0.0
                                                    else:
                                                        unit_cost = 0.0
                                            except Exception:
                                                pass
                                    line_cost = (
                                        qty_kg * unit_cost
                                        if unit_cost > 0 and qty_kg > 0
                                        else 0.0
                                    )
                                    total_cost += line_cost
                                    total_quantity_kg += qty_kg
                                    # Calculate L if density available
                                    density = safe_float(
                                        product.get("density_kg_per_l")
                                    )
                                    if density and density > 0:
                                        total_quantity_l += qty_kg / density
                            # Store total cost (even if quantity_kg is 0)
                            if total_cost > 0:
                                assembly_total_cost = round(total_cost, 4)
                                print(
                                    f"[open_product_modal] Calculated assembly_total_cost: {assembly_total_cost}"
                                )
                            if total_quantity_kg > 0:
                                assembly_cost_per_kg = total_cost / total_quantity_kg
                                assembly_total_kg = total_quantity_kg
                            if total_quantity_l > 0:
                                total_cost / total_quantity_l
                except Exception as e:
                    print(f"Error fetching assembly data: {e}")
                    import traceback

                    traceback.print_exc()

            # Determine primary cost: if purchase type only, auto-flag purchase; otherwise check if purchase or assembly is primary
            # For now, default to purchase if available, otherwise assembly
            purchase_is_primary = False
            assembly_is_primary = False
            if purchase_per_unit is not None and purchase_per_unit > 0:
                # If purchase exists and no assembly, purchase is primary
                if not has_assembly or assembly_cost_per_kg is None:
                    purchase_is_primary = True
                else:
                    # Both exist - check saved preference (could be stored in product, but for now default to purchase)
                    purchase_is_primary = True  # Default to purchase if both exist

            cost_data = [
                {
                    "cost_type": "Purchase",
                    "is_primary": "✓" if purchase_is_primary else "[Set Primary]",
                    "is_primary_bool": purchase_is_primary,
                    "qty": safe_float(product.get("purchase_quantity")),
                    "unit": purchase_unit_display,
                    "ex_gst": safe_float(product.get("purchase_cost_ex_gst")),
                    "inc_gst": safe_float(product.get("purchase_cost_inc_gst")),
                    "tax_included": "✓"
                    if product.get("purchase_tax_included")
                    else "✗",
                    "tax_included_bool": product.get("purchase_tax_included") or False,
                    "action": "",  # Ensure action field exists
                },
                {
                    "cost_type": "Assembly",
                    "is_primary": "✓" if assembly_is_primary else "[Set Primary]",
                    "is_primary_bool": assembly_is_primary,
                    "qty": assembly_total_kg,
                    "unit": "kg",
                    "ex_gst": round(assembly_cost_per_kg, 4)
                    if assembly_cost_per_kg is not None
                    else None,
                    "inc_gst": round(assembly_cost_per_kg * 1.1, 4)
                    if assembly_cost_per_kg
                    else None,
                    "tax_included": "✗",
                    "tax_included_bool": False,
                    "total_cost": assembly_total_cost,  # Store total cost for copying to usage
                    "action": "**Use Total as Usage Cost**"
                    if (assembly_total_cost is not None and assembly_total_cost > 0)
                    else "",
                },
                {
                    "cost_type": "Usage",
                    "is_primary": "[Set Primary]",
                    "is_primary_bool": False,
                    "qty": safe_float(product.get("usage_quantity"))
                    if product.get("usage_quantity")
                    else None,
                    "unit": (
                        str(product.get("usage_unit", "")).upper()
                        if product.get("usage_unit")
                        else ""
                    ),
                    "ex_gst": (
                        round(safe_float(product.get("usage_cost_ex_gst")), 4)
                        if safe_float(product.get("usage_cost_ex_gst")) is not None
                        else None
                    ),
                    "inc_gst": (
                        round(safe_float(product.get("usage_cost_inc_gst")), 4)
                        if safe_float(product.get("usage_cost_inc_gst")) is not None
                        else None
                    ),
                    "tax_included": "✓" if product.get("usage_tax_included") else "✗",
                    "tax_included_bool": product.get("usage_tax_included") or False,
                    "action": "",
                },
                {
                    "cost_type": "Manufactured Cost",
                    "is_primary": "",
                    "is_primary_bool": False,
                    "qty": None,
                    "unit": None,
                    "ex_gst": safe_float(product.get("manufactured_cost_ex_gst")),
                    "inc_gst": safe_float(product.get("manufactured_cost_inc_gst")),
                    "tax_included": "N/A",
                    "tax_included_bool": False,
                    "action": "",
                },
            ]

            # For duplicate, modify SKU and name to indicate it's a copy
            sku_base = product.get("sku") or ""
            name_base = product.get("name") or ""
            if is_duplicate:
                # Generate new SKU by appending "-COPY" or incrementing number
                if sku_base:
                    if sku_base.endswith("-COPY"):
                        # If already has -COPY, try to increment
                        base = sku_base[:-5]
                        sku_new = f"{base}-COPY2"
                    else:
                        sku_new = f"{sku_base}-COPY"
                else:
                    sku_new = "NEW-PRODUCT"

                # Add " (Copy)" to name
                name_new = f"{name_base} (Copy)" if name_base else "New Product (Copy)"
            else:
                sku_new = sku_base
                name_new = name_base

            return (
                True,  # is_open
                "Duplicate Product" if is_duplicate else "Edit Product",  # title
                sku_new,
                name_new,
                product.get("description") or "",
                product.get("ean13") or "",
                (
                    str(product.get("supplier_id", ""))
                    if product.get("supplier_id")
                    else ""
                ),
                product.get("base_unit") or "",
                is_active_str,
                is_purchase,
                is_sell,
                is_assemble,
                allow_negative_flag,
                pricing_data,
                cost_data,
                product.get("size") or "",
                safe_float(product.get("density_kg_per_l")),
                safe_float(product.get("abv_percent")),
                product.get("dgflag") or "",
                purchase_unit_id,
                safe_float(product.get("purchase_quantity")),
                # Purchase cost per unit (ex GST)
                safe_float(product.get("purchase_cost_ex_gst")),
                # Purchase cost per unit (inc GST) - calculate if ex_gst exists
                (
                    round(safe_float(product.get("purchase_cost_ex_gst")) * 1.1, 2)
                    if product.get("purchase_cost_ex_gst")
                    else safe_float(product.get("purchase_cost_inc_gst"))
                ),
                product.get("usage_unit") or "",
                safe_float(product.get("usage_quantity")),
                purchase_format_id,
                ""
                if is_duplicate
                else (
                    str(product_id) if product_id else ""
                ),  # Empty ID for duplicate (new product)
            )

        raise PreventUpdate

    # Close modal on cancel only (save handles its own closing)
    @app.callback(
        Output("product-form-modal", "is_open", allow_duplicate=True),
        [Input("product-cancel-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def close_modal(cancel_clicks):
        """Close modal when cancel is clicked."""
        if cancel_clicks:
            return False
        raise PreventUpdate

    # Auto-calculate between purchase cost ex GST and inc GST
    @app.callback(
        [
            Output("product-purchase-cost-ex-gst", "value", allow_duplicate=True),
            Output("product-purchase-cost-inc-gst", "value", allow_duplicate=True),
        ],
        [
            Input("product-purchase-cost-ex-gst", "value"),
            Input("product-purchase-cost-inc-gst", "value"),
        ],
        prevent_initial_call=True,
    )
    def calculate_purchase_cost_gst(ex_gst_value, inc_gst_value):
        """Auto-calculate inc GST from ex GST or vice versa."""
        GST_RATE = 0.10

        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        try:
            if (
                triggered_id == "product-purchase-cost-ex-gst"
                and ex_gst_value is not None
            ):
                # User entered ex GST, calculate inc GST
                ex_gst_float = float(ex_gst_value)
                inc_gst = round(ex_gst_float * (1 + GST_RATE), 2)
                return dash.no_update, inc_gst
            elif (
                triggered_id == "product-purchase-cost-inc-gst"
                and inc_gst_value is not None
            ):
                # User entered inc GST, calculate ex GST
                inc_gst_float = float(inc_gst_value)
                ex_gst = round(inc_gst_float / (1 + GST_RATE), 2)
                return ex_gst, dash.no_update
        except (ValueError, TypeError):
            pass

        raise PreventUpdate

    # Save product (create or update)
    @app.callback(
        [
            Output("product-form-modal", "is_open", allow_duplicate=True),
            Output("toast", "is_open"),
            Output("toast", "header"),
            Output("toast", "children"),
            Output("products-refresh-trigger", "children", allow_duplicate=True),
            Output("product-form-hidden", "children", allow_duplicate=True),
            Output("product-assemblies-table", "data", allow_duplicate=True),
        ],
        [Input("product-save-btn", "n_clicks")],
        [
            State("product-sku", "value"),
            State("product-name", "value"),
            State("product-description", "value"),
            State("product-ean13", "value"),
            State("product-supplier-dropdown", "value"),
            State("product-base-unit", "value"),
            State("product-is-active", "value"),
            State("product-is-purchase", "value"),
            State("product-is-sell", "value"),
            State("product-is-assemble", "value"),
            State("product-allow-negative", "value"),
            State("product-pricing-table", "data"),
            State("product-cost-table", "data"),
            State("product-size", "value"),
            State("product-weight", "value"),
            State("product-density", "value"),
            State("product-abv", "value"),
            State("product-dgflag", "value"),
            State("product-purchase-unit-dropdown", "value"),
            State("product-purchase-quantity", "value"),
            State("product-purchase-cost-ex-gst", "value"),
            State("product-purchase-cost-inc-gst", "value"),
            State("product-usage-unit-dropdown", "value"),
            State("product-usage-quantity", "value"),
            State("product-purchase-format-dropdown", "value"),
            State("product-form-hidden", "children"),
        ],
        prevent_initial_call=True,
    )
    def save_product(n_clicks, *args):
        """Save product - create or update based on hidden state."""
        if not n_clicks:
            raise PreventUpdate

        # Extract all form values
        (
            sku,
            name,
            description,
            ean13,
            supplier_id,
            base_unit,
            is_active,
            is_purchase,
            is_sell,
            is_assemble,
            allow_negative,
            pricing_data,
            cost_data,
            size,
            weight,
            density,
            abv,
            dgflag,
            purchase_unit_id,
            purchase_quantity,
            purchase_cost_ex_gst,
            purchase_cost_inc_gst,
            usage_unit,
            usage_quantity,
            purchase_format_id,
            product_id,
        ) = args

        # Validate required fields
        if not sku or not name:
            return True, True, "Error", "SKU and Name are required", ""

        # Extract pricing data from table
        def get_price_value(pricing_data, price_level, field):
            if not pricing_data:
                return None
            for row in pricing_data:
                if row.get("price_level") == price_level:
                    val = row.get(field)
                    if val is None or val == "":
                        return None
                    try:
                        return float(val)
                    except (ValueError, TypeError):
                        return None
            return None

        # Extract cost data from table
        def get_cost_value(cost_data, cost_type, field):
            if not cost_data:
                return None
            for row in cost_data:
                if row.get("cost_type") == cost_type:
                    val = row.get(field)
                    if field == "tax_included":
                        # Handle tax_included - can be bool, markdown string, or "N/A"
                        if val == "N/A":
                            return None
                        # Check tax_included_bool first, then parse from tax_included string
                        tax_included_bool = row.get("tax_included_bool")
                        if tax_included_bool is not None:
                            return tax_included_bool
                        if isinstance(val, bool):
                            return val
                        if isinstance(val, str):
                            return val == "✓" or val.lower() in (
                                "true",
                                "1",
                                "yes",
                                "y",
                            )
                        return False
                    if val is None or val == "":
                        return None
                    try:
                        # Preserve 4 decimal places for cost fields (ex_gst, inc_gst, excise)
                        float_val = float(val)
                        if field in ("ex_gst", "inc_gst", "excise"):
                            return round(float_val, 4)
                        return float_val
                    except (ValueError, TypeError):
                        return None
            return None

        # Prepare product data
        # For updates, always include fields even if empty to allow clearing them
        # For creates, None is fine for optional fields
        product_data = {
            "sku": sku.strip() if sku else None,
            "name": name.strip() if name else None,
            # Always include description, base_unit, density - send empty string if provided to clear
            "description": description.strip() if description is not None else None,
            # Convert checkbox values to explicit booleans - handle bool, None, or string
            "is_purchase": (
                True
                if (
                    is_purchase is True
                    or (
                        isinstance(is_purchase, str)
                        and is_purchase.lower() in ("true", "1", "yes", "y")
                    )
                )
                else False
            ),
            "is_sell": (
                True
                if (
                    is_sell is True
                    or (
                        isinstance(is_sell, str)
                        and is_sell.lower() in ("true", "1", "yes", "y")
                    )
                )
                else False
            ),
            "is_assemble": (
                True
                if (
                    is_assemble is True
                    or (
                        isinstance(is_assemble, str)
                        and is_assemble.lower() in ("true", "1", "yes", "y")
                    )
                )
                else False
            ),
            "allow_negative_inventory": (
                True
                if (
                    allow_negative is True
                    or (
                        isinstance(allow_negative, str)
                        and allow_negative.lower() in ("true", "1", "yes", "y")
                    )
                )
                else False
            ),
            "ean13": ean13.strip() if ean13 else None,
            "supplier_id": str(supplier_id) if supplier_id else None,
            "purchase_format_id": (
                str(purchase_format_id)
                if purchase_format_id
                and purchase_format_id != ""
                and str(purchase_format_id).strip() != ""
                and str(purchase_format_id).lower() != "none"
                else None
            ),
            # raw_material_group_id removed - deprecated field
            # Base unit: include even if empty string to allow clearing
            "base_unit": base_unit.strip()
            if base_unit is not None and base_unit != ""
            else None,
            "is_active": bool(
                is_active == "true"
                if isinstance(is_active, str)
                else (is_active if is_active is not None else True)
            ),
            "size": size.strip() if size else None,
            # weight_kg removed - not a Product model field
            # pack removed - deprecated field
            "pkge": None,  # Not in form, always None
            # Density: include if provided (even if 0), None if empty
            "density_kg_per_l": (
                float(density)
                if density is not None
                and str(density).strip()
                and str(density).strip() != ""
                else None
            ),
            "abv_percent": (
                float(abv)
                if abv is not None and str(abv).strip() and str(abv).strip() != ""
                else None
            ),
            "dgflag": dgflag if dgflag else None,
            # Legacy pricing fields (not in form, set to None - handled by pricing/cost tables)
            "taxinc": None,
            "salestaxcde": None,
            "purcost": None,
            "purtax": None,
            "wholesalecost": None,
            "excise_amount": None,
            "wholesalecde": None,
            "retailcde": None,
            "countercde": None,
            "tradecde": None,
            "contractcde": None,
            "industrialcde": None,
            "distributorcde": None,
            "disccdeone": None,
            "disccdetwo": None,
            # Sales Pricing from table
            "retail_price_inc_gst": get_price_value(pricing_data, "Retail", "inc_gst"),
            "retail_price_ex_gst": get_price_value(pricing_data, "Retail", "ex_gst"),
            "retail_excise": get_price_value(pricing_data, "Retail", "excise"),
            "wholesale_price_inc_gst": get_price_value(
                pricing_data, "Wholesale", "inc_gst"
            ),
            "wholesale_price_ex_gst": get_price_value(
                pricing_data, "Wholesale", "ex_gst"
            ),
            "wholesale_excise": get_price_value(pricing_data, "Wholesale", "excise"),
            "distributor_price_inc_gst": get_price_value(
                pricing_data, "Distributor", "inc_gst"
            ),
            "distributor_price_ex_gst": get_price_value(
                pricing_data, "Distributor", "ex_gst"
            ),
            "distributor_excise": get_price_value(
                pricing_data, "Distributor", "excise"
            ),
            "counter_price_inc_gst": get_price_value(
                pricing_data, "Counter", "inc_gst"
            ),
            "counter_price_ex_gst": get_price_value(pricing_data, "Counter", "ex_gst"),
            "counter_excise": get_price_value(pricing_data, "Counter", "excise"),
            "trade_price_inc_gst": get_price_value(pricing_data, "Trade", "inc_gst"),
            "trade_price_ex_gst": get_price_value(pricing_data, "Trade", "ex_gst"),
            "trade_excise": get_price_value(pricing_data, "Trade", "excise"),
            "contract_price_inc_gst": get_price_value(
                pricing_data, "Contract", "inc_gst"
            ),
            "contract_price_ex_gst": get_price_value(
                pricing_data, "Contract", "ex_gst"
            ),
            "contract_excise": get_price_value(pricing_data, "Contract", "excise"),
            "industrial_price_inc_gst": get_price_value(
                pricing_data, "Industrial", "inc_gst"
            ),
            "industrial_price_ex_gst": get_price_value(
                pricing_data, "Industrial", "ex_gst"
            ),
            "industrial_excise": get_price_value(pricing_data, "Industrial", "excise"),
            # Cost Pricing from table (now using "Purchase", "Assembly", and "Usage" as cost_type)
            "purchase_cost_ex_gst": get_cost_value(cost_data, "Purchase", "ex_gst"),
            "purchase_cost_inc_gst": get_cost_value(cost_data, "Purchase", "inc_gst"),
            "purchase_tax_included": get_cost_value(
                cost_data, "Purchase", "tax_included"
            ),
            "usage_cost_ex_gst": get_cost_value(cost_data, "Usage", "ex_gst"),
            "usage_cost_inc_gst": get_cost_value(cost_data, "Usage", "inc_gst"),
            "usage_tax_included": get_cost_value(cost_data, "Usage", "tax_included"),
            "manufactured_cost_ex_gst": get_cost_value(
                cost_data, "Manufactured Cost", "ex_gst"
            ),
            "manufactured_cost_inc_gst": get_cost_value(
                cost_data, "Manufactured Cost", "inc_gst"
            ),
            # Note: Assembly cost is not stored directly in product model - it's calculated from formulas
            # Raw Material specific fields
            "purchase_unit_id": purchase_unit_id if purchase_unit_id else None,
            "purchase_quantity": (
                float(purchase_quantity)
                if purchase_quantity is not None
                and str(purchase_quantity).strip()
                and str(purchase_quantity).strip() != ""
                else None
            ),
            # Note: purchase_cost is not stored directly - it's calculated from purchase_cost_ex_gst/inc_gst in cost table
            "usage_unit": usage_unit if usage_unit else None,
            "usage_quantity": (
                float(usage_quantity)
                if usage_quantity is not None
                and str(usage_quantity).strip()
                and str(usage_quantity).strip() != ""
                else None
            ),
            "restock_level": None,  # Not in form, always None
            # formula_id and formula_revision removed - deprecated fields (use Assembly section instead)
        }

        try:
            # Validate product_id - handle empty string case
            product_id_clean = (
                product_id.strip()
                if product_id and isinstance(product_id, str)
                else None
            )

            if product_id_clean:
                # Update existing product
                response = make_api_request(
                    "PUT", f"/products/{product_id_clean}", product_data
                )
                success_msg = f"Product {sku} updated successfully"
            else:
                # Create new product
                response = make_api_request("POST", "/products/", product_data)
                success_msg = f"Product {sku} created successfully"

            if "error" in response:
                error_msg = response["error"]
                if isinstance(error_msg, str):
                    try:
                        import json

                        error_obj = json.loads(error_msg)
                        if "message" in error_obj:
                            error_msg = error_obj["message"]
                    except (KeyError, ValueError, TypeError):
                        pass
                # On error, don't refresh table (operation failed)
                return (
                    True,
                    True,
                    "Error",
                    error_msg,
                    "",
                    product_id_clean or "",
                    no_update,
                )

            # Extract product_id from response (for new products, it's in the response)
            saved_product_id = product_id_clean
            if not saved_product_id and isinstance(response, dict):
                saved_product_id = response.get("id") or response.get("product_id")
            if saved_product_id:
                saved_product_id = str(saved_product_id)
            else:
                saved_product_id = product_id_clean or ""

            # Reload assemblies table after saving product
            assemblies_data = []
            if saved_product_id:
                try:
                    formulas_response = make_api_request(
                        "GET", f"/formulas/?product_id={saved_product_id}"
                    )
                    if isinstance(formulas_response, list):
                        # Get parent product density for L calculations
                        parent_density = 0.0
                        try:
                            parent_resp = make_api_request(
                                "GET", f"/products/{saved_product_id}"
                            )
                            if (
                                isinstance(parent_resp, dict)
                                and "error" not in parent_resp
                            ):
                                parent_density = float(
                                    parent_resp.get("density_kg_per_l", 0) or 0
                                )
                        except Exception:
                            pass

                        for formula in formulas_response:
                            lines_list = formula.get("lines", [])
                            if not isinstance(lines_list, list):
                                lines_list = []
                            lines_count = len(lines_list)

                            # Calculate total cost and quantities from lines
                            total_cost = 0.0
                            total_quantity_kg = 0.0
                            for line in lines_list:
                                if isinstance(line, dict):
                                    qty_kg = float(line.get("quantity_kg", 0.0) or 0.0)
                                    unit_cost = line.get("unit_cost") or 0.0
                                    if not unit_cost:
                                        product_id_line = line.get("raw_material_id")
                                        if product_id_line:
                                            try:
                                                prod_resp = make_api_request(
                                                    "GET",
                                                    f"/products/{product_id_line}",
                                                )
                                                if (
                                                    isinstance(prod_resp, dict)
                                                    and "error" not in prod_resp
                                                ):
                                                    # Preserve 4 decimal places
                                                    cost_val = (
                                                        prod_resp.get(
                                                            "usage_cost_ex_gst"
                                                        )
                                                        or prod_resp.get(
                                                            "purchase_cost_ex_gst"
                                                        )
                                                        or 0
                                                    )
                                                    if cost_val:
                                                        try:
                                                            unit_cost = round(
                                                                float(cost_val), 4
                                                            )
                                                        except (ValueError, TypeError):
                                                            unit_cost = 0.0
                                                    else:
                                                        unit_cost = 0.0
                                            except (ValueError, KeyError, TypeError):
                                                pass
                                    total_cost += (
                                        qty_kg * float(unit_cost) if unit_cost else 0.0
                                    )
                                    total_quantity_kg += qty_kg

                            # Calculate quantity in liters if density available
                            total_quantity_l = (
                                total_quantity_kg / parent_density
                                if parent_density > 0
                                else 0.0
                            )

                            # Calculate cost per kg and cost per L
                            cost_per_kg = (
                                total_cost / total_quantity_kg
                                if total_quantity_kg > 0
                                else 0.0
                            )
                            cost_per_l = (
                                total_cost / total_quantity_l
                                if total_quantity_l > 0
                                else 0.0
                            )

                            # Get yield_factor from formula
                            yield_factor = formula.get("yield_factor", 1.0)
                            if yield_factor is None:
                                yield_factor = 1.0
                            try:
                                yield_factor = float(yield_factor)
                            except (ValueError, TypeError):
                                yield_factor = 1.0

                            assemblies_data.append(
                                {
                                    "formula_id": str(formula.get("id", "")),
                                    "version": int(formula.get("version", 1)),
                                    "formula_code": str(
                                        formula.get("formula_code", "")
                                    ),
                                    "formula_name": str(
                                        formula.get("formula_name", "")
                                    ),
                                    "yield_factor": round(yield_factor, 2),
                                    "is_primary": "✓"
                                    if formula.get("is_active")
                                    else "",
                                    "cost": f"${total_cost:.2f}"
                                    if total_cost > 0
                                    else "-",
                                    "cost_per_kg": round(cost_per_kg, 4),
                                    "cost_per_l": round(cost_per_l, 4),
                                    "lines_count": int(lines_count),
                                }
                            )
                except Exception as e:
                    print(f"Error loading assemblies after save: {e}")

            # Trigger table refresh by updating refresh trigger
            import time

            refresh_timestamp = str(time.time())
            return (
                False,
                True,
                "Success",
                success_msg,
                refresh_timestamp,
                saved_product_id,
                assemblies_data,
            )

        except Exception as e:
            # On error, don't refresh table (operation failed)
            return (
                True,
                True,
                "Error",
                f"Failed to save product: {str(e)}",
                "",
                product_id_clean or "",
                no_update,
            )

    # Update delete modal with product name
    @app.callback(
        [
            Output("delete-product-name", "children"),
            Output("delete-confirm-modal", "is_open"),
        ],
        [
            Input("delete-product-btn", "n_clicks"),
            Input("delete-confirm-btn", "n_clicks"),
            Input("delete-cancel-btn", "n_clicks"),
        ],
        [State("products-table", "selected_rows"), State("products-table", "data")],
        prevent_initial_call=True,
    )
    def toggle_delete_modal(
        delete_clicks, confirm_clicks, cancel_clicks, selected_rows, data
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return "", False

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "delete-product-btn" and selected_rows and data:
            product = data[selected_rows[0]]
            product_name = f"{product.get('sku')} - {product.get('name')}"
            return product_name, True
        elif button_id == "delete-cancel-btn":
            return "", False
        elif button_id == "delete-confirm-btn":
            return "", False

        return "", False

    # Actual delete
    @app.callback(
        [
            Output("products-refresh-trigger", "children", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
        ],
        [Input("delete-confirm-btn", "n_clicks")],
        [State("products-table", "selected_rows"), State("products-table", "data")],
        prevent_initial_call=True,
    )
    def delete_product(n_clicks, selected_rows, data):
        if not n_clicks or not selected_rows or not data:
            raise PreventUpdate

        product = data[selected_rows[0]]
        product_id = product.get("id")
        sku = product.get("sku")

        try:
            make_api_request("DELETE", f"/products/{product_id}")

            # Trigger table refresh by updating refresh trigger
            import time

            refresh_timestamp = str(time.time())
            return (
                refresh_timestamp,
                True,
                "Success",
                f"Product {sku} deleted successfully",
            )

        except Exception as e:
            import time

            refresh_timestamp = str(time.time())
            return (
                refresh_timestamp,
                True,
                "Error",
                f"Failed to delete product: {str(e)}",
            )

    # Auto-calculate excise and GST for pricing table
    @app.callback(
        Output("product-pricing-table", "data", allow_duplicate=True),
        [
            Input("product-pricing-table", "data"),
            Input("product-abv", "value"),
            Input("product-density", "value"),
            Input("product-size", "value"),
            Input("product-base-unit", "value"),
        ],
        prevent_initial_call=True,
    )
    def calculate_pricing_table(pricing_data, abv, density, size, base_unit):
        """Auto-calculate excise and GST when pricing values change."""
        if not pricing_data:
            raise PreventUpdate

        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        # Get current excise rate
        try:
            excise_response = make_api_request("GET", "/excise-rates/current")
            excise_rate_per_l_abv = (
                float(excise_response.get("rate_per_l_abv", 0))
                if isinstance(excise_response, dict)
                else 0.0
            )
        except Exception as e:
            print(f"Error fetching excise rate: {e}")
            excise_rate_per_l_abv = 0.0

        # GST rate (10% in Australia)
        GST_RATE = 0.10

        # Calculate volume in liters from basic information
        volume_liters = 1.0  # Default to 1 liter per unit
        try:
            if size:
                # Try to parse size as a number (assume it's in liters or convert)
                size_val = float(size)
                base_unit_upper = base_unit.upper() if base_unit else ""

                # If base_unit is L/LT, size is already in liters
                if base_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    volume_liters = size_val
                elif base_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                    # Convert from mL to liters (divide by 1000)
                    volume_liters = size_val / 1000.0
                elif base_unit_upper in ["KG", "KILOGRAM"]:
                    # Convert from kg to liters using density
                    if density:
                        density_val = float(density)
                        if density_val > 0:
                            volume_liters = size_val / density_val
                        else:
                            volume_liters = size_val  # Fallback
                    else:
                        volume_liters = size_val  # Fallback
                elif base_unit_upper in ["G", "GRAM", "GRAMS"]:
                    # Convert from grams to liters using density
                    if density:
                        density_val = float(density)
                        if density_val > 0:
                            # Convert g -> kg -> L
                            volume_liters = (size_val / 1000.0) / density_val
                        else:
                            # Fallback: assume 1 g = 1 mL = 0.001 L
                            volume_liters = size_val / 1000.0
                    else:
                        # Fallback: assume 1 g = 1 mL = 0.001 L
                        volume_liters = size_val / 1000.0
                else:
                    # Assume size is already in liters if no conversion info
                    volume_liters = size_val
            elif base_unit:
                base_unit_upper = base_unit.upper()
                if base_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    # No size specified, but base_unit is L, so 1 liter per unit
                    volume_liters = 1.0
                elif base_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                    # No size specified, but base_unit is mL, so 0.001 liters per unit
                    volume_liters = 0.001
                elif base_unit_upper in ["KG", "KILOGRAM"]:
                    # No size specified, but base_unit is KG, convert 1 kg to liters
                    if density:
                        density_val = float(density)
                        if density_val > 0:
                            volume_liters = 1.0 / density_val
                        else:
                            volume_liters = 1.0
                    else:
                        volume_liters = 1.0
                elif base_unit_upper in ["G", "GRAM", "GRAMS"]:
                    # No size specified, but base_unit is G, convert 1 g to liters
                    if density:
                        density_val = float(density)
                        if density_val > 0:
                            # 1 g = 0.001 kg -> L
                            volume_liters = 0.001 / density_val
                        else:
                            # Fallback: 1 g = 1 mL = 0.001 L
                            volume_liters = 0.001
                    else:
                        volume_liters = 0.001
        except (ValueError, TypeError):
            volume_liters = 1.0  # Default fallback

        # Calculate excise and GST for each price level
        updated_data = []
        for row in pricing_data:
            price_level = row.get("price_level", "")
            inc_gst = row.get("inc_gst")
            ex_gst = row.get("ex_gst")

            # If inc_gst is provided, calculate ex_gst
            if inc_gst is not None and inc_gst != "":
                try:
                    inc_gst_val = float(inc_gst)
                    # Calculate ex_gst (remove GST)
                    ex_gst_val = inc_gst_val / (1 + GST_RATE)
                except (ValueError, TypeError):
                    ex_gst_val = None
            # If ex_gst is provided, calculate inc_gst
            elif ex_gst is not None and ex_gst != "":
                try:
                    ex_gst_val = float(ex_gst)
                    # Calculate inc_gst (add GST)
                    inc_gst_val = ex_gst_val * (1 + GST_RATE)
                except (ValueError, TypeError):
                    inc_gst_val = None
                    ex_gst_val = None
            else:
                inc_gst_val = None
                ex_gst_val = None

            # Calculate excise based on ABV * volume from basic information
            excise_val = None
            if abv:
                try:
                    abv_val = float(abv)
                    # Excise = volume_in_liters * (ABV/100) * excise_rate_per_l_abv
                    abv_liters = volume_liters * (abv_val / 100.0)
                    excise_val = abv_liters * excise_rate_per_l_abv
                except (ValueError, TypeError):
                    excise_val = None

            # Preserve COGS columns
            updated_data.append(
                {
                    "price_level": price_level,
                    "inc_gst": (
                        round(inc_gst_val, 2) if inc_gst_val is not None else None
                    ),
                    "ex_gst": round(ex_gst_val, 2) if ex_gst_val is not None else None,
                    "excise": round(excise_val, 2) if excise_val is not None else None,
                    "inc_gst_cogs": row.get("inc_gst_cogs"),  # Preserve COGS
                    "inc_excise_cogs": row.get("inc_excise_cogs"),  # Preserve COGS
                }
            )

        return updated_data

    # Auto-calculate GST for cost table
    @app.callback(
        Output("product-cost-table", "data", allow_duplicate=True),
        [
            Input("product-cost-table", "data"),
            Input("product-purchase-unit-dropdown", "value"),
            Input("product-purchase-quantity", "value"),
            Input("product-purchase-cost-ex-gst", "value"),
            Input("product-purchase-cost-inc-gst", "value"),
            Input("product-usage-unit-dropdown", "value"),
            Input("product-usage-quantity", "value"),
            Input("product-density", "value"),
        ],
        prevent_initial_call=True,
    )
    def calculate_cost_table(
        cost_data,
        purchase_unit_id,
        purchase_quantity,
        purchase_cost_ex_gst,
        purchase_cost_inc_gst,
        usage_unit,
        usage_quantity,
        density,
    ):
        """Auto-calculate GST when cost values change and propagate to cost table. Allow values to be cleared."""
        if not cost_data:
            raise PreventUpdate

        # Check if this was triggered by active_cell (tax_included click)
        # If so, don't recalculate to preserve the tax_included toggle
        ctx = dash.callback_context
        if ctx.triggered:
            triggered_id = ctx.triggered[0]["prop_id"]
            if triggered_id == "product-cost-table.data":
                # This was triggered by a data change, which might be from active_cell click
                # Check if we should preserve tax_included changes
                # We'll preserve tax_included_bool and tax_included display values
                pass  # Continue with calculation but preserve tax_included values

        GST_RATE = 0.10

        # Get purchase unit code if purchase_unit_id is provided
        purchase_unit_code = None
        if purchase_unit_id:
            try:
                units_response = make_api_request("GET", "/units/?is_active=true")
                units = units_response if isinstance(units_response, list) else []
                for unit in units:
                    if str(unit.get("id")) == str(purchase_unit_id):
                        purchase_unit_code = unit.get("code", "").upper()
                        break
            except Exception:
                pass

        # Convert purchase and usage quantities to floats
        purchase_qty = None
        if purchase_quantity and str(purchase_quantity).strip():
            try:
                purchase_qty = float(purchase_quantity)
            except (ValueError, TypeError):
                pass

        # Get purchase cost per unit - prefer ex_gst if available, otherwise calculate from inc_gst
        if purchase_cost_ex_gst and str(purchase_cost_ex_gst).strip():
            try:
                float(purchase_cost_ex_gst)
            except (ValueError, TypeError):
                pass
        elif purchase_cost_inc_gst and str(purchase_cost_inc_gst).strip():
            try:
                # Calculate ex_gst from inc_gst
                inc_gst_float = float(purchase_cost_inc_gst)
                inc_gst_float / (1 + GST_RATE)
            except (ValueError, TypeError):
                pass

        usage_qty = None
        if usage_quantity and str(usage_quantity).strip():
            try:
                usage_qty = float(usage_quantity)
            except (ValueError, TypeError):
                pass

        usage_unit_upper = str(usage_unit).upper() if usage_unit else None

        updated_data = []
        for row in cost_data:
            cost_type = row.get("cost_type", "")
            ex_gst = row.get("ex_gst")
            inc_gst = row.get("inc_gst")
            # Handle tax_included - can be bool, string, or markdown format
            tax_included_raw = row.get("tax_included")
            tax_included_bool = row.get("tax_included_bool", False)
            # If tax_included_bool exists, use it; otherwise try to parse from tax_included
            if tax_included_bool is not None:
                tax_included = tax_included_bool
            elif isinstance(tax_included_raw, bool):
                tax_included = tax_included_raw
            elif isinstance(tax_included_raw, str):
                tax_included = tax_included_raw == "✓" or tax_included_raw.lower() in (
                    "true",
                    "1",
                    "yes",
                    "y",
                )
            else:
                tax_included = False
            row.get("qty")
            unit = row.get("unit")

            # Helper to check if value is empty/None
            def is_empty(val):
                return (
                    val is None
                    or val == ""
                    or val == "None"
                    or (isinstance(val, str) and val.strip() == "")
                )

            # Helper to convert to float safely
            def to_float(val):
                try:
                    if is_empty(val):
                        return None
                    return float(val)
                except (ValueError, TypeError):
                    return None

            ex_gst_float = to_float(ex_gst)
            inc_gst_float = to_float(inc_gst)

            # Calculate missing value based on tax_included flag - only if one has value
            if cost_type == "Manufactured Cost":
                # Manufactured cost doesn't have tax_included option
                if (
                    not is_empty(inc_gst)
                    and inc_gst_float is not None
                    and is_empty(ex_gst)
                ):
                    # Calculate ex_gst from inc_gst
                    ex_gst_val = inc_gst_float / (1 + GST_RATE)
                    inc_gst_val = inc_gst_float
                elif (
                    not is_empty(ex_gst)
                    and ex_gst_float is not None
                    and is_empty(inc_gst)
                ):
                    # Calculate inc_gst from ex_gst
                    ex_gst_val = ex_gst_float
                    inc_gst_val = ex_gst_float * (1 + GST_RATE)
                else:
                    # Both empty or both have values - preserve user input
                    ex_gst_val = ex_gst_float
                    inc_gst_val = inc_gst_float

                updated_data.append(
                    {
                        "cost_type": cost_type,
                        "qty": None,
                        "unit": None,
                        "ex_gst": (
                            round(ex_gst_val, 4) if ex_gst_val is not None else None
                        ),
                        "inc_gst": (
                            round(inc_gst_val, 4) if inc_gst_val is not None else None
                        ),
                        "tax_included": "N/A",
                        "tax_included_bool": False,
                        "action": row.get("action", ""),  # Preserve action field
                    }
                )
            else:
                # Purchase/Usage cost - use tax_included flag
                if (
                    tax_included
                    and not is_empty(inc_gst)
                    and inc_gst_float is not None
                    and is_empty(ex_gst)
                ):
                    # Price includes tax, calculate ex_gst
                    ex_gst_val = inc_gst_float / (1 + GST_RATE)
                    inc_gst_val = inc_gst_float
                elif (
                    not tax_included
                    and not is_empty(ex_gst)
                    and ex_gst_float is not None
                    and is_empty(inc_gst)
                ):
                    # Price excludes tax, calculate inc_gst
                    ex_gst_val = ex_gst_float
                    inc_gst_val = ex_gst_float * (1 + GST_RATE)
                elif (
                    not is_empty(inc_gst)
                    and inc_gst_float is not None
                    and is_empty(ex_gst)
                ):
                    # Default: assume includes tax if only inc_gst provided
                    ex_gst_val = inc_gst_float / (1 + GST_RATE)
                    inc_gst_val = inc_gst_float
                    tax_included = True
                elif (
                    not is_empty(ex_gst)
                    and ex_gst_float is not None
                    and is_empty(inc_gst)
                ):
                    # Default: assume excludes tax if only ex_gst provided
                    ex_gst_val = ex_gst_float
                    inc_gst_val = ex_gst_float * (1 + GST_RATE)
                    tax_included = False
                else:
                    # Both empty or both have values - preserve user input
                    ex_gst_val = ex_gst_float
                    inc_gst_val = inc_gst_float

                # Preserve is_primary flags and tax_included flags from existing data
                existing_row = None
                for existing in cost_data:
                    if existing.get("cost_type") == cost_type:
                        existing_row = existing
                        break
                is_primary_bool = (
                    existing_row.get("is_primary_bool", False)
                    if existing_row
                    else False
                )
                is_primary_display = (
                    existing_row.get("is_primary", "[Set Primary]")
                    if existing_row
                    else "[Set Primary]"
                )

                # IMPORTANT: Preserve tax_included_bool from existing row - don't recalculate it
                # The user may have manually toggled it via the click handler
                preserved_tax_included_bool = (
                    existing_row.get("tax_included_bool", False)
                    if existing_row
                    else tax_included
                )
                preserved_tax_included = preserved_tax_included_bool

                # Update inc_gst based on preserved tax_included flag
                # If tax_included is True, ensure inc_gst is calculated from ex_gst
                # If tax_included is False, clear inc_gst
                if preserved_tax_included and ex_gst_val is not None:
                    inc_gst_val = round(ex_gst_val * (1 + GST_RATE), 4)
                elif not preserved_tax_included:
                    inc_gst_val = None

                # Auto-populate purchase row with purchase info
                if cost_type == "Purchase":
                    # Use preserved tax_included_bool (from manual toggle or existing value)
                    # Only update it if user entered a new value in form fields
                    existing_tax_included_bool = preserved_tax_included_bool

                    # Form fields now contain per-unit costs directly
                    # Update cost table from form fields when they are provided
                    # If user enters ex_gst, tax is excluded. If user enters inc_gst, tax is included.
                    # Check if form fields were actually changed (not just callback triggered by data change)
                    ctx = dash.callback_context
                    form_field_changed = False
                    if ctx.triggered:
                        for trigger in ctx.triggered:
                            trigger_id = trigger["prop_id"].split(".")[0]
                            if trigger_id in [
                                "product-purchase-cost-ex-gst",
                                "product-purchase-cost-inc-gst",
                            ]:
                                form_field_changed = True
                                break

                    if form_field_changed:
                        if (
                            purchase_cost_ex_gst is not None
                            and str(purchase_cost_ex_gst).strip()
                        ):
                            try:
                                # User entered ex GST per unit - tax is excluded
                                ex_gst_per_unit = float(purchase_cost_ex_gst)
                                ex_gst_val = round(ex_gst_per_unit, 4)
                                inc_gst_val = round(ex_gst_per_unit * (1 + GST_RATE), 4)
                                existing_tax_included_bool = (
                                    False  # Tax excluded when user enters ex_gst
                                )
                            except (ValueError, TypeError):
                                pass
                        elif (
                            purchase_cost_inc_gst is not None
                            and str(purchase_cost_inc_gst).strip()
                        ):
                            try:
                                # User entered inc GST per unit - tax is included
                                inc_gst_per_unit = float(purchase_cost_inc_gst)
                                ex_gst_val = round(inc_gst_per_unit / (1 + GST_RATE), 4)
                                inc_gst_val = round(inc_gst_per_unit, 4)
                                existing_tax_included_bool = (
                                    True  # Tax included when user enters inc_gst
                                )
                            except (ValueError, TypeError):
                                pass

                    tax_included_display = "✓" if existing_tax_included_bool else "✗"

                    # Only set inc_gst if tax_included is True
                    # If tax_included is False, inc_gst should be None (not used in calculations)
                    final_inc_gst = None
                    if existing_tax_included_bool and inc_gst_val is not None:
                        final_inc_gst = round(inc_gst_val, 4)

                    updated_data.append(
                        {
                            "cost_type": "Purchase",
                            "is_primary": is_primary_display,
                            "is_primary_bool": is_primary_bool,
                            "qty": purchase_qty,
                            "unit": purchase_unit_code,
                            "ex_gst": (
                                round(ex_gst_val, 4) if ex_gst_val is not None else None
                            ),
                            "inc_gst": final_inc_gst,
                            "tax_included": tax_included_display,
                            "tax_included_bool": existing_tax_included_bool,
                            "action": existing_row.get("action", "")
                            if existing_row
                            else "",  # Preserve action field
                        }
                    )
                elif cost_type == "Assembly":
                    # Assembly row - keep existing values or update from assembly summary if available
                    # Note: Assembly data should be updated from assembly-summary-table via separate callback
                    # Use preserved tax_included_bool (from manual toggle or existing value)
                    existing_tax_included_bool = preserved_tax_included_bool
                    tax_included_display = "✓" if existing_tax_included_bool else "✗"

                    # Only set inc_gst if tax_included is True
                    # If tax_included is False, inc_gst should be None (not used in calculations)
                    final_inc_gst = None
                    if existing_tax_included_bool and inc_gst_val is not None:
                        final_inc_gst = round(inc_gst_val, 4)

                    # Preserve total_cost and action from existing row for Assembly
                    existing_total_cost = (
                        existing_row.get("total_cost") if existing_row else None
                    )
                    existing_action = (
                        existing_row.get("action", "") if existing_row else ""
                    )

                    updated_data.append(
                        {
                            "cost_type": "Assembly",
                            "is_primary": is_primary_display,
                            "is_primary_bool": is_primary_bool,
                            "qty": existing_row.get("qty") if existing_row else None,
                            "unit": existing_row.get("unit") if existing_row else "kg",
                            "ex_gst": (
                                round(ex_gst_val, 4) if ex_gst_val is not None else None
                            ),
                            "inc_gst": final_inc_gst,
                            "tax_included": tax_included_display,
                            "tax_included_bool": existing_tax_included_bool,
                            "total_cost": existing_total_cost,  # Preserve total_cost for action button
                            "action": existing_action,  # Preserve action field
                        }
                    )
                elif cost_type == "Usage":
                    # Use preserved tax_included_bool (from manual toggle or existing value)
                    existing_tax_included_bool = preserved_tax_included_bool
                    tax_included_display = "✓" if existing_tax_included_bool else "✗"

                    # Only set inc_gst if tax_included is True
                    # If tax_included is False, inc_gst should be None (not used in calculations)
                    final_inc_gst = None
                    if existing_tax_included_bool and inc_gst_val is not None:
                        final_inc_gst = round(inc_gst_val, 4)

                    updated_data.append(
                        {
                            "cost_type": "Usage",
                            "is_primary": "",
                            "is_primary_bool": False,
                            "qty": usage_qty,
                            "unit": usage_unit_upper,
                            "ex_gst": (
                                round(ex_gst_val, 4) if ex_gst_val is not None else None
                            ),
                            "inc_gst": final_inc_gst,
                            "tax_included": tax_included_display,
                            "tax_included_bool": existing_tax_included_bool,
                            "action": existing_row.get("action", "")
                            if existing_row
                            else "",  # Preserve action field
                        }
                    )
                else:
                    # Manufactured Cost or other
                    updated_data.append(
                        {
                            "cost_type": cost_type,
                            "is_primary": "",
                            "is_primary_bool": False,
                            "qty": None,
                            "unit": None,
                            "ex_gst": (
                                round(ex_gst_val, 4) if ex_gst_val is not None else None
                            ),
                            "inc_gst": (
                                round(inc_gst_val, 4)
                                if inc_gst_val is not None
                                else None
                            ),
                            "action": row.get("action", ""),  # Preserve action field
                            "tax_included": "N/A",
                            "tax_included_bool": False,
                        }
                    )

        # Find which cost source is primary (Purchase, Assembly, or Usage)
        primary_cost_row = None
        primary_cost_type = None
        for row in updated_data:
            if row.get("is_primary_bool", False) and row.get("cost_type") in [
                "Purchase",
                "Assembly",
                "Usage",
            ]:
                primary_cost_row = row
                primary_cost_type = row.get("cost_type")
                break

        # If no primary is set, default to Purchase if available, otherwise Usage, otherwise Assembly
        if not primary_cost_row:
            for row in updated_data:
                if row.get("cost_type") == "Purchase" and row.get("ex_gst") is not None:
                    primary_cost_row = row
                    primary_cost_type = "Purchase"
                    row["is_primary"] = "✓"
                    row["is_primary_bool"] = True
                    break
            # If no Purchase, try Usage
            if not primary_cost_row:
                for row in updated_data:
                    if (
                        row.get("cost_type") == "Usage"
                        and row.get("ex_gst") is not None
                    ):
                        primary_cost_row = row
                        primary_cost_type = "Usage"
                        row["is_primary"] = "✓"
                        row["is_primary_bool"] = True
                        break
            # If no Purchase or Usage, try Assembly
            if not primary_cost_row:
                for row in updated_data:
                    if (
                        row.get("cost_type") == "Assembly"
                        and row.get("ex_gst") is not None
                    ):
                        primary_cost_row = row
                        primary_cost_type = "Assembly"
                        row["is_primary"] = "✓"
                        row["is_primary_bool"] = True
                        break

        # Calculate usage cost from primary cost source (only if primary is Purchase or Assembly)
        # Run conversion even if usage_qty is 0/empty - conversion is about unit conversion, not quantity
        if (
            primary_cost_row
            and primary_cost_type
            and primary_cost_type in ["Purchase", "Assembly"]
            and usage_unit_upper
        ):
            try:
                # Find usage cost row
                usage_cost_row = None
                for row in updated_data:
                    if row.get("cost_type") == "Usage":
                        usage_cost_row = row
                        break

                if usage_cost_row:
                    # Get primary cost values
                    primary_ex_gst = primary_cost_row.get("ex_gst")
                    primary_unit = primary_cost_row.get("unit", "").upper()
                    primary_cost_row.get("qty")

                    if primary_ex_gst is not None and primary_unit:
                        # Helper function to get conversion factor (kg equivalent of 1 unit)
                        def get_unit_to_kg_factor(unit_code, density_val=None):
                            """Get the kg equivalent of 1 unit."""
                            unit = unit_code.upper()

                            # Mass units
                            MASS_TO_KG = {
                                "MG": 0.000001,
                                "G": 0.001,
                                "KG": 1.0,
                                "TON": 1000.0,
                            }

                            # Volume units
                            VOLUME_TO_L = {
                                "ML": 0.001,
                                "L": 1.0,
                                "LT": 1.0,
                                "LTR": 1.0,
                                "LITER": 1.0,
                                "LITRE": 1.0,
                            }

                            if unit in MASS_TO_KG:
                                return MASS_TO_KG[unit]
                            elif unit in VOLUME_TO_L:
                                if density_val and density_val > 0:
                                    return VOLUME_TO_L[unit] * float(density_val)
                                else:
                                    return None
                            return None

                        # Calculate usage cost: convert from primary unit to usage unit
                        density_val = (
                            float(density) if density and density != "" else None
                        )
                        usage_unit_factor = get_unit_to_kg_factor(
                            usage_unit_upper, density_val
                        )
                        primary_unit_factor = get_unit_to_kg_factor(
                            primary_unit, density_val
                        )

                        if (
                            usage_unit_factor is not None
                            and primary_unit_factor is not None
                            and primary_unit_factor > 0
                        ):
                            # Formula: (use_unit/primary_unit) × primary_cost_per_unit = use_cost_per_unit
                            unit_ratio = usage_unit_factor / primary_unit_factor
                            converted_usage_cost = unit_ratio * primary_ex_gst

                            if converted_usage_cost is not None:
                                # Always update usage cost row with converted value when fields change
                                # Round to 4 decimal places for small values
                                # The converted_usage_cost is ex-GST (derived from primary ex_gst)
                                usage_cost_row["ex_gst"] = round(
                                    converted_usage_cost, 4
                                )
                                # Only calculate inc_gst if tax_included is True
                                # If tax_included is False, clear inc_gst (it's not used in calculations)
                                tax_included_bool = usage_cost_row.get(
                                    "tax_included_bool", False
                                )
                                if tax_included_bool:
                                    usage_cost_row["inc_gst"] = round(
                                        converted_usage_cost * (1 + GST_RATE), 4
                                    )
                                else:
                                    usage_cost_row["inc_gst"] = None
            except Exception as e:
                print(f"Error converting primary cost to usage cost: {e}")
                # Continue with original data if conversion fails

        return updated_data

    # Handle primary button and tax included button clicks in cost table
    @app.callback(
        Output("product-cost-table", "data", allow_duplicate=True),
        [Input("product-cost-table", "active_cell")],
        [
            State("product-cost-table", "data"),
            State("product-usage-unit-dropdown", "value"),
            State("product-usage-quantity", "value"),
            State("product-density", "value"),
        ],
        prevent_initial_call=True,
    )
    def handle_cost_table_clicks(
        active_cell, cost_data, usage_unit, usage_quantity, density
    ):
        """Handle clicks on primary or tax included columns in cost table."""
        if not active_cell or not cost_data:
            raise PreventUpdate

        col_id = active_cell.get("column_id")
        row_idx = active_cell.get("row")

        if row_idx is None:
            raise PreventUpdate

        clicked_row = cost_data[row_idx]
        clicked_cost_type = clicked_row.get("cost_type")

        # Handle tax_included column clicks
        if col_id == "tax_included":
            # Don't allow toggling for Manufactured Cost
            if clicked_cost_type == "Manufactured Cost":
                raise PreventUpdate

            # Toggle tax_included for the clicked row
            updated_data = []
            GST_RATE = 0.10
            for idx, row in enumerate(cost_data):
                if idx == row_idx:
                    # Toggle the clicked row
                    current_tax_included = row.get("tax_included_bool", False)
                    new_tax_included = not current_tax_included

                    # Get ex_gst value to calculate inc_gst if needed
                    ex_gst = row.get("ex_gst")
                    ex_gst_float = None
                    if ex_gst is not None and str(ex_gst).strip():
                        try:
                            ex_gst_float = float(ex_gst)
                        except (ValueError, TypeError):
                            pass

                    # Update inc_gst based on tax_included flag
                    # If tax_included is True, calculate inc_gst from ex_gst
                    # If tax_included is False, clear inc_gst (set to None)
                    if new_tax_included:
                        # Tax included - calculate inc_gst from ex_gst
                        if ex_gst_float is not None:
                            inc_gst_val = round(ex_gst_float * (1 + GST_RATE), 4)
                        else:
                            inc_gst_val = None
                        tax_included_display = "✓"
                    else:
                        # Tax excluded - clear inc_gst
                        inc_gst_val = None
                        tax_included_display = "✗"

                    updated_row = {
                        **row,
                        "tax_included": tax_included_display,
                        "tax_included_bool": new_tax_included,
                        "inc_gst": inc_gst_val,
                        "action": row.get("action", ""),  # Preserve action field
                    }
                    updated_data.append(updated_row)
                else:
                    # Keep other rows unchanged - ensure action field exists
                    row_with_action = {
                        **row,
                        "action": row.get("action", ""),
                    }
                    updated_data.append(row_with_action)
            return updated_data

        # Handle action column clicks - copy assembly total cost to usage cost
        elif col_id == "action":
            # Only handle if clicking on Assembly row
            if clicked_cost_type == "Assembly":
                # Get the total cost from Assembly row
                assembly_total_cost = clicked_row.get("total_cost")
                if assembly_total_cost is None or assembly_total_cost == 0:
                    raise PreventUpdate  # No total cost to copy

                # Copy total cost to Usage row as ex_gst and calculate inc_gst
                GST_RATE = 0.10
                updated_data = []
                for idx, row in enumerate(cost_data):
                    if row.get("cost_type") == "Usage":
                        # Copy total cost to usage cost
                        updated_row = {
                            **row,
                            "ex_gst": round(float(assembly_total_cost), 4),
                            "inc_gst": round(
                                float(assembly_total_cost) * (1 + GST_RATE), 4
                            ),
                            "tax_included": "✗",  # Default to excluded
                            "tax_included_bool": False,
                            "action": row.get("action", ""),  # Preserve action field
                        }
                        updated_data.append(updated_row)
                    else:
                        # Ensure action field exists in all rows
                        row_with_action = {
                            **row,
                            "action": row.get("action", ""),
                        }
                        updated_data.append(row_with_action)
                return updated_data
            else:
                raise PreventUpdate

        # Handle is_primary column clicks
        elif col_id == "is_primary":
            # Allow Purchase, Assembly, or Usage to be primary (not Manufactured Cost)
            if clicked_cost_type not in ["Purchase", "Assembly", "Usage"]:
                raise PreventUpdate

            # Update all rows - set primary to False for Purchase/Assembly/Usage, then set selected one to True
            updated_data = []
            for idx, row in enumerate(cost_data):
                cost_type = row.get("cost_type")
                if cost_type in ["Purchase", "Assembly", "Usage"]:
                    is_primary = idx == row_idx
                    updated_row = {
                        **row,
                        "is_primary": "✓" if is_primary else "[Set Primary]",
                        "is_primary_bool": is_primary,
                        "action": row.get("action", ""),  # Preserve action field
                    }
                else:
                    # Manufactured Cost rows don't have primary buttons
                    updated_row = {
                        **row,
                        "is_primary": "",
                        "is_primary_bool": False,
                        "action": row.get("action", ""),  # Preserve action field
                    }
                updated_data.append(updated_row)

            # Recalculate usage cost from the new primary source (if primary is Purchase or Assembly)
            # Find the primary cost row
            primary_cost_row = None
            for row in updated_data:
                if row.get("is_primary_bool", False) and row.get("cost_type") in [
                    "Purchase",
                    "Assembly",
                    "Usage",
                ]:
                    primary_cost_row = row
                    break

            # Recalculate usage cost if primary changed and usage data is available
            # Only recalculate if primary is Purchase or Assembly (not Usage)
            if (
                primary_cost_row
                and primary_cost_row.get("cost_type") in ["Purchase", "Assembly"]
                and usage_unit
                and usage_quantity
            ):
                try:
                    usage_unit_upper = str(usage_unit).upper()
                    try:
                        usage_qty = float(usage_quantity) if usage_quantity else None
                    except (ValueError, TypeError):
                        usage_qty = None

                    if usage_qty and usage_qty > 0:
                        # Find usage row
                        usage_row = None
                        for row in updated_data:
                            if row.get("cost_type") == "Usage":
                                usage_row = row
                                break

                        if usage_row:
                            # Get primary cost values
                            primary_ex_gst = primary_cost_row.get("ex_gst")
                            primary_unit = primary_cost_row.get("unit", "").upper()

                            if primary_ex_gst is not None and primary_unit:
                                # Helper function to get conversion factor
                                def get_unit_to_kg_factor(unit_code, density_val=None):
                                    unit = unit_code.upper()
                                    MASS_TO_KG = {
                                        "MG": 0.000001,
                                        "G": 0.001,
                                        "KG": 1.0,
                                        "TON": 1000.0,
                                    }
                                    VOLUME_TO_L = {
                                        "ML": 0.001,
                                        "L": 1.0,
                                        "LT": 1.0,
                                        "LTR": 1.0,
                                        "LITER": 1.0,
                                        "LITRE": 1.0,
                                    }
                                    if unit in MASS_TO_KG:
                                        return MASS_TO_KG[unit]
                                    elif unit in VOLUME_TO_L:
                                        if density_val and density_val > 0:
                                            return VOLUME_TO_L[unit] * float(
                                                density_val
                                            )
                                        return None
                                    return None

                                density_val = (
                                    float(density)
                                    if density and density != ""
                                    else None
                                )
                                usage_unit_factor = get_unit_to_kg_factor(
                                    usage_unit_upper, density_val
                                )
                                primary_unit_factor = get_unit_to_kg_factor(
                                    primary_unit, density_val
                                )

                                if (
                                    usage_unit_factor is not None
                                    and primary_unit_factor is not None
                                    and primary_unit_factor > 0
                                ):
                                    unit_ratio = usage_unit_factor / primary_unit_factor
                                    converted_usage_cost = unit_ratio * primary_ex_gst

                                    if converted_usage_cost is not None:
                                        # Update usage cost
                                        usage_row["ex_gst"] = round(
                                            converted_usage_cost, 4
                                        )
                                        tax_included_bool = usage_row.get(
                                            "tax_included_bool", False
                                        )
                                        if not tax_included_bool:
                                            usage_row["inc_gst"] = round(
                                                converted_usage_cost * 1.1, 4
                                            )
                except Exception as e:
                    print(f"Error recalculating usage cost after primary change: {e}")

            return updated_data

        # If clicked on a different column, don't update
        raise PreventUpdate

    # Update Assembly row in cost table when assembly summary changes
    @app.callback(
        Output("product-cost-table", "data", allow_duplicate=True),
        [Input("assembly-summary-table", "data")],
        [
            State("product-cost-table", "data"),
            State("product-usage-unit-dropdown", "value"),
            State("product-usage-quantity", "value"),
            State("product-density", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_cost_table_assembly_row(
        assembly_summary_data, cost_data, usage_unit, usage_quantity, density
    ):
        """Update Assembly row in cost table when assembly summary changes and recalculate usage if assembly is primary."""
        if not assembly_summary_data or not cost_data:
            raise PreventUpdate

        # Find assembly row in summary (type="assembly")
        assembly_row = None
        for row in assembly_summary_data:
            if row.get("type") == "assembly":
                assembly_row = row
                break

        if not assembly_row:
            raise PreventUpdate

        # Update cost table with assembly data
        updated_data = []
        assembly_is_primary = False
        for row in cost_data:
            if row.get("cost_type") == "Assembly":
                # Preserve is_primary flags
                is_primary_bool = row.get("is_primary_bool", False)
                assembly_is_primary = is_primary_bool
                is_primary_display = "✓" if is_primary_bool else "[Set Primary]"

                # Get assembly values
                assembly_cost_per_kg = assembly_row.get("cost_per_kg", 0) or 0
                assembly_total_kg = assembly_row.get("assembly_mass_kg", 0) or 0

                # Preserve tax_included state
                existing_tax_included_bool = row.get("tax_included_bool", False)
                tax_included_display = "✓" if existing_tax_included_bool else "✗"

                # Preserve total_cost and action from existing row for Assembly
                existing_total_cost = row.get("total_cost")
                existing_action = row.get("action", "")

                updated_row = {
                    **row,
                    "is_primary": is_primary_display,
                    "is_primary_bool": is_primary_bool,
                    "qty": round(assembly_total_kg, 3)
                    if assembly_total_kg > 0
                    else None,
                    "unit": "kg",
                    "ex_gst": round(assembly_cost_per_kg, 4)
                    if assembly_cost_per_kg > 0
                    else None,
                    "inc_gst": round(assembly_cost_per_kg * 1.1, 4)
                    if (assembly_cost_per_kg > 0 and existing_tax_included_bool)
                    else None,
                    "tax_included": tax_included_display,
                    "tax_included_bool": existing_tax_included_bool,
                    "total_cost": existing_total_cost,  # Preserve total_cost for action button
                    "action": existing_action,  # Preserve action field
                }
                updated_data.append(updated_row)
            else:
                # Ensure action field exists in all rows
                row_with_action = {
                    **row,
                    "action": row.get("action", ""),
                }
                updated_data.append(row_with_action)

        # If assembly is primary, recalculate usage cost
        if assembly_is_primary and usage_unit and usage_quantity:
            usage_unit_upper = str(usage_unit).upper()
            try:
                usage_qty = float(usage_quantity) if usage_quantity else None
            except (ValueError, TypeError):
                usage_qty = None

            if usage_qty and usage_qty > 0:
                # Find usage row and assembly row
                usage_row = None
                assembly_row_data = None
                for row in updated_data:
                    if row.get("cost_type") == "Usage":
                        usage_row = row
                    elif row.get("cost_type") == "Assembly":
                        assembly_row_data = row

                if usage_row and assembly_row_data:
                    assembly_per_unit_cost = assembly_row_data.get(
                        "per_unit_cost"
                    ) or assembly_row_data.get("ex_gst")
                    assembly_unit = assembly_row_data.get("unit", "kg").upper()

                    if assembly_per_unit_cost is not None and assembly_unit:
                        # Helper function to get conversion factor
                        def get_unit_to_kg_factor(unit_code, density_val=None):
                            unit = unit_code.upper()
                            MASS_TO_KG = {
                                "MG": 0.000001,
                                "G": 0.001,
                                "KG": 1.0,
                                "TON": 1000.0,
                            }
                            VOLUME_TO_L = {
                                "ML": 0.001,
                                "L": 1.0,
                                "LT": 1.0,
                                "LTR": 1.0,
                                "LITER": 1.0,
                                "LITRE": 1.0,
                            }
                            if unit in MASS_TO_KG:
                                return MASS_TO_KG[unit]
                            elif unit in VOLUME_TO_L:
                                if density_val and density_val > 0:
                                    return VOLUME_TO_L[unit] * float(density_val)
                                return None
                            return None

                        density_val = (
                            float(density) if density and density != "" else None
                        )
                        usage_unit_factor = get_unit_to_kg_factor(
                            usage_unit_upper, density_val
                        )
                        assembly_unit_factor = get_unit_to_kg_factor(
                            assembly_unit, density_val
                        )

                        if (
                            usage_unit_factor is not None
                            and assembly_unit_factor is not None
                            and assembly_unit_factor > 0
                        ):
                            unit_ratio = usage_unit_factor / assembly_unit_factor
                            converted_usage_cost = unit_ratio * assembly_per_unit_cost

                            if converted_usage_cost is not None:
                                # Update usage cost
                                usage_row["ex_gst"] = round(converted_usage_cost, 4)
                                usage_row["per_unit_cost"] = round(
                                    converted_usage_cost, 4
                                )
                                if not usage_row.get("tax_included"):
                                    usage_row["inc_gst"] = round(
                                        converted_usage_cost * 1.1, 4
                                    )

        return updated_data

    # Display product detail panel when product is selected
    @app.callback(
        [
            Output("product-detail-title", "children"),
            Output("product-detail-sku", "children"),
            Output("product-detail-capabilities", "children"),
            Output("product-detail-is-purchase", "children"),
            Output("product-detail-is-sell", "children"),
            Output("product-detail-is-assemble", "children"),
            Output("product-detail-name", "children"),
            Output("product-detail-description", "children"),
            Output("product-detail-base-unit", "children"),
            Output("product-detail-size", "children"),
            Output("product-detail-density", "children"),
            Output("product-detail-abv", "children"),
            Output("product-detail-consolidated-cost-pricing-table", "children"),
            Output("product-detail-stock", "children"),
            Output("product-detail-lots-count", "children"),
            Output("product-detail-avg-cost", "children"),
            Output("product-detail-cost-source", "children"),
            Output("product-detail-restock", "children"),
            Output("product-detail-active", "children"),
            Output("adjust-inventory-btn", "style"),
            Output("product-detail-assemblies-table-container", "children"),
        ],
        [Input("products-table", "selected_rows")],
        [State("products-table", "data")],
        prevent_initial_call=True,
    )
    def display_product_detail(selected_rows, data):
        """Display product details in the right panel when product is selected."""
        if not selected_rows or not data or len(selected_rows) == 0:
            return (
                "Select a product...",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                html.Div("No cost/pricing data"),
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                {"display": "none"},
            )

        product = data[selected_rows[0]]
        product_id = product.get("id")

        # Fetch inventory summary if product has ID
        stock_kg = 0.0
        lots_count = 0
        avg_cost = 0.0
        cost_source = "-"

        if product_id:
            try:
                inv_summary = make_api_request(
                    "GET", f"/inventory/product/{product_id}/summary"
                )
                if isinstance(inv_summary, dict) and "error" not in inv_summary:
                    stock_kg = inv_summary.get("stock_on_hand_kg", 0.0) or 0.0
                    lots_count = inv_summary.get("active_lots_count", 0) or 0
                    avg_cost = inv_summary.get("avg_cost_per_kg", 0.0) or 0.0
                    cost_source = inv_summary.get("cost_source", "-") or "-"
            except Exception as e:
                print(f"Error fetching inventory summary: {e}")
                # Try simple SOH endpoint as fallback
                try:
                    soh_response = make_api_request(
                        "GET", f"/inventory/product/{product_id}/soh"
                    )
                    if isinstance(soh_response, dict) and "error" not in soh_response:
                        stock_kg = soh_response.get("stock_on_hand_kg", 0.0) or 0.0
                except (KeyError, ValueError, TypeError):
                    pass

        # Format product type - handle both boolean and string (✓) formats
        caps = []
        is_purchase = product.get("is_purchase")
        is_sell = product.get("is_sell")
        is_assemble = product.get("is_assemble")

        is_purchase_bool = (
            is_purchase is True
            or is_purchase == "✓"
            or (isinstance(is_purchase, str) and is_purchase.strip() == "✓")
        )
        is_sell_bool = (
            is_sell is True
            or is_sell == "✓"
            or (isinstance(is_sell, str) and is_sell.strip() == "✓")
        )
        is_assemble_bool = (
            is_assemble is True
            or is_assemble == "✓"
            or (isinstance(is_assemble, str) and is_assemble.strip() == "✓")
        )

        if is_purchase_bool:
            caps.append("Purchase")
        if is_sell_bool:
            caps.append("Sell")
        if is_assemble_bool:
            caps.append("Assemble")
        product_type = ", ".join(caps) if caps else "None"

        # Format badges for product type booleans
        purchase_badge = (
            html.Span("Purchase", className="badge bg-primary me-1")
            if is_purchase_bool
            else html.Span("")
        )
        sell_badge = (
            html.Span("Sell", className="badge bg-success me-1")
            if is_sell_bool
            else html.Span("")
        )
        assemble_badge = (
            html.Span("Assemble", className="badge bg-info")
            if is_assemble_bool
            else html.Span("")
        )

        # Load assemblies for this product
        assemblies_table = html.Div("No assemblies")
        if product_id and is_assemble_bool:
            try:
                formulas_response = make_api_request(
                    "GET", f"/formulas/?product_id={product_id}&is_active=true"
                )
                if isinstance(formulas_response, list) and len(formulas_response) > 0:
                    # Format assemblies for table
                    assembly_data = []
                    for formula in formulas_response:
                        lines_list = formula.get("lines", [])
                        if not isinstance(lines_list, list):
                            lines_list = []
                        lines_count = len(lines_list)

                        # Calculate costs (simplified - similar to load_product_assemblies)
                        total_cost = 0.0
                        total_quantity_kg = 0.0
                        for line in lines_list:
                            if isinstance(line, dict):
                                qty_kg = float(line.get("quantity_kg", 0.0) or 0.0)
                                unit_cost = line.get("unit_cost") or 0.0
                                if not unit_cost:
                                    line_product_id = line.get("raw_material_id")
                                    if line_product_id:
                                        try:
                                            line_product = make_api_request(
                                                "GET", f"/products/{line_product_id}"
                                            )
                                            if isinstance(line_product, dict):
                                                cost_val = (
                                                    line_product.get(
                                                        "usage_cost_inc_gst"
                                                    )
                                                    or line_product.get(
                                                        "purchase_cost_inc_gst"
                                                    )
                                                    or 0
                                                )
                                                if cost_val:
                                                    try:
                                                        unit_cost = round(
                                                            float(cost_val), 4
                                                        )
                                                    except (ValueError, TypeError):
                                                        unit_cost = 0.0
                                        except Exception:
                                            pass
                                total_cost += (
                                    qty_kg * float(unit_cost) if unit_cost else 0.0
                                )
                                total_quantity_kg += qty_kg

                        # Get yield factor
                        yield_factor = float(formula.get("yield_factor", 1.0) or 1.0)

                        # Calculate cost per kg and cost per L
                        parent_density = float(product.get("density_kg_per_l", 0) or 0)
                        total_quantity_l = (
                            total_quantity_kg / parent_density
                            if parent_density > 0
                            else 0.0
                        )
                        cost_per_kg = (
                            total_cost / total_quantity_kg
                            if total_quantity_kg > 0
                            else 0.0
                        )
                        cost_per_l = (
                            total_cost / total_quantity_l
                            if total_quantity_l > 0
                            else 0.0
                        )

                        assembly_data.append(
                            {
                                "formula_id": str(formula.get("id", "")),
                                "formula_name": str(formula.get("formula_name", "")),
                                "version": int(formula.get("version", 1)),
                                "yield_factor": round(yield_factor, 2),
                                "is_primary": "✓"
                                if formula.get("is_active")
                                and formula.get("is_primary")
                                else "",
                                "total_cost": f"${total_cost:.2f}"
                                if total_cost > 0
                                else "-",
                                "cost_per_kg": round(cost_per_kg, 4),
                                "cost_per_l": round(cost_per_l, 4),
                                "lines_count": lines_count,
                            }
                        )

                    if assembly_data:
                        assemblies_table = dash_table.DataTable(
                            id="product-detail-assemblies-table",
                            data=assembly_data,
                            columns=[
                                {"name": "Name", "id": "formula_name"},
                                {"name": "Version", "id": "version"},
                                {
                                    "name": "Yield",
                                    "id": "yield_factor",
                                    "type": "numeric",
                                    "format": {"specifier": ".2f"},
                                },
                                {
                                    "name": "Primary",
                                    "id": "is_primary",
                                    "presentation": "markdown",
                                },
                                {"name": "Total Cost", "id": "total_cost"},
                                {
                                    "name": "Cost/kg",
                                    "id": "cost_per_kg",
                                    "type": "numeric",
                                    "format": {"specifier": ".4f"},
                                },
                                {
                                    "name": "Cost/L",
                                    "id": "cost_per_l",
                                    "type": "numeric",
                                    "format": {"specifier": ".4f"},
                                },
                                {"name": "Lines", "id": "lines_count"},
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
                            row_selectable="single",
                            selected_rows=[],
                        )
            except Exception as e:
                print(f"Error loading assemblies: {e}")

        # Build consolidated cost/pricing table with all requested calculations
        consolidated_rows = []

        # Pricing data - ensure numeric types
        def safe_float(value, default=None):
            """Safely convert value to float, returning default if conversion fails."""
            if value is None or value == "":
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        # Calculate excise based on ABV, density, size, and base_unit
        excise_value = None
        try:
            abv = safe_float(product.get("abv_percent"))
            density = safe_float(product.get("density_kg_per_l"))
            size = safe_float(product.get("size"))
            base_unit = product.get("base_unit")

            if abv and abv > 0:
                # Get current excise rate
                excise_response = make_api_request("GET", "/excise-rates/current")
                excise_rate_per_l_abv = (
                    float(excise_response.get("rate_per_l_abv", 0))
                    if isinstance(excise_response, dict)
                    else 0.0
                )

                # Calculate volume in liters
                volume_liters = 1.0  # Default
                if size and base_unit:
                    size_val = float(size)
                    base_unit_upper = base_unit.upper() if base_unit else ""

                    if base_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                        volume_liters = size_val
                    elif base_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                        volume_liters = size_val / 1000.0
                    elif base_unit_upper in ["KG", "KILOGRAM"]:
                        if density and density > 0:
                            volume_liters = size_val / density
                        else:
                            volume_liters = size_val
                    elif base_unit_upper in ["G", "GRAM", "GRAMS"]:
                        if density and density > 0:
                            volume_liters = (size_val / 1000.0) / density
                        else:
                            volume_liters = size_val / 1000.0
                elif base_unit:
                    base_unit_upper = base_unit.upper()
                    if base_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                        volume_liters = 1.0
                    elif base_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                        volume_liters = 0.001
                    elif base_unit_upper in ["KG", "KILOGRAM"]:
                        if density and density > 0:
                            volume_liters = 1.0 / density
                        else:
                            volume_liters = 1.0
                    elif base_unit_upper in ["G", "GRAM", "GRAMS"]:
                        if density and density > 0:
                            volume_liters = 0.001 / density
                        else:
                            volume_liters = 0.001

                # Calculate excise: volume_in_liters * (ABV/100) * excise_rate_per_l_abv
                abv_liters = volume_liters * (abv / 100.0)
                excise_value = abv_liters * excise_rate_per_l_abv
        except Exception as e:
            print(f"Error calculating excise: {e}")
            excise_value = None

        # Cost types
        cost_types = [
            {
                "name": "Purchase Cost",
                "ex_gst": product.get("purchase_cost_ex_gst"),
                "excise": excise_value,
            },
            {
                "name": "Usage Cost",
                "ex_gst": product.get("usage_cost_ex_gst"),
                "excise": excise_value,
            },
            {
                "name": "Manufactured Cost",
                "ex_gst": product.get("manufactured_cost_ex_gst"),
                "excise": excise_value,
            },
        ]

        distributor_ex_gst = safe_float(product.get("distributor_price_ex_gst"))
        distributor_inc_gst = safe_float(product.get("distributor_price_inc_gst"))
        retail_ex_gst = safe_float(product.get("retail_price_ex_gst"))
        retail_inc_gst = safe_float(product.get("retail_price_inc_gst"))

        # Check if product is GST free (salestaxcde indicates GST free status)
        # Common values: "F" = Free, "G" = GST Free, or empty/None = GST applies
        salestaxcde = product.get("salestaxcde")
        is_gst_free = salestaxcde and str(salestaxcde).upper() in ["F", "G"]
        gst_multiplier = 1.0 if is_gst_free else 1.1  # Don't apply GST if GST free

        for cost_type in cost_types:
            # Ensure numeric types - convert strings/Decimals to float
            ex_gst_raw = cost_type["ex_gst"]
            if ex_gst_raw is None or ex_gst_raw == "":
                ex_gst = 0.0
            else:
                try:
                    ex_gst = float(ex_gst_raw)
                except (ValueError, TypeError):
                    ex_gst = 0.0

            excise_raw = cost_type.get("excise")
            if excise_raw is None or excise_raw == "":
                excise = 0.0
            else:
                try:
                    excise = float(excise_raw)
                except (ValueError, TypeError):
                    excise = 0.0

            # Calculate Ex-GST+Excise
            ex_gst_plus_excise = ex_gst + excise

            # Calculate Excised (calculated as [ex-excise + Excise]*gst_multiplier)
            # If GST free, don't apply GST (multiply by 1.0 instead of 1.1)
            excised = (ex_gst + excise) * gst_multiplier

            # Calculate UnExcised (calculated as ex-GST * gst_multiplier)
            # If GST free, don't apply GST (multiply by 1.0 instead of 1.1)
            unexcised = ex_gst * gst_multiplier

            # Distributor and Retail calculations (only for rows with pricing data)
            if cost_type["name"] == "Manufactured Cost":
                # Use distributor pricing for profit margin calculation
                dist_inc_gst_calc = distributor_inc_gst if distributor_inc_gst else None
                dist_profit_margin = (
                    ((distributor_ex_gst - ex_gst) / ex_gst * 100)
                    if distributor_ex_gst and ex_gst > 0
                    else None
                )
                retail_price_calc = retail_inc_gst if retail_inc_gst else None
                retail_profit_margin = (
                    ((retail_ex_gst - distributor_ex_gst) / distributor_ex_gst * 100)
                    if retail_ex_gst and distributor_ex_gst and distributor_ex_gst > 0
                    else None
                )
            else:
                dist_inc_gst_calc = None
                dist_profit_margin = None
                retail_price_calc = None
                retail_profit_margin = None

            # Get use unit for display
            use_unit = (
                str(product.get("usage_unit", "")).upper()
                if product.get("usage_unit")
                else "-"
            )

            # For Usage Cost row, use usage_cost_ex_gst; for others use the cost type's ex_gst
            cogs_value = ex_gst
            if cost_type["name"] == "Usage Cost":
                # Use usage_cost_ex_gst specifically for Usage Cost row
                usage_ex_gst = safe_float(product.get("usage_cost_ex_gst"), 0.0)
                cogs_value = usage_ex_gst if usage_ex_gst else ex_gst

            consolidated_rows.append(
                {
                    "Cost Type": cost_type["name"],
                    "Use Unit": use_unit,
                    "COGS": f"${cogs_value:.4f}"
                    if cogs_value
                    else "-",  # Shows usage_cost_ex_gst for Usage Cost, ex_gst for others
                    "Excise": f"${excise:.4f}"
                    if excise
                    else "-",  # Calculated excise value
                    "Cost+Excise": f"${ex_gst_plus_excise:.4f}"
                    if ex_gst_plus_excise
                    else "-",  # COGS + Excise
                    "Excised": f"${excised:.4f}"
                    if excised
                    else "-",  # (COGS + Excise) * GST multiplier
                    "UnExcised": f"${unexcised:.4f}" if unexcised else "-",
                    "Distributor Inc GST": (
                        f"${dist_inc_gst_calc:.4f}" if dist_inc_gst_calc else "-"
                    ),
                    "Dist Profit Margin": (
                        f"{dist_profit_margin:.1f}%"
                        if dist_profit_margin is not None
                        else "-"
                    ),
                    "Retail Price": (
                        f"${retail_price_calc:.4f}" if retail_price_calc else "-"
                    ),
                    "Retail Margin": (
                        f"{retail_profit_margin:.1f}%"
                        if retail_profit_margin is not None
                        else "-"
                    ),
                }
            )

        consolidated_table = dash_table.DataTable(
            data=consolidated_rows,
            columns=[
                {"name": "Cost Type", "id": "Cost Type"},
                {"name": "COGS", "id": "COGS"},  # Renamed from "Ex GST"
                {"name": "Excise", "id": "Excise"},
                {
                    "name": "Cost+Excise",
                    "id": "Cost+Excise",
                },  # Renamed from "Ex-GST+Excise" - shows Ex-GST + Excise
                {
                    "name": "Excised",
                    "id": "Excised",
                },  # (Ex-GST + Excise) * GST multiplier
                {"name": "UnExcised", "id": "UnExcised"},
                {"name": "Distributor Inc GST", "id": "Distributor Inc GST"},
                {"name": "Dist Profit Margin", "id": "Dist Profit Margin"},
                {"name": "Retail Price", "id": "Retail Price"},
                {"name": "Retail Margin", "id": "Retail Margin"},
            ],
            style_cell={"textAlign": "left", "fontSize": "10px", "padding": "4px"},
            style_header={
                "backgroundColor": "rgb(230, 230, 230)",
                "fontWeight": "bold",
            },
        )

        return (
            product.get("name", "Product Details"),
            product.get("sku", "-"),
            product_type,
            purchase_badge,
            sell_badge,
            assemble_badge,
            product.get("name", "-"),
            product.get("description") or "-",
            product.get("base_unit") or "-",
            product.get("size") or "-",
            (
                f"{float(product.get('density_kg_per_l', 0) or 0):.3f}"
                if product.get("density_kg_per_l") is not None
                and str(product.get("density_kg_per_l", "")).strip() != ""
                else "-"
            ),
            (
                f"{float(product.get('abv_percent', 0) or 0):.2f}%"
                if product.get("abv_percent") is not None
                and str(product.get("abv_percent", "")).strip() != ""
                else "-"
            ),
            consolidated_table,
            f"{stock_kg:.3f}",
            f"{lots_count}",
            f"${avg_cost:.2f}/kg" if avg_cost > 0 else "-",
            cost_source,
            (
                f"{float(product.get('restock_level', 0) or 0):.3f} kg"
                if product.get("restock_level") is not None
                and str(product.get("restock_level", "")).strip() != ""
                else "-"
            ),
            "Yes" if product.get("is_active") else "No",
            {"display": "block"} if product_id else {"display": "none"},
            assemblies_table,
        )

    # Load assembly line items when assembly is selected in view panel
    @app.callback(
        Output("product-detail-assembly-lines-container", "children"),
        [Input("product-detail-assemblies-table", "selected_rows")],
        [State("product-detail-assemblies-table", "data")],
        prevent_initial_call=True,
    )
    def load_assembly_line_items_view(selected_rows, assembly_data):
        """Load line items for selected assembly in view panel."""
        if not selected_rows or not assembly_data or len(selected_rows) == 0:
            return html.Div("Select an assembly to view line items")

        formula_id = assembly_data[selected_rows[0]].get("formula_id")

        try:
            formula_response = make_api_request("GET", f"/formulas/{formula_id}")

            if isinstance(formula_response, dict) and "error" not in formula_response:
                # Get parent product_id from formula response
                parent_product_id = formula_response.get("product_id")

                # Get parent product density for totals
                if parent_product_id:
                    try:
                        parent_resp = make_api_request(
                            "GET", f"/products/{parent_product_id}"
                        )
                        if isinstance(parent_resp, dict) and "error" not in parent_resp:
                            density_val = parent_resp.get("density_kg_per_l", 0) or 0
                            try:
                                float(density_val)
                            except (ValueError, TypeError):
                                pass
                    except Exception:
                        pass

                lines_data = []
                total_cost = 0.0
                total_quantity_kg = 0.0
                total_quantity_l = 0.0

                for line in formula_response.get("lines", []):
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
                            if (
                                isinstance(product_resp, dict)
                                and "error" not in product_resp
                            ):
                                product_sku = product_resp.get("sku", "")
                                product_name = product_resp.get("name", product_name)

                                # Get density
                                density_val = (
                                    product_resp.get("density_kg_per_l", 0) or 0
                                )
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
                                            # First, try to find an active formula
                                            for f in formulas_response:
                                                if f.get("is_active") is True:
                                                    primary_formula = f
                                                    break

                                            # If no active formula found, use first one
                                            if not primary_formula:
                                                primary_formula = formulas_response[0]

                                            print(
                                                f"[load_assembly_line_items_view] Using formula {primary_formula.get('formula_code')} (is_active={primary_formula.get('is_active')}) for product {line_product_id}"
                                            )

                                            # Calculate primary assembly's cost per kg
                                            if primary_formula:
                                                lines_list = primary_formula.get(
                                                    "lines", []
                                                )
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
                                                            assembly_line.get(
                                                                "raw_material_id"
                                                            )
                                                        )
                                                        assembly_line_cost = 0.0

                                                        if assembly_line_product_id:
                                                            try:
                                                                assembly_line_product = make_api_request(
                                                                    "GET",
                                                                    f"/products/{assembly_line_product_id}",
                                                                )
                                                                if isinstance(
                                                                    assembly_line_product,
                                                                    dict,
                                                                ):
                                                                    # Try ex_gst first, then inc_gst (for consistency)
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
                                                                            # Get product's usage_unit to convert cost to $/kg
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

                                                                            # Handle "EA" (each) unit - cost is per item, not per weight
                                                                            (
                                                                                assembly_line.get(
                                                                                    "unit",
                                                                                    "",
                                                                                ).upper()
                                                                                if assembly_line.get(
                                                                                    "unit"
                                                                                )
                                                                                else "KG"
                                                                            )
                                                                            if (
                                                                                assembly_line_usage_unit
                                                                                in [
                                                                                    "EA",
                                                                                    "EACH",
                                                                                    "UNIT",
                                                                                    "UNITS",
                                                                                ]
                                                                            ):
                                                                                # Cost is per item, so multiply cost per item by quantity (in items)
                                                                                # For EA items, quantity_kg might store the quantity (if no weight) or quantity * weight
                                                                                # Get quantity from quantity_kg - if product has weight, reverse calculate
                                                                                assembly_line_qty_ea = assembly_qty_kg  # Default: quantity_kg stores quantity
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
                                                                                    # Product has weight - reverse calculate: quantity = quantity_kg / weight_kg
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
                                                                                # Otherwise, quantity_kg IS the quantity (we stored it that way)

                                                                                assembly_line_cost = (
                                                                                    assembly_line_qty_ea
                                                                                    * assembly_line_unit_cost_raw
                                                                                )
                                                                                # For cost per kg calculation, we need the weight per item
                                                                                # If we have quantity_kg, we can calculate cost per kg
                                                                                if (
                                                                                    assembly_qty_kg
                                                                                    > 0
                                                                                ):
                                                                                    # Cost per kg = total cost / total kg
                                                                                    assembly_line_cost_per_kg = (
                                                                                        assembly_line_cost
                                                                                        / assembly_qty_kg
                                                                                    )
                                                                                else:
                                                                                    # Can't calculate cost per kg without weight
                                                                                    assembly_line_cost_per_kg = 0.0
                                                                            else:
                                                                                # Convert unit cost to $/kg for weight/volume units
                                                                                assembly_line_cost_per_kg = assembly_line_unit_cost_raw
                                                                                if (
                                                                                    assembly_line_usage_unit
                                                                                    in [
                                                                                        "G",
                                                                                        "GRAM",
                                                                                        "GRAMS",
                                                                                    ]
                                                                                ):
                                                                                    # Cost per gram -> cost per kg
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
                                                                                    # Cost per L -> cost per kg (need density)
                                                                                    if (
                                                                                        assembly_line_density
                                                                                        > 0
                                                                                    ):
                                                                                        assembly_line_cost_per_kg = (
                                                                                            assembly_line_unit_cost_raw
                                                                                            / assembly_line_density
                                                                                        )
                                                                                    else:
                                                                                        # Fallback: assume 1 L = 1 kg
                                                                                        assembly_line_cost_per_kg = assembly_line_unit_cost_raw
                                                                                elif (
                                                                                    assembly_line_usage_unit
                                                                                    in [
                                                                                        "ML",
                                                                                        "MILLILITER",
                                                                                        "MILLILITRE",
                                                                                    ]
                                                                                ):
                                                                                    # Cost per mL -> cost per kg (via L)
                                                                                    if (
                                                                                        assembly_line_density
                                                                                        > 0
                                                                                    ):
                                                                                        # mL -> L -> kg
                                                                                        assembly_line_cost_per_kg = (
                                                                                            (
                                                                                                assembly_line_unit_cost_raw
                                                                                                * 1000.0
                                                                                            )
                                                                                            / assembly_line_density
                                                                                        )
                                                                                    else:
                                                                                        # Fallback: assume 1 mL = 1 g
                                                                                        assembly_line_cost_per_kg = (
                                                                                            assembly_line_unit_cost_raw
                                                                                            * 1000.0
                                                                                        )
                                                                                # If already in KG, no conversion needed

                                                                                # Calculate line cost: quantity_kg * cost_per_kg
                                                                                assembly_line_cost = (
                                                                                    assembly_qty_kg
                                                                                    * assembly_line_cost_per_kg
                                                                                )
                                                                        except (
                                                                            ValueError,
                                                                            TypeError,
                                                                        ) as e:
                                                                            print(
                                                                                f"Error calculating assembly line cost: {e}"
                                                                            )
                                                                            pass
                                                            except Exception as e:
                                                                print(
                                                                    f"Error fetching assembly line product: {e}"
                                                                )
                                                                pass

                                                        assembly_total_cost += (
                                                            assembly_line_cost
                                                        )
                                                        assembly_total_kg += (
                                                            assembly_qty_kg
                                                        )

                                                # Calculate cost per kg for the assembly
                                                if assembly_total_kg > 0:
                                                    assembly_cost_per_kg = (
                                                        assembly_total_cost
                                                        / assembly_total_kg
                                                    )
                                                    # Set product_usage_cost to assembly cost per kg
                                                    # and usage_unit to kg since we're using cost per kg
                                                    product_usage_cost = round(
                                                        assembly_cost_per_kg, 4
                                                    )
                                                    product_usage_unit = "KG"
                                                    print(
                                                        f"[load_assembly_line_items_view] Calculated assembly cost for {line_product_id}: total_cost={assembly_total_cost:.4f}, total_kg={assembly_total_kg:.4f}, cost_per_kg={assembly_cost_per_kg:.4f}"
                                                    )
                                                else:
                                                    print(
                                                        f"[load_assembly_line_items_view] WARNING: assembly_total_kg is 0 for product {line_product_id}, cannot calculate cost per kg"
                                                    )
                                                    # Fallback to usage/purchase cost
                                                    cost_val = (
                                                        product_resp.get(
                                                            "usage_cost_ex_gst"
                                                        )
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
                                        print(
                                            f"Error fetching assembly cost for {line_product_id}: {e}"
                                        )
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
                                                product_usage_cost = round(
                                                    float(cost_val), 4
                                                )
                                            except (ValueError, TypeError):
                                                product_usage_cost = 0.0
                                else:
                                    # Not an assembly - use usage/purchase cost
                                    # Try ex_gst first, then inc_gst (for consistency)
                                    cost_val = (
                                        product_resp.get("usage_cost_ex_gst")
                                        or product_resp.get("purchase_cost_ex_gst")
                                        or product_resp.get("usage_cost_inc_gst")
                                        or product_resp.get("purchase_cost_inc_gst")
                                        or 0
                                    )
                                    if cost_val:
                                        try:
                                            product_usage_cost = round(
                                                float(cost_val), 4
                                            )
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

                    # Calculate quantity_l
                    quantity_l = quantity_kg / density if density > 0 else 0.0

                    # Calculate line cost with proper unit conversions
                    # Convert assembly line quantity to product's usage_unit, then multiply by cost
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
                        ] and product_usage_unit in [
                            "L",
                            "LT",
                            "LTR",
                            "LITER",
                            "LITRE",
                        ]:
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
                        ] and product_usage_unit in [
                            "L",
                            "LT",
                            "LTR",
                            "LITER",
                            "LITRE",
                        ]:
                            quantity_in_usage_unit = quantity_l
                        # Volume to mass (using density)
                        elif assembly_unit_upper in [
                            "L",
                            "LT",
                            "LTR",
                            "LITER",
                            "LITRE",
                        ] and product_usage_unit in ["KG", "KILOGRAM", "KILOGRAMS"]:
                            quantity_in_usage_unit = (
                                quantity_kg if density > 0 else quantity_l
                            )
                        elif assembly_unit_upper in [
                            "L",
                            "LT",
                            "LTR",
                            "LITER",
                            "LITRE",
                        ] and product_usage_unit in ["G", "GRAM", "GRAMS"]:
                            quantity_in_usage_unit = (
                                quantity_kg * 1000.0
                                if density > 0
                                else quantity_l * 1000.0
                            )
                        elif assembly_unit_upper in [
                            "ML",
                            "MILLILITER",
                            "MILLILITRE",
                        ] and product_usage_unit in ["KG", "KILOGRAM", "KILOGRAMS"]:
                            quantity_in_usage_unit = (
                                quantity_kg if density > 0 else quantity_l
                            )
                        elif assembly_unit_upper in [
                            "ML",
                            "MILLILITER",
                            "MILLILITRE",
                        ] and product_usage_unit in ["G", "GRAM", "GRAMS"]:
                            quantity_in_usage_unit = (
                                quantity_kg * 1000.0
                                if density > 0
                                else quantity_l * 1000.0
                            )
                        # Mass to volume (using density)
                        elif assembly_unit_upper in [
                            "KG",
                            "KILOGRAM",
                            "KILOGRAMS",
                        ] and product_usage_unit in [
                            "L",
                            "LT",
                            "LTR",
                            "LITER",
                            "LITRE",
                        ]:
                            quantity_in_usage_unit = (
                                quantity_l if density > 0 else quantity_kg
                            )
                        elif assembly_unit_upper in [
                            "G",
                            "GRAM",
                            "GRAMS",
                        ] and product_usage_unit in [
                            "L",
                            "LT",
                            "LTR",
                            "LITER",
                            "LITRE",
                        ]:
                            quantity_in_usage_unit = (
                                quantity_l if density > 0 else quantity_kg
                            )
                        elif assembly_unit_upper in [
                            "KG",
                            "KILOGRAM",
                            "KILOGRAMS",
                        ] and product_usage_unit in ["ML", "MILLILITER", "MILLILITRE"]:
                            quantity_in_usage_unit = (
                                quantity_l * 1000.0
                                if density > 0
                                else quantity_kg * 1000.0
                            )
                        elif assembly_unit_upper in [
                            "G",
                            "GRAM",
                            "GRAMS",
                        ] and product_usage_unit in ["ML", "MILLILITER", "MILLILITRE"]:
                            quantity_in_usage_unit = (
                                quantity_l * 1000.0
                                if density > 0
                                else quantity_kg * 1000.0
                            )
                        # Handle "EA" (each) units
                        elif assembly_unit_upper in [
                            "EA",
                            "EACH",
                            "UNIT",
                            "UNITS",
                        ] and product_usage_unit.upper() in [
                            "EA",
                            "EACH",
                            "UNIT",
                            "UNITS",
                        ]:
                            # Both are "each" - quantity is already in items
                            quantity_in_usage_unit = quantity_display
                        elif assembly_unit_upper in ["EA", "EACH", "UNIT", "UNITS"]:
                            # Assembly line is "ea" but product usage_unit is not - can't convert without weight/volume per item
                            # Use quantity as-is (assume cost is per item)
                            quantity_in_usage_unit = quantity_display
                            print(
                                f"[load_assembly_line_items_view] WARNING: Assembly line unit is 'EA' but product usage_unit is '{product_usage_unit}' - using quantity as-is"
                            )
                        elif product_usage_unit.upper() in [
                            "EA",
                            "EACH",
                            "UNIT",
                            "UNITS",
                        ]:
                            # Product usage_unit is "ea" but assembly line unit is not - can't convert
                            # Use quantity as-is (cost is per item regardless of assembly line unit)
                            quantity_in_usage_unit = quantity_display
                            print(
                                f"[load_assembly_line_items_view] WARNING: Product usage_unit is 'EA' but assembly line unit is '{assembly_unit_upper}' - using quantity as-is"
                            )
                        else:
                            # Fallback: use quantity_kg
                            quantity_in_usage_unit = quantity_kg

                        line_cost = quantity_in_usage_unit * product_usage_cost
                    elif product_usage_cost > 0:
                        # If no usage_unit, assume it's per kg
                        line_cost = quantity_kg * product_usage_cost

                    # Calculate display unit_cost (cost per assembly line unit)
                    display_unit_cost = 0.0
                    if (
                        product_usage_cost > 0
                        and product_usage_unit
                        and quantity_display > 0
                    ):
                        # Convert product_usage_cost to assembly line's unit
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
                        ] and product_usage_unit in [
                            "L",
                            "LT",
                            "LTR",
                            "LITER",
                            "LITRE",
                        ]:
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
                        ] and product_usage_unit.upper() in [
                            "EA",
                            "EACH",
                            "UNIT",
                            "UNITS",
                        ]:
                            # Both are "each" - cost is already per item
                            display_unit_cost = product_usage_cost
                        elif assembly_unit_upper in [
                            "EA",
                            "EACH",
                            "UNIT",
                            "UNITS",
                        ] or product_usage_unit.upper() in [
                            "EA",
                            "EACH",
                            "UNIT",
                            "UNITS",
                        ]:
                            # One is "ea" - cost is per item, use as-is
                            display_unit_cost = product_usage_cost
                        else:
                            display_unit_cost = (
                                line_cost / quantity_display
                                if quantity_display > 0
                                else 0.0
                            )
                    elif product_usage_cost > 0:
                        # Fallback: calculate from line_cost
                        display_unit_cost = (
                            line_cost / quantity_display
                            if quantity_display > 0
                            else 0.0
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
                    # Calculate totals
                    cost_per_kg = (
                        total_cost / total_quantity_kg if total_quantity_kg > 0 else 0.0
                    )
                    cost_per_l = (
                        total_cost / total_quantity_l if total_quantity_l > 0 else 0.0
                    )

                    # Create table with totals row
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

                    # Create summary totals
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

                    return html.Div([lines_table, summary])
                else:
                    return html.Div("No line items in this assembly")
            else:
                return html.Div("Error loading assembly details")
        except Exception as e:
            print(f"Error loading assembly line items: {e}")
            import traceback

            traceback.print_exc()
            return html.Div(f"Error: {str(e)}")

    # Update view panel when form fields change
    @app.callback(
        [
            Output("product-detail-title", "children", allow_duplicate=True),
            Output("product-detail-sku", "children", allow_duplicate=True),
            Output("product-detail-capabilities", "children", allow_duplicate=True),
            Output("product-detail-name", "children", allow_duplicate=True),
            Output("product-detail-description", "children", allow_duplicate=True),
            Output("product-detail-base-unit", "children", allow_duplicate=True),
            Output("product-detail-size", "children", allow_duplicate=True),
            Output("product-detail-density", "children", allow_duplicate=True),
            Output("product-detail-abv", "children", allow_duplicate=True),
            Output(
                "product-detail-consolidated-cost-pricing-table",
                "children",
                allow_duplicate=True,
            ),
        ],
        [
            Input("product-sku", "value"),
            Input("product-name", "value"),
            Input("product-description", "value"),
            Input("product-base-unit", "value"),
            Input("product-size", "value"),
            Input("product-density", "value"),
            Input("product-abv", "value"),
            Input("product-is-purchase", "value"),
            Input("product-is-sell", "value"),
            Input("product-is-assemble", "value"),
            Input("product-cost-table", "data"),
            Input("product-pricing-table", "data"),
            Input("product-purchase-quantity", "value"),
            Input("product-purchase-cost-ex-gst", "value"),
            Input("product-purchase-cost-inc-gst", "value"),
            Input("product-purchase-unit-dropdown", "value"),
            Input("product-usage-quantity", "value"),
            Input("product-usage-unit-dropdown", "value"),
        ],
        [
            State("product-form-modal", "is_open"),
            State("product-form-hidden", "children"),
            State("products-table", "selected_rows"),
            State("products-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def update_view_panel_from_form(
        sku,
        name,
        description,
        base_unit,
        size,
        density,
        abv,
        is_purchase,
        is_sell,
        is_assemble,
        cost_data,
        pricing_data,
        purchase_quantity,
        purchase_cost_ex_gst,
        purchase_cost_inc_gst,
        purchase_unit_id,
        usage_quantity,
        usage_unit_id,
        modal_is_open,
        product_id,
        selected_rows,
        table_data,
    ):
        """Update view panel as form fields change."""
        # Only update if modal is open, product is selected, and we're in edit mode (not add mode)
        if not modal_is_open:
            raise PreventUpdate

        # Skip if product_id is empty (add mode) or if we don't have valid data
        if not product_id or product_id == "" or not product_id.strip():
            raise PreventUpdate

        # Check if modal is actually open by checking if product_id exists and form has data
        if not selected_rows or not table_data or len(selected_rows) == 0:
            raise PreventUpdate

        # Check if we have valid table data
        if not isinstance(table_data, list) or len(table_data) == 0:
            raise PreventUpdate

        # Additional safety check: ensure the selected row index is valid
        if selected_rows[0] >= len(table_data):
            raise PreventUpdate

        # Get current product from table to maintain other fields
        product = (
            table_data[selected_rows[0]]
            if selected_rows and len(selected_rows) > 0
            else {}
        )

        # Build updated product dict from form values
        updated_product = product.copy()
        if sku:
            updated_product["sku"] = sku
        if name:
            updated_product["name"] = name
        if description is not None:
            updated_product["description"] = description
        if base_unit:
            updated_product["base_unit"] = base_unit
        if size:
            updated_product["size"] = size
        if density:
            try:
                updated_product["density_kg_per_l"] = float(density)
            except (ValueError, TypeError):
                pass
        if abv:
            try:
                updated_product["abv_percent"] = float(abv)
            except (ValueError, TypeError):
                pass

        # Update product type booleans
        updated_product["is_purchase"] = is_purchase if is_purchase else False
        updated_product["is_sell"] = is_sell if is_sell else False
        updated_product["is_assemble"] = is_assemble if is_assemble else False

        # Update cost/pricing from tables
        if cost_data:
            for row in cost_data:
                cost_type = row.get("cost_type", "")
                if cost_type == "Purchase":
                    ex_gst = row.get("ex_gst")
                    inc_gst = row.get("inc_gst")
                    if ex_gst is not None:
                        updated_product["purchase_cost_ex_gst"] = ex_gst
                    if inc_gst is not None:
                        updated_product["purchase_cost_inc_gst"] = inc_gst
                elif cost_type == "Usage":
                    ex_gst = row.get("ex_gst")
                    inc_gst = row.get("inc_gst")
                    if ex_gst is not None:
                        updated_product["usage_cost_ex_gst"] = ex_gst
                    if inc_gst is not None:
                        updated_product["usage_cost_inc_gst"] = inc_gst

        if pricing_data:
            for row in pricing_data:
                price_level = row.get("price_level", "")
                if price_level == "Retail":
                    updated_product["retail_price_ex_gst"] = row.get("ex_gst")
                    updated_product["retail_price_inc_gst"] = row.get("inc_gst")
                elif price_level == "Distributor":
                    updated_product["distributor_price_ex_gst"] = row.get("ex_gst")
                    updated_product["distributor_price_inc_gst"] = row.get("inc_gst")

        # Format product type
        caps = []
        if updated_product.get("is_purchase"):
            caps.append("Purchase")
        if updated_product.get("is_sell"):
            caps.append("Sell")
        if updated_product.get("is_assemble"):
            caps.append("Assemble")
        product_type = ", ".join(caps) if caps else "None"

        # Build consolidated cost/pricing table
        def safe_float(value):
            if value is None or value == "":
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None

        consolidated_rows = []
        cost_types = [
            {
                "name": "Purchase Cost",
                "ex_gst": updated_product.get("purchase_cost_ex_gst"),
                "excise": None,
            },
            {
                "name": "Usage Cost",
                "ex_gst": updated_product.get("usage_cost_ex_gst"),
                "excise": None,
            },
            {
                "name": "Manufactured Cost",
                "ex_gst": updated_product.get("manufactured_cost_ex_gst"),
                "excise": None,
            },
        ]

        distributor_ex_gst = safe_float(updated_product.get("distributor_price_ex_gst"))
        distributor_inc_gst = safe_float(
            updated_product.get("distributor_price_inc_gst")
        )
        retail_ex_gst = safe_float(updated_product.get("retail_price_ex_gst"))
        retail_inc_gst = safe_float(updated_product.get("retail_price_inc_gst"))

        # Check if product is GST free (salestaxcde indicates GST free status)
        # Common values: "F" = Free, "G" = GST Free, or empty/None = GST applies
        salestaxcde = updated_product.get("salestaxcde")
        is_gst_free = salestaxcde and str(salestaxcde).upper() in ["F", "G"]
        gst_multiplier = 1.0 if is_gst_free else 1.1  # Don't apply GST if GST free

        for cost_type in cost_types:
            ex_gst = safe_float(cost_type["ex_gst"]) or 0.0
            excise = safe_float(cost_type.get("excise")) or 0.0
            ex_gst_plus_excise = ex_gst + excise
            # If GST free, don't apply GST (multiply by 1.0 instead of 1.1)
            excised = (ex_gst + excise) * gst_multiplier
            unexcised = ex_gst * gst_multiplier

            if cost_type["name"] == "Manufactured Cost":
                dist_inc_gst_calc = distributor_inc_gst if distributor_inc_gst else None
                dist_profit_margin = (
                    ((distributor_ex_gst - ex_gst) / ex_gst * 100)
                    if distributor_ex_gst and ex_gst > 0
                    else None
                )
                retail_price_calc = retail_inc_gst if retail_inc_gst else None
                retail_profit_margin = (
                    ((retail_ex_gst - distributor_ex_gst) / distributor_ex_gst * 100)
                    if retail_ex_gst and distributor_ex_gst and distributor_ex_gst > 0
                    else None
                )
            else:
                dist_inc_gst_calc = None
                dist_profit_margin = None
                retail_price_calc = None
                retail_profit_margin = None

            consolidated_rows.append(
                {
                    "Cost Type": cost_type["name"],
                    "Ex GST": f"${ex_gst:.2f}" if ex_gst else "-",
                    "Excise": f"${excise:.2f}" if excise else "-",
                    "Ex-GST+Excise": f"${ex_gst_plus_excise:.2f}"
                    if ex_gst_plus_excise
                    else "-",
                    "Excised": f"${excised:.2f}" if excised else "-",
                    "UnExcised": f"${unexcised:.2f}" if unexcised else "-",
                    "Distributor Inc GST": f"${dist_inc_gst_calc:.2f}"
                    if dist_inc_gst_calc
                    else "-",
                    "Dist Profit Margin": f"{dist_profit_margin:.1f}%"
                    if dist_profit_margin is not None
                    else "-",
                    "Retail Price": f"${retail_price_calc:.2f}"
                    if retail_price_calc
                    else "-",
                    "Retail Margin": f"{retail_profit_margin:.1f}%"
                    if retail_profit_margin is not None
                    else "-",
                }
            )

        consolidated_table = dash_table.DataTable(
            data=consolidated_rows,
            columns=[
                {"name": "Cost Type", "id": "Cost Type"},
                {"name": "Ex GST", "id": "Ex GST"},
                {"name": "Excise", "id": "Excise"},
                {"name": "Ex-GST+Excise", "id": "Ex-GST+Excise"},
                {"name": "Excised", "id": "Excised"},
                {"name": "UnExcised", "id": "UnExcised"},
                {"name": "Distributor Inc GST", "id": "Distributor Inc GST"},
                {"name": "Dist Profit Margin", "id": "Dist Profit Margin"},
                {"name": "Retail Price", "id": "Retail Price"},
                {"name": "Retail Margin", "id": "Retail Margin"},
            ],
            style_cell={"textAlign": "left", "fontSize": "10px", "padding": "4px"},
            style_header={
                "backgroundColor": "rgb(230, 230, 230)",
                "fontWeight": "bold",
            },
        )

        return (
            updated_product.get("name", "Product Details"),
            updated_product.get("sku", "-"),
            product_type,
            updated_product.get("name", "-"),
            updated_product.get("description") or "-",
            updated_product.get("base_unit") or "-",
            updated_product.get("size") or "-",
            (
                f"{float(updated_product.get('density_kg_per_l', 0) or 0):.3f}"
                if updated_product.get("density_kg_per_l") is not None
                and str(updated_product.get("density_kg_per_l", "")).strip() != ""
                else "-"
            ),
            (
                f"{float(updated_product.get('abv_percent', 0) or 0):.2f}%"
                if updated_product.get("abv_percent") is not None
                and str(updated_product.get("abv_percent", "")).strip() != ""
                else "-"
            ),
            consolidated_table,
        )

    # Open inventory adjustment modal
    @app.callback(
        [
            Output("adjust-inventory-modal", "is_open", allow_duplicate=True),
            Output("adjust-product-name", "children", allow_duplicate=True),
            Output("adjust-current-stock", "children", allow_duplicate=True),
            Output("adjust-product-id-hidden", "children", allow_duplicate=True),
            Output("adjust-quantity", "value", allow_duplicate=True),
            Output("adjust-unit-cost", "value", allow_duplicate=True),
            Output("adjust-lot-code", "value", allow_duplicate=True),
            Output("adjust-notes", "value", allow_duplicate=True),
            Output("adjust-type", "value", allow_duplicate=True),
            Output("adjust-quantity-label", "children", allow_duplicate=True),
            Output("adjust-usage-metadata", "children", allow_duplicate=True),
        ],
        [Input("adjust-inventory-btn", "n_clicks")],
        [State("products-table", "selected_rows"), State("products-table", "data")],
        prevent_initial_call=True,
    )
    def open_adjust_inventory_modal(n_clicks, selected_rows, data):
        """Open inventory adjustment modal and populate product info."""
        if not n_clicks or not selected_rows or not data:
            raise PreventUpdate

        product = data[selected_rows[0]]
        product_id = product.get("id")
        product_name = product.get("name", "Unknown Product")

        # Get current stock
        current_stock = "-"
        if product_id:
            try:
                soh_response = make_api_request(
                    "GET", f"/inventory/product/{product_id}/soh"
                )
                if isinstance(soh_response, dict) and "error" not in soh_response:
                    stock_kg = soh_response.get("stock_on_hand_kg", 0.0) or 0.0
                    current_stock = f"{stock_kg:.3f} kg"
            except Exception as e:
                print(f"Error fetching stock: {e}")
                current_stock = "Unknown"

        # Determine usage unit and supporting metadata for conversions
        usage_unit_raw = product.get("usage_unit")
        usage_unit_display = (
            str(usage_unit_raw).strip().upper() if usage_unit_raw else "KG"
        )
        if not usage_unit_display:
            usage_unit_display = "KG"

        def _safe_float(value):
            if value is None or value == "":
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        density_value = _safe_float(product.get("density_kg_per_l"))
        weight_value = _safe_float(product.get("weight_kg"))

        quantity_label = f"Quantity ({usage_unit_display}) *"
        usage_metadata = json.dumps(
            {
                "usage_unit": usage_unit_display,
                "density_kg_per_l": density_value,
                "weight_kg": weight_value,
            }
        )

        return (
            True,  # is_open
            product_name,  # product_name
            current_stock,  # current_stock
            product_id or "",  # product_id (hidden)
            None,  # quantity
            None,  # unit_cost
            None,  # lot_code
            "",  # notes
            "INCREASE",  # adjustment_type
            quantity_label,  # quantity label
            usage_metadata,  # usage metadata for conversions
        )

    # Close inventory adjustment modal
    @app.callback(
        Output("adjust-inventory-modal", "is_open", allow_duplicate=True),
        [
            Input("adjust-cancel-btn", "n_clicks"),
            Input("adjust-confirm-btn", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def close_adjust_modal(cancel_clicks, confirm_clicks):
        """Close modal on cancel or confirm."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        return False

    # Apply inventory adjustment
    @app.callback(
        [
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
            Output("product-detail-stock", "children", allow_duplicate=True),
        ],
        [Input("adjust-confirm-btn", "n_clicks")],
        [
            State("adjust-product-id-hidden", "children"),
            State("adjust-type", "value"),
            State("adjust-quantity", "value"),
            State("adjust-unit-cost", "value"),
            State("adjust-lot-code", "value"),
            State("adjust-notes", "value"),
            State("adjust-usage-metadata", "children"),
        ],
        prevent_initial_call=True,
    )
    def apply_inventory_adjustment(
        n_clicks,
        product_id,
        adjustment_type,
        quantity,
        unit_cost,
        lot_code,
        notes,
        usage_metadata,
    ):
        """Apply inventory adjustment."""
        if not n_clicks:
            raise PreventUpdate

        if not product_id:
            return True, "Error", "Product ID not found", no_update

        if not adjustment_type or quantity is None:
            return True, "Error", "Adjustment Type and Quantity are required", no_update

        try:
            quantity_value = float(quantity)
        except (TypeError, ValueError):
            return True, "Error", "Quantity must be a number", no_update

        def _safe_float(value):
            if value in (None, "", "null"):
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        usage_unit = None
        density_val = None
        weight_val = None
        if usage_metadata:
            try:
                metadata = json.loads(usage_metadata)
            except (TypeError, json.JSONDecodeError):
                metadata = {}
            else:
                usage_unit = metadata.get("usage_unit")
                density_val = _safe_float(metadata.get("density_kg_per_l"))
                weight_val = _safe_float(metadata.get("weight_kg"))

        usage_unit_display = str(usage_unit).strip().upper() if usage_unit else "KG"

        def convert_quantity_to_kg(qty, unit_code, density_value, weight_value):
            if qty is None:
                return None, "Quantity is required"

            unit = (unit_code or "").strip().upper()
            if unit in ("", "KG", "KILOGRAM", "KILOGRAMS"):
                return qty, None

            mass_to_kg = {
                "MG": 0.000001,
                "G": 0.001,
                "GRAM": 0.001,
                "GRAMS": 0.001,
                "KG": 1.0,
                "KILOGRAM": 1.0,
                "KILOGRAMS": 1.0,
                "TON": 1000.0,
                "TONNE": 1000.0,
                "TONNES": 1000.0,
            }
            if unit in mass_to_kg:
                return qty * mass_to_kg[unit], None

            volume_to_l = {
                "ML": 0.001,
                "MILLILITER": 0.001,
                "MILLILITRE": 0.001,
                "L": 1.0,
                "LT": 1.0,
                "LTR": 1.0,
                "LITRE": 1.0,
                "LITER": 1.0,
            }
            if unit in volume_to_l:
                if density_value and density_value > 0:
                    liters = qty * volume_to_l[unit]
                    return liters * density_value, None
                return (
                    None,
                    "Cannot convert quantity without density (kg/L). Please set the product density or enter quantity in kg.",
                )

            each_units = {"EA", "EACH", "UNIT", "UNITS", "ITEM", "CTN", "CARTON"}
            if unit in each_units:
                if weight_value and weight_value > 0:
                    return qty * weight_value, None
                return (
                    None,
                    "Cannot convert quantity without weight per unit. Please set the product weight or enter quantity in kg.",
                )

            return (
                None,
                f"Unsupported usage unit '{unit}'. Please enter quantity in kg or update unit configuration.",
            )

        quantity_kg, conversion_error = convert_quantity_to_kg(
            quantity_value, usage_unit_display, density_val, weight_val
        )

        if quantity_kg is None:
            return True, "Error", conversion_error, no_update

        conversion_note = None
        if usage_unit_display not in ("", "KG", "KILOGRAM", "KILOGRAMS"):
            conversion_note = (
                f"{quantity_value:g} {usage_unit_display} -> {quantity_kg:.3f} kg"
            )

        try:
            adjustment_data = {
                "product_id": product_id,
                "adjustment_type": adjustment_type,
                "quantity_kg": float(quantity_kg),
                "unit_cost": float(unit_cost) if unit_cost else None,
                "lot_id": None,  # Let API create new lot or use existing based on lot_code if needed
                "notes": notes.strip() if notes else None,
                "reference_type": "MANUAL",
                "reference_id": None,
            }

            response = make_api_request("POST", "/inventory/adjust", adjustment_data)

            if "error" in response:
                error_msg = response["error"]
                if isinstance(error_msg, dict) and "detail" in error_msg:
                    error_msg = error_msg["detail"]
                return (
                    True,
                    "Error",
                    f"Failed to adjust inventory: {error_msg}",
                    no_update,
                )

            # Refresh stock display
            try:
                soh_response = make_api_request(
                    "GET", f"/inventory/product/{product_id}/soh"
                )
                if isinstance(soh_response, dict) and "error" not in soh_response:
                    stock_kg = soh_response.get("stock_on_hand_kg", 0.0) or 0.0
                    new_stock = f"{stock_kg:.3f} kg"
                else:
                    new_stock = no_update
            except (ValueError, KeyError, TypeError):
                new_stock = no_update

            success_message = "Inventory adjusted successfully."
            if conversion_note:
                success_message += f" Converted {conversion_note}."
            if isinstance(new_stock, str):
                success_message += f" New stock: {new_stock}"

            return (True, "Success", success_message, new_stock)

        except Exception as e:
            return True, "Error", f"Failed to adjust inventory: {str(e)}", no_update

    # Load assembly definitions (formulas) for a product
    @app.callback(
        Output("product-assemblies-table", "data", allow_duplicate=True),
        [
            Input("product-form-modal", "is_open"),
            Input("product-form-hidden", "children"),
        ],
        prevent_initial_call=True,
    )
    def load_product_assemblies(modal_open, product_id):
        """Load assembly definitions (formulas) when product modal opens."""
        if not modal_open or not product_id:
            return []

        try:
            # Get all formulas for this product
            formulas_response = make_api_request(
                "GET", f"/formulas/?product_id={product_id}"
            )

            if isinstance(formulas_response, list):
                # Format for display in table - ensure all fields are flat (strings/numbers/booleans only)
                assembly_data = []
                for formula in formulas_response:
                    # Get lines safely - ensure it's a list, not an object
                    lines_list = formula.get("lines", [])
                    if not isinstance(lines_list, list):
                        lines_list = []

                    lines_count = len(lines_list)

                    # Calculate total cost and quantities from lines using actual product costs
                    total_cost = 0.0
                    total_quantity_kg = 0.0
                    total_quantity_l = 0.0

                    # Get parent product density for L calculations
                    parent_density = 0.0
                    if product_id:
                        try:
                            parent_resp = make_api_request(
                                "GET", f"/products/{product_id}"
                            )
                            if (
                                isinstance(parent_resp, dict)
                                and "error" not in parent_resp
                            ):
                                parent_density = float(
                                    parent_resp.get("density_kg_per_l", 0) or 0
                                )
                        except Exception:
                            pass

                    for line in lines_list:
                        if isinstance(line, dict):
                            qty_kg = float(line.get("quantity_kg", 0.0) or 0.0)
                            # Try to get unit cost from line, or fetch from product
                            unit_cost = line.get("unit_cost") or 0.0
                            if not unit_cost:
                                product_id_line = line.get("raw_material_id")
                                if product_id_line:
                                    try:
                                        prod_resp = make_api_request(
                                            "GET", f"/products/{product_id_line}"
                                        )
                                        if (
                                            isinstance(prod_resp, dict)
                                            and "error" not in prod_resp
                                        ):
                                            # Preserve 4 decimal places
                                            cost_val = (
                                                prod_resp.get("usage_cost_ex_gst")
                                                or prod_resp.get("purchase_cost_ex_gst")
                                                or 0
                                            )
                                            if cost_val:
                                                try:
                                                    unit_cost = round(
                                                        float(cost_val), 4
                                                    )
                                                except (ValueError, TypeError):
                                                    unit_cost = 0.0
                                            else:
                                                unit_cost = 0.0
                                    except (ValueError, KeyError, TypeError):
                                        pass
                            total_cost += (
                                qty_kg * float(unit_cost) if unit_cost else 0.0
                            )
                            total_quantity_kg += qty_kg

                    # Calculate quantity in liters if density available
                    if parent_density > 0:
                        total_quantity_l = total_quantity_kg / parent_density
                    else:
                        total_quantity_l = 0.0

                    # Calculate cost per kg and cost per L
                    cost_per_kg = (
                        total_cost / total_quantity_kg if total_quantity_kg > 0 else 0.0
                    )
                    cost_per_l = (
                        total_cost / total_quantity_l if total_quantity_l > 0 else 0.0
                    )

                    # Get yield_factor from formula
                    yield_factor = formula.get("yield_factor", 1.0)
                    if yield_factor is None:
                        yield_factor = 1.0
                    try:
                        yield_factor = float(yield_factor)
                    except (ValueError, TypeError):
                        yield_factor = 1.0

                    # Create flattened structure - no nested objects
                    assembly_data.append(
                        {
                            "formula_id": str(formula.get("id", "")),
                            "version": int(formula.get("version", 1)),
                            "formula_code": str(formula.get("formula_code", "")),
                            "formula_name": str(formula.get("formula_name", "")),
                            "yield_factor": round(yield_factor, 2),
                            "is_primary": "✓" if formula.get("is_active") else "",
                            "cost": f"${total_cost:.2f}" if total_cost > 0 else "-",
                            "cost_per_kg": round(cost_per_kg, 2),
                            "cost_per_l": round(cost_per_l, 2),
                            "lines_count": int(lines_count),  # Convert to int, not list
                        }
                    )

                return assembly_data

            return []
        except Exception as e:
            print(f"Error loading assemblies: {e}")
            return []

    # Toggle edit/delete/duplicate/archive buttons based on selection
    @app.callback(
        [
            Output("edit-assembly-btn", "disabled"),
            Output("duplicate-assembly-btn", "disabled"),
            Output("archive-assembly-btn", "disabled"),
        ],
        [Input("product-assemblies-table", "selected_rows")],
    )
    def toggle_assembly_buttons(selected_rows):
        """Enable/disable assembly action buttons based on selection."""
        disabled = not selected_rows or len(selected_rows) == 0
        return disabled, disabled, disabled

    # Open assembly form modal (for new/edit)
    @app.callback(
        [
            Output("assembly-form-modal", "is_open", allow_duplicate=True),
            Output("assembly-form-title", "children", allow_duplicate=True),
            Output("assembly-formula-id", "children", allow_duplicate=True),
            Output("assembly-product-id", "children", allow_duplicate=True),
            Output(
                "assembly-parent-product-id-hidden", "children", allow_duplicate=True
            ),
            Output("assembly-name", "value", allow_duplicate=True),
            Output("assembly-yield-factor", "value", allow_duplicate=True),
            Output("assembly-lines-table", "data", allow_duplicate=True),
        ],
        [Input("new-assembly-btn", "n_clicks"), Input("edit-assembly-btn", "n_clicks")],
        [
            State("product-assemblies-table", "selected_rows"),
            State("product-assemblies-table", "data"),
            State("product-form-hidden", "children"),
        ],
        prevent_initial_call=True,
    )
    def open_assembly_modal(
        new_clicks, edit_clicks, selected_rows, assembly_data, product_id
    ):
        """Open assembly form modal for new or edit."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "new-assembly-btn":
            # New assembly - clear form
            # Get product's usage_unit for default unit
            if product_id:
                try:
                    product_resp = make_api_request("GET", f"/products/{product_id}")
                    if isinstance(product_resp, dict) and "error" not in product_resp:
                        (
                            product_resp.get("usage_unit")
                            or product_resp.get("base_unit")
                            or "kg"
                        )
                except Exception:
                    pass

            return (
                True,  # is_open
                "New Assembly Definition",  # title
                "",  # formula_id (hidden)
                product_id or "",  # product_id (hidden)
                product_id or "",  # parent_product_id (hidden)
                "",  # name
                1.0,  # yield_factor (default)
                [],  # lines data
            )

        elif button_id == "edit-assembly-btn":
            if not selected_rows or not assembly_data or not product_id:
                raise PreventUpdate

            formula_id = assembly_data[selected_rows[0]].get("formula_id")

            # Fetch formula details
            try:
                formula_response = make_api_request("GET", f"/formulas/{formula_id}")

                if (
                    isinstance(formula_response, dict)
                    and "error" not in formula_response
                ):
                    # Format lines for table
                    lines_data = []
                    primary_index = None
                    for idx, line in enumerate(formula_response.get("lines", [])):
                        # Get product details
                        line_product_id = line.get("raw_material_id")
                        product_sku = ""
                        product_name = line.get("ingredient_name", "")
                        unit_cost = 0.0
                        density = 0.0
                        product_usage_unit_for_cost = (
                            None  # Store for later use in line_cost calculation
                        )

                        if line_product_id:
                            try:
                                product_resp = make_api_request(
                                    "GET", f"/products/{line_product_id}"
                                )
                                if (
                                    isinstance(product_resp, dict)
                                    and "error" not in product_resp
                                ):
                                    product_sku = product_resp.get("sku", "")
                                    product_name = product_resp.get(
                                        "name", product_name
                                    )
                                    # Try ex_gst first, then inc_gst (for consistency)
                                    cost_val = (
                                        product_resp.get("usage_cost_ex_gst")
                                        or product_resp.get("purchase_cost_ex_gst")
                                        or product_resp.get("usage_cost_inc_gst")
                                        or product_resp.get("purchase_cost_inc_gst")
                                        or 0
                                    )
                                    if cost_val:
                                        try:
                                            unit_cost = round(float(cost_val), 4)
                                        except (ValueError, TypeError):
                                            unit_cost = 0.0
                                    else:
                                        unit_cost = 0.0
                                    density = float(
                                        product_resp.get("density_kg_per_l", 0) or 0
                                    )
                                    # Store usage_unit for line_cost calculation
                                    product_usage_unit_for_cost = (
                                        product_resp.get("usage_unit", "").upper()
                                        if product_resp.get("usage_unit")
                                        else None
                                    )
                            except (ValueError, KeyError, TypeError):
                                pass

                        quantity_kg = float(line.get("quantity_kg", 0.0) or 0.0)
                        # Get unit from line or product default
                        unit = line.get("unit", "kg") or "kg"
                        if line_product_id:
                            try:
                                product_resp_check = make_api_request(
                                    "GET", f"/products/{line_product_id}"
                                )
                                if (
                                    isinstance(product_resp_check, dict)
                                    and "error" not in product_resp_check
                                ):
                                    unit = (
                                        product_resp_check.get("usage_unit")
                                        or product_resp_check.get("base_unit")
                                        or unit
                                    )
                            except (ValueError, KeyError, TypeError):
                                pass

                        # Convert kg back to display unit (reverse conversion)
                        # For EA units, we need to preserve the original quantity from the line
                        # since quantity_kg might be 0 for EA items
                        unit_upper = unit.upper() if unit else "KG"

                        if unit_upper in ["EA", "EACH", "UNIT", "UNITS"]:
                            # For EA units, quantity_kg stores the quantity (if no weight) or quantity * weight_kg
                            # If product has weight_kg, reverse calculate: quantity = quantity_kg / weight_kg
                            # Otherwise, quantity_kg IS the quantity (we stored it that way)
                            if line_product_id:
                                try:
                                    product_resp_check = make_api_request(
                                        "GET", f"/products/{line_product_id}"
                                    )
                                    if (
                                        isinstance(product_resp_check, dict)
                                        and "error" not in product_resp_check
                                    ):
                                        weight_kg_per_item = (
                                            product_resp_check.get("weight_kg") or 0.0
                                        )
                                        if (
                                            weight_kg_per_item
                                            and weight_kg_per_item > 0
                                        ):
                                            # Product has weight - reverse calculate: quantity = quantity_kg / weight_kg
                                            quantity_display = quantity_kg / float(
                                                weight_kg_per_item
                                            )
                                        else:
                                            # No weight - quantity_kg stores the quantity directly
                                            quantity_display = quantity_kg
                                    else:
                                        # Can't get product - use quantity_kg directly
                                        quantity_display = quantity_kg
                                except Exception:
                                    # On error - use quantity_kg directly
                                    quantity_display = quantity_kg
                            else:
                                # No product ID - use quantity_kg directly
                                quantity_display = quantity_kg
                        elif unit_upper in ["G", "GRAM", "GRAMS"]:
                            # Convert kg back to grams
                            quantity_display = quantity_kg * 1000.0
                        elif unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                            # Convert kg back to liters using density
                            if density > 0:
                                quantity_display = quantity_kg / density
                            else:
                                quantity_display = quantity_kg  # Fallback
                        elif unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                            # Convert kg back to mL via L
                            if density > 0:
                                quantity_l = quantity_kg / density
                                quantity_display = quantity_l * 1000.0
                            else:
                                # Assume 1 mL = 1 g (water-like) if no density
                                quantity_display = quantity_kg * 1000.0
                        else:
                            # For kg, no conversion needed (quantity_display = quantity_kg)
                            quantity_display = quantity_kg

                        # Calculate quantity in L
                        quantity_l = 0.0
                        if density > 0:
                            quantity_l = quantity_kg / density

                        # Calculate line_cost - handle EA units correctly
                        # unit_cost is per product_usage_unit, so we need to use the correct quantity
                        if product_usage_unit_for_cost in [
                            "EA",
                            "EACH",
                            "UNIT",
                            "UNITS",
                        ]:
                            # For EA items, unit_cost is per item, so use quantity_display (in items)
                            line_cost = quantity_display * unit_cost
                        else:
                            # For weight/volume units, convert quantity to usage_unit first
                            # For now, use quantity_kg * unit_cost as fallback
                            # (The calculate_assembly_line_costs callback will recalculate this properly)
                            line_cost = quantity_kg * unit_cost

                        # Check if this is the primary line (first line or marked)
                        is_primary = line.get("is_primary", False) or (
                            idx == 0 and primary_index is None
                        )
                        if is_primary:
                            primary_index = idx

                        primary_button = "✓" if is_primary else "[Set Primary]"

                        # Calculate cost per kg and cost per L
                        cost_per_kg = 0.0
                        cost_per_l = 0.0
                        if unit_cost > 0 and product_usage_unit_for_cost:
                            # Unit cost is per product_usage_unit, need to convert to per kg and per L
                            usage_unit_upper = product_usage_unit_for_cost.upper()
                            if usage_unit_upper in ["KG", "KILOGRAM", "KILOGRAMS"]:
                                cost_per_kg = unit_cost
                                if density > 0:
                                    cost_per_l = unit_cost / density
                            elif usage_unit_upper in ["G", "GRAM", "GRAMS"]:
                                cost_per_kg = unit_cost * 1000.0  # $/g to $/kg
                                if density > 0:
                                    cost_per_l = (unit_cost * 1000.0) / density
                            elif usage_unit_upper in [
                                "L",
                                "LT",
                                "LTR",
                                "LITER",
                                "LITRE",
                            ]:
                                cost_per_l = unit_cost
                                if density > 0:
                                    cost_per_kg = unit_cost * density
                            elif usage_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                                cost_per_l = unit_cost * 1000.0  # $/mL to $/L
                                if density > 0:
                                    cost_per_kg = (unit_cost * 1000.0) * density
                            else:
                                # Fallback: assume per kg
                                cost_per_kg = unit_cost
                                if density > 0:
                                    cost_per_l = unit_cost / density
                        elif unit_cost > 0:
                            # No usage_unit specified - assume per kg (legacy behavior)
                            cost_per_kg = unit_cost
                            if density > 0:
                                cost_per_l = unit_cost / density

                        lines_data.append(
                            {
                                "sequence": line.get("sequence", idx + 1),
                                "product_search": f"{product_sku} - {product_name}"
                                if product_sku and product_name
                                else (product_sku or product_name or ""),
                                "product_id": line_product_id,
                                "product_sku": product_sku,
                                "product_name": product_name,
                                "quantity": round(quantity_display, 3),
                                "unit": unit,
                                "quantity_kg": round(quantity_kg, 3),
                                "quantity_l": round(quantity_l, 3),
                                "density": round(density, 6) if density > 0 else 0.0,
                                "unit_cost": round(unit_cost, 4),
                                "cost_per_kg": round(cost_per_kg, 4),
                                "cost_per_l": round(cost_per_l, 4),
                                "line_cost": round(line_cost, 4),
                                "is_primary": primary_button,
                                "is_primary_bool": is_primary,
                                "notes": line.get("notes", ""),
                            }
                        )

                    # Get yield_factor from formula or default to 1.0
                    yield_factor = formula_response.get("yield_factor", 1.0)
                    if yield_factor is None:
                        yield_factor = 1.0
                    try:
                        yield_factor = float(yield_factor)
                    except (ValueError, TypeError):
                        yield_factor = 1.0

                    return (
                        True,  # is_open
                        f"Edit Assembly: {formula_response.get('formula_name', '')}",  # title
                        formula_id,  # formula_id
                        product_id,  # product_id
                        product_id or "",  # parent_product_id (hidden)
                        formula_response.get("formula_name", ""),  # name
                        yield_factor,  # yield_factor
                        lines_data,  # lines data
                    )
            except Exception as e:
                print(f"Error loading formula: {e}")
                raise PreventUpdate

        raise PreventUpdate

    # Save assembly (create or update)
    @app.callback(
        [
            Output("assembly-form-modal", "is_open", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
            Output("product-assemblies-table", "data", allow_duplicate=True),
        ],
        [Input("assembly-save-btn", "n_clicks")],
        [
            State("assembly-formula-id", "children"),
            State("assembly-product-id", "children"),
            State("assembly-name", "value"),
            State("assembly-yield-factor", "value"),
            State("assembly-lines-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_assembly(n_clicks, formula_id, product_id, name, yield_factor, lines_data):
        """Save assembly definition (formula)."""
        if not n_clicks:
            raise PreventUpdate

        if not product_id or not name:
            return (
                False,
                True,
                "Error",
                "Product ID and Assembly Name are required",
                no_update,
            )

        try:
            # Format lines for API - use quantity_kg from calculations
            # Deduplicate by (product_id, sequence) to prevent duplicate lines
            seen_lines = set()
            formula_lines = []

            for i, line in enumerate(lines_data or []):
                product_id_line = line.get("product_id")
                if not product_id_line:
                    continue  # Skip lines without product

                # Check for duplicates based on product_id and sequence
                sequence = int(line.get("sequence", i + 1))
                line_key = (str(product_id_line), sequence)
                if line_key in seen_lines:
                    # Skip duplicate line
                    continue
                seen_lines.add(line_key)

                # Get the original quantity and unit from the line
                quantity = line.get("quantity")
                # Handle both string and numeric values
                if quantity is None or quantity == "":
                    quantity = 0.0
                else:
                    try:
                        quantity = float(quantity)
                    except (ValueError, TypeError):
                        quantity = 0.0

                unit = str(line.get("unit", "kg") or "kg").upper()

                print(
                    f"[save_assembly] Line {sequence}: quantity={quantity}, unit={unit}, quantity_kg from table={line.get('quantity_kg')}"
                )

                # Convert quantity to kg based on the unit
                # For EA units, always use quantity from table (not quantity_kg which might be 0)
                # For other units, use quantity_kg if available, otherwise convert from quantity
                quantity_kg = line.get("quantity_kg")

                # For EA units, always recalculate from quantity (don't use quantity_kg which might be 0)
                if unit in ["EA", "EACH", "UNIT", "UNITS"]:
                    # For "each" units, try to get weight per item
                    # If weight_kg is available, use it; otherwise store quantity in quantity_kg as-is
                    # IMPORTANT: Always use quantity from the table, not quantity_kg (which might be 0)
                    quantity_kg = quantity  # Default: store quantity as quantity_kg
                    if product_id_line:
                        try:
                            product_resp = make_api_request(
                                "GET", f"/products/{product_id_line}"
                            )
                            if (
                                isinstance(product_resp, dict)
                                and "error" not in product_resp
                            ):
                                # Check if product has weight_kg field
                                weight_kg_per_item = (
                                    product_resp.get("weight_kg") or 0.0
                                )
                                if weight_kg_per_item:
                                    try:
                                        # Calculate actual weight: quantity * weight per item
                                        quantity_kg = quantity * float(
                                            weight_kg_per_item
                                        )
                                        print(
                                            f"[save_assembly] EA item with weight: quantity={quantity}, weight_kg_per_item={weight_kg_per_item}, quantity_kg={quantity_kg}"
                                        )
                                    except (ValueError, TypeError):
                                        # Fallback: store quantity as quantity_kg
                                        quantity_kg = quantity
                                        print(
                                            f"[save_assembly] EA item weight conversion error, using quantity as quantity_kg: {quantity_kg}"
                                        )
                        except Exception as e:
                            # On error, store quantity as quantity_kg
                            quantity_kg = quantity
                            print(
                                f"[save_assembly] EA item error fetching product: {e}, using quantity as quantity_kg: {quantity_kg}"
                            )
                    else:
                        print(
                            f"[save_assembly] EA item no product_id, using quantity as quantity_kg: {quantity_kg}"
                        )
                    # If no weight_kg, quantity_kg = quantity (preserves the quantity value)
                elif quantity_kg is None:
                    # Convert based on unit (for non-EA units)
                    if unit in ["G", "GRAM", "GRAMS"]:
                        quantity_kg = quantity / 1000.0
                    elif unit in ["L", "LT", "LTR", "LITER", "LITRE"]:
                        # Need density for L to kg conversion - try to get from product
                        density = 0.0
                        if product_id_line:
                            try:
                                product_resp = make_api_request(
                                    "GET", f"/products/{product_id_line}"
                                )
                                if (
                                    isinstance(product_resp, dict)
                                    and "error" not in product_resp
                                ):
                                    density_val = (
                                        product_resp.get("density_kg_per_l", 0) or 0
                                    )
                                    try:
                                        density = float(density_val)
                                    except (ValueError, TypeError):
                                        pass
                            except Exception:
                                pass
                        if density > 0:
                            quantity_kg = quantity * density
                        else:
                            quantity_kg = quantity  # Fallback: assume 1 L = 1 kg
                    elif unit in ["ML", "MILLILITER", "MILLILITRE"]:
                        # Convert mL to L, then L to kg using density
                        quantity_l = quantity / 1000.0
                        density = 0.0
                        if product_id_line:
                            try:
                                product_resp = make_api_request(
                                    "GET", f"/products/{product_id_line}"
                                )
                                if (
                                    isinstance(product_resp, dict)
                                    and "error" not in product_resp
                                ):
                                    density_val = (
                                        product_resp.get("density_kg_per_l", 0) or 0
                                    )
                                    try:
                                        density = float(density_val)
                                    except (ValueError, TypeError):
                                        pass
                            except Exception:
                                pass
                        if density > 0:
                            quantity_kg = quantity_l * density
                        else:
                            # Assume 1 mL = 1 g (water-like) if no density
                            quantity_kg = quantity / 1000.0
                    else:
                        # Default: assume kg
                        quantity_kg = quantity

                # Ensure all required fields are present and properly typed
                formula_lines.append(
                    {
                        "raw_material_id": str(product_id_line),
                        "quantity_kg": float(quantity_kg),
                        "sequence": int(sequence),
                        "notes": str(line.get("notes", "") or ""),
                        "unit": str(line.get("unit", "kg") or "kg"),
                    }
                )

            # Validate we have at least one line for new formulas
            if not formula_id and len(formula_lines) == 0:
                return (
                    True,
                    True,
                    "Error",
                    "At least one assembly line is required",
                    no_update,
                )

            # Process yield_factor - default to 1.0 if not provided
            yield_factor_val = 1.0
            if yield_factor is not None and str(yield_factor).strip():
                try:
                    yield_factor_val = float(yield_factor)
                    if yield_factor_val <= 0:
                        yield_factor_val = 1.0
                except (ValueError, TypeError):
                    yield_factor_val = 1.0

            if formula_id:
                # Update existing formula
                # First update header
                update_data = {
                    "formula_name": name,
                    "yield_factor": yield_factor_val,
                }
                update_response = make_api_request(
                    "PUT", f"/formulas/{formula_id}", update_data
                )
                if isinstance(update_response, dict) and "error" in update_response:
                    return (
                        True,
                        True,
                        "Error",
                        f"Failed to update assembly: {update_response.get('error', 'Unknown error')}",
                        no_update,
                    )

                # Then replace lines
                lines_response = make_api_request(
                    "PUT", f"/formulas/{formula_id}/lines", formula_lines
                )
                if isinstance(lines_response, dict) and "error" in lines_response:
                    return (
                        True,
                        True,
                        "Error",
                        f"Failed to update assembly lines: {lines_response.get('error', 'Unknown error')}",
                        no_update,
                    )

                message = f"Assembly '{name}' updated successfully"
            else:
                # Create new formula - generate formula code automatically
                # Fetch all formulas to generate next code
                all_formulas = make_api_request("GET", "/formulas/")
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

                # Create new formula
                formula_data = {
                    "product_id": str(product_id),
                    "formula_code": str(next_code),
                    "formula_name": str(name),
                    "version": 1,
                    "is_active": True,
                    "yield_factor": yield_factor_val,
                    "lines": formula_lines,
                }

                create_response = make_api_request("POST", "/formulas/", formula_data)
                if isinstance(create_response, dict) and "error" in create_response:
                    error_msg = create_response.get("error", "Unknown error")
                    # Try to extract a more user-friendly error message
                    if isinstance(error_msg, str):
                        try:
                            import json

                            error_dict = json.loads(error_msg)
                            if isinstance(error_dict, dict) and "message" in error_dict:
                                error_msg = error_dict["message"]
                        except (ValueError, KeyError, TypeError):
                            pass
                    return (
                        True,  # Keep modal open on error
                        True,
                        "Error",
                        f"Failed to save assembly: {error_msg}",
                        no_update,
                    )

                message = f"Assembly '{name}' created successfully"

            # Reload assemblies table
            try:
                formulas_response = make_api_request(
                    "GET", f"/formulas/?product_id={product_id}"
                )

                if isinstance(formulas_response, list):
                    assembly_data = []
                    # Get parent product density for L calculations
                    parent_density = 0.0
                    try:
                        parent_resp = make_api_request("GET", f"/products/{product_id}")
                        if isinstance(parent_resp, dict) and "error" not in parent_resp:
                            parent_density = float(
                                parent_resp.get("density_kg_per_l", 0) or 0
                            )
                    except Exception:
                        pass

                    for formula in formulas_response:
                        # Get lines safely - ensure it's a list, not an object
                        lines_list = formula.get("lines", [])
                        if not isinstance(lines_list, list):
                            lines_list = []

                        lines_count = len(lines_list)

                        # Calculate total cost and quantities from lines
                        total_cost = 0.0
                        total_quantity_kg = 0.0
                        for line in lines_list:
                            if isinstance(line, dict):
                                qty_kg = float(line.get("quantity_kg", 0.0) or 0.0)
                                unit_cost = line.get("unit_cost") or 0.0
                                if not unit_cost:
                                    product_id_line = line.get("raw_material_id")
                                    if product_id_line:
                                        try:
                                            prod_resp = make_api_request(
                                                "GET", f"/products/{product_id_line}"
                                            )
                                            if (
                                                isinstance(prod_resp, dict)
                                                and "error" not in prod_resp
                                            ):
                                                # Preserve 4 decimal places
                                                cost_val = (
                                                    prod_resp.get("usage_cost_ex_gst")
                                                    or prod_resp.get(
                                                        "purchase_cost_ex_gst"
                                                    )
                                                    or 0
                                                )
                                                if cost_val:
                                                    try:
                                                        unit_cost = round(
                                                            float(cost_val), 4
                                                        )
                                                    except (ValueError, TypeError):
                                                        unit_cost = 0.0
                                                else:
                                                    unit_cost = 0.0
                                        except (ValueError, KeyError, TypeError):
                                            pass
                                total_cost += (
                                    qty_kg * float(unit_cost) if unit_cost else 0.0
                                )
                                total_quantity_kg += qty_kg

                        # Calculate quantity in liters if density available
                        total_quantity_l = (
                            total_quantity_kg / parent_density
                            if parent_density > 0
                            else 0.0
                        )

                        # Calculate cost per kg and cost per L
                        cost_per_kg = (
                            total_cost / total_quantity_kg
                            if total_quantity_kg > 0
                            else 0.0
                        )
                        cost_per_l = (
                            total_cost / total_quantity_l
                            if total_quantity_l > 0
                            else 0.0
                        )

                        # Get yield_factor from formula
                        yield_factor = formula.get("yield_factor", 1.0)
                        if yield_factor is None:
                            yield_factor = 1.0
                        try:
                            yield_factor = float(yield_factor)
                        except (ValueError, TypeError):
                            yield_factor = 1.0

                        # Create flattened structure - no nested objects
                        assembly_data.append(
                            {
                                "formula_id": str(formula.get("id", "")),
                                "version": int(formula.get("version", 1)),
                                "formula_code": str(formula.get("formula_code", "")),
                                "formula_name": str(formula.get("formula_name", "")),
                                "yield_factor": round(yield_factor, 2),
                                "is_primary": "✓" if formula.get("is_active") else "",
                                "cost": f"${total_cost:.2f}" if total_cost > 0 else "-",
                                "cost_per_kg": round(cost_per_kg, 2),
                                "cost_per_l": round(cost_per_l, 2),
                                "lines_count": int(lines_count),
                            }
                        )

                    return False, True, "Success", message, assembly_data
            except Exception as e:
                print(f"Error reloading assemblies: {e}")

            return False, True, "Success", message, no_update

        except Exception as e:
            return True, True, "Error", f"Failed to save assembly: {str(e)}", no_update

    # Cancel assembly form
    @app.callback(
        Output("assembly-form-modal", "is_open", allow_duplicate=True),
        [Input("assembly-cancel-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def cancel_assembly_form(n_clicks):
        """Close assembly form modal."""
        if n_clicks:
            return False
        raise PreventUpdate

    # Duplicate assembly (create new version)
    @app.callback(
        [
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
            Output("product-assemblies-table", "data", allow_duplicate=True),
        ],
        [Input("duplicate-assembly-btn", "n_clicks")],
        [
            State("product-assemblies-table", "selected_rows"),
            State("product-assemblies-table", "data"),
            State("product-form-hidden", "children"),
        ],
        prevent_initial_call=True,
    )
    def duplicate_assembly(n_clicks, selected_rows, assembly_data, product_id):
        """Duplicate assembly as new version."""
        if not n_clicks or not selected_rows or not assembly_data or not product_id:
            raise PreventUpdate

        formula_id = assembly_data[selected_rows[0]].get("formula_id")

        try:
            # Create new version using API
            make_api_request("POST", f"/formulas/{formula_id}/new-version", {})

            # Reload assemblies
            formulas_response = make_api_request(
                "GET", f"/formulas/?product_id={product_id}"
            )

            if isinstance(formulas_response, list):
                assembly_data_new = []
                # Get parent product density for L calculations
                parent_density = 0.0
                try:
                    parent_resp = make_api_request("GET", f"/products/{product_id}")
                    if isinstance(parent_resp, dict) and "error" not in parent_resp:
                        parent_density = float(
                            parent_resp.get("density_kg_per_l", 0) or 0
                        )
                except Exception:
                    pass

                for formula in formulas_response:
                    lines_list = formula.get("lines", [])
                    if not isinstance(lines_list, list):
                        lines_list = []
                    lines_count = len(lines_list)

                    # Calculate total cost and quantities from lines
                    total_cost = 0.0
                    total_quantity_kg = 0.0
                    for line in lines_list:
                        if isinstance(line, dict):
                            qty_kg = float(line.get("quantity_kg", 0.0) or 0.0)
                            unit_cost = line.get("unit_cost") or 0.0
                            if not unit_cost:
                                product_id_line = line.get("raw_material_id")
                                if product_id_line:
                                    try:
                                        prod_resp = make_api_request(
                                            "GET", f"/products/{product_id_line}"
                                        )
                                        if (
                                            isinstance(prod_resp, dict)
                                            and "error" not in prod_resp
                                        ):
                                            # Preserve 4 decimal places
                                            cost_val = (
                                                prod_resp.get("usage_cost_ex_gst")
                                                or prod_resp.get("purchase_cost_ex_gst")
                                                or 0
                                            )
                                            if cost_val:
                                                try:
                                                    unit_cost = round(
                                                        float(cost_val), 4
                                                    )
                                                except (ValueError, TypeError):
                                                    unit_cost = 0.0
                                            else:
                                                unit_cost = 0.0
                                    except (ValueError, KeyError, TypeError):
                                        pass
                            total_cost += (
                                qty_kg * float(unit_cost) if unit_cost else 0.0
                            )
                            total_quantity_kg += qty_kg

                    # Calculate quantity in liters if density available
                    total_quantity_l = (
                        total_quantity_kg / parent_density
                        if parent_density > 0
                        else 0.0
                    )

                    # Calculate cost per kg and cost per L
                    cost_per_kg = (
                        total_cost / total_quantity_kg if total_quantity_kg > 0 else 0.0
                    )
                    cost_per_l = (
                        total_cost / total_quantity_l if total_quantity_l > 0 else 0.0
                    )

                    # Get yield_factor from formula
                    yield_factor = formula.get("yield_factor", 1.0)
                    if yield_factor is None:
                        yield_factor = 1.0
                    try:
                        yield_factor = float(yield_factor)
                    except (ValueError, TypeError):
                        yield_factor = 1.0

                    assembly_data_new.append(
                        {
                            "formula_id": str(formula.get("id", "")),
                            "version": int(formula.get("version", 1)),
                            "formula_code": str(formula.get("formula_code", "")),
                            "formula_name": str(formula.get("formula_name", "")),
                            "yield_factor": round(yield_factor, 2),
                            "is_primary": "✓" if formula.get("is_active") else "",
                            "cost": f"${total_cost:.2f}" if total_cost > 0 else "-",
                            "cost_per_kg": round(cost_per_kg, 2),
                            "cost_per_l": round(cost_per_l, 2),
                            "lines_count": int(lines_count),
                        }
                    )

                return (
                    True,
                    "Success",
                    "Assembly duplicated successfully",
                    assembly_data_new,
                )

            return True, "Success", "Assembly duplicated successfully", no_update

        except Exception as e:
            return True, "Error", f"Failed to duplicate assembly: {str(e)}", no_update

    # Archive assembly (set is_active=False)
    @app.callback(
        [
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
            Output("product-assemblies-table", "data", allow_duplicate=True),
        ],
        [Input("archive-assembly-btn", "n_clicks")],
        [
            State("product-assemblies-table", "selected_rows"),
            State("product-assemblies-table", "data"),
            State("product-form-hidden", "children"),
        ],
        prevent_initial_call=True,
    )
    def archive_assembly(n_clicks, selected_rows, assembly_data, product_id):
        """Archive assembly (set is_active=False)."""
        if not n_clicks or not selected_rows or not assembly_data or not product_id:
            raise PreventUpdate

        formula_id = assembly_data[selected_rows[0]].get("formula_id")

        try:
            # Update formula to set is_active=False
            make_api_request("PUT", f"/formulas/{formula_id}", {"is_active": False})

            # Reload assemblies
            formulas_response = make_api_request(
                "GET", f"/formulas/?product_id={product_id}"
            )

            if isinstance(formulas_response, list):
                assembly_data_new = []
                # Get parent product density for L calculations
                parent_density = 0.0
                try:
                    parent_resp = make_api_request("GET", f"/products/{product_id}")
                    if isinstance(parent_resp, dict) and "error" not in parent_resp:
                        parent_density = float(
                            parent_resp.get("density_kg_per_l", 0) or 0
                        )
                except Exception:
                    pass

                for formula in formulas_response:
                    lines_list = formula.get("lines", [])
                    if not isinstance(lines_list, list):
                        lines_list = []
                    lines_count = len(lines_list)

                    # Calculate total cost and quantities from lines
                    total_cost = 0.0
                    total_quantity_kg = 0.0
                    for line in lines_list:
                        if isinstance(line, dict):
                            qty_kg = float(line.get("quantity_kg", 0.0) or 0.0)
                            unit_cost = line.get("unit_cost") or 0.0
                            if not unit_cost:
                                product_id_line = line.get("raw_material_id")
                                if product_id_line:
                                    try:
                                        prod_resp = make_api_request(
                                            "GET", f"/products/{product_id_line}"
                                        )
                                        if (
                                            isinstance(prod_resp, dict)
                                            and "error" not in prod_resp
                                        ):
                                            # Preserve 4 decimal places
                                            cost_val = (
                                                prod_resp.get("usage_cost_ex_gst")
                                                or prod_resp.get("purchase_cost_ex_gst")
                                                or 0
                                            )
                                            if cost_val:
                                                try:
                                                    unit_cost = round(
                                                        float(cost_val), 4
                                                    )
                                                except (ValueError, TypeError):
                                                    unit_cost = 0.0
                                            else:
                                                unit_cost = 0.0
                                    except (ValueError, KeyError, TypeError):
                                        pass
                            total_cost += (
                                qty_kg * float(unit_cost) if unit_cost else 0.0
                            )
                            total_quantity_kg += qty_kg

                    # Calculate quantity in liters if density available
                    total_quantity_l = (
                        total_quantity_kg / parent_density
                        if parent_density > 0
                        else 0.0
                    )

                    # Calculate cost per kg and cost per L
                    cost_per_kg = (
                        total_cost / total_quantity_kg if total_quantity_kg > 0 else 0.0
                    )
                    cost_per_l = (
                        total_cost / total_quantity_l if total_quantity_l > 0 else 0.0
                    )

                    # Get yield_factor from formula
                    yield_factor = formula.get("yield_factor", 1.0)
                    if yield_factor is None:
                        yield_factor = 1.0
                    try:
                        yield_factor = float(yield_factor)
                    except (ValueError, TypeError):
                        yield_factor = 1.0

                    assembly_data_new.append(
                        {
                            "formula_id": str(formula.get("id", "")),
                            "version": int(formula.get("version", 1)),
                            "formula_code": str(formula.get("formula_code", "")),
                            "formula_name": str(formula.get("formula_name", "")),
                            "yield_factor": round(yield_factor, 2),
                            "is_primary": "✓" if formula.get("is_active") else "",
                            "cost": f"${total_cost:.2f}" if total_cost > 0 else "-",
                            "cost_per_kg": round(cost_per_kg, 2),
                            "cost_per_l": round(cost_per_l, 2),
                            "lines_count": int(lines_count),
                        }
                    )

                return (
                    True,
                    "Success",
                    "Assembly archived successfully",
                    assembly_data_new,
                )

            return True, "Success", "Assembly archived successfully", no_update

        except Exception as e:
            return True, "Error", f"Failed to archive assembly: {str(e)}", no_update

    # Add line to assembly table
    @app.callback(
        Output("assembly-lines-table", "data", allow_duplicate=True),
        [Input("assembly-add-line-btn", "n_clicks")],
        [
            State("assembly-lines-table", "data"),
            State("assembly-product-id", "children"),
        ],
        prevent_initial_call=True,
    )
    def add_assembly_line(n_clicks, current_data, product_id):
        """Add a new empty line to assembly table."""
        if not n_clicks:
            raise PreventUpdate

        # Get default unit from product
        default_unit = "kg"
        if product_id:
            try:
                product_resp = make_api_request("GET", f"/products/{product_id}")
                if isinstance(product_resp, dict) and "error" not in product_resp:
                    default_unit = (
                        product_resp.get("usage_unit")
                        or product_resp.get("base_unit")
                        or "kg"
                    )
            except Exception:
                pass

        new_line = {
            "sequence": len(current_data) + 1 if current_data else 1,
            "product_search": "",
            "product_id": "",
            "product_sku": "",
            "product_name": "",
            "quantity": 0.0,
            "unit": default_unit,
            "quantity_kg": 0.0,
            "quantity_l": 0.0,
            "unit_cost": 0.0,
            "line_cost": 0.0,
            "is_primary": "[Set Primary]",
            "is_primary_bool": False,
            "notes": "",
        }

        return (current_data or []) + [new_line]

    # Handle primary button click
    @app.callback(
        Output("assembly-lines-table", "data", allow_duplicate=True),
        [Input("assembly-lines-table", "active_cell")],
        [State("assembly-lines-table", "data")],
        prevent_initial_call=True,
    )
    def handle_primary_button(active_cell, lines_data):
        """Handle click on primary button column."""
        if not active_cell or not lines_data:
            raise PreventUpdate

        col_id = active_cell.get("column_id")
        row_idx = active_cell.get("row")

        # Only handle clicks on primary column
        if col_id != "is_primary" or row_idx is None:
            raise PreventUpdate

        # Update all lines - set primary to False, then set selected one to True
        updated_data = []
        for idx, line in enumerate(lines_data):
            is_primary = idx == row_idx
            updated_line = {
                **line,
                "is_primary": "✓" if is_primary else "[Set Primary]",
                "is_primary_bool": is_primary,
            }
            updated_data.append(updated_line)

        return updated_data

    # Delete line from assembly table
    @app.callback(
        Output("assembly-lines-table", "data", allow_duplicate=True),
        [Input("assembly-delete-line-btn", "n_clicks")],
        [
            State("assembly-lines-table", "data"),
            State("assembly-lines-table", "selected_rows"),
        ],
        prevent_initial_call=True,
    )
    def delete_assembly_line(n_clicks, lines_data, selected_rows):
        """Delete selected line from assembly table."""
        if not n_clicks or not lines_data or not selected_rows:
            raise PreventUpdate

        # Remove selected rows and renumber sequences
        updated_data = []
        for idx, line in enumerate(lines_data):
            if idx not in selected_rows:
                updated_line = {
                    **line,
                    "sequence": len(updated_data) + 1,
                }
                updated_data.append(updated_line)

        return updated_data

    # Move assembly line up
    @app.callback(
        Output("assembly-lines-table", "data", allow_duplicate=True),
        [Input("assembly-move-up-btn", "n_clicks")],
        [
            State("assembly-lines-table", "data"),
            State("assembly-lines-table", "selected_rows"),
        ],
        prevent_initial_call=True,
    )
    def move_assembly_line_up(n_clicks, lines_data, selected_rows):
        """Move selected assembly line up (decrease sequence)."""
        if (
            not n_clicks
            or not lines_data
            or not selected_rows
            or len(selected_rows) == 0
        ):
            raise PreventUpdate

        selected_idx = selected_rows[0]
        if selected_idx <= 0:
            # Already at top, can't move up
            raise PreventUpdate

        # Swap with line above
        updated_data = lines_data.copy()
        current_line = updated_data[selected_idx].copy()
        previous_line = updated_data[selected_idx - 1].copy()

        # Swap sequences
        current_seq = current_line.get("sequence", selected_idx + 1)
        previous_seq = previous_line.get("sequence", selected_idx)

        current_line["sequence"] = previous_seq
        previous_line["sequence"] = current_seq

        # Swap the lines
        updated_data[selected_idx] = current_line
        updated_data[selected_idx - 1] = previous_line

        return updated_data

    # Move assembly line down
    @app.callback(
        Output("assembly-lines-table", "data", allow_duplicate=True),
        [Input("assembly-move-down-btn", "n_clicks")],
        [
            State("assembly-lines-table", "data"),
            State("assembly-lines-table", "selected_rows"),
        ],
        prevent_initial_call=True,
    )
    def move_assembly_line_down(n_clicks, lines_data, selected_rows):
        """Move selected assembly line down (increase sequence)."""
        if (
            not n_clicks
            or not lines_data
            or not selected_rows
            or len(selected_rows) == 0
        ):
            raise PreventUpdate

        selected_idx = selected_rows[0]
        if selected_idx >= len(lines_data) - 1:
            # Already at bottom, can't move down
            raise PreventUpdate

        # Swap with line below
        updated_data = lines_data.copy()
        current_line = updated_data[selected_idx].copy()
        next_line = updated_data[selected_idx + 1].copy()

        # Swap sequences
        current_seq = current_line.get("sequence", selected_idx + 1)
        next_seq = next_line.get("sequence", selected_idx + 2)

        current_line["sequence"] = next_seq
        next_line["sequence"] = current_seq

        # Swap the lines
        updated_data[selected_idx] = current_line
        updated_data[selected_idx + 1] = next_line

        return updated_data

    # Edit line - show edit area and populate fields
    @app.callback(
        [
            Output("assembly-line-edit-card", "style"),
            Output("assembly-line-edit-product", "value"),
            Output("assembly-line-edit-quantity", "value"),
            Output("assembly-line-edit-unit", "value"),
            Output("assembly-line-edit-notes", "value"),
            Output("assembly-line-edit-index", "children"),
        ],
        [Input("assembly-edit-line-btn", "n_clicks")],
        [
            State("assembly-lines-table", "data"),
            State("assembly-lines-table", "selected_rows"),
        ],
        prevent_initial_call=True,
    )
    def open_edit_line_area(n_clicks, lines_data, selected_rows):
        """Open edit area for selected line."""
        if not n_clicks or not lines_data or not selected_rows:
            raise PreventUpdate

        selected_line = lines_data[selected_rows[0]]

        return (
            {"display": "block"},  # Show edit card
            selected_line.get("product_id", ""),
            selected_line.get("quantity", 0.0),
            selected_line.get("unit", ""),
            selected_line.get("notes", ""),
            str(selected_rows[0]),  # Store index for saving
        )

    # Cancel line edit - hide edit area
    @app.callback(
        Output("assembly-line-edit-card", "style", allow_duplicate=True),
        [Input("assembly-line-cancel-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def cancel_edit_line(n_clicks):
        """Hide edit area."""
        if not n_clicks:
            raise PreventUpdate
        return {"display": "none"}

    # Save edited line
    @app.callback(
        [
            Output("assembly-lines-table", "data", allow_duplicate=True),
            Output("assembly-line-edit-card", "style", allow_duplicate=True),
        ],
        [Input("assembly-line-save-btn", "n_clicks")],
        [
            State("assembly-lines-table", "data"),
            State("assembly-line-edit-index", "children"),
            State("assembly-line-edit-product", "value"),
            State("assembly-line-edit-quantity", "value"),
            State("assembly-line-edit-unit", "value"),
            State("assembly-line-edit-notes", "value"),
            State("assembly-product-id", "children"),
        ],
        prevent_initial_call=True,
    )
    def save_edited_line(
        n_clicks,
        lines_data,
        edit_index,
        product_id,
        quantity,
        unit,
        notes,
        parent_product_id,
    ):
        """Save edited line back to table."""
        if not n_clicks or not lines_data or not edit_index:
            raise PreventUpdate

        try:
            line_idx = int(edit_index)
            if line_idx < 0 or line_idx >= len(lines_data):
                raise PreventUpdate

            # Get product details for cost calculation
            unit_cost = 0.0
            density = 0.0
            product_sku = ""
            product_name = ""

            if product_id:
                try:
                    product_resp = make_api_request("GET", f"/products/{product_id}")
                    if isinstance(product_resp, dict) and "error" not in product_resp:
                        product_sku = product_resp.get("sku", "")
                        product_name = product_resp.get("name", "")
                        # Preserve 4 decimal places
                        # Use inc_gst costs for line cost calculation
                        cost_val = (
                            product_resp.get("usage_cost_inc_gst")
                            or product_resp.get("purchase_cost_inc_gst")
                            or 0
                        )
                        if cost_val:
                            try:
                                unit_cost = round(float(cost_val), 4)
                            except (ValueError, TypeError):
                                unit_cost = 0.0
                        else:
                            unit_cost = 0.0
                        density = float(product_resp.get("density_kg_per_l", 0) or 0)
                except Exception:
                    pass

            # Calculate quantity_kg and quantity_l
            quantity_val = float(quantity or 0.0)
            quantity_kg = 0.0
            quantity_l = 0.0

            if unit.upper() in ["L", "LT", "LTR", "LITER", "LITRE"]:
                if density > 0:
                    quantity_kg = quantity_val * density
                    quantity_l = quantity_val
                else:
                    quantity_kg = quantity_val
                    quantity_l = 0.0
            else:
                quantity_kg = quantity_val
                quantity_l = quantity_kg / density if density > 0 else 0.0

            line_cost = quantity_kg * unit_cost if unit_cost > 0 else 0.0

            # Update the line
            updated_data = lines_data.copy()
            product_display = (
                f"{product_sku} - {product_name}"
                if product_sku and product_name
                else (product_sku or product_name or "[Select product]")
            )
            updated_data[line_idx] = {
                **updated_data[line_idx],
                "product_search": product_display,
                "product_id": product_id or "",
                "product_sku": product_sku,
                "product_name": product_name,
                "quantity": round(quantity_val, 3),
                "unit": unit or "kg",
                "quantity_kg": round(quantity_kg, 3),
                "quantity_l": round(quantity_l, 3),
                "unit_cost": round(unit_cost, 4),
                "line_cost": round(line_cost, 4),
                "notes": notes or "",
            }

            return updated_data, {"display": "none"}
        except Exception as e:
            print(f"Error saving edited line: {e}")
            raise PreventUpdate

    # Load product and unit dropdowns for edit area
    @app.callback(
        [
            Output("assembly-line-edit-product", "options"),
            Output("assembly-line-edit-unit", "options"),
        ],
        [Input("assembly-form-modal", "is_open")],
        [State("assembly-product-id", "children")],
        prevent_initial_call=True,
    )
    def load_edit_area_dropdowns(modal_is_open, product_id):
        """Load product and unit dropdowns for edit area."""
        if not modal_is_open:
            raise PreventUpdate

        try:
            # Load products
            products_response = make_api_request("GET", "/products/?limit=1000")
            product_options = []
            if isinstance(products_response, list):
                product_options = [
                    {
                        "label": f"{p.get('sku', '')} - {p.get('name', '')}",
                        "value": p.get("id", ""),
                    }
                    for p in products_response
                ]

            # Load units
            units_response = make_api_request("GET", "/units/?is_active=true")
            unit_options = []
            if isinstance(units_response, list):
                unit_options = [
                    {
                        "label": f"{u.get('code', '')} - {u.get('name', '')}",
                        "value": u.get("code", ""),
                    }
                    for u in units_response
                ]

            return product_options, unit_options
        except Exception as e:
            print(f"Error loading edit area dropdowns: {e}")
            return [], []

    # Update unit dropdown default when product is selected in edit area
    @app.callback(
        Output("assembly-line-edit-unit", "value", allow_duplicate=True),
        [Input("assembly-line-edit-product", "value")],
        prevent_initial_call=True,
    )
    def update_edit_unit_default(product_id):
        """Update unit dropdown default when product is selected."""
        if not product_id:
            raise PreventUpdate

        try:
            product_resp = make_api_request("GET", f"/products/{product_id}")
            if isinstance(product_resp, dict) and "error" not in product_resp:
                default_unit = (
                    product_resp.get("usage_unit")
                    or product_resp.get("base_unit")
                    or "kg"
                )
                return default_unit
        except Exception:
            pass

        raise PreventUpdate

    # Product lookup for assembly lines
    @app.callback(
        Output("assembly-lines-table", "data", allow_duplicate=True),
        [Input("assembly-lookup-product-btn", "n_clicks")],
        [
            State("assembly-product-search", "value"),
            State("assembly-lines-table", "data"),
            State("assembly-lines-table", "selected_rows"),
        ],
        prevent_initial_call=True,
    )
    def lookup_product_for_line(n_clicks, search_term, lines_data, selected_rows):
        """Lookup product and populate selected line."""
        if not n_clicks or not search_term or not lines_data:
            raise PreventUpdate

        if not selected_rows or len(selected_rows) == 0:
            raise PreventUpdate

        try:
            # Search for product
            products_response = make_api_request(
                "GET", f"/products/?query={search_term}&limit=1"
            )

            if isinstance(products_response, list) and len(products_response) > 0:
                product = products_response[0]

                # Update selected line
                updated_data = lines_data.copy()
                selected_idx = selected_rows[0]

                if selected_idx < len(updated_data):
                    # Get base unit from product, default to kg
                    base_unit = product.get("base_unit", "kg") or "kg"
                    # Only update unit if it's currently empty or default
                    current_unit = updated_data[selected_idx].get("unit", "kg")
                    if not current_unit or current_unit == "kg":
                        updated_data[selected_idx]["unit"] = base_unit

                    updated_data[selected_idx] = {
                        **updated_data[selected_idx],
                        "product_search": search_term,
                        "product_id": product.get("id", ""),
                        "product_sku": product.get("sku", ""),
                        "product_name": product.get("name", ""),
                        "unit": base_unit,
                        "unit_cost": round(
                            float(
                                product.get("usage_cost_inc_gst", 0)
                                or product.get("purchase_cost_inc_gst", 0)
                                or 0
                            ),
                            4,
                        ),
                    }

                    # Auto-calculate quantity_kg and line_cost
                    quantity = float(
                        updated_data[selected_idx].get("quantity", 0.0) or 0.0
                    )
                    unit = updated_data[selected_idx].get("unit", "kg")
                    # Ensure density is numeric
                    density_val = product.get("density_kg_per_l", 0) or 0
                    try:
                        density = float(density_val)
                    except (ValueError, TypeError):
                        density = 0.0

                    # Convert to kg and calculate L
                    if unit.upper() in ["L", "LT", "LTR", "LITER", "LITRE"]:
                        if density > 0:
                            quantity_kg = quantity * density
                            quantity_l = quantity
                        else:
                            quantity_kg = quantity  # Fallback
                            quantity_l = 0.0
                    else:
                        quantity_kg = quantity
                        quantity_l = quantity_kg / density if density > 0 else 0.0

                    unit_cost = float(
                        updated_data[selected_idx].get("unit_cost", 0.0) or 0.0
                    )
                    line_cost = quantity_kg * unit_cost if unit_cost > 0 else 0.0

                    updated_data[selected_idx]["quantity_kg"] = round(quantity_kg, 3)
                    updated_data[selected_idx]["quantity_l"] = round(quantity_l, 3)
                    updated_data[selected_idx]["line_cost"] = round(line_cost, 2)

                return updated_data

            return no_update
        except Exception as e:
            print(f"Error looking up product: {e}")
            return no_update

    # Auto-calculate unit conversions and costs when quantity/unit changes
    @app.callback(
        [
            Output("assembly-lines-table", "data", allow_duplicate=True),
            Output("assembly-summary-total-cost", "children", allow_duplicate=True),
            Output("assembly-summary-total-kg", "children", allow_duplicate=True),
            Output("assembly-summary-total-l", "children", allow_duplicate=True),
            Output("assembly-summary-cost-per-kg", "children", allow_duplicate=True),
            Output("assembly-summary-cost-per-l", "children", allow_duplicate=True),
            Output("assembly-summary-table", "data", allow_duplicate=True),
        ],
        [Input("assembly-lines-table", "data")],
        [State("assembly-parent-product-id-hidden", "children")],
        prevent_initial_call=True,
    )
    def calculate_assembly_line_costs(lines_data, parent_product_id):
        """Calculate quantity_kg, quantity_l, line_cost, and update all summaries."""
        if not lines_data:
            empty_summary = [
                {
                    "type": "assembly",
                    "total_cost": 0.0,
                    "assembly_mass_kg": 0.0,
                    "assembly_volume_l": 0.0,
                    "cost_per_kg": 0.0,
                    "cost_per_l": 0.0,
                },
                {
                    "type": "normalised",
                    "total_cost": 0.0,
                    "assembly_mass_kg": 0.0,
                    "assembly_volume_l": 0.0,
                    "cost_per_kg": 0.0,
                    "cost_per_l": 0.0,
                },
            ]
            return [], "$0.00", "0.000", "0.000", "$0.00", "$0.00", empty_summary

        total_cost = 0.0
        total_quantity_kg = 0.0
        total_quantity_l = 0.0
        updated_data = []

        # Get parent product density for cost per L calculation
        if parent_product_id:
            try:
                parent_response = make_api_request(
                    "GET", f"/products/{parent_product_id}"
                )
                if isinstance(parent_response, dict) and "error" not in parent_response:
                    density_val = parent_response.get("density_kg_per_l", 0) or 0
                    try:
                        float(density_val)
                    except (ValueError, TypeError):
                        pass
            except (ValueError, KeyError, TypeError):
                pass

        for line in lines_data:
            if not isinstance(line, dict):
                continue  # Skip invalid lines

            product_id = line.get("product_id")
            quantity = float(line.get("quantity", 0.0) or 0.0)
            unit = line.get("unit", "kg")

            # Get product density and usage unit if needed
            density = 0.0
            product_usage_unit = None
            product_usage_cost = 0.0

            if product_id:
                try:
                    product_response = make_api_request(
                        "GET", f"/products/{product_id}"
                    )
                    if (
                        isinstance(product_response, dict)
                        and "error" not in product_response
                    ):
                        # Ensure density is numeric
                        density_val = product_response.get("density_kg_per_l", 0) or 0
                        try:
                            density = float(density_val)
                        except (ValueError, TypeError):
                            density = 0.0

                        # Get product's usage_unit (the unit that usage_cost is per)
                        product_usage_unit = (
                            product_response.get("usage_unit", "").upper()
                            if product_response.get("usage_unit")
                            else None
                        )

                        # Check if product is an assembly - if so, use primary assembly cost
                        is_assemble = product_response.get("is_assemble", False)
                        if is_assemble:
                            # Fetch formulas for this assembly product
                            try:
                                formulas_response = make_api_request(
                                    "GET",
                                    f"/formulas/?product_id={product_id}&is_active=true",
                                )
                                if (
                                    isinstance(formulas_response, list)
                                    and len(formulas_response) > 0
                                ):
                                    # Find primary assembly (use first active one, or first one if none active)
                                    primary_formula = None
                                    # First, try to find an active formula
                                    for f in formulas_response:
                                        if f.get("is_active") is True:
                                            primary_formula = f
                                            break

                                    # If no active formula found, use first one
                                    if not primary_formula:
                                        primary_formula = formulas_response[0]

                                    print(
                                        f"[calculate_assembly_line_costs] Using formula {primary_formula.get('formula_code')} (is_active={primary_formula.get('is_active')}) for product {product_id}"
                                    )

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
                                                            # Try ex_gst first, then inc_gst (for consistency)
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
                                                                    # Get product's usage_unit to convert cost to $/kg
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

                                                                    # Handle "EA" (each) unit - cost is per item, not per weight
                                                                    (
                                                                        assembly_line.get(
                                                                            "unit", ""
                                                                        ).upper()
                                                                        if assembly_line.get(
                                                                            "unit"
                                                                        )
                                                                        else "KG"
                                                                    )
                                                                    if (
                                                                        assembly_line_usage_unit
                                                                        in [
                                                                            "EA",
                                                                            "EACH",
                                                                            "UNIT",
                                                                            "UNITS",
                                                                        ]
                                                                    ):
                                                                        # Cost is per item, so multiply cost per item by quantity (in items)
                                                                        # For EA items, quantity_kg might store the quantity (if no weight) or quantity * weight
                                                                        # Get quantity from quantity_kg - if product has weight, reverse calculate
                                                                        assembly_line_qty_ea = assembly_qty_kg  # Default: quantity_kg stores quantity
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
                                                                            # Product has weight - reverse calculate: quantity = quantity_kg / weight_kg
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
                                                                        # Otherwise, quantity_kg IS the quantity (we stored it that way)

                                                                        assembly_line_cost = (
                                                                            assembly_line_qty_ea
                                                                            * assembly_line_unit_cost_raw
                                                                        )
                                                                        # For cost per kg calculation, we need the weight per item
                                                                        # If we have quantity_kg, we can calculate cost per kg
                                                                        if (
                                                                            assembly_qty_kg
                                                                            > 0
                                                                        ):
                                                                            # Cost per kg = total cost / total kg
                                                                            assembly_line_cost_per_kg = (
                                                                                assembly_line_cost
                                                                                / assembly_qty_kg
                                                                            )
                                                                        else:
                                                                            # Can't calculate cost per kg without weight
                                                                            assembly_line_cost_per_kg = 0.0
                                                                    else:
                                                                        # Convert unit cost to $/kg for weight/volume units
                                                                        assembly_line_cost_per_kg = assembly_line_unit_cost_raw
                                                                        if (
                                                                            assembly_line_usage_unit
                                                                            in [
                                                                                "G",
                                                                                "GRAM",
                                                                                "GRAMS",
                                                                            ]
                                                                        ):
                                                                            # Cost per gram -> cost per kg
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
                                                                            # Cost per L -> cost per kg (need density)
                                                                            if (
                                                                                assembly_line_density
                                                                                > 0
                                                                            ):
                                                                                assembly_line_cost_per_kg = (
                                                                                    assembly_line_unit_cost_raw
                                                                                    / assembly_line_density
                                                                                )
                                                                            else:
                                                                                # Fallback: assume 1 L = 1 kg
                                                                                assembly_line_cost_per_kg = assembly_line_unit_cost_raw
                                                                        elif (
                                                                            assembly_line_usage_unit
                                                                            in [
                                                                                "ML",
                                                                                "MILLILITER",
                                                                                "MILLILITRE",
                                                                            ]
                                                                        ):
                                                                            # Cost per mL -> cost per kg (via L)
                                                                            if (
                                                                                assembly_line_density
                                                                                > 0
                                                                            ):
                                                                                # mL -> L -> kg
                                                                                assembly_line_cost_per_kg = (
                                                                                    (
                                                                                        assembly_line_unit_cost_raw
                                                                                        * 1000.0
                                                                                    )
                                                                                    / assembly_line_density
                                                                                )
                                                                            else:
                                                                                # Fallback: assume 1 mL = 1 g
                                                                                assembly_line_cost_per_kg = (
                                                                                    assembly_line_unit_cost_raw
                                                                                    * 1000.0
                                                                                )
                                                                        # If already in KG, no conversion needed

                                                                        # Calculate line cost: quantity_kg * cost_per_kg
                                                                        assembly_line_cost = (
                                                                            assembly_qty_kg
                                                                            * assembly_line_cost_per_kg
                                                                        )
                                                                except (
                                                                    ValueError,
                                                                    TypeError,
                                                                ) as e:
                                                                    print(
                                                                        f"Error calculating assembly line cost: {e}"
                                                                    )
                                                                    pass
                                                    except Exception as e:
                                                        print(
                                                            f"Error fetching assembly line product: {e}"
                                                        )
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
                                            # Set product_usage_cost to assembly cost per kg
                                            # and usage_unit to kg since we're using cost per kg
                                            product_usage_cost = round(
                                                assembly_cost_per_kg, 4
                                            )
                                            product_usage_unit = "KG"
                                            print(
                                                f"[calculate_assembly_line_costs] Calculated assembly cost for {product_id}: total_cost={assembly_total_cost:.4f}, total_kg={assembly_total_kg:.4f}, cost_per_kg={assembly_cost_per_kg:.4f}"
                                            )
                                        else:
                                            print(
                                                f"[calculate_assembly_line_costs] WARNING: assembly_total_kg is 0 for product {product_id}, cannot calculate cost per kg"
                                            )
                                            # Fallback to usage/purchase cost
                                            cost_val = (
                                                product_response.get(
                                                    "usage_cost_ex_gst"
                                                )
                                                or product_response.get(
                                                    "purchase_cost_ex_gst"
                                                )
                                                or product_response.get(
                                                    "usage_cost_inc_gst"
                                                )
                                                or product_response.get(
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
                                print(
                                    f"Error fetching assembly cost for {product_id}: {e}"
                                )
                                # Fallback to usage/purchase cost
                                cost_val = (
                                    product_response.get("usage_cost_inc_gst")
                                    or product_response.get("purchase_cost_inc_gst")
                                    or 0
                                )
                                if cost_val:
                                    try:
                                        product_usage_cost = round(float(cost_val), 4)
                                    except (ValueError, TypeError):
                                        product_usage_cost = 0.0
                        else:
                            # Not an assembly - use usage/purchase cost
                            # Try ex_gst first, then inc_gst (for consistency)
                            # This cost is per product_usage_unit (e.g., per gram, per kg, per L, per EA)
                            cost_val = (
                                product_response.get("usage_cost_ex_gst")
                                or product_response.get("purchase_cost_ex_gst")
                                or product_response.get("usage_cost_inc_gst")
                                or product_response.get("purchase_cost_inc_gst")
                                or 0
                            )
                            if cost_val:
                                try:
                                    product_usage_cost = round(float(cost_val), 4)
                                except (ValueError, TypeError):
                                    product_usage_cost = 0.0
                            else:
                                product_usage_cost = 0.0
                except (ValueError, KeyError, TypeError):
                    pass

            # Convert quantity to kg
            try:
                density = float(density) if density else 0.0
            except (ValueError, TypeError):
                density = 0.0

            # Convert quantity to kg and L based on unit
            unit_upper = unit.upper() if unit else "KG"

            if unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                # Liters to kg (using density) and L (no conversion)
                if density > 0:
                    quantity_kg = quantity * density
                    quantity_l = quantity
                else:
                    quantity_kg = quantity  # Fallback - treat L as kg if no density
                    quantity_l = quantity
            elif unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                # Milliliters to kg and L
                quantity_l = quantity / 1000.0  # Convert mL to L
                if density > 0:
                    quantity_kg = quantity_l * density  # Convert L to kg using density
                else:
                    # Assume 1 mL = 1 g (water-like density) if no density
                    quantity_kg = quantity / 1000.0  # Convert mL to kg (via g)
            elif unit_upper in ["G", "GRAM", "GRAMS"]:
                # Grams to kg
                quantity_kg = quantity / 1000.0
                # Convert kg to L using density
                quantity_l = quantity_kg / density if density > 0 else 0.0
            elif unit_upper in ["KG", "KILOGRAM", "KILOGRAMS"]:
                # Kilograms - no conversion needed
                quantity_kg = quantity
                # Convert kg to L using density
                quantity_l = quantity_kg / density if density > 0 else 0.0
            elif unit_upper in ["EA", "EACH", "UNIT", "UNITS"]:
                # For "each" units, check if product has weight_kg
                # If no weight, store quantity in quantity_kg (preserves the quantity value)
                if product_id:
                    try:
                        product_response = make_api_request(
                            "GET", f"/products/{product_id}"
                        )
                        if (
                            isinstance(product_response, dict)
                            and "error" not in product_response
                        ):
                            weight_kg = product_response.get("weight_kg") or 0.0
                            if weight_kg:
                                # Product has weight - calculate actual weight
                                quantity_kg = quantity * float(weight_kg)
                                quantity_l = (
                                    quantity_kg / density if density > 0 else 0.0
                                )
                            else:
                                # No weight - store quantity in quantity_kg to preserve it
                                quantity_kg = quantity
                                quantity_l = 0.0
                        else:
                            # Can't get product - store quantity in quantity_kg to preserve it
                            quantity_kg = quantity
                            quantity_l = 0.0
                    except (ValueError, KeyError, TypeError):
                        # On error - store quantity in quantity_kg to preserve it
                        quantity_kg = quantity
                        quantity_l = 0.0
                else:
                    # No product ID - store quantity in quantity_kg to preserve it
                    quantity_kg = quantity
                    quantity_l = 0.0
            else:
                # Default: assume kg for unknown units
                quantity_kg = quantity
                quantity_l = quantity_kg / density if density > 0 else 0.0

            # Calculate line cost
            # Convert assembly line quantity to product's usage_unit, then multiply by cost per usage_unit
            line_cost = 0.0
            if product_usage_cost > 0 and product_usage_unit:
                # Convert assembly line quantity to product's usage_unit
                quantity_in_usage_unit = 0.0

                # Convert assembly line quantity (in its unit) to product's usage_unit
                assembly_unit_upper = unit.upper() if unit else "KG"
                product_usage_unit_upper = product_usage_unit.upper()

                # If units match, no conversion needed
                if assembly_unit_upper == product_usage_unit_upper:
                    quantity_in_usage_unit = quantity
                # Mass conversions
                elif assembly_unit_upper in [
                    "G",
                    "GRAM",
                    "GRAMS",
                ] and product_usage_unit_upper in ["G", "GRAM", "GRAMS"]:
                    quantity_in_usage_unit = quantity
                elif assembly_unit_upper in [
                    "G",
                    "GRAM",
                    "GRAMS",
                ] and product_usage_unit_upper in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    quantity_in_usage_unit = quantity / 1000.0  # g to kg
                elif assembly_unit_upper in [
                    "KG",
                    "KILOGRAM",
                    "KILOGRAMS",
                ] and product_usage_unit_upper in ["G", "GRAM", "GRAMS"]:
                    quantity_in_usage_unit = quantity * 1000.0  # kg to g
                elif assembly_unit_upper in [
                    "KG",
                    "KILOGRAM",
                    "KILOGRAMS",
                ] and product_usage_unit_upper in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    quantity_in_usage_unit = quantity
                # Volume conversions
                elif assembly_unit_upper in [
                    "ML",
                    "MILLILITER",
                    "MILLILITRE",
                ] and product_usage_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                    quantity_in_usage_unit = quantity
                elif assembly_unit_upper in [
                    "ML",
                    "MILLILITER",
                    "MILLILITRE",
                ] and product_usage_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    quantity_in_usage_unit = quantity / 1000.0  # mL to L
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                    quantity_in_usage_unit = quantity * 1000.0  # L to mL
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    quantity_in_usage_unit = quantity
                # Volume to mass (using density) - if assembly is volume and product usage_unit is mass
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit_upper in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    if density > 0:
                        quantity_in_usage_unit = quantity * density  # L to kg
                    else:
                        quantity_in_usage_unit = quantity  # Fallback
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit_upper in ["G", "GRAM", "GRAMS"]:
                    if density > 0:
                        quantity_in_usage_unit = quantity * density * 1000.0  # L to g
                    else:
                        quantity_in_usage_unit = quantity * 1000.0  # Fallback
                elif assembly_unit_upper in [
                    "ML",
                    "MILLILITER",
                    "MILLILITRE",
                ] and product_usage_unit_upper in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    if density > 0:
                        quantity_in_usage_unit = (
                            quantity / 1000.0
                        ) * density  # mL to L to kg
                    else:
                        quantity_in_usage_unit = quantity / 1000.0  # Fallback
                elif assembly_unit_upper in [
                    "ML",
                    "MILLILITER",
                    "MILLILITRE",
                ] and product_usage_unit_upper in ["G", "GRAM", "GRAMS"]:
                    if density > 0:
                        quantity_in_usage_unit = (
                            (quantity / 1000.0) * density * 1000.0
                        )  # mL to L to kg to g
                    else:
                        quantity_in_usage_unit = (
                            quantity  # Fallback (assume 1 mL = 1 g)
                        )
                # Mass to volume (using density) - if assembly is mass and product usage_unit is volume
                elif assembly_unit_upper in [
                    "KG",
                    "KILOGRAM",
                    "KILOGRAMS",
                ] and product_usage_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    if density > 0:
                        quantity_in_usage_unit = quantity / density  # kg to L
                    else:
                        quantity_in_usage_unit = 0.0
                elif assembly_unit_upper in [
                    "G",
                    "GRAM",
                    "GRAMS",
                ] and product_usage_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    if density > 0:
                        quantity_in_usage_unit = (
                            quantity / 1000.0
                        ) / density  # g to kg to L
                    else:
                        quantity_in_usage_unit = 0.0
                elif assembly_unit_upper in [
                    "G",
                    "GRAM",
                    "GRAMS",
                ] and product_usage_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                    if density > 0:
                        quantity_in_usage_unit = (
                            (quantity / 1000.0) / density
                        ) * 1000.0  # g to kg to L to mL
                    else:
                        quantity_in_usage_unit = (
                            quantity  # Fallback (assume 1 g = 1 mL)
                        )
                elif assembly_unit_upper in [
                    "KG",
                    "KILOGRAM",
                    "KILOGRAMS",
                ] and product_usage_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                    if density > 0:
                        quantity_in_usage_unit = (
                            quantity / density
                        ) * 1000.0  # kg to L to mL
                    else:
                        quantity_in_usage_unit = 0.0
                # Handle "EA" (each) units
                elif assembly_unit_upper in [
                    "EA",
                    "EACH",
                    "UNIT",
                    "UNITS",
                ] and product_usage_unit_upper in ["EA", "EACH", "UNIT", "UNITS"]:
                    # Both are "each" - quantity is already in items
                    quantity_in_usage_unit = quantity
                elif assembly_unit_upper in ["EA", "EACH", "UNIT", "UNITS"]:
                    # Assembly line is "ea" but product usage_unit is not - can't convert without weight/volume per item
                    # Use quantity as-is (assume cost is per item)
                    quantity_in_usage_unit = quantity
                    print(
                        f"[calculate_assembly_line_costs] WARNING: Assembly line unit is 'EA' but product usage_unit is '{product_usage_unit_upper}' - using quantity as-is"
                    )
                elif product_usage_unit_upper in ["EA", "EACH", "UNIT", "UNITS"]:
                    # Product usage_unit is "ea" but assembly line unit is not - can't convert
                    # Use quantity as-is (cost is per item regardless of assembly line unit)
                    quantity_in_usage_unit = quantity
                    print(
                        f"[calculate_assembly_line_costs] WARNING: Product usage_unit is 'EA' but assembly line unit is '{assembly_unit_upper}' - using quantity as-is"
                    )
                else:
                    # Fallback: convert assembly quantity to kg, then try to convert to usage_unit
                    # If we can't determine, use quantity_kg and assume usage_unit is kg
                    if product_usage_unit_upper in ["KG", "KILOGRAM", "KILOGRAMS"]:
                        quantity_in_usage_unit = quantity_kg
                    elif product_usage_unit_upper in ["G", "GRAM", "GRAMS"]:
                        quantity_in_usage_unit = quantity_kg * 1000.0
                    elif product_usage_unit_upper in [
                        "L",
                        "LT",
                        "LTR",
                        "LITER",
                        "LITRE",
                    ]:
                        quantity_in_usage_unit = (
                            quantity_l
                            if quantity_l > 0
                            else quantity_kg / density
                            if density > 0
                            else 0.0
                        )
                    elif product_usage_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                        quantity_in_usage_unit = (
                            quantity_l * 1000.0
                            if quantity_l > 0
                            else (quantity_kg / density * 1000.0)
                            if density > 0
                            else 0.0
                        )
                    else:
                        quantity_in_usage_unit = quantity_kg  # Default fallback

                # Calculate line cost: quantity in usage_unit × cost per usage_unit
                line_cost = quantity_in_usage_unit * product_usage_cost
            elif product_usage_cost > 0:
                # If no usage_unit specified, assume it's per kg (legacy behavior)
                line_cost = quantity_kg * product_usage_cost
            else:
                line_cost = 0.0
            total_cost += line_cost
            total_quantity_kg += quantity_kg
            total_quantity_l += quantity_l

            # Calculate unit_cost for display (cost per assembly line unit)
            # Convert product_usage_cost from product's usage_unit to assembly line's unit
            display_unit_cost = 0.0
            if product_usage_cost > 0 and product_usage_unit:
                assembly_unit_upper = unit.upper() if unit else "KG"
                product_usage_unit_upper = product_usage_unit.upper()

                # If units match, no conversion needed
                if assembly_unit_upper == product_usage_unit_upper:
                    display_unit_cost = product_usage_cost
                # Mass conversions
                elif assembly_unit_upper in [
                    "G",
                    "GRAM",
                    "GRAMS",
                ] and product_usage_unit_upper in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    display_unit_cost = product_usage_cost / 1000.0  # $/kg to $/g
                elif assembly_unit_upper in [
                    "KG",
                    "KILOGRAM",
                    "KILOGRAMS",
                ] and product_usage_unit_upper in ["G", "GRAM", "GRAMS"]:
                    display_unit_cost = product_usage_cost * 1000.0  # $/g to $/kg
                # Volume conversions
                elif assembly_unit_upper in [
                    "ML",
                    "MILLILITER",
                    "MILLILITRE",
                ] and product_usage_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    display_unit_cost = product_usage_cost / 1000.0  # $/L to $/mL
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                    display_unit_cost = product_usage_cost * 1000.0  # $/mL to $/L
                # Volume to mass (using density)
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit_upper in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    if density > 0:
                        display_unit_cost = product_usage_cost / density  # $/kg to $/L
                    else:
                        display_unit_cost = product_usage_cost  # Fallback
                elif assembly_unit_upper in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ] and product_usage_unit_upper in ["G", "GRAM", "GRAMS"]:
                    if density > 0:
                        display_unit_cost = product_usage_cost / (
                            density * 1000.0
                        )  # $/g to $/L
                    else:
                        display_unit_cost = product_usage_cost / 1000.0  # Fallback
                elif assembly_unit_upper in [
                    "ML",
                    "MILLILITER",
                    "MILLILITRE",
                ] and product_usage_unit_upper in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    if density > 0:
                        display_unit_cost = (
                            product_usage_cost / density
                        ) / 1000.0  # $/kg to $/mL
                    else:
                        display_unit_cost = product_usage_cost / 1000.0  # Fallback
                elif assembly_unit_upper in [
                    "ML",
                    "MILLILITER",
                    "MILLILITRE",
                ] and product_usage_unit_upper in ["G", "GRAM", "GRAMS"]:
                    if density > 0:
                        display_unit_cost = (
                            product_usage_cost / (density * 1000.0)
                        ) / 1000.0  # $/g to $/mL
                    else:
                        display_unit_cost = product_usage_cost / 1000000.0  # Fallback
                # Mass to volume (using density)
                elif assembly_unit_upper in [
                    "KG",
                    "KILOGRAM",
                    "KILOGRAMS",
                ] and product_usage_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    if density > 0:
                        display_unit_cost = product_usage_cost * density  # $/L to $/kg
                    else:
                        display_unit_cost = product_usage_cost  # Fallback
                elif assembly_unit_upper in [
                    "G",
                    "GRAM",
                    "GRAMS",
                ] and product_usage_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    if density > 0:
                        display_unit_cost = (
                            product_usage_cost * density
                        ) * 1000.0  # $/L to $/g
                    else:
                        display_unit_cost = product_usage_cost * 1000.0  # Fallback
                elif assembly_unit_upper in [
                    "G",
                    "GRAM",
                    "GRAMS",
                ] and product_usage_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                    if density > 0:
                        display_unit_cost = (
                            (product_usage_cost * density) * 1000.0
                        ) * 1000.0  # $/mL to $/g
                    else:
                        display_unit_cost = product_usage_cost * 1000000.0  # Fallback
                elif assembly_unit_upper in [
                    "KG",
                    "KILOGRAM",
                    "KILOGRAMS",
                ] and product_usage_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                    if density > 0:
                        display_unit_cost = (
                            product_usage_cost * density
                        ) * 1000.0  # $/mL to $/kg
                    else:
                        display_unit_cost = product_usage_cost * 1000.0  # Fallback
                else:
                    # Fallback: calculate from line_cost if available
                    if quantity > 0 and line_cost > 0:
                        display_unit_cost = line_cost / quantity
                    else:
                        display_unit_cost = product_usage_cost  # Default fallback
            elif product_usage_cost > 0:
                # If no usage_unit, assume it's per kg and convert to assembly unit
                if unit.upper() in ["G", "GRAM", "GRAMS"]:
                    display_unit_cost = product_usage_cost / 1000.0
                elif unit.upper() in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    display_unit_cost = product_usage_cost
                else:
                    display_unit_cost = product_usage_cost

            # Preserve the original quantity value (not converted) - only update calculated fields
            # IMPORTANT: For EA items, preserve the original quantity from the table
            # For other units, preserve original if available, otherwise use calculated
            original_quantity = line.get("quantity")
            if original_quantity is None or original_quantity == "":
                # No original quantity in table - use calculated quantity
                preserved_quantity = quantity
            else:
                # Preserve original user-entered quantity
                try:
                    preserved_quantity = float(original_quantity)
                except (ValueError, TypeError):
                    preserved_quantity = quantity  # Fallback to calculated

            # Calculate cost per kg and cost per L for display
            cost_per_kg_display = 0.0
            cost_per_l_display = 0.0
            if product_usage_cost > 0 and product_usage_unit:
                usage_unit_upper = product_usage_unit.upper()
                if usage_unit_upper in ["KG", "KILOGRAM", "KILOGRAMS"]:
                    cost_per_kg_display = product_usage_cost
                    if density > 0:
                        cost_per_l_display = product_usage_cost / density
                elif usage_unit_upper in ["G", "GRAM", "GRAMS"]:
                    cost_per_kg_display = product_usage_cost * 1000.0  # $/g to $/kg
                    if density > 0:
                        cost_per_l_display = (product_usage_cost * 1000.0) / density
                elif usage_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    cost_per_l_display = product_usage_cost
                    if density > 0:
                        cost_per_kg_display = product_usage_cost * density
                elif usage_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                    cost_per_l_display = product_usage_cost * 1000.0  # $/mL to $/L
                    if density > 0:
                        cost_per_kg_display = (product_usage_cost * 1000.0) * density
                else:
                    # Fallback: assume per kg
                    cost_per_kg_display = product_usage_cost
                    if density > 0:
                        cost_per_l_display = product_usage_cost / density
            elif product_usage_cost > 0:
                # No usage_unit specified - assume per kg
                cost_per_kg_display = product_usage_cost
                if density > 0:
                    cost_per_l_display = product_usage_cost / density

            updated_line = {
                **line,
                # Keep the original quantity value as entered by user
                "quantity": preserved_quantity,  # Preserve original user-entered value
                "quantity_kg": round(quantity_kg, 3),  # Calculated kg value for API
                "quantity_l": round(quantity_l, 3),  # Calculated L value
                "density": round(density, 6) if density > 0 else 0.0,
                "unit_cost": round(display_unit_cost, 4),
                "cost_per_kg": round(cost_per_kg_display, 4),
                "cost_per_l": round(cost_per_l_display, 4),
                "line_cost": round(line_cost, 4),
            }
            # Remove is_primary from updated_line if it exists
            updated_line.pop("is_primary", None)
            updated_line.pop("is_primary_bool", None)
            updated_data.append(updated_line)

        # Calculate summary values
        cost_per_kg = total_cost / total_quantity_kg if total_quantity_kg > 0 else 0.0
        cost_per_l = total_cost / total_quantity_l if total_quantity_l > 0 else 0.0

        # Build assembly summary table
        summary_data = [
            {
                "type": "assembly",
                "total_cost": round(total_cost, 2),
                "assembly_mass_kg": round(total_quantity_kg, 3),
                "assembly_volume_l": round(total_quantity_l, 3),
                "cost_per_kg": round(cost_per_kg, 4),
                "cost_per_l": round(cost_per_l, 4),
            },
            {
                "type": "normalised",
                "total_cost": round(total_cost, 2),
                "assembly_mass_kg": round(total_quantity_kg, 3),
                "assembly_volume_l": round(total_quantity_l, 3),
                "cost_per_kg": round(cost_per_kg, 4),
                "cost_per_l": round(cost_per_l, 4),
            },
        ]

        return (
            updated_data,
            f"${total_cost:.2f}",
            f"{total_quantity_kg:.3f}",
            f"{total_quantity_l:.3f}",
            f"${cost_per_kg:.4f}",
            f"${cost_per_l:.4f}",
            summary_data,
        )

    # Populate product and unit dropdown options
    @app.callback(
        Output("assembly-lines-table", "dropdown", allow_duplicate=True),
        [Input("assembly-form-modal", "is_open")],
        [State("assembly-product-id", "children")],
        prevent_initial_call=True,
    )
    def update_assembly_dropdowns(modal_is_open, product_id):
        """Update product and unit dropdown options for assembly lines."""
        if not modal_is_open:
            raise PreventUpdate

        try:
            # Get all products for dropdown
            products_response = make_api_request("GET", "/products/?limit=1000")

            product_options = []
            if isinstance(products_response, list):
                product_options = [
                    {
                        "label": f"{p.get('sku', '')} - {p.get('name', '')}",
                        "value": p.get("id", ""),
                    }
                    for p in products_response
                ]

            # Get units from units API
            units_response = make_api_request("GET", "/units/?is_active=true")
            unit_options = []

            if isinstance(units_response, list):
                unit_options = [
                    {
                        "label": f"{u.get('code', '')} - {u.get('name', '')}",
                        "value": u.get("code", ""),
                    }
                    for u in units_response
                ]

                # Get default unit from product's usage_unit
                if product_id:
                    try:
                        product_resp = make_api_request(
                            "GET", f"/products/{product_id}"
                        )
                        if (
                            isinstance(product_resp, dict)
                            and "error" not in product_resp
                        ):
                            (
                                product_resp.get("usage_unit")
                                or product_resp.get("base_unit")
                                or "kg"
                            )
                    except Exception:
                        pass

            return {
                "product_search": {"options": product_options},
                "unit": {"options": unit_options},
            }
        except (ValueError, KeyError, TypeError):
            pass

        return no_update

    # Handle product selection and sequence changes from dropdown
    @app.callback(
        Output("assembly-lines-table", "data", allow_duplicate=True),
        [Input("assembly-lines-table", "data_previous")],
        [State("assembly-lines-table", "data")],
        prevent_initial_call=True,
    )
    def handle_table_changes(previous_data, current_data):
        """Handle product selection changes and sequence number edits."""
        if not previous_data or not current_data:
            raise PreventUpdate

        # Check what changed - product or sequence
        product_changed = False
        sequence_changed = False
        changed_line_index = None

        for i, (prev_line, curr_line) in enumerate(zip(previous_data, current_data)):
            prev_seq = prev_line.get("sequence")
            curr_seq = curr_line.get("sequence")
            prev_product = prev_line.get("product_search")
            curr_product = curr_line.get("product_search")

            # Check if product changed
            if prev_product != curr_product:
                product_changed = True
                changed_line_index = i
                break

            # Check if sequence changed but product didn't
            if prev_seq != curr_seq and prev_product == curr_product:
                sequence_changed = True

        # Handle product selection change
        if product_changed and changed_line_index is not None:
            product_search = current_data[changed_line_index].get("product_search")
            if product_search:
                try:
                    product_id = product_search
                    product_response = make_api_request(
                        "GET", f"/products/{product_id}"
                    )

                    if (
                        isinstance(product_response, dict)
                        and "error" not in product_response
                    ):
                        updated_data = current_data.copy()
                        updated_data[changed_line_index] = {
                            **updated_data[changed_line_index],
                            "product_id": product_id,
                            "product_sku": product_response.get("sku", ""),
                            "product_name": product_response.get("name", ""),
                            "unit": product_response.get("base_unit", "kg") or "kg",
                            "unit_cost": float(
                                product_response.get("usage_cost_ex_gst", 0)
                                or product_response.get("purchase_cost_ex_gst", 0)
                                or 0
                            ),
                        }

                        # Recalculate quantity_kg and line_cost
                        quantity = float(
                            updated_data[changed_line_index].get("quantity", 0.0) or 0.0
                        )
                        unit = updated_data[changed_line_index].get("unit", "kg")
                        density = float(
                            product_response.get("density_kg_per_l", 0) or 0
                        )

                        if unit.lower() in ["l", "ltr", "liter", "litre"]:
                            quantity_kg = (
                                quantity * density if density > 0 else quantity
                            )
                        else:
                            quantity_kg = quantity

                        unit_cost = float(
                            updated_data[changed_line_index].get("unit_cost", 0.0)
                            or 0.0
                        )
                        line_cost = quantity_kg * unit_cost

                        updated_data[changed_line_index]["quantity_kg"] = round(
                            quantity_kg, 3
                        )
                        updated_data[changed_line_index]["line_cost"] = round(
                            line_cost, 2
                        )

                        return updated_data
                except Exception as e:
                    print(f"Error fetching product: {e}")

        # Handle sequence change - reorder lines
        if sequence_changed:
            # Sort by sequence number
            sorted_data = sorted(
                current_data, key=lambda x: int(x.get("sequence", 0) or 0)
            )

            # Renumber sequences to be consecutive starting from 1
            for idx, line in enumerate(sorted_data):
                line["sequence"] = idx + 1

            return sorted_data

        raise PreventUpdate

    # Load assembly summary table for product edit form (shows primary assembly)
    @app.callback(
        Output("product-assembly-summary-table", "data"),
        [
            Input("product-assemblies-table", "data"),
            Input("product-form-hidden", "children"),
        ],
        prevent_initial_call=True,
    )
    def load_product_assembly_summary(assemblies_data, product_id):
        """Load assembly summary table with primary/active assembly data."""
        if not assemblies_data or not product_id:
            return []

        # Find primary/active assembly
        primary_assembly = None
        for assembly in assemblies_data:
            if assembly.get("is_primary") == "✓":
                primary_assembly = assembly
                break

        # If no primary found, use first active assembly
        if not primary_assembly and assemblies_data:
            primary_assembly = assemblies_data[0]

        if not primary_assembly:
            return []

        # Get formula details to calculate summary
        formula_id = primary_assembly.get("formula_id")
        if not formula_id:
            return []

        try:
            formula_response = make_api_request("GET", f"/formulas/{formula_id}")
            if not isinstance(formula_response, dict) or "error" in formula_response:
                return []

            # Get parent product density
            parent_density = 0.0
            if product_id:
                try:
                    parent_resp = make_api_request("GET", f"/products/{product_id}")
                    if isinstance(parent_resp, dict) and "error" not in parent_resp:
                        parent_density = float(
                            parent_resp.get("density_kg_per_l", 0) or 0
                        )
                except Exception:
                    pass

            # Calculate totals from lines (similar to calculate_assembly_line_costs)
            total_cost = 0.0
            total_quantity_kg = 0.0
            total_quantity_l = 0.0

            for line in formula_response.get("lines", []):
                if isinstance(line, dict):
                    qty_kg = float(line.get("quantity_kg", 0.0) or 0.0)

                    # Get unit cost
                    unit_cost = line.get("unit_cost") or 0.0
                    if not unit_cost:
                        line_product_id = line.get("raw_material_id")
                        if line_product_id:
                            try:
                                line_product = make_api_request(
                                    "GET", f"/products/{line_product_id}"
                                )
                                if isinstance(line_product, dict):
                                    cost_val = (
                                        line_product.get("usage_cost_ex_gst")
                                        or line_product.get("purchase_cost_ex_gst")
                                        or 0
                                    )
                                    if cost_val:
                                        try:
                                            unit_cost = round(float(cost_val), 4)
                                        except (ValueError, TypeError):
                                            unit_cost = 0.0
                            except Exception:
                                pass

                    total_cost += qty_kg * float(unit_cost) if unit_cost else 0.0
                    total_quantity_kg += qty_kg

            # Calculate quantity in liters
            if parent_density > 0:
                total_quantity_l = total_quantity_kg / parent_density
            else:
                total_quantity_l = 0.0

            # Calculate cost per kg and cost per L
            cost_per_kg = (
                total_cost / total_quantity_kg if total_quantity_kg > 0 else 0.0
            )
            cost_per_l = total_cost / total_quantity_l if total_quantity_l > 0 else 0.0

            # Build summary table (same format as assembly-summary-table)
            summary_data = [
                {
                    "type": "assembly",
                    "total_cost": round(total_cost, 2),
                    "assembly_mass_kg": round(total_quantity_kg, 3),
                    "assembly_volume_l": round(total_quantity_l, 3),
                    "cost_per_kg": round(cost_per_kg, 4),
                    "cost_per_l": round(cost_per_l, 4),
                },
                {
                    "type": "normalised",
                    "total_cost": round(total_cost, 2),
                    "assembly_mass_kg": round(total_quantity_kg, 3),
                    "assembly_volume_l": round(total_quantity_l, 3),
                    "cost_per_kg": round(cost_per_kg, 4),
                    "cost_per_l": round(cost_per_l, 4),
                },
            ]

            return summary_data
        except Exception as e:
            print(f"Error loading assembly summary: {e}")
            return []

    # Recalculate excise when button is clicked
    @app.callback(
        Output("product-pricing-table", "data", allow_duplicate=True),
        [Input("recalculate-excise-btn", "n_clicks")],
        [
            State("product-pricing-table", "data"),
            State("product-abv", "value"),
            State("product-density", "value"),
            State("product-size", "value"),
            State("product-base-unit", "value"),
        ],
        prevent_initial_call=True,
    )
    def recalculate_excise(n_clicks, pricing_data, abv, density, size, base_unit):
        """Manually trigger excise recalculation."""
        if not n_clicks or not pricing_data:
            raise PreventUpdate

        # Use the same calculation logic as calculate_pricing_table
        # Get current excise rate
        try:
            excise_response = make_api_request("GET", "/excise-rates/current")
            excise_rate_per_l_abv = (
                float(excise_response.get("rate_per_l_abv", 0))
                if isinstance(excise_response, dict)
                else 0.0
            )
        except Exception as e:
            print(f"Error fetching excise rate: {e}")
            excise_rate_per_l_abv = 0.0

        # GST rate (10% in Australia)
        GST_RATE = 0.10

        # Calculate volume in liters from basic information
        volume_liters = 1.0  # Default to 1 liter per unit
        try:
            if size:
                size_val = float(size)
                base_unit_upper = base_unit.upper() if base_unit else ""

                if base_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    volume_liters = size_val
                elif base_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                    volume_liters = size_val / 1000.0
                elif base_unit_upper in ["KG", "KILOGRAM"]:
                    if density:
                        density_val = float(density)
                        if density_val > 0:
                            volume_liters = size_val / density_val
                        else:
                            volume_liters = size_val
                    else:
                        volume_liters = size_val
                elif base_unit_upper in ["G", "GRAM", "GRAMS"]:
                    if density:
                        density_val = float(density)
                        if density_val > 0:
                            volume_liters = (size_val / 1000.0) / density_val
                        else:
                            volume_liters = size_val / 1000.0
                    else:
                        volume_liters = size_val / 1000.0
                else:
                    volume_liters = size_val
            elif base_unit:
                base_unit_upper = base_unit.upper()
                if base_unit_upper in ["L", "LT", "LTR", "LITER", "LITRE"]:
                    volume_liters = 1.0
                elif base_unit_upper in ["ML", "MILLILITER", "MILLILITRE"]:
                    volume_liters = 0.001
                elif base_unit_upper in ["KG", "KILOGRAM"]:
                    if density:
                        density_val = float(density)
                        if density_val > 0:
                            volume_liters = 1.0 / density_val
                        else:
                            volume_liters = 1.0
                    else:
                        volume_liters = 1.0
                elif base_unit_upper in ["G", "GRAM", "GRAMS"]:
                    if density:
                        density_val = float(density)
                        if density_val > 0:
                            volume_liters = 0.001 / density_val
                        else:
                            volume_liters = 0.001
                    else:
                        volume_liters = 0.001
        except (ValueError, TypeError):
            volume_liters = 1.0

        # Calculate excise and GST for each price level
        updated_data = []
        for row in pricing_data:
            price_level = row.get("price_level", "")
            inc_gst = row.get("inc_gst")
            ex_gst = row.get("ex_gst")

            # If inc_gst is provided, calculate ex_gst
            if inc_gst is not None and inc_gst != "":
                try:
                    inc_gst_val = float(inc_gst)
                    ex_gst_val = inc_gst_val / (1 + GST_RATE)
                except (ValueError, TypeError):
                    ex_gst_val = None
            # If ex_gst is provided, calculate inc_gst
            elif ex_gst is not None and ex_gst != "":
                try:
                    ex_gst_val = float(ex_gst)
                    inc_gst_val = ex_gst_val * (1 + GST_RATE)
                except (ValueError, TypeError):
                    inc_gst_val = None
                    ex_gst_val = None
            else:
                inc_gst_val = None
                ex_gst_val = None

            # Calculate excise based on ABV * volume from basic information
            excise_val = None
            if abv:
                try:
                    abv_val = float(abv)
                    abv_liters = volume_liters * (abv_val / 100.0)
                    excise_val = abv_liters * excise_rate_per_l_abv
                except (ValueError, TypeError):
                    excise_val = None

            # Preserve COGS columns
            updated_data.append(
                {
                    "price_level": price_level,
                    "inc_gst": (
                        round(inc_gst_val, 2) if inc_gst_val is not None else None
                    ),
                    "ex_gst": round(ex_gst_val, 2) if ex_gst_val is not None else None,
                    "excise": round(excise_val, 2) if excise_val is not None else None,
                    "inc_gst_cogs": row.get("inc_gst_cogs"),  # Preserve COGS
                    "inc_excise_cogs": row.get("inc_excise_cogs"),  # Preserve COGS
                }
            )

        return updated_data

    # Note: Table refresh is now handled by the main callback in app.py that responds to filter changes
