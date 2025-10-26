"""CRUD callbacks for products page."""

import dash
from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc


def register_product_callbacks(app, make_api_request):
    """Register all product CRUD callbacks."""
    
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
         Output("product-base-unit", "value", allow_duplicate=True),
         Output("product-is-active", "value", allow_duplicate=True),
         Output("product-size", "value", allow_duplicate=True),
         Output("product-pack", "value", allow_duplicate=True),
         Output("product-pkge", "value", allow_duplicate=True),
         Output("product-density", "value", allow_duplicate=True),
         Output("product-abv", "value", allow_duplicate=True),
         Output("product-form", "value", allow_duplicate=True),
         Output("product-dgflag", "value", allow_duplicate=True),
         Output("product-label", "value", allow_duplicate=True),
         Output("product-manu", "value", allow_duplicate=True),
         Output("product-taxinc", "value", allow_duplicate=True),
         Output("product-salestaxcde", "value", allow_duplicate=True),
         Output("product-purcost", "value", allow_duplicate=True),
         Output("product-purtax", "value", allow_duplicate=True),
         Output("product-wholesalecost", "value", allow_duplicate=True),
         Output("product-wholesalecde", "value", allow_duplicate=True),
         Output("product-retailcde", "value", allow_duplicate=True),
         Output("product-countercde", "value", allow_duplicate=True),
         Output("product-tradecde", "value", allow_duplicate=True),
         Output("product-contractcde", "value", allow_duplicate=True),
         Output("product-industrialcde", "value", allow_duplicate=True),
         Output("product-distributorcde", "value", allow_duplicate=True),
         Output("product-disccdeone", "value", allow_duplicate=True),
         Output("product-disccdetwo", "value", allow_duplicate=True),
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
            empty_values = [None] * 31  # 31 outputs (first 2 are modal state)
            return [True, "Add Product"] + empty_values
        
        elif button_id == "edit-product-btn":
            if not selected_rows or not data:
                raise PreventUpdate
            
            product = data[selected_rows[0]]
            
            return (
                True,  # is_open
                "Edit Product",  # title
                product.get("sku", ""),
                product.get("name", ""),
                product.get("description", ""),
                product.get("ean13", ""),
                product.get("supplier_id", ""),
                product.get("base_unit", ""),
                str(product.get("is_active", True)).lower(),
                product.get("size", ""),
                product.get("pack", ""),
                product.get("pkge", ""),
                float(product.get("density_kg_per_l", 0)) if product.get("density_kg_per_l") else None,
                float(product.get("abv_percent", 0)) if product.get("abv_percent") else None,
                product.get("form", ""),
                product.get("dgflag", ""),
                product.get("label", ""),
                product.get("manu", ""),
                product.get("taxinc", ""),
                product.get("salestaxcde", ""),
                float(product.get("purcost", 0)) if product.get("purcost") else None,
                float(product.get("purtax", 0)) if product.get("purtax") else None,
                float(product.get("wholesalecost", 0)) if product.get("wholesalecost") else None,
                product.get("wholesalecde", ""),
                product.get("retailcde", ""),
                product.get("countercde", ""),
                product.get("tradecde", ""),
                product.get("contractcde", ""),
                product.get("industrialcde", ""),
                product.get("distributorcde", ""),
                product.get("disccdeone", ""),
                product.get("disccdetwo", ""),
                product.get("id")  # Hidden field - product ID
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
         State("product-base-unit", "value"),
         State("product-is-active", "value"),
         State("product-size", "value"),
         State("product-pack", "value"),
         State("product-pkge", "value"),
         State("product-density", "value"),
         State("product-abv", "value"),
         State("product-form", "value"),
         State("product-dgflag", "value"),
         State("product-label", "value"),
         State("product-manu", "value"),
         State("product-taxinc", "value"),
         State("product-salestaxcde", "value"),
         State("product-purcost", "value"),
         State("product-purtax", "value"),
         State("product-wholesalecost", "value"),
         State("product-wholesalecde", "value"),
         State("product-retailcde", "value"),
         State("product-countercde", "value"),
         State("product-tradecde", "value"),
         State("product-contractcde", "value"),
         State("product-industrialcde", "value"),
         State("product-distributorcde", "value"),
         State("product-disccdeone", "value"),
         State("product-disccdetwo", "value"),
         State("product-form-hidden", "children")],
        prevent_initial_call=True
    )
    def save_product(n_clicks, *args):
        """Save product - create or update based on hidden state."""
        if not n_clicks:
            raise PreventUpdate
        
        # Extract all form values
        (sku, name, description, ean13, supplier_id, base_unit, is_active,
         size, pack, pkge, density, abv, form, dgflag, label, manu,
         taxinc, salestaxcde, purcost, purtax, wholesalecost,
         wholesalecde, retailcde, countercde, tradecde, contractcde, industrialcde, distributorcde,
         disccdeone, disccdetwo, product_id) = args
        
        # Validate required fields
        if not sku or not name:
            return True, "Error", "SKU and Name are required", dash.no_update
        
        # Prepare product data
        product_data = {
            "sku": sku,
            "name": name,
            "description": description if description else None,
            "ean13": ean13 if ean13 else None,
            "supplier_id": supplier_id if supplier_id else None,
            "base_unit": base_unit if base_unit else None,
            "is_active": is_active == "true" if isinstance(is_active, str) else is_active,
            "size": size if size else None,
            "pack": int(pack) if pack else None,
            "pkge": int(pkge) if pkge else None,
            "density_kg_per_l": float(density) if density else None,
            "abv_percent": float(abv) if abv else None,
            "form": form if form else None,
            "dgflag": dgflag if dgflag else None,
            "label": int(label) if label else None,
            "manu": int(manu) if manu else None,
            "taxinc": taxinc if taxinc else None,
            "salestaxcde": salestaxcde if salestaxcde else None,
            "purcost": float(purcost) if purcost else None,
            "purtax": float(purtax) if purtax else None,
            "wholesalecost": float(wholesalecost) if wholesalecost else None,
            "wholesalecde": wholesalecde if wholesalecde else None,
            "retailcde": retailcde if retailcde else None,
            "countercde": countercde if countercde else None,
            "tradecde": tradecde if tradecde else None,
            "contractcde": contractcde if contractcde else None,
            "industrialcde": industrialcde if industrialcde else None,
            "distributorcde": distributorcde if distributorcde else None,
            "disccdeone": disccdeone if disccdeone else None,
            "disccdetwo": disccdetwo if disccdetwo else None,
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
    
    # Refresh table callback
    @app.callback(
        Output("products-table", "data", allow_duplicate=True),
        [Input("products-refresh", "n_clicks")],
        prevent_initial_call=True
    )
    def refresh_table(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        
        response = make_api_request("GET", "/products/")
        
        if "error" in response:
            return []
        
        products = response if isinstance(response, list) else response.get("products", [])
        
        # Flatten nested fields for DataTable display
        for product in products:
            if "variants" in product and isinstance(product["variants"], list):
                variant_names = [v.get("variant_name", v.get("variant_code", "")) for v in product["variants"] if isinstance(v, dict)]
                product["variants"] = ", ".join(variant_names) if variant_names else "None"
            if "created_at" in product:
                product["created_at"] = str(product["created_at"]) if product["created_at"] else ""
            if "updated_at" in product:
                product["updated_at"] = str(product["updated_at"]) if product["updated_at"] else ""
        
        # Filter out non-scalar columns
        import pandas as pd
        df = pd.DataFrame(products)
        scalar_cols = [col for col in df.columns if not df[col].apply(lambda x: isinstance(x, (list, dict))).any()]
        df = df[scalar_cols] if scalar_cols else df
        
        return df.to_dict("records")

