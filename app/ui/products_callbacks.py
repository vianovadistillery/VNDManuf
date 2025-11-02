"""CRUD callbacks for products page."""

import dash
from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc


def register_product_callbacks(app, make_api_request):
    """Register all product CRUD callbacks."""
    
    # Load units for dropdowns
    @app.callback(
        [Output("product-base-unit", "options"),
         Output("product-purchase-unit", "options"),
         Output("product-usage-unit", "options")],
        [Input("product-form-modal", "is_open")]
    )
    def load_units_dropdowns(modal_is_open):
        """Load units from API for dropdown options."""
        if not modal_is_open:
            raise PreventUpdate
        
        try:
            response = make_api_request("GET", "/units/?is_active=true")
            units = response if isinstance(response, list) else []
            
            # Create options list for base_unit and usage_unit (store code, not ID)
            code_options = [{"label": f"{u.get('code', '')} - {u.get('name', '')}", "value": u.get("code", "")} for u in units]
            
            # Create options list for purchase_unit (store ID, not code)
            id_options = [{"label": f"{u.get('code', '')} - {u.get('name', '')}", "value": str(u.get("id", ""))} for u in units]
            
            return code_options, id_options, code_options
        except Exception as e:
            print(f"Error loading units: {e}")
            return [], [], []
    
    # Toggle edit/delete buttons based on selection
    @app.callback(
        [Output("edit-product-btn", "disabled"),
         Output("delete-product-btn", "disabled")],
        [Input("products-table", "selected_rows")]
    )
    def toggle_action_buttons(selected_rows):
        disabled = not selected_rows or len(selected_rows) == 0
        return disabled, disabled
    
    # Open modal for add/edit and populate form
    @app.callback(
        [Output("product-form-modal", "is_open", allow_duplicate=True),
         Output("product-modal-title", "children", allow_duplicate=True),
         Output("product-sku", "value", allow_duplicate=True),
         Output("product-name", "value", allow_duplicate=True),
         Output("product-description", "value", allow_duplicate=True),
         Output("product-ean13", "value", allow_duplicate=True),
         Output("product-supplier-id", "value", allow_duplicate=True),
         Output("product-raw-material-group-id", "value", allow_duplicate=True),
         Output("product-base-unit", "value", allow_duplicate=True),
         Output("product-is-active", "value", allow_duplicate=True),
         Output("product-type", "value", allow_duplicate=True),
         Output("product-size", "value", allow_duplicate=True),
         Output("product-weight", "value", allow_duplicate=True),
         Output("product-pack", "value", allow_duplicate=True),
         Output("product-pkge", "value", allow_duplicate=True),
         Output("product-density", "value", allow_duplicate=True),
         Output("product-abv", "value", allow_duplicate=True),
         Output("product-vol-solid", "value", allow_duplicate=True),
         Output("product-solid-sg", "value", allow_duplicate=True),
         Output("product-wt-solid", "value", allow_duplicate=True),
         Output("product-form", "value", allow_duplicate=True),
         Output("product-dgflag", "value", allow_duplicate=True),
         Output("product-label", "value", allow_duplicate=True),
         Output("product-manu", "value", allow_duplicate=True),
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
         Output("product-form-hidden", "children", allow_duplicate=True)],
        [Input("add-product-btn", "n_clicks"),
         Input("edit-product-btn", "n_clicks")],
        [State("products-table", "selected_rows"),
         State("products-table", "data")],
        prevent_initial_call=True
    )
    def open_product_modal(add_clicks, edit_clicks, selected_rows, data):
        """Open modal for add or edit and populate form data."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "add-product-btn":
            # Add mode - clear form
            empty_values = [None] * 43  # 43 outputs (first 2 are modal state)
            return tuple([True, "Add Product"] + empty_values)
        
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
                is_active_str = "true" if is_active.lower() in ("true", "1", "yes", "y") else "false"
            else:
                is_active_str = "true" if bool(is_active) else "false"
            
            # Handle purchase_unit_id - ensure it's a string or None (for dropdown)
            purchase_unit_id = product.get("purchase_unit_id")
            if purchase_unit_id is None or purchase_unit_id == "":
                purchase_unit_id = None
            else:
                purchase_unit_id = str(purchase_unit_id)
            
            return (
                True,  # is_open
                "Edit Product",  # title
                product.get("sku") or "",
                product.get("name") or "",
                product.get("description") or "",
                product.get("ean13") or "",
                str(product.get("supplier_id", "")) if product.get("supplier_id") else "",
                str(product.get("raw_material_group_id", "")) if product.get("raw_material_group_id") else "",
                product.get("base_unit") or "",
                is_active_str,  # Fixed: ensure "true" or "false"
                product.get("product_type") or "RAW",
                product.get("size") or "",
                safe_float(product.get("weight")),
                safe_int(product.get("pack")),
                safe_int(product.get("pkge")),
                safe_float(product.get("density_kg_per_l")),
                safe_float(product.get("abv_percent")),
                safe_float(product.get("vol_solid")),
                safe_float(product.get("solid_sg")),
                safe_float(product.get("wt_solid")),
                product.get("form") or "",
                product.get("dgflag") or "",
                safe_int(product.get("label")),
                safe_int(product.get("manu")),
                product.get("taxinc") or "",
                product.get("salestaxcde") or "",
                safe_float(product.get("purcost")),
                safe_float(product.get("purtax")),
                safe_float(product.get("wholesalecost")),
                safe_float(product.get("excise_amount")),
                # Pricing fields - try to convert to float if numeric, otherwise None
                safe_float(product.get("wholesalecde")),
                safe_float(product.get("retailcde")),
                safe_float(product.get("countercde")),
                safe_float(product.get("tradecde")),
                safe_float(product.get("contractcde")),
                safe_float(product.get("industrialcde")),
                safe_float(product.get("distributorcde")),
                safe_float(product.get("disccdeone")),
                safe_float(product.get("disccdetwo")),
                purchase_unit_id,  # Fixed: ensure proper type
                safe_float(product.get("purchase_volume")),
                product.get("usage_unit") or "",
                safe_float(product.get("usage_cost")),
                safe_float(product.get("restock_level")),
                str(product.get("formula_id", "")) if product.get("formula_id") else "",
                safe_int(product.get("formula_revision")),
                str(product.get("id", "")) if product.get("id") else ""  # Hidden field - product ID, ensure string
            )
        
        raise PreventUpdate
    
    # Close modal on cancel or save
    @app.callback(
        Output("product-form-modal", "is_open", allow_duplicate=True),
        [Input("product-cancel-btn", "n_clicks"),
         Input("product-save-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def close_modal(cancel_clicks, save_clicks):
        """Close modal when cancel or save is clicked."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        return False
    
    # Save product (create or update)
    @app.callback(
        [Output("toast", "is_open"),
         Output("toast", "header"),
         Output("toast", "children"),
         Output("products-table", "data", allow_duplicate=True)],
        [Input("product-save-btn", "n_clicks")],
        [State("product-sku", "value"),
         State("product-name", "value"),
         State("product-description", "value"),
         State("product-ean13", "value"),
         State("product-supplier-id", "value"),
         State("product-raw-material-group-id", "value"),
         State("product-base-unit", "value"),
         State("product-is-active", "value"),
         State("product-type", "value"),
         State("product-size", "value"),
         State("product-weight", "value"),
         State("product-pack", "value"),
         State("product-pkge", "value"),
         State("product-density", "value"),
         State("product-abv", "value"),
         State("product-vol-solid", "value"),
         State("product-solid-sg", "value"),
         State("product-wt-solid", "value"),
         State("product-form", "value"),
         State("product-dgflag", "value"),
         State("product-label", "value"),
         State("product-manu", "value"),
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
         State("product-form-hidden", "children")],
        prevent_initial_call=True
    )
    def save_product(n_clicks, *args):
        """Save product - create or update based on hidden state."""
        if not n_clicks:
            raise PreventUpdate
        
        # Extract all form values
        (sku, name, description, ean13, supplier_id, raw_material_group_id, base_unit, is_active, product_type,
         size, weight, pack, pkge, density, abv, vol_solid, solid_sg, wt_solid, form, dgflag, label, manu,
         taxinc, salestaxcde, purcost, purtax, wholesalecost, excise_amount,
         wholesalecde, retailcde, countercde, tradecde, contractcde, industrialcde, distributorcde,
         disccdeone, disccdetwo, purchase_unit_id, purchase_volume,
         usage_unit, usage_cost, restock_level, formula_id, formula_revision, product_id) = args
        
        # Validate required fields
        if not sku or not name:
            return True, "Error", "SKU and Name are required", dash.no_update
        
        # Prepare product data
        product_data = {
            "sku": sku,
            "name": name,
            "description": description if description else None,
            "product_type": product_type if product_type else "RAW",
            "ean13": ean13 if ean13 else None,
            "supplier_id": supplier_id if supplier_id else None,
            "raw_material_group_id": raw_material_group_id if raw_material_group_id else None,
            "base_unit": base_unit if base_unit else None,
            "is_active": is_active == "true" if isinstance(is_active, str) else is_active,
            "size": size if size else None,
            "weight": float(weight) if weight else None,
            "pack": int(pack) if pack else None,
            "pkge": int(pkge) if pkge else None,
            "density_kg_per_l": float(density) if density else None,
            "abv_percent": float(abv) if abv else None,
            "vol_solid": float(vol_solid) if vol_solid else None,
            "solid_sg": float(solid_sg) if solid_sg else None,
            "wt_solid": float(wt_solid) if wt_solid else None,
            "form": form if form else None,
            "dgflag": dgflag if dgflag else None,
            "label": int(label) if label else None,
            "manu": int(manu) if manu else None,
            "taxinc": taxinc if taxinc else None,
            "salestaxcde": salestaxcde if salestaxcde else None,
            "purcost": float(purcost) if purcost else None,
            "purtax": float(purtax) if purtax else None,
            "wholesalecost": float(wholesalecost) if wholesalecost else None,
            "excise_amount": float(excise_amount) if excise_amount else None,
            # Pricing fields - store as string codes (legacy format) but UI displays as currency
            # Note: Database may store codes as strings, but UI treats them as currency amounts
            "wholesalecde": str(wholesalecde) if wholesalecde else None,
            "retailcde": str(retailcde) if retailcde else None,
            "countercde": str(countercde) if countercde else None,
            "tradecde": str(tradecde) if tradecde else None,
            "contractcde": str(contractcde) if contractcde else None,
            "industrialcde": str(industrialcde) if industrialcde else None,
            "distributorcde": str(distributorcde) if distributorcde else None,
            "disccdeone": str(disccdeone) if disccdeone else None,
            "disccdetwo": str(disccdetwo) if disccdetwo else None,
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
                response = make_api_request("PUT", f"/products/{product_id}", product_data)
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
                    except:
                        pass
                return True, "Error", error_msg, no_update
            
            # Refresh table by returning current data (will trigger table update)
            return False, "Success", success_msg, no_update
        
        except Exception as e:
            return True, "Error", f"Failed to save product: {str(e)}", no_update
    
    # Update delete modal with product name
    @app.callback(
        [Output("delete-product-name", "children"),
         Output("delete-confirm-modal", "is_open")],
        [Input("delete-product-btn", "n_clicks"),
         Input("delete-confirm-btn", "n_clicks"),
         Input("delete-cancel-btn", "n_clicks")],
        [State("products-table", "selected_rows"),
         State("products-table", "data")],
        prevent_initial_call=True
    )
    def toggle_delete_modal(delete_clicks, confirm_clicks, cancel_clicks, selected_rows, data):
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
        [Output("products-table", "data", allow_duplicate=True),
         Output("toast", "is_open", allow_duplicate=True),
         Output("toast", "header", allow_duplicate=True),
         Output("toast", "children", allow_duplicate=True)],
        [Input("delete-confirm-btn", "n_clicks")],
        [State("products-table", "selected_rows"),
         State("products-table", "data")],
        prevent_initial_call=True
    )
    def delete_product(n_clicks, selected_rows, data):
        if not n_clicks or not selected_rows or not data:
            raise PreventUpdate
        
        product = data[selected_rows[0]]
        product_id = product.get("id")
        sku = product.get("sku")
        
        try:
            response = make_api_request("DELETE", f"/products/{product_id}")
            
            # Remove from table
            new_data = [row for i, row in enumerate(data) if i not in selected_rows]
            
            return new_data, True, "Success", f"Product {sku} deleted successfully"
        
        except Exception as e:
            return no_update, True, "Error", f"Failed to delete product: {str(e)}"
    
    # Note: Table refresh is now handled by the main callback in app.py that responds to filter changes

