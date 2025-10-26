"""CRUD callbacks for formulas page."""

import dash
from dash import Input, Output, State, no_update, html, dash_table
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd


def register_formulas_callbacks(app, make_api_request):
    """Register all formula CRUD callbacks."""
    
    # Update formula master table
    @app.callback(
        [Output("formula-master-table", "data"),
         Output("formula-master-table", "columns")],
        [Input("main-tabs", "active_tab"),
         Input("formula-search-btn", "n_clicks"),
         Input("formula-refresh-btn", "n_clicks")],
        [State("formula-search", "value")],
        prevent_initial_call=False
    )
    def update_formula_table(active_tab, search_clicks, refresh_clicks, search_value):
        """Update formula master table."""
        # Only update when formulas tab is active
        if active_tab != "formulas":
            return no_update, no_update
        
        # Fetch formulas from API
        response = make_api_request("GET", "/formulas/")
        
        if "error" in response:
            print(f"Error loading formulas: {response.get('error')}")
            return [], []
        
        formulas = response if isinstance(response, list) else response.get("formulas", [])
        
        if not formulas:
            print("No formulas returned from API")
            return [], []
        
        print(f"Loaded {len(formulas)} formulas")
        
        # Flatten and format data for display
        formatted_data = []
        for formula in formulas:
            formatted_data.append({
                "formula_code": formula.get("formula_code", ""),
                "formula_name": formula.get("formula_name", ""),
                "version": formula.get("version", 1),
                "product_name": formula.get("product_name", ""),
                "is_active": "✓" if formula.get("is_active", True) else "✗",
                "id": formula.get("id", "")
            })
        
        # Apply search filter
        if search_value:
            search_lower = search_value.lower()
            formatted_data = [
                f for f in formatted_data
                if search_lower in f["formula_code"].lower() or 
                   search_lower in f["formula_name"].lower()
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
        [Output("formula-detail-title", "children"),
         Output("formula-info-code", "children"),
         Output("formula-info-version", "children"),
         Output("formula-info-product", "children"),
         Output("formula-info-status", "children"),
         Output("formula-lines-table", "data"),
         Output("formula-lines-table", "columns"),
         Output("formula-total-lines", "children"),
         Output("formula-total-qty", "children")],
        [Input("formula-master-table", "selected_rows")],
        [State("formula-master-table", "data")]
    )
    def update_formula_detail(selected_rows, data):
        """Update formula detail panel."""
        if not selected_rows or not data:
            return (
                "Select a formula...",
                "-", "-", "-", "-",
                [], [], "0", "0.000 kg"
            )
        
        formula = data[selected_rows[0]]
        formula_id = formula.get("id")
        
        if not formula_id:
            return (
                "Select a formula...",
                "-", "-", "-", "-",
                [], [], "0", "0.000 kg"
            )
        
        # Fetch formula details from API
        response = make_api_request("GET", f"/formulas/{formula_id}")
        
        if "error" in response:
            return (
                f"{formula.get('formula_code', 'Unknown')}",
                formula.get("formula_code", "-"),
                str(formula.get("version", "-")),
                formula.get("product_name", "-"),
                formula.get("is_active", "-"),
                [], [], "0", "0.000 kg"
            )
        
        formula_data = response
        
        # Get formula lines
        lines_data = formula_data.get("lines", [])
        formatted_lines = []
        total_qty = 0.0
        
        for line in lines_data:
            qty = float(line.get("quantity_kg", 0))
            total_qty += qty
            unit = line.get("unit", "kg")
            formatted_lines.append({
                "sequence": line.get("sequence", ""),
                "ingredient_name": line.get("ingredient_name", ""),
                "quantity": f"{qty:.3f}",
                "unit": unit,
                "notes": line.get("notes", "")
            })
        
        # Create columns for lines table
        lines_columns = [
            {"name": "Seq", "id": "sequence"},
            {"name": "Ingredient", "id": "ingredient_name"},
            {"name": "Quantity", "id": "quantity", "type": "numeric", "format": {"specifier": ".3f"}},
            {"name": "Unit", "id": "unit"},
            {"name": "Notes", "id": "notes"},
        ]
        
        return (
            f"{formula_data.get('formula_name', formula.get('formula_code', 'Unknown'))}",
            formula_data.get("formula_code", "-"),
            str(formula_data.get("version", "-")),
            formula_data.get("product_name", "-"),
            "Active" if formula_data.get("is_active", True) else "Inactive",
            formatted_lines,
            lines_columns,
            str(len(formatted_lines)),
            f"{total_qty:.3f} kg"
        )
    
    # Open formula editor modal
    @app.callback(
        [Output("formula-editor-modal", "is_open", allow_duplicate=True),
         Output("formula-editor-title", "children", allow_duplicate=True),
         Output("formula-input-name", "value", allow_duplicate=True),
         Output("formula-input-version", "value", allow_duplicate=True),
         Output("formula-input-product", "options", allow_duplicate=True),
         Output("formula-input-product", "value", allow_duplicate=True),
         Output("formula-input-active", "value", allow_duplicate=True),
         Output("formula-editor-lines", "data", allow_duplicate=True)],
        [Input("formula-add-btn", "n_clicks"),
         Input("formula-edit-btn", "n_clicks")],
        [State("formula-master-table", "selected_rows"),
         State("formula-master-table", "data")],
        prevent_initial_call=True
    )
    def open_formula_editor(add_clicks, edit_clicks, selected_rows, data):
        """Open formula editor modal."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # Get products for dropdown
        products_response = make_api_request("GET", "/products/")
        products = products_response if isinstance(products_response, list) else products_response.get("products", [])
        
        product_options = [
            {"label": f"{p.get('sku', '')} - {p.get('name', '')}", "value": p.get("id", "")}
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
                True,  # is_active
                []  # empty lines
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
                qty_kg = float(line.get('quantity_kg', 0))
                unit = line.get('unit', 'kg')
                
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
                
                lines_data.append({
                    "sequence": str(line.get("sequence", "")),
                    "ingredient_name": line.get("ingredient_name", ""),
                    "raw_material_id": line.get("raw_material_id", ""),
                    "quantity": f"{display_qty:.3f}",
                    "unit": unit,  # Use saved unit
                    "notes": line.get("notes", "")
                })
            
            return (
                True,  # is_open
                "Edit Formula",  # title
                formula_data.get("formula_name", ""),
                formula_data.get("version", 1),
                product_options,
                formula_data.get("product_id", ""),
                formula_data.get("is_active", True),
                lines_data  # lines data
            )
        
        raise PreventUpdate
    
    # Save formula
    @app.callback(
        [Output("formula-editor-modal", "is_open", allow_duplicate=True),
         Output("formula-master-table", "data", allow_duplicate=True),
         Output("formula-master-table", "columns", allow_duplicate=True)],
        [Input("formula-editor-save-btn", "n_clicks")],
        [State("formula-input-name", "value"),
         State("formula-input-version", "value"),
         State("formula-input-product", "value"),
         State("formula-input-active", "value"),
         State("formula-editor-title", "children"),
         State("formula-editor-lines", "data"),
         State("formula-master-table", "selected_rows"),
         State("formula-master-table", "data")],
        prevent_initial_call=True
    )
    def save_formula(n_clicks, name, version, product_id, is_active, title, lines_data, selected_rows, current_data):
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
            payload = {
                "formula_name": name,
                "is_active": is_active
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
                    
                    lines.append({
                        "raw_material_id": raw_material_id,
                        "quantity_kg": quantity_kg,
                        "sequence": int(line.get("sequence", 0)),
                        "notes": line.get("notes", ""),
                        "unit": line.get("unit", "kg")  # Save the display unit
                    })
                
                # Update lines
                if lines:
                    lines_response = make_api_request("PUT", f"/formulas/{formula_id}/lines", lines)
                    if "error" in lines_response:
                        print(f"Error saving formula lines: {lines_response.get('error')}")
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
                    
                    lines.append({
                        "raw_material_id": raw_material_id,
                        "quantity_kg": quantity_kg,
                        "sequence": int(line.get("sequence", 0)),
                        "notes": line.get("notes", ""),
                        "unit": line.get("unit", "kg")  # Save the display unit
                    })
            
            payload = {
                "formula_code": str(next_code),
                "formula_name": name,
                "version": version or 1,
                "product_id": product_id,
                "is_active": is_active,
                "lines": lines
            }
            response = make_api_request("POST", "/formulas/", payload)
        
        if "error" in response:
            print(f"Error saving formula: {response.get('error')}")
            return False, no_update, no_update
        
        print(f"Formula saved successfully")
        
        # Reload formulas to refresh table
        reload_response = make_api_request("GET", "/formulas/")
        if "error" in reload_response:
            print(f"Error reloading formulas: {reload_response.get('error')}")
            return False, [], []
        
        formulas = reload_response if isinstance(reload_response, list) else reload_response.get("formulas", [])
        
        if not formulas:
            print("No formulas in reload")
            return False, [], []
        
        # Format data for display
        formatted_data = []
        for formula in formulas:
            formatted_data.append({
                "formula_code": formula.get("formula_code", ""),
                "formula_name": formula.get("formula_name", ""),
                "version": formula.get("version", 1),
                "product_name": formula.get("product_name", ""),
                "is_active": "✓" if formula.get("is_active", True) else "✗",
                "id": formula.get("id", "")
            })
        
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
        prevent_initial_call=True
    )
    def close_modal(n_clicks):
        """Close formula editor modal."""
        return False
    
    # Clear search
    @app.callback(
        Output("formula-search", "value"),
        [Input("formula-clear-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def clear_search(n_clicks):
        """Clear search input."""
        return ""
    
    # Add line to formula editor
    @app.callback(
        Output("formula-editor-lines", "data", allow_duplicate=True),
        [Input("formula-add-line-btn", "n_clicks")],
        [State("formula-editor-lines", "data")],
        prevent_initial_call=True
    )
    def add_formula_line(n_clicks, current_data):
        """Add a new line to the formula."""
        if not n_clicks:
            raise PreventUpdate
        
        if current_data is None:
            current_data = []
        
        # Find next sequence number
        existing_sequences = [int(line.get("sequence", 0)) for line in current_data if line.get("sequence")]
        next_seq = max(existing_sequences, default=0) + 1 if existing_sequences else 1
        
        # Add new line
        new_line = {
            "sequence": str(next_seq),
            "ingredient_name": "[Click to select ingredient]",  # Placeholder
            "raw_material_id": "",  # To be filled when ingredient is selected
            "quantity": "0.000",
            "unit": "kg",  # Default unit
            "notes": ""
        }
        
        return current_data + [new_line]
    
    # Edit line - open ingredient selection modal for selected line
    @app.callback(
        [Output("ingredient-selection-modal", "is_open", allow_duplicate=True),
         Output("current-line-index-store", "children", allow_duplicate=True)],
        [Input("formula-edit-line-btn", "n_clicks")],
        [State("formula-editor-lines", "selected_rows"),
         State("formula-editor-lines", "data")],
        prevent_initial_call=True
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
        [State("formula-editor-lines", "selected_rows"),
         State("formula-editor-lines", "data")],
        prevent_initial_call=True
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
        [Output("ingredient-selection-modal", "is_open"),
         Output("current-line-index-store", "children")],
        [Input("formula-editor-lines", "active_cell"),
         Input("ingredient-modal-cancel", "n_clicks")],
        [State("formula-editor-lines", "data")],
        prevent_initial_call=True
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
        [Output("ingredient-search-results", "children"),
         Output("ingredient-search-message", "children")],
        [Input("ingredient-search-input", "value")],
        prevent_initial_call=False
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
            code = str(rm.get('code', '')).strip()
            desc1 = str(rm.get('desc1', '')).strip()
            desc2 = str(rm.get('desc2', '')).strip()
            desc = f"{code} - {desc1} {desc2}".strip()
            
            results.append({
                "id": rm.get("id", ""),
                "code": code,
                "description": desc,
            })
        
        return html.Div([
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
                    'textAlign': 'left', 
                    'fontSize': '11px',
                    'padding': '8px'
                },
                style_header={
                    'backgroundColor': 'rgb(220, 220, 220)', 
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
            )
        ]), message
    
    # Handle ingredient selection from results table
    @app.callback(
        [Output("formula-editor-lines", "data", allow_duplicate=True),
         Output("ingredient-selection-modal", "is_open", allow_duplicate=True),
         Output("ingredient-results-table", "selected_rows")],
        [Input("ingredient-results-table", "selected_rows"),
         Input("ingredient-modal-cancel", "n_clicks")],
        [State("ingredient-results-table", "data"),
         State("current-line-index-store", "children"),
         State("formula-editor-lines", "data")],
        prevent_initial_call=True
    )
    def handle_ingredient_selection(selected_rows, cancel_clicks, results_data, line_index, current_lines):
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
