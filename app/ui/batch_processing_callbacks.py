"""Callbacks for batch processing page."""

import dash
from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate
import requests
from decimal import Decimal


def register_batch_processing_callbacks(app, api_base_url: str = "http://127.0.0.1:8000/api/v1"):
    """Register callbacks for batch processing page."""
    
    @app.callback(
        [Output("batch-formula-select", "options")],
        [Input("main-tabs", "active_tab")],
        prevent_initial_call=False
    )
    def load_formulas_on_tab(active_tab):
        """Load formulas dropdown when batch-processing tab is active."""
        if active_tab != "batch-processing":
            return [no_update]
        
        try:
            url = f"{api_base_url}/formulas/"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                formulas = response.json()
                # Get unique formula codes with names
                formula_codes = {}
                for formula in formulas:
                    code = formula.get("formula_code", "")
                    name = formula.get("formula_name", "")
                    if code and code not in formula_codes:
                        formula_codes[code] = {
                            "code": code,
                            "name": name
                        }
                
                # Sort by code and create options with code and name
                options = [
                    {"label": f"{info['code']} - {info['name']}", "value": info['code']}
                    for code, info in sorted(formula_codes.items())
                ]
                return [options]
            else:
                print(f"Error loading formulas: {response.status_code}")
                return [[]]
        except Exception as e:
            print(f"Error in load_formulas_on_tab: {e}")
            return [[]]
    
    @app.callback(
        [Output("batch-formula-revision", "options"),
         Output("batch-formula-revision", "value")],
        [Input("batch-formula-select", "value")],
        prevent_initial_call=True
    )
    def load_formula_versions(formula_code):
        """Load formula versions for selected formula."""
        if not formula_code:
            return [], None
        
        try:
            url = f"{api_base_url}/formulas/code/{formula_code}/versions"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                versions = response.json()
                # Sort by version descending to show newest first
                versions_sorted = sorted(versions, key=lambda v: v.get("version", 0), reverse=True)
                
                options = [
                    {"label": f"Rev. {v.get('version', 1)}", "value": str(v.get('id', ''))}
                    for v in versions_sorted
                ]
                
                # Default to most recent version
                default_value = str(versions_sorted[0].get('id', '')) if versions_sorted else None
                
                return options, default_value
            else:
                print(f"Error loading formula versions: {response.status_code}")
                return [], None
        except Exception as e:
            print(f"Error in load_formula_versions: {e}")
            return [], None
    
    @app.callback(
        [Output("batch-formula-lines", "data"),
         Output("batch-multiplier", "value")],
        [Input("batch-formula-revision", "value"),
         Input("batch-target-production", "value"),
         Input("batch-target-production-unit", "value")],
        [State("batch-formula-select", "value")],
        prevent_initial_call=True
    )
    def calculate_batch_multiplier(formula_id, target_production, target_unit, formula_code):
        """Calculate multiplier and populate formula lines."""
        if not formula_id or not target_production or not target_unit:
            return [], 1.0
        
        try:
            # Get formula details
            url = f"{api_base_url}/formulas/{formula_id}"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                print(f"Error loading formula: {response.status_code}")
                return [], 1.0
            
            formula = response.json()
            lines = formula.get("lines", [])
            product_id = formula.get("product_id")
            
            if not lines:
                return [], 1.0
            
            # Get product info to get density for L → kg conversion
            product_density = None
            if target_unit == "L" and product_id:
                try:
                    product_url = f"{api_base_url}/products/{product_id}"
                    product_response = requests.get(product_url, timeout=5)
                    if product_response.status_code == 200:
                        product = product_response.json()
                        product_density = product.get("density_kg_per_l")
                except Exception as e:
                    print(f"Error loading product for density conversion: {e}")
            
            # Convert target production to kg based on unit
            target_kg = Decimal(str(target_production))
            if target_unit == "L":
                if product_density:
                    target_kg = target_kg * Decimal(str(product_density))
                    print(f"Converted {target_production} L to {target_kg} kg using density {product_density}")
                else:
                    print(f"Warning: Cannot convert {target_production} L to kg - product density not available")
            elif target_unit == "ea":
                # ea is typically for count-based items (non-mass based), 
                # but for now we'll use the target as-is if provided
                print(f"Warning: 'ea' unit conversion not fully implemented")
            
            # Calculate base quantity (sum of all line quantities in kg)
            # This represents the total ingredients in the recipe
            base_quantity_kg = sum(float(line.get("quantity_kg", 0)) for line in lines)
            
            if base_quantity_kg == 0:
                return [], 1.0
            
            # Calculate multiplier
            multiplier = float(target_kg / Decimal(str(base_quantity_kg)))
            
            # Populate lines with scaled quantities and fetch SOH
            line_data = []
            product_ids_to_fetch = []
            
            for line in lines:
                product_id = line.get("raw_material_id") or line.get("product_id")
                if product_id:
                    product_ids_to_fetch.append(product_id)
            
            # Fetch SOH for all products in parallel
            soh_data = {}
            if product_ids_to_fetch:
                try:
                    soh_url = f"{api_base_url}/inventory/products/soh"
                    soh_params = {"product_ids": ",".join(product_ids_to_fetch)}
                    soh_response = requests.get(soh_url, params=soh_params, timeout=5)
                    
                    if soh_response.status_code == 200:
                        soh_results = soh_response.json().get("results", [])
                        for result in soh_results:
                            product_id = result.get("product_id")
                            soh_kg = result.get("stock_on_hand_kg", 0)
                            soh_data[product_id] = round(float(soh_kg), 3) if soh_kg else 0.0
                except Exception as e:
                    print(f"Error fetching SOH data: {e}")
            
            for line in lines:
                scaled_qty = float(line.get("quantity_kg", 0)) * multiplier
                product_id = line.get("raw_material_id") or line.get("product_id")
                
                # Get SOH for this product with fallback
                soh = soh_data.get(product_id, 0.0)
                if soh <= 0:
                    soh_display = f"{soh:.3f} (LOW)"
                else:
                    soh_display = f"{soh:.3f}"
                
                line_data.append({
                    "sequence": line.get("sequence", 0),
                    "ingredient_name": line.get("ingredient_name", ""),
                    "quantity_kg": round(scaled_qty, 3),
                    "available_soh": soh_display
                })
            
            return line_data, round(multiplier, 3)
            
        except Exception as e:
            print(f"Error in calculate_batch_multiplier: {e}")
            return [], 1.0
    
    @app.callback(
        Output("toast", "is_open", allow_duplicate=True),
        Output("toast", "children", allow_duplicate=True),
        Output("toast", "header", allow_duplicate=True),
        Input("batch-create-btn", "n_clicks"),
        [State("batch-formula-select", "value"),
         State("batch-formula-revision", "value"),
         State("batch-target-production", "value"),
         State("batch-target-production-unit", "value"),
         State("batch-operator", "value"),
         State("batch-notes-plan", "value"),
         State("batch-date-ordered", "date"),
         State("batch-due-date", "date")],
        prevent_initial_call=True
    )
    def create_batch(n_clicks, formula_code, formula_id, target_production, target_unit, operator, notes, date_ordered, due_date):
        """Create a new batch with work order."""
        if not n_clicks:
            return False, "", ""
        
        if not formula_id or not target_production or not target_unit:
            return True, "Please fill in recipe, revision, and target production", "Validation Error"
        
        try:
            # Get formula to get product_id
            formula_url = f"{api_base_url}/formulas/{formula_id}"
            formula_response = requests.get(formula_url, timeout=5)
            
            if formula_response.status_code != 200:
                return True, f"Error loading formula: {formula_response.status_code}", "Error"
            
            formula = formula_response.json()
            product_id = formula.get("product_id")
            
            # Convert target production to kg
            target_kg = Decimal(str(target_production))
            if target_unit == "L":
                # Get product density
                product_url = f"{api_base_url}/products/{product_id}"
                product_response = requests.get(product_url, timeout=5)
                if product_response.status_code == 200:
                    product = product_response.json()
                    density = product.get("density_kg_per_l")
                    if density:
                        target_kg = target_kg * Decimal(str(density))
            
            # First create work order
            wo_url = f"{api_base_url}/work-orders/"
            wo_data = {
                "product_id": product_id,
                "formula_id": formula_id,
                "quantity_kg": float(target_kg),
                "notes": notes if notes else None
            }
            
            wo_response = requests.post(wo_url, json=wo_data, timeout=5)
            
            if wo_response.status_code != 201:
                return True, f"Error creating work order: {wo_response.text}", "Error"
            
            wo_result = wo_response.json()
            wo_id = wo_result.get("id")
            
            # Generate batch code
            from datetime import datetime
            now = datetime.utcnow()
            batch_code = f"{now.strftime('%y')}{str(wo_result.get('code', 'WO')[-4:])}"
            
            # Create batch
            batch_url = f"{api_base_url}/batches/"
            batch_data = {
                "work_order_id": wo_id,
                "batch_code": batch_code,
                "quantity_kg": float(target_kg),
                "notes": f"Created by {operator if operator else 'system'}"
            }
            
            batch_response = requests.post(batch_url, json=batch_data, timeout=5)
            
            if batch_response.status_code != 201:
                return True, f"Error creating batch: {batch_response.text}", "Error"
            
            batch_result = batch_response.json()
            
            return True, f"Batch {batch_code} created successfully!", "Success"
            
        except Exception as e:
            print(f"Error creating batch: {e}")
            return True, f"Error creating batch: {str(e)}", "Error"
    
    @app.callback(
        [Output("batch-plan-content", "style"),
         Output("batch-execute-content", "style"),
         Output("batch-qc-content", "style"),
         Output("batch-history-content", "style")],
        [Input("batch-process-tabs", "active_tab")]
    )
    def switch_batch_tabs(active_tab):
        """Switch between batch process tabs."""
        # Default to hidden
        plan_style = {"display": "none"}
        execute_style = {"display": "none"}
        qc_style = {"display": "none"}
        history_style = {"display": "none"}
        
        # Show the active tab
        if active_tab == "plan":
            plan_style = {}
        elif active_tab == "execute":
            execute_style = {}
        elif active_tab == "qc":
            qc_style = {}
        elif active_tab == "history":
            history_style = {}
        
        return plan_style, execute_style, qc_style, history_style
    
    @app.callback(
        Output("batch-history-table", "data"),
        [Input("batch-history-refresh", "n_clicks"),
         Input("main-tabs", "active_tab")],
        [State("batch-history-year", "value"),
         State("batch-history-status", "value")],
        prevent_initial_call=False
    )
    def load_batch_history(n_clicks, active_tab, year, status):
        """Load batch history table."""
        if active_tab != "batch-processing":
            return []
        
        try:
            url = f"{api_base_url}/batches/history/"
            params = {}
            
            if year:
                params["year"] = year
            if status and status != "all":
                params["status"] = status
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                batches = response.json()
                # Format data for table
                formatted_data = []
                for batch in batches:
                    started = batch.get("started_at", "")
                    if started:
                        # Extract date only
                        started = started.split("T")[0]
                    
                    formatted_data.append({
                        "batch_id": batch.get("id", ""),  # Store ID for lookup
                        "batch_code": batch.get("batch_code", ""),
                        "formula_code": "N/A",  # Would need to join work order → formula
                        "quantity_kg": batch.get("quantity_kg", 0),
                        "yield_actual": batch.get("yield_actual", 0) if batch.get("yield_actual") else None,
                        "variance_percent": batch.get("variance_percent", 0) if batch.get("variance_percent") else None,
                        "status": batch.get("status", ""),
                        "started_at": started
                    })
                
                return formatted_data
            else:
                print(f"Error loading batch history: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error in load_batch_history: {e}")
            return []
    
    @app.callback(
        [Output("toast", "is_open", allow_duplicate=True),
         Output("toast", "children", allow_duplicate=True),
         Output("toast", "header", allow_duplicate=True)],
        Input("batch-record-actual-btn", "n_clicks"),
        [State("batch-history-table", "selected_rows"),
         State("batch-history-table", "data"),
         State("batch-actual-kg", "value"),
         State("batch-actual-litres", "value"),
         State("batch-notes-execute", "value")],
        prevent_initial_call=True
    )
    def record_batch_actuals(n_clicks, selected_rows, batch_data, actual_kg, actual_litres, notes):
        """Record actual production data for a batch."""
        if not n_clicks or not selected_rows or not batch_data:
            return False, "", ""
        
        try:
            # Get selected batch
            batch_idx = selected_rows[0]
            batch_row = batch_data[batch_idx]
            batch_code = batch_row.get("batch_code")
            
            if not batch_code:
                return True, "No batch selected", "Error"
            
            # Get batch ID from table data
            batch_id = batch_row.get("batch_id")
            
            if not batch_id:
                return True, "Batch ID not found", "Error"
            
            # Calculate variance if target available
            variance = None
            if actual_kg and batch_row.get("quantity_kg"):
                target_kg = float(batch_row.get("quantity_kg"))
                variance = ((actual_kg - target_kg) / target_kg) * 100
            
            # Prepare actual data
            actual_data = {}
            if actual_kg:
                actual_data["yield_kg"] = actual_kg
            if actual_litres:
                actual_data["yield_litres"] = actual_litres
            if variance is not None:
                actual_data["variance"] = variance
            if notes:
                actual_data["notes"] = notes
            
            # Update batch
            update_url = f"{api_base_url}/batches/{batch_id}/record-actual"
            update_response = requests.put(update_url, json=actual_data, timeout=5)
            
            if update_response.status_code != 200:
                return True, f"Error recording actuals: {update_response.text}", "Error"
            
            return True, f"Actuals recorded for batch {batch_code}", "Success"
            
        except Exception as e:
            print(f"Error recording actuals: {e}")
            return True, f"Error: {str(e)}", "Error"
    
    @app.callback(
        [Output("toast", "is_open", allow_duplicate=True),
         Output("toast", "children", allow_duplicate=True),
         Output("toast", "header", allow_duplicate=True)],
        Input("batch-record-qc-btn", "n_clicks"),
        [State("batch-history-table", "selected_rows"),
         State("batch-history-table", "data"),
         State("batch-qc-sg", "value"),
         State("batch-qc-visc", "value"),
         State("batch-qc-ph", "value"),
         State("batch-qc-filter", "value"),
         State("batch-qc-grind", "value"),
         State("batch-qc-vsol", "value"),
         State("batch-qc-wsol", "value"),
         State("batch-qc-dry-dust", "value"),
         State("batch-qc-dry-tack", "value"),
         State("batch-qc-dry-hard", "value"),
         State("batch-qc-dry-bake", "value")],
        prevent_initial_call=True
    )
    def record_qc_results(n_clicks, selected_rows, batch_data, sg, visc, ph, filter_flag, grind, vsol, wsol, dry_dust, dry_tack, dry_hard, dry_bake):
        """Record QC test results for a batch."""
        if not n_clicks or not selected_rows or not batch_data:
            return False, "", ""
        
        try:
            # Get selected batch
            batch_idx = selected_rows[0]
            batch_row = batch_data[batch_idx]
            batch_code = batch_row.get("batch_code")
            batch_id = batch_row.get("batch_id")
            
            if not batch_id:
                return True, "Batch ID not found", "Error"
            
            # Prepare QC data
            qc_data = {}
            if sg is not None:
                qc_data["sg"] = sg
            if visc is not None:
                qc_data["viscosity"] = visc
            if ph is not None:
                qc_data["ph"] = ph
            if filter_flag:
                qc_data["filter_flag"] = filter_flag
            if grind is not None:
                qc_data["grind"] = grind
            if vsol is not None:
                qc_data["vsol"] = vsol
            if wsol is not None:
                qc_data["wsol"] = wsol
            if dry_dust is not None:
                qc_data["dry_dust"] = dry_dust
            if dry_tack is not None:
                qc_data["dry_tack"] = dry_tack
            if dry_hard is not None:
                qc_data["dry_hard"] = dry_hard
            if dry_bake is not None:
                qc_data["dry_bake"] = dry_bake
            
            # Update batch with QC data
            update_url = f"{api_base_url}/batches/{batch_id}/qc-results"
            update_response = requests.put(update_url, json=qc_data, timeout=5)
            
            if update_response.status_code != 200:
                return True, f"Error recording QC: {update_response.text}", "Error"
            
            return True, f"QC results saved for batch {batch_code}", "Success"
            
        except Exception as e:
            print(f"Error recording QC: {e}")
            return True, f"Error: {str(e)}", "Error"

