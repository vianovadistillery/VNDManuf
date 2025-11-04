"""CRUD callbacks for products page."""

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
            Output("product-pricing-table", "data", allow_duplicate=True),
            Output("product-cost-table", "data", allow_duplicate=True),
            Output("product-size", "value", allow_duplicate=True),
            Output("product-density", "value", allow_duplicate=True),
            Output("product-abv", "value", allow_duplicate=True),
            Output("product-dgflag", "value", allow_duplicate=True),
            Output("product-purchase-unit-dropdown", "value", allow_duplicate=True),
            Output("product-usage-unit-dropdown", "value", allow_duplicate=True),
            Output("product-usage-cost", "value", allow_duplicate=True),
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
                    "inc_gst": None,
                    "ex_gst": None,
                    "excise": None,
                },
                {
                    "price_level": "Distributor",
                    "inc_gst": None,
                    "ex_gst": None,
                    "excise": None,
                },
                {
                    "price_level": "Counter",
                    "inc_gst": None,
                    "ex_gst": None,
                    "excise": None,
                },
                {
                    "price_level": "Trade",
                    "inc_gst": None,
                    "ex_gst": None,
                    "excise": None,
                },
                {
                    "price_level": "Contract",
                    "inc_gst": None,
                    "ex_gst": None,
                    "excise": None,
                },
                {
                    "price_level": "Industrial",
                    "inc_gst": None,
                    "ex_gst": None,
                    "excise": None,
                },
            ]
            cost_data = [
                {
                    "cost_type": "Purchase Cost",
                    "ex_gst": None,
                    "inc_gst": None,
                    "tax_included": False,
                },
                {
                    "cost_type": "Usage Cost",
                    "ex_gst": None,
                    "inc_gst": None,
                    "tax_included": False,
                },
                {
                    "cost_type": "Manufactured Cost",
                    "ex_gst": None,
                    "inc_gst": None,
                    "tax_included": "N/A",
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
                pricing_data,  # pricing_table
                cost_data,  # cost_table
                None,  # size
                None,  # density
                None,  # abv
                None,  # dgflag
                None,  # purchase-unit
                None,  # usage-unit
                None,  # usage-cost
                None,  # purchase-format
                "",  # product-form-hidden (product_id)
            )

        elif button_id == "edit-product-btn" or button_id == "duplicate-product-btn":
            if not selected_rows or not data:
                raise PreventUpdate

            product = data[selected_rows[0]]
            is_duplicate = button_id == "duplicate-product-btn"

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

            # Build pricing table data
            pricing_data = [
                {
                    "price_level": "Retail",
                    "inc_gst": safe_float(product.get("retail_price_inc_gst")),
                    "ex_gst": safe_float(product.get("retail_price_ex_gst")),
                    "excise": safe_float(product.get("retail_excise")),
                },
                {
                    "price_level": "Wholesale",
                    "inc_gst": safe_float(product.get("wholesale_price_inc_gst")),
                    "ex_gst": safe_float(product.get("wholesale_price_ex_gst")),
                    "excise": safe_float(product.get("wholesale_excise")),
                },
                {
                    "price_level": "Distributor",
                    "inc_gst": safe_float(product.get("distributor_price_inc_gst")),
                    "ex_gst": safe_float(product.get("distributor_price_ex_gst")),
                    "excise": safe_float(product.get("distributor_excise")),
                },
                {
                    "price_level": "Counter",
                    "inc_gst": safe_float(product.get("counter_price_inc_gst")),
                    "ex_gst": safe_float(product.get("counter_price_ex_gst")),
                    "excise": safe_float(product.get("counter_excise")),
                },
                {
                    "price_level": "Trade",
                    "inc_gst": safe_float(product.get("trade_price_inc_gst")),
                    "ex_gst": safe_float(product.get("trade_price_ex_gst")),
                    "excise": safe_float(product.get("trade_excise")),
                },
                {
                    "price_level": "Contract",
                    "inc_gst": safe_float(product.get("contract_price_inc_gst")),
                    "ex_gst": safe_float(product.get("contract_price_ex_gst")),
                    "excise": safe_float(product.get("contract_excise")),
                },
                {
                    "price_level": "Industrial",
                    "inc_gst": safe_float(product.get("industrial_price_inc_gst")),
                    "ex_gst": safe_float(product.get("industrial_price_ex_gst")),
                    "excise": safe_float(product.get("industrial_excise")),
                },
            ]

            # Build cost table data
            cost_data = [
                {
                    "cost_type": "Purchase Cost",
                    "ex_gst": safe_float(product.get("purchase_cost_ex_gst")),
                    "inc_gst": safe_float(product.get("purchase_cost_inc_gst")),
                    "tax_included": product.get("purchase_tax_included") or False,
                },
                {
                    "cost_type": "Usage Cost",
                    "ex_gst": safe_float(product.get("usage_cost_ex_gst")),
                    "inc_gst": safe_float(product.get("usage_cost_inc_gst")),
                    "tax_included": product.get("usage_tax_included") or False,
                },
                {
                    "cost_type": "Manufactured Cost",
                    "ex_gst": safe_float(product.get("manufactured_cost_ex_gst")),
                    "inc_gst": safe_float(product.get("manufactured_cost_inc_gst")),
                    "tax_included": "N/A",
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
                pricing_data,
                cost_data,
                product.get("size") or "",
                safe_float(product.get("density_kg_per_l")),
                safe_float(product.get("abv_percent")),
                product.get("dgflag") or "",
                purchase_unit_id,
                product.get("usage_unit") or "",
                safe_float(product.get("usage_cost")),
                purchase_format_id,
                ""
                if is_duplicate
                else (
                    str(product.get("id", "")) if product.get("id") else ""
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

    # Save product (create or update)
    @app.callback(
        [
            Output("product-form-modal", "is_open", allow_duplicate=True),
            Output("toast", "is_open"),
            Output("toast", "header"),
            Output("toast", "children"),
            Output("products-refresh-trigger", "children", allow_duplicate=True),
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
            State("product-pricing-table", "data"),
            State("product-cost-table", "data"),
            State("product-size", "value"),
            State("product-weight", "value"),
            State("product-density", "value"),
            State("product-abv", "value"),
            State("product-dgflag", "value"),
            State("product-purchase-unit-dropdown", "value"),
            State("product-usage-unit-dropdown", "value"),
            State("product-usage-cost", "value"),
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
            pricing_data,
            cost_data,
            size,
            weight,
            density,
            abv,
            dgflag,
            purchase_unit_id,
            usage_unit,
            usage_cost,
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
                        return val if val != "N/A" else None
                    if val is None or val == "":
                        return None
                    try:
                        return float(val)
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
            "ean13": ean13.strip() if ean13 else None,
            "supplier_id": str(supplier_id) if supplier_id else None,
            "purchase_format_id": str(purchase_format_id)
            if purchase_format_id
            else None,
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
            # Cost Pricing from table
            "purchase_cost_ex_gst": get_cost_value(
                cost_data, "Purchase Cost", "ex_gst"
            ),
            "purchase_cost_inc_gst": get_cost_value(
                cost_data, "Purchase Cost", "inc_gst"
            ),
            "purchase_tax_included": get_cost_value(
                cost_data, "Purchase Cost", "tax_included"
            ),
            "usage_cost_ex_gst": get_cost_value(cost_data, "Usage Cost", "ex_gst"),
            "usage_cost_inc_gst": get_cost_value(cost_data, "Usage Cost", "inc_gst"),
            "usage_tax_included": get_cost_value(
                cost_data, "Usage Cost", "tax_included"
            ),
            "manufactured_cost_ex_gst": get_cost_value(
                cost_data, "Manufactured Cost", "ex_gst"
            ),
            "manufactured_cost_inc_gst": get_cost_value(
                cost_data, "Manufactured Cost", "inc_gst"
            ),
            # Raw Material specific fields
            "purchase_unit_id": purchase_unit_id if purchase_unit_id else None,
            # purchase_volume renamed to purchase_quantity in model - not in form, always None
            "usage_unit": usage_unit if usage_unit else None,
            "usage_cost": (
                float(usage_cost)
                if usage_cost is not None
                and str(usage_cost).strip()
                and str(usage_cost).strip() != ""
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
                return True, True, "Error", error_msg, ""

            # Trigger table refresh by updating refresh trigger
            import time

            refresh_timestamp = str(time.time())
            return False, True, "Success", success_msg, refresh_timestamp

        except Exception as e:
            # On error, don't refresh table (operation failed)
            return True, True, "Error", f"Failed to save product: {str(e)}", ""

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
                # If base_unit is L/LT, size is already in liters
                if base_unit and base_unit.upper() in [
                    "L",
                    "LT",
                    "LTR",
                    "LITER",
                    "LITRE",
                ]:
                    volume_liters = size_val
                elif base_unit and base_unit.upper() in ["KG", "KILOGRAM"] and density:
                    # Convert from kg to liters using density
                    density_val = float(density)
                    if density_val > 0:
                        volume_liters = size_val / density_val
                    else:
                        volume_liters = size_val  # Fallback
                else:
                    # Assume size is already in liters if no conversion info
                    volume_liters = size_val
            elif base_unit and base_unit.upper() in [
                "L",
                "LT",
                "LTR",
                "LITER",
                "LITRE",
            ]:
                # No size specified, but base_unit is L, so 1 liter per unit
                volume_liters = 1.0
            elif base_unit and base_unit.upper() in ["KG", "KILOGRAM"] and density:
                # No size specified, but base_unit is KG, convert 1 kg to liters
                density_val = float(density)
                if density_val > 0:
                    volume_liters = 1.0 / density_val
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

            updated_data.append(
                {
                    "price_level": price_level,
                    "inc_gst": (
                        round(inc_gst_val, 2) if inc_gst_val is not None else None
                    ),
                    "ex_gst": round(ex_gst_val, 2) if ex_gst_val is not None else None,
                    "excise": round(excise_val, 2) if excise_val is not None else None,
                }
            )

        return updated_data

    # Auto-calculate GST for cost table
    @app.callback(
        Output("product-cost-table", "data", allow_duplicate=True),
        [Input("product-cost-table", "data")],
        prevent_initial_call=True,
    )
    def calculate_cost_table(cost_data):
        """Auto-calculate GST when cost values change. Allow values to be cleared."""
        if not cost_data:
            raise PreventUpdate

        GST_RATE = 0.10

        updated_data = []
        for row in cost_data:
            cost_type = row.get("cost_type", "")
            ex_gst = row.get("ex_gst")
            inc_gst = row.get("inc_gst")
            tax_included = row.get("tax_included")

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
                        "ex_gst": (
                            round(ex_gst_val, 2) if ex_gst_val is not None else None
                        ),
                        "inc_gst": (
                            round(inc_gst_val, 2) if inc_gst_val is not None else None
                        ),
                        "tax_included": "N/A",
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

                updated_data.append(
                    {
                        "cost_type": cost_type,
                        "ex_gst": (
                            round(ex_gst_val, 2) if ex_gst_val is not None else None
                        ),
                        "inc_gst": (
                            round(inc_gst_val, 2) if inc_gst_val is not None else None
                        ),
                        "tax_included": (
                            tax_included if tax_included is not None else False
                        ),
                    }
                )

        return updated_data

    # Display product detail panel when product is selected
    @app.callback(
        [
            Output("product-detail-title", "children"),
            Output("product-detail-sku", "children"),
            Output("product-detail-capabilities", "children"),
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

        if (
            is_purchase is True
            or is_purchase == "✓"
            or (isinstance(is_purchase, str) and is_purchase.strip() == "✓")
        ):
            caps.append("Purchase")
        if (
            is_sell is True
            or is_sell == "✓"
            or (isinstance(is_sell, str) and is_sell.strip() == "✓")
        ):
            caps.append("Sell")
        if (
            is_assemble is True
            or is_assemble == "✓"
            or (isinstance(is_assemble, str) and is_assemble.strip() == "✓")
        ):
            caps.append("Assemble")
        product_type = ", ".join(caps) if caps else "None"

        # Build consolidated cost/pricing table with all requested calculations
        consolidated_rows = []

        # Cost types
        cost_types = [
            {
                "name": "Purchase Cost",
                "ex_gst": product.get("purchase_cost_ex_gst"),
                "excise": None,
            },
            {
                "name": "Usage Cost",
                "ex_gst": product.get("usage_cost_ex_gst"),
                "excise": None,
            },
            {
                "name": "Manufactured Cost",
                "ex_gst": product.get("manufactured_cost_ex_gst"),
                "excise": None,
            },
        ]

        # Pricing data
        distributor_ex_gst = product.get("distributor_price_ex_gst")
        distributor_inc_gst = product.get("distributor_price_inc_gst")
        retail_ex_gst = product.get("retail_price_ex_gst")
        retail_inc_gst = product.get("retail_price_inc_gst")

        for cost_type in cost_types:
            ex_gst = cost_type["ex_gst"] or 0.0
            excise = cost_type.get("excise") or 0.0

            # Calculate Ex-GST+Excise
            ex_gst_plus_excise = ex_gst + excise

            # Calculate Excised (calculated as [ex-excise + Excise]*1.1)
            excised = (ex_gst + excise) * 1.1

            # Calculate UnExcised (calculated as ex-GST * 1.1)
            unexcised = ex_gst * 1.1

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

            consolidated_rows.append(
                {
                    "Cost Type": cost_type["name"],
                    "Ex GST": f"${ex_gst:.2f}" if ex_gst else "-",
                    "Excise": f"${excise:.2f}" if excise else "-",
                    "Ex-GST+Excise": (
                        f"${ex_gst_plus_excise:.2f}" if ex_gst_plus_excise else "-"
                    ),
                    "Excised": f"${excised:.2f}" if excised else "-",
                    "UnExcised": f"${unexcised:.2f}" if unexcised else "-",
                    "Distributor Inc GST": (
                        f"${dist_inc_gst_calc:.2f}" if dist_inc_gst_calc else "-"
                    ),
                    "Dist Profit Margin": (
                        f"{dist_profit_margin:.1f}%"
                        if dist_profit_margin is not None
                        else "-"
                    ),
                    "Retail Price": (
                        f"${retail_price_calc:.2f}" if retail_price_calc else "-"
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
            product.get("name", "Product Details"),
            product.get("sku", "-"),
            product_type,
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
        ],
        prevent_initial_call=True,
    )
    def apply_inventory_adjustment(
        n_clicks, product_id, adjustment_type, quantity, unit_cost, lot_code, notes
    ):
        """Apply inventory adjustment."""
        if not n_clicks:
            raise PreventUpdate

        if not product_id:
            return True, "Error", "Product ID not found", no_update

        if not adjustment_type or quantity is None:
            return True, "Error", "Adjustment Type and Quantity are required", no_update

        try:
            adjustment_data = {
                "product_id": product_id,
                "adjustment_type": adjustment_type,
                "quantity_kg": float(quantity),
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

            return (
                True,
                "Success",
                f"Inventory adjusted successfully. New stock: {new_stock if isinstance(new_stock, str) else 'updated'}",
                new_stock,
            )

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

                    # Calculate total cost from lines using actual product costs
                    total_cost = 0.0
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
                                            unit_cost = float(
                                                prod_resp.get("usage_cost_ex_gst", 0)
                                                or prod_resp.get(
                                                    "purchase_cost_ex_gst", 0
                                                )
                                                or 0
                                            )
                                    except (ValueError, KeyError, TypeError):
                                        pass
                            total_cost += (
                                qty_kg * float(unit_cost) if unit_cost else 0.0
                            )

                    # Create flattened structure - no nested objects
                    assembly_data.append(
                        {
                            "formula_id": str(formula.get("id", "")),
                            "version": int(formula.get("version", 1)),
                            "formula_code": str(formula.get("formula_code", "")),
                            "formula_name": str(formula.get("formula_name", "")),
                            "sequence": 1,  # Would be from formula or line
                            "ratio": "1:1",  # Would calculate from formula lines
                            "yield_factor": "1.0",  # Would be from formula
                            "is_primary": "✓" if formula.get("is_active") else "",
                            "cost": f"${total_cost:.2f}" if total_cost > 0 else "-",
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
                                    unit_cost = float(
                                        product_resp.get("usage_cost_ex_gst", 0)
                                        or product_resp.get("purchase_cost_ex_gst", 0)
                                        or 0
                                    )
                                    density = float(
                                        product_resp.get("density_kg_per_l", 0) or 0
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

                        # Convert kg to display unit
                        quantity_display = quantity_kg
                        if (
                            unit.upper() in ["L", "LT", "LTR", "LITER", "LITRE"]
                            and density > 0
                        ):
                            quantity_display = quantity_kg / density

                        # Calculate quantity in L
                        quantity_l = 0.0
                        if density > 0:
                            quantity_l = quantity_kg / density

                        line_cost = quantity_kg * unit_cost

                        # Check if this is the primary line (first line or marked)
                        is_primary = line.get("is_primary", False) or (
                            idx == 0 and primary_index is None
                        )
                        if is_primary:
                            primary_index = idx

                        primary_button = "✓" if is_primary else "[Set Primary]"

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
                                "unit_cost": round(unit_cost, 2),
                                "line_cost": round(line_cost, 2),
                                "is_primary": primary_button,
                                "is_primary_bool": is_primary,
                                "notes": line.get("notes", ""),
                            }
                        )

                    return (
                        True,  # is_open
                        f"Edit Assembly: {formula_response.get('formula_name', '')}",  # title
                        formula_id,  # formula_id
                        product_id,  # product_id
                        product_id or "",  # parent_product_id (hidden)
                        formula_response.get("formula_name", ""),  # name
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
            State("assembly-lines-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_assembly(n_clicks, formula_id, product_id, name, lines_data):
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
            formula_lines = []
            for i, line in enumerate(lines_data or []):
                product_id_line = line.get("product_id")
                if not product_id_line:
                    continue  # Skip lines without product

                # Use quantity_kg if available (from calculations), otherwise convert
                quantity_kg = line.get("quantity_kg")
                if quantity_kg is None:
                    quantity = float(line.get("quantity", 0.0) or 0.0)
                    # Would need density for L conversion, but use quantity as fallback
                    quantity_kg = quantity

                # Ensure all required fields are present and properly typed
                formula_lines.append(
                    {
                        "raw_material_id": str(product_id_line),
                        "quantity_kg": float(quantity_kg),
                        "sequence": int(line.get("sequence", i + 1)),
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

            if formula_id:
                # Update existing formula
                # First update header
                update_data = {
                    "formula_name": name,
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
                    for formula in formulas_response:
                        # Get lines safely - ensure it's a list, not an object
                        lines_list = formula.get("lines", [])
                        if not isinstance(lines_list, list):
                            lines_list = []

                        lines_count = len(lines_list)
                        total_cost = 0.0
                        for line in lines_list:
                            if isinstance(line, dict):
                                qty = float(line.get("quantity_kg", 0.0) or 0.0)
                                total_cost += qty  # Placeholder

                        # Create flattened structure - no nested objects
                        assembly_data.append(
                            {
                                "formula_id": str(formula.get("id", "")),
                                "version": int(formula.get("version", 1)),
                                "formula_code": str(formula.get("formula_code", "")),
                                "formula_name": str(formula.get("formula_name", "")),
                                "sequence": 1,
                                "ratio": "1:1",
                                "yield_factor": "1.0",
                                "is_primary": "✓" if formula.get("is_active") else "",
                                "cost": f"${total_cost:.2f}" if total_cost > 0 else "-",
                                "lines_count": int(
                                    lines_count
                                ),  # Convert to int, not list
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
                for formula in formulas_response:
                    lines_count = len(formula.get("lines", []))
                    total_cost = 0.0
                    for line in formula.get("lines", []):
                        qty = line.get("quantity_kg", 0.0) or 0.0
                        total_cost += qty

                    assembly_data_new.append(
                        {
                            "formula_id": formula.get("id"),
                            "version": formula.get("version", 1),
                            "formula_code": formula.get("formula_code", ""),
                            "formula_name": formula.get("formula_name", ""),
                            "sequence": 1,
                            "ratio": "1:1",
                            "yield_factor": "1.0",
                            "is_primary": "✓" if formula.get("is_active") else "",
                            "cost": f"${total_cost:.2f}" if total_cost > 0 else "-",
                            "lines_count": lines_count,
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
                for formula in formulas_response:
                    lines_count = len(formula.get("lines", []))
                    total_cost = 0.0
                    for line in formula.get("lines", []):
                        qty = line.get("quantity_kg", 0.0) or 0.0
                        total_cost += qty

                    assembly_data_new.append(
                        {
                            "formula_id": formula.get("id"),
                            "version": formula.get("version", 1),
                            "formula_code": formula.get("formula_code", ""),
                            "formula_name": formula.get("formula_name", ""),
                            "sequence": 1,
                            "ratio": "1:1",
                            "yield_factor": "1.0",
                            "is_primary": "✓" if formula.get("is_active") else "",
                            "cost": f"${total_cost:.2f}" if total_cost > 0 else "-",
                            "lines_count": lines_count,
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
                        unit_cost = float(
                            product_resp.get("usage_cost_ex_gst", 0)
                            or product_resp.get("purchase_cost_ex_gst", 0)
                            or 0
                        )
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
                "unit_cost": round(unit_cost, 2),
                "line_cost": round(line_cost, 2),
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
                        "unit_cost": float(
                            product.get("usage_cost_ex_gst", 0)
                            or product.get("purchase_cost_ex_gst", 0)
                            or 0
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
            product_id = line.get("product_id")
            quantity = float(line.get("quantity", 0.0) or 0.0)
            unit = line.get("unit", "kg")

            # Get product density if needed
            density = 0.0
            unit_cost = float(line.get("unit_cost", 0.0) or 0.0)

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
                        if unit_cost == 0:
                            # Get cost from product - prefer usage_cost, then purchase_cost
                            unit_cost = float(
                                product_response.get("usage_cost_ex_gst", 0)
                                or product_response.get("purchase_cost_ex_gst", 0)
                                or 0
                            )
                except (ValueError, KeyError, TypeError):
                    pass

            # Convert quantity to kg
            try:
                density = float(density) if density else 0.0
            except (ValueError, TypeError):
                density = 0.0

            if unit.upper() in ["L", "LT", "LTR", "LITER", "LITRE"]:
                if density > 0:
                    quantity_kg = quantity * density
                    quantity_l = quantity
                else:
                    quantity_kg = quantity  # Fallback - treat L as kg if no density
                    quantity_l = 0.0
            elif unit.upper() in ["EA", "EACH", "UNIT", "UNITS"]:
                # For "each" units, check if product has weight_kg
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
                                quantity_kg = quantity * float(weight_kg)
                                quantity_l = (
                                    quantity_kg / density if density > 0 else 0.0
                                )
                            else:
                                quantity_kg = 0.0
                                quantity_l = 0.0
                        else:
                            quantity_kg = 0.0
                            quantity_l = 0.0
                    except (ValueError, KeyError, TypeError):
                        quantity_kg = 0.0
                        quantity_l = 0.0
                else:
                    quantity_kg = 0.0
                    quantity_l = 0.0
            else:
                # Assume kg for other units
                quantity_kg = quantity
                quantity_l = quantity_kg / density if density > 0 else 0.0

            # Calculate line cost using actual unit cost
            line_cost = (
                quantity_kg * unit_cost if unit_cost > 0 and quantity_kg > 0 else 0.0
            )
            total_cost += line_cost
            total_quantity_kg += quantity_kg
            total_quantity_l += quantity_l

            # Check if this is the primary line
            is_primary = line.get("is_primary_bool", False)
            if is_primary:
                pass

            # Update primary button display
            primary_button = "✓" if is_primary else "[Set Primary]"

            updated_line = {
                **line,
                "quantity_kg": round(quantity_kg, 3),
                "quantity_l": round(quantity_l, 3),
                "unit_cost": round(unit_cost, 2),
                "line_cost": round(line_cost, 2),
                "is_primary": primary_button,
            }
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
                "cost_per_kg": round(cost_per_kg, 2),
                "cost_per_l": round(cost_per_l, 2),
            },
            {
                "type": "normalised",
                "total_cost": round(total_cost, 2),
                "assembly_mass_kg": round(total_quantity_kg, 3),
                "assembly_volume_l": round(total_quantity_l, 3),
                "cost_per_kg": round(cost_per_kg, 2),
                "cost_per_l": round(cost_per_l, 2),
            },
        ]

        return (
            updated_data,
            f"${total_cost:.2f}",
            f"{total_quantity_kg:.3f}",
            f"{total_quantity_l:.3f}",
            f"${cost_per_kg:.2f}",
            f"${cost_per_l:.2f}",
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

    # Handle product selection from dropdown
    @app.callback(
        Output("assembly-lines-table", "data", allow_duplicate=True),
        [Input("assembly-lines-table", "data_previous")],
        [State("assembly-lines-table", "data")],
        prevent_initial_call=True,
    )
    def handle_product_selection(previous_data, current_data):
        """Handle product selection change in dropdown."""
        if not previous_data or not current_data:
            raise PreventUpdate

        # Find which line changed
        for i, (prev_line, curr_line) in enumerate(zip(previous_data, current_data)):
            if prev_line.get("product_search") != curr_line.get("product_search"):
                # Product changed - fetch product details
                product_search = curr_line.get("product_search")
                if product_search:
                    # Extract product ID from dropdown value
                    try:
                        # Dropdown returns product ID as value
                        product_id = product_search

                        product_response = make_api_request(
                            "GET", f"/products/{product_id}"
                        )

                        if (
                            isinstance(product_response, dict)
                            and "error" not in product_response
                        ):
                            updated_data = current_data.copy()
                            updated_data[i] = {
                                **updated_data[i],
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
                                updated_data[i].get("quantity", 0.0) or 0.0
                            )
                            unit = updated_data[i].get("unit", "kg")
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
                                updated_data[i].get("unit_cost", 0.0) or 0.0
                            )
                            line_cost = quantity_kg * unit_cost

                            updated_data[i]["quantity_kg"] = round(quantity_kg, 3)
                            updated_data[i]["line_cost"] = round(line_cost, 2)

                            return updated_data
                    except Exception as e:
                        print(f"Error fetching product: {e}")

        raise PreventUpdate

    # Note: Table refresh is now handled by the main callback in app.py that responds to filter changes
