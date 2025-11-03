"""CRUD callbacks for products page."""

import dash
from dash import Input, Output, State, dash_table, html, no_update
from dash.exceptions import PreventUpdate


def register_product_callbacks(app, make_api_request):
    """Register all product CRUD callbacks."""

    # Load units for dropdowns
    @app.callback(
        [
            Output("product-base-unit", "options"),
            Output("product-purchase-unit", "options"),
            Output("product-usage-unit", "options"),
        ],
        [Input("product-form-modal", "is_open")],
    )
    def load_units_dropdowns(modal_is_open):
        """Load units from API for dropdown options."""
        if not modal_is_open:
            raise PreventUpdate

        try:
            response = make_api_request("GET", "/units/?is_active=true")
            units = response if isinstance(response, list) else []

            # Create options list for base_unit and usage_unit (store code, not ID)
            code_options = [
                {
                    "label": f"{u.get('code', '')} - {u.get('name', '')}",
                    "value": u.get("code", ""),
                }
                for u in units
            ]

            # Create options list for purchase_unit (store ID, not code)
            id_options = [
                {
                    "label": f"{u.get('code', '')} - {u.get('name', '')}",
                    "value": str(u.get("id", "")),
                }
                for u in units
            ]

            return code_options, id_options, code_options
        except Exception as e:
            print(f"Error loading units: {e}")
            return [], [], []

    # Toggle edit/delete buttons based on selection
    @app.callback(
        [
            Output("edit-product-btn", "disabled"),
            Output("delete-product-btn", "disabled"),
        ],
        [Input("products-table", "selected_rows")],
    )
    def toggle_action_buttons(selected_rows):
        disabled = not selected_rows or len(selected_rows) == 0
        return disabled, disabled

    # Open modal for add/edit and populate form
    @app.callback(
        [
            Output("product-form-modal", "is_open", allow_duplicate=True),
            Output("product-modal-title", "children", allow_duplicate=True),
            Output("product-sku", "value", allow_duplicate=True),
            Output("product-name", "value", allow_duplicate=True),
            Output("product-description", "value", allow_duplicate=True),
            Output("product-ean13", "value", allow_duplicate=True),
            Output("product-supplier-id", "value", allow_duplicate=True),
            Output("product-raw-material-group-id", "value", allow_duplicate=True),
            Output("product-base-unit", "value", allow_duplicate=True),
            Output("product-is-active", "value", allow_duplicate=True),
            Output("product-is-purchase", "value", allow_duplicate=True),
            Output("product-is-sell", "value", allow_duplicate=True),
            Output("product-is-assemble", "value", allow_duplicate=True),
            Output("product-pricing-table", "data", allow_duplicate=True),
            Output("product-cost-table", "data", allow_duplicate=True),
            Output("product-size", "value", allow_duplicate=True),
            Output("product-pack", "value", allow_duplicate=True),
            Output("product-pkge", "value", allow_duplicate=True),
            Output("product-density", "value", allow_duplicate=True),
            Output("product-abv", "value", allow_duplicate=True),
            Output("product-dgflag", "value", allow_duplicate=True),
            Output("product-taxinc", "value", allow_duplicate=True),
            Output("product-salestaxcde", "value", allow_duplicate=True),
            Output("product-purcost", "value", allow_duplicate=True),
            Output("product-purtax", "value", allow_duplicate=True),
            Output("product-wholesalecost", "value", allow_duplicate=True),
            Output("product-excise-amount", "value", allow_duplicate=True),
            Output("product-wholesalecde", "value", allow_duplicate=True),
            Output("product-retailcde", "value", allow_duplicate=True),
            Output("product-countercde", "value", allow_duplicate=True),
            Output("product-tradecde", "value", allow_duplicate=True),
            Output("product-contractcde", "value", allow_duplicate=True),
            Output("product-industrialcde", "value", allow_duplicate=True),
            Output("product-distributorcde", "value", allow_duplicate=True),
            Output("product-disccdeone", "value", allow_duplicate=True),
            Output("product-disccdetwo", "value", allow_duplicate=True),
            Output("product-purchase-unit", "value", allow_duplicate=True),
            Output("product-purchase-volume", "value", allow_duplicate=True),
            Output("product-usage-unit", "value", allow_duplicate=True),
            Output("product-usage-cost", "value", allow_duplicate=True),
            Output("product-restock-level", "value", allow_duplicate=True),
            Output("product-formula-id", "value", allow_duplicate=True),
            Output("product-formula-revision", "value", allow_duplicate=True),
            Output("product-form-hidden", "children", allow_duplicate=True),
        ],
        [Input("add-product-btn", "n_clicks"), Input("edit-product-btn", "n_clicks")],
        [State("products-table", "selected_rows"), State("products-table", "data")],
        prevent_initial_call=True,
    )
    def open_product_modal(add_clicks, edit_clicks, selected_rows, data):
        """Open modal for add or edit and populate form data."""
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
                None,  # raw_material_group_id
                None,  # base_unit
                "true",  # is_active
                False,  # is_purchase
                False,  # is_sell
                False,  # is_assemble
                pricing_data,  # pricing_table
                cost_data,  # cost_table
                None,  # size
                None,  # pack
                None,  # pkge
                None,  # density
                None,  # abv
                None,  # dgflag
                None,  # taxinc
                None,  # salestaxcde
                None,  # purcost
                None,  # purtax
                None,  # wholesalecost
                None,  # excise-amount
                None,  # wholesalecde
                None,  # retailcde
                None,  # countercde
                None,  # tradecde
                None,  # contractcde
                None,  # industrialcde
                None,  # distributorcde
                None,  # disccdeone
                None,  # disccdetwo
                None,  # purchase-unit
                None,  # purchase-volume
                None,  # usage-unit
                None,  # usage-cost
                None,  # restock-level
                None,  # formula-id
                None,  # formula-revision
                "",  # product-form-hidden (product_id)
            )

        elif button_id == "edit-product-btn":
            if not selected_rows or not data:
                raise PreventUpdate

            product = data[selected_rows[0]]

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

            return (
                True,  # is_open
                "Edit Product",  # title
                product.get("sku") or "",
                product.get("name") or "",
                product.get("description") or "",
                product.get("ean13") or "",
                str(product.get("supplier_id", ""))
                if product.get("supplier_id")
                else "",
                str(product.get("raw_material_group_id", ""))
                if product.get("raw_material_group_id")
                else "",
                product.get("base_unit") or "",
                is_active_str,
                product.get("is_purchase") or False,
                product.get("is_sell") or False,
                product.get("is_assemble") or False,
                pricing_data,
                cost_data,
                product.get("size") or "",
                safe_int(product.get("pack")),
                safe_int(product.get("pkge")),
                safe_float(product.get("density_kg_per_l")),
                safe_float(product.get("abv_percent")),
                product.get("dgflag") or "",
                product.get("taxinc") or "",
                product.get("salestaxcde") or "",
                safe_float(product.get("purcost")),
                safe_float(product.get("purtax")),
                safe_float(product.get("wholesalecost")),
                safe_float(product.get("excise_amount")),
                safe_float(product.get("wholesalecde")),
                safe_float(product.get("retailcde")),
                safe_float(product.get("countercde")),
                safe_float(product.get("tradecde")),
                safe_float(product.get("contractcde")),
                safe_float(product.get("industrialcde")),
                safe_float(product.get("distributorcde")),
                safe_float(product.get("disccdeone")),
                safe_float(product.get("disccdetwo")),
                purchase_unit_id,
                safe_float(product.get("purchase_volume")),
                product.get("usage_unit") or "",
                safe_float(product.get("usage_cost")),
                safe_float(product.get("restock_level")),
                str(product.get("formula_id", "")) if product.get("formula_id") else "",
                safe_int(product.get("formula_revision")),
                str(product.get("id", "")) if product.get("id") else "",
            )

        raise PreventUpdate

    # Close modal on cancel or save
    @app.callback(
        Output("product-form-modal", "is_open", allow_duplicate=True),
        [
            Input("product-cancel-btn", "n_clicks"),
            Input("product-save-btn", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def close_modal(cancel_clicks, save_clicks):
        """Close modal when cancel or save is clicked."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        return False

    # Save product (create or update)
    @app.callback(
        [
            Output("toast", "is_open"),
            Output("toast", "header"),
            Output("toast", "children"),
            Output("products-table", "data", allow_duplicate=True),
        ],
        [Input("product-save-btn", "n_clicks")],
        [
            State("product-sku", "value"),
            State("product-name", "value"),
            State("product-description", "value"),
            State("product-ean13", "value"),
            State("product-supplier-id", "value"),
            State("product-raw-material-group-id", "value"),
            State("product-base-unit", "value"),
            State("product-is-active", "value"),
            State("product-is-purchase", "value"),
            State("product-is-sell", "value"),
            State("product-is-assemble", "value"),
            State("product-pricing-table", "data"),
            State("product-cost-table", "data"),
            State("product-size", "value"),
            State("product-weight", "value"),
            State("product-pack", "value"),
            State("product-pkge", "value"),
            State("product-density", "value"),
            State("product-abv", "value"),
            State("product-dgflag", "value"),
            State("product-taxinc", "value"),
            State("product-salestaxcde", "value"),
            State("product-purcost", "value"),
            State("product-purtax", "value"),
            State("product-wholesalecost", "value"),
            State("product-excise-amount", "value"),
            State("product-wholesalecde", "value"),
            State("product-retailcde", "value"),
            State("product-countercde", "value"),
            State("product-tradecde", "value"),
            State("product-contractcde", "value"),
            State("product-industrialcde", "value"),
            State("product-distributorcde", "value"),
            State("product-disccdeone", "value"),
            State("product-disccdetwo", "value"),
            State("product-purchase-unit", "value"),
            State("product-purchase-volume", "value"),
            State("product-usage-unit", "value"),
            State("product-usage-cost", "value"),
            State("product-restock-level", "value"),
            State("product-formula-id", "value"),
            State("product-formula-revision", "value"),
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
            raw_material_group_id,
            base_unit,
            is_active,
            is_purchase,
            is_sell,
            is_assemble,
            pricing_data,
            cost_data,
            size,
            weight,
            pack,
            pkge,
            density,
            abv,
            dgflag,
            taxinc,
            salestaxcde,
            purcost,
            purtax,
            wholesalecost,
            excise_amount,
            wholesalecde,
            retailcde,
            countercde,
            tradecde,
            contractcde,
            industrialcde,
            distributorcde,
            disccdeone,
            disccdetwo,
            purchase_unit_id,
            purchase_volume,
            usage_unit,
            usage_cost,
            restock_level,
            formula_id,
            formula_revision,
            product_id,
        ) = args

        # Validate required fields
        if not sku or not name:
            return True, "Error", "SKU and Name are required", dash.no_update

        # Extract pricing data from table
        def get_price_value(pricing_data, price_level, field):
            if not pricing_data:
                return None
            for row in pricing_data:
                if row.get("price_level") == price_level:
                    val = row.get(field)
                    return float(val) if val is not None and val != "" else None
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
                    return float(val) if val is not None and val != "" else None
            return None

        # Prepare product data
        product_data = {
            "sku": sku,
            "name": name,
            "description": description if description else None,
            "is_purchase": bool(is_purchase) if is_purchase is not None else False,
            "is_sell": bool(is_sell) if is_sell is not None else False,
            "is_assemble": bool(is_assemble) if is_assemble is not None else False,
            "ean13": ean13 if ean13 else None,
            "supplier_id": supplier_id if supplier_id else None,
            "raw_material_group_id": raw_material_group_id
            if raw_material_group_id
            else None,
            "base_unit": base_unit if base_unit else None,
            "is_active": bool(
                is_active == "true"
                if isinstance(is_active, str)
                else (is_active if is_active is not None else True)
            ),
            "size": size if size else None,
            "weight_kg": float(weight) if weight else None,
            "pack": int(pack) if pack else None,
            "pkge": int(pkge) if pkge else None,
            "density_kg_per_l": float(density) if density else None,
            "abv_percent": float(abv) if abv else None,
            "dgflag": dgflag if dgflag else None,
            "taxinc": taxinc if taxinc else None,
            "salestaxcde": salestaxcde if salestaxcde else None,
            "purcost": float(purcost) if purcost else None,
            "purtax": float(purtax) if purtax else None,
            "wholesalecost": float(wholesalecost) if wholesalecost else None,
            "excise_amount": float(excise_amount) if excise_amount else None,
            # Legacy pricing fields (for backward compatibility)
            "wholesalecde": str(wholesalecde) if wholesalecde else None,
            "retailcde": str(retailcde) if retailcde else None,
            "countercde": str(countercde) if countercde else None,
            "tradecde": str(tradecde) if tradecde else None,
            "contractcde": str(contractcde) if contractcde else None,
            "industrialcde": str(industrialcde) if industrialcde else None,
            "distributorcde": str(distributorcde) if distributorcde else None,
            "disccdeone": str(disccdeone) if disccdeone else None,
            "disccdetwo": str(disccdetwo) if disccdetwo else None,
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
            "purchase_volume": float(purchase_volume) if purchase_volume else None,
            "usage_unit": usage_unit if usage_unit else None,
            "usage_cost": float(usage_cost) if usage_cost else None,
            "restock_level": float(restock_level) if restock_level else None,
            # Finished Good specific fields
            "formula_id": formula_id if formula_id else None,
            "formula_revision": int(formula_revision) if formula_revision else None,
        }

        try:
            if product_id and isinstance(product_id, str):
                # Update existing product
                response = make_api_request(
                    "PUT", f"/products/{product_id}", product_data
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
                return True, "Error", error_msg, no_update

            # Refresh table by returning current data (will trigger table update)
            return False, "Success", success_msg, no_update

        except Exception as e:
            return True, "Error", f"Failed to save product: {str(e)}", no_update

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
            Output("products-table", "data", allow_duplicate=True),
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

            # Remove from table
            new_data = [row for i, row in enumerate(data) if i not in selected_rows]

            return new_data, True, "Success", f"Product {sku} deleted successfully"

        except Exception as e:
            return no_update, True, "Error", f"Failed to delete product: {str(e)}"

    # Auto-calculate excise and GST for pricing table
    @app.callback(
        Output("product-pricing-table", "data", allow_duplicate=True),
        [
            Input("product-pricing-table", "data"),
            Input("product-abv", "value"),
            Input("product-density", "value"),
        ],
        prevent_initial_call=True,
    )
    def calculate_pricing_table(pricing_data, abv, density):
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

        # Calculate excise and GST for each price level
        updated_data = []
        for row in pricing_data:
            price_level = row.get("price_level", "")
            inc_gst = row.get("inc_gst")
            ex_gst = row.get("ex_gst")

            # If inc_gst is provided, calculate ex_gst and excise
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

            # Calculate excise if we have ABV and density
            excise_val = None
            if abv and density and ex_gst_val is not None:
                try:
                    abv_val = float(abv)
                    density_val = float(density)
                    # Excise is calculated per liter of ABV
                    # If price is per kg, convert to liters first
                    # Excise = (ex_gst_price / density) * (abv/100) * excise_rate_per_l_abv
                    if density_val > 0:
                        liters = 1.0 / density_val  # 1 kg = X liters
                        abv_liters = liters * (abv_val / 100.0)
                        excise_val = abv_liters * excise_rate_per_l_abv
                except (ValueError, TypeError):
                    excise_val = None

            updated_data.append(
                {
                    "price_level": price_level,
                    "inc_gst": round(inc_gst_val, 2)
                    if inc_gst_val is not None
                    else None,
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
                        "ex_gst": round(ex_gst_val, 2)
                        if ex_gst_val is not None
                        else None,
                        "inc_gst": round(inc_gst_val, 2)
                        if inc_gst_val is not None
                        else None,
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
                        "ex_gst": round(ex_gst_val, 2)
                        if ex_gst_val is not None
                        else None,
                        "inc_gst": round(inc_gst_val, 2)
                        if inc_gst_val is not None
                        else None,
                        "tax_included": tax_included
                        if tax_included is not None
                        else False,
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

        # Format capabilities - handle both boolean and string (✓) formats
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
        capabilities = ", ".join(caps) if caps else "None"

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
            product.get("name", "Product Details"),
            product.get("sku", "-"),
            capabilities,
            product.get("name", "-"),
            product.get("description") or "-",
            product.get("base_unit") or "-",
            product.get("size") or "-",
            f"{product.get('density_kg_per_l', 0):.3f}"
            if product.get("density_kg_per_l")
            else "-",
            f"{product.get('abv_percent', 0):.2f}%"
            if product.get("abv_percent")
            else "-",
            consolidated_table,
            f"{stock_kg:.3f}",
            f"{lots_count}",
            f"${avg_cost:.2f}/kg" if avg_cost > 0 else "-",
            cost_source,
            f"{product.get('restock_level', 0):.3f} kg"
            if product.get("restock_level")
            else "-",
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
            Output("assembly-code", "value", allow_duplicate=True),
            Output("assembly-name", "value", allow_duplicate=True),
            Output("assembly-version", "value", allow_duplicate=True),
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
            return (
                True,  # is_open
                "New Assembly Definition",  # title
                "",  # formula_id (hidden)
                product_id or "",  # product_id (hidden)
                product_id or "",  # parent_product_id (hidden)
                "",  # code
                "",  # name
                1,  # version
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
                    for line in formula_response.get("lines", []):
                        # Get product details
                        product_id = line.get("raw_material_id")
                        product_sku = ""
                        product_name = line.get("ingredient_name", "")
                        unit_cost = 0.0

                        if product_id:
                            try:
                                product_resp = make_api_request(
                                    "GET", f"/products/{product_id}"
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
                            except (ValueError, KeyError, TypeError):
                                pass

                        quantity_kg = line.get("quantity_kg", 0.0) or 0.0
                        # Get base unit from product if available
                        base_unit_from_line = line.get("unit", "kg") or "kg"
                        if product_id:
                            try:
                                # Re-fetch to ensure we have base_unit
                                product_resp_check = make_api_request(
                                    "GET", f"/products/{product_id}"
                                )
                                if (
                                    isinstance(product_resp_check, dict)
                                    and "error" not in product_resp_check
                                ):
                                    base_unit_from_line = (
                                        product_resp_check.get(
                                            "base_unit", base_unit_from_line
                                        )
                                        or base_unit_from_line
                                    )
                            except (ValueError, KeyError, TypeError):
                                pass

                        unit = base_unit_from_line
                        density = line.get("ingredient_density_kg_per_l") or 0

                        # Convert kg to display unit
                        if (
                            unit.lower() in ["l", "ltr", "liter", "litre"]
                            and density > 0
                        ):
                            quantity_display = quantity_kg / density
                        else:
                            quantity_display = quantity_kg

                        line_cost = quantity_kg * unit_cost

                        lines_data.append(
                            {
                                "sequence": line.get("sequence", 0),
                                "product_search": product_sku or product_name or "",
                                "product_id": product_id,
                                "product_sku": product_sku,
                                "product_name": product_name,
                                "quantity": round(quantity_display, 3),
                                "unit": unit,
                                "quantity_kg": round(quantity_kg, 3),
                                "unit_cost": round(unit_cost, 2),
                                "line_cost": round(line_cost, 2),
                                "notes": line.get("notes", ""),
                            }
                        )

                    return (
                        True,  # is_open
                        f"Edit Assembly: {formula_response.get('formula_code', '')}",  # title
                        formula_id,  # formula_id
                        product_id,  # product_id
                        product_id or "",  # parent_product_id (hidden)
                        formula_response.get("formula_code", ""),  # code
                        formula_response.get("formula_name", ""),  # name
                        formula_response.get("version", 1),  # version
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
            State("assembly-code", "value"),
            State("assembly-name", "value"),
            State("assembly-version", "value"),
            State("assembly-lines-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_assembly(
        n_clicks, formula_id, product_id, code, name, version, lines_data
    ):
        """Save assembly definition (formula)."""
        if not n_clicks:
            raise PreventUpdate

        if not product_id or not code or not name:
            return (
                False,
                True,
                "Error",
                "Product ID, Formula Code, and Name are required",
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

                message = f"Assembly '{code}' updated successfully"
            else:
                # Create new formula
                formula_data = {
                    "product_id": str(product_id),
                    "formula_code": str(code),
                    "formula_name": str(name),
                    "version": int(version) if version else 1,
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
                        True,
                        True,
                        "Error",
                        f"Failed to save assembly: {error_msg}",
                        no_update,
                    )

                message = f"Assembly '{code}' created successfully"

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
        [State("assembly-lines-table", "data")],
        prevent_initial_call=True,
    )
    def add_assembly_line(n_clicks, current_data):
        """Add a new empty line to assembly table."""
        if not n_clicks:
            raise PreventUpdate

        new_line = {
            "sequence": len(current_data) + 1 if current_data else 1,
            "product_search": "",
            "product_id": "",
            "product_sku": "",
            "product_name": "",
            "quantity": 0.0,
            "unit": "kg",
            "quantity_kg": 0.0,
            "unit_cost": 0.0,
            "line_cost": 0.0,
            "notes": "",
        }

        return (current_data or []) + [new_line]

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

                    # Convert to kg
                    if unit.lower() in ["l", "ltr", "liter", "litre"]:
                        if density > 0:
                            quantity_kg = quantity * density
                        else:
                            quantity_kg = quantity  # Fallback
                    else:
                        quantity_kg = quantity

                    unit_cost = float(
                        updated_data[selected_idx].get("unit_cost", 0.0) or 0.0
                    )
                    line_cost = quantity_kg * unit_cost if unit_cost > 0 else 0.0

                    updated_data[selected_idx]["quantity_kg"] = round(quantity_kg, 3)
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
            Output("assembly-total-cost", "children", allow_duplicate=True),
        ],
        [Input("assembly-lines-table", "data")],
        [State("assembly-parent-product-id-hidden", "children")],
        prevent_initial_call=True,
    )
    def calculate_assembly_line_costs(lines_data, parent_product_id):
        """Calculate quantity_kg, line_cost, and total cost for assembly lines."""
        if not lines_data:
            return [], "$0.00 (per kg: $0.00, per L: $0.00)"

        total_cost = 0.0
        total_quantity_kg = 0.0
        total_quantity_l = 0.0
        updated_data = []

        # Get parent product density for cost per L calculation
        parent_density = 0.0
        if parent_product_id:
            try:
                parent_response = make_api_request(
                    "GET", f"/products/{parent_product_id}"
                )
                if isinstance(parent_response, dict) and "error" not in parent_response:
                    density_val = parent_response.get("density_kg_per_l", 0) or 0
                    try:
                        parent_density = float(density_val)
                    except (ValueError, TypeError):
                        parent_density = 0.0
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
                        # Default unit to product base_unit if not set
                        if not unit or unit == "kg":
                            unit = product_response.get("base_unit", "kg") or "kg"
                            line["unit"] = unit
                except (ValueError, KeyError, TypeError):
                    pass

            # Convert quantity to kg
            # Ensure density is numeric
            try:
                density = float(density) if density else 0.0
            except (ValueError, TypeError):
                density = 0.0

            if unit.lower() in ["l", "ltr", "liter", "litre"]:
                if density > 0:
                    quantity_kg = quantity * density
                else:
                    quantity_kg = quantity  # Fallback - treat L as kg if no density
            elif unit.lower() in ["ea", "each", "unit", "units"]:
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
                            else:
                                quantity_kg = 0.0  # No weight available, can't convert
                        else:
                            quantity_kg = 0.0
                    except (ValueError, KeyError, TypeError):
                        quantity_kg = 0.0
                else:
                    quantity_kg = 0.0
            else:
                # Assume kg for other units
                quantity_kg = quantity

            # Calculate line cost using actual unit cost
            line_cost = (
                quantity_kg * unit_cost if unit_cost > 0 and quantity_kg > 0 else 0.0
            )
            total_cost += line_cost
            total_quantity_kg += quantity_kg

            updated_line = {
                **line,
                "quantity_kg": round(quantity_kg, 3),
                "unit_cost": round(unit_cost, 2),
                "line_cost": round(line_cost, 2),
            }
            updated_data.append(updated_line)

        # Calculate total quantity in liters if parent has density
        if parent_density > 0:
            total_quantity_l = total_quantity_kg / parent_density

        # Format total cost display with per kg and per L
        cost_display = f"${total_cost:.2f}"
        if total_quantity_kg > 0:
            cost_per_kg = total_cost / total_quantity_kg
            cost_display += f" (per kg: ${cost_per_kg:.2f}"
            if total_quantity_l > 0:
                cost_per_l = total_cost / total_quantity_l
                cost_display += f", per L: ${cost_per_l:.2f}"
            cost_display += ")"

        return updated_data, cost_display

    # Populate product dropdown options
    @app.callback(
        Output("assembly-lines-table", "dropdown", allow_duplicate=True),
        [Input("assembly-lines-table", "data")],
        prevent_initial_call=True,
    )
    def update_assembly_product_dropdown(lines_data):
        """Update product dropdown options for assembly lines."""
        try:
            # Get all products for dropdown
            products_response = make_api_request("GET", "/products/?limit=1000")

            if isinstance(products_response, list):
                product_options = [
                    {
                        "label": f"{p.get('sku', '')} - {p.get('name', '')}",
                        "value": p.get("id", ""),
                    }
                    for p in products_response
                ]

                # Also get units for unit dropdown
                unit_options = [
                    {"label": "kg", "value": "kg"},
                    {"label": "g", "value": "g"},
                    {"label": "L", "value": "L"},
                    {"label": "mL", "value": "mL"},
                ]

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
