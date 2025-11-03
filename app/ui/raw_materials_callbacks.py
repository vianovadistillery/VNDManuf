"""CRUD callbacks for Raw Materials page."""

import dash
from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate


def register_raw_materials_callbacks(app, make_api_request):
    """Register all raw materials CRUD callbacks."""

    # Load raw materials data
    @app.callback(
        Output("rm-table", "data"),
        [Input("rm-search-btn", "n_clicks"), Input("rm-refresh-btn", "n_clicks")],
        State("rm-search-filter", "value"),
        State("rm-status-filter", "value"),
        prevent_initial_call=False,
    )
    def load_raw_materials(
        n_clicks_search, n_clicks_refresh, search_text, status_filter
    ):
        """Load raw materials from API."""
        try:
            # Build query params
            params = {}

            # If refresh button was clicked, don't use filters
            ctx = dash.callback_context
            if (
                ctx.triggered
                and ctx.triggered[0]["prop_id"] == "rm-refresh-btn.n_clicks"
            ):
                # Refresh button clicked - get all data
                params = {}
            else:
                # Use filters - API expects 'search' and 'status'
                if search_text:
                    params["search"] = search_text
                if status_filter and status_filter != "all":
                    params["status"] = status_filter

            response = make_api_request("GET", "/raw-materials/", data=params)

            # Handle error response
            if "error" in response:
                print(f"Error loading raw materials: {response.get('error')}")
                return []

            # API returns a list directly
            return response if isinstance(response, list) else []

        except Exception as e:
            print(f"Exception loading raw materials: {e}")
            return []

    # Open add/edit modal
    @app.callback(
        [
            Output("rm-modal", "is_open", allow_duplicate=True),
            Output("rm-modal-title", "children", allow_duplicate=True),
            Output("rm-input-desc1", "value", allow_duplicate=True),
            Output("rm-input-desc2", "value", allow_duplicate=True),
            Output("rm-input-search-key", "value", allow_duplicate=True),
            Output("rm-input-search-ext", "value", allow_duplicate=True),
            Output("rm-input-notes", "value", allow_duplicate=True),
            Output("rm-input-xero-account", "value", allow_duplicate=True),
            Output("rm-input-sg", "value", allow_duplicate=True),
            Output("rm-input-purcost", "value", allow_duplicate=True),
            Output("rm-input-purunit", "value", allow_duplicate=True),
            Output("rm-input-usecost", "value", allow_duplicate=True),
            Output("rm-input-useunit", "value", allow_duplicate=True),
            Output("rm-input-dealcost", "value", allow_duplicate=True),
            Output("rm-input-supunit", "value", allow_duplicate=True),
            Output("rm-input-supqty", "value", allow_duplicate=True),
            Output("rm-input-soh", "value", allow_duplicate=True),
            Output("rm-input-osoh", "value", allow_duplicate=True),
            Output("rm-input-sohv", "value", allow_duplicate=True),
            Output("rm-input-restock", "value", allow_duplicate=True),
            Output("rm-input-hazard", "value", allow_duplicate=True),
            Output("rm-input-condition", "value", allow_duplicate=True),
            Output("rm-input-msds", "value", allow_duplicate=True),
            Output("rm-input-active", "value", allow_duplicate=True),
            Output("rm-input-supplier", "value", allow_duplicate=True),
        ],
        [Input("rm-add-btn", "n_clicks"), Input("rm-edit-btn", "n_clicks")],
        [State("rm-table", "selected_rows"), State("rm-table", "data")],
        prevent_initial_call=True,
    )
    def open_rm_modal(add_clicks, edit_clicks, selected_rows, data):
        """Open modal for add or edit."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "rm-add-btn":
            # Add mode - clear form
            return [True, "Add Raw Material"] + [None] * 24

        elif button_id == "rm-edit-btn":
            if not selected_rows or not data:
                return [False, ""] + [None] * 24

            rm = data[selected_rows[0]]

            return [
                True,  # is_open
                "Edit Raw Material",  # title
                rm.get("desc1", ""),
                rm.get("desc2", ""),
                rm.get("search_key", ""),
                rm.get("search_ext", ""),
                rm.get("notes", ""),
                rm.get("xero_account", ""),
                float(rm.get("sg", 0)) if rm.get("sg") else None,
                float(rm.get("purchase_cost", 0)) if rm.get("purchase_cost") else None,
                rm.get("purchase_unit", ""),
                float(rm.get("usage_cost", 0)) if rm.get("usage_cost") else None,
                rm.get("usage_unit", ""),
                float(rm.get("deal_cost", 0)) if rm.get("deal_cost") else None,
                rm.get("sup_unit", ""),
                float(rm.get("sup_qty", 0)) if rm.get("sup_qty") else None,
                float(rm.get("soh", 0)) if rm.get("soh") else None,
                float(rm.get("opening_soh", 0)) if rm.get("opening_soh") else None,
                float(rm.get("soh_value", 0)) if rm.get("soh_value") else None,
                float(rm.get("restock_level", 0)) if rm.get("restock_level") else None,
                rm.get("hazard", ""),
                rm.get("condition", ""),
                rm.get("msds_flag", ""),
                rm.get("active_flag", "A"),
                None,  # supplier_id - TODO: load from API
            ]

        raise PreventUpdate

    # Close modal
    @app.callback(
        Output("rm-modal", "is_open", allow_duplicate=True),
        [Input("rm-modal-cancel", "n_clicks"), Input("rm-modal-save", "n_clicks")],
        prevent_initial_call=True,
    )
    def close_rm_modal(cancel_clicks, save_clicks):
        """Close modal when cancel or save is clicked."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        return False

    # Save raw material
    @app.callback(
        Output("rm-table", "data", allow_duplicate=True),
        [Input("rm-modal-save", "n_clicks")],
        [
            State("rm-input-desc1", "value"),
            State("rm-input-desc2", "value"),
            State("rm-input-search-key", "value"),
            State("rm-input-search-ext", "value"),
            State("rm-input-notes", "value"),
            State("rm-input-xero-account", "value"),
            State("rm-input-sg", "value"),
            State("rm-input-purcost", "value"),
            State("rm-input-purunit", "value"),
            State("rm-input-usecost", "value"),
            State("rm-input-useunit", "value"),
            State("rm-input-dealcost", "value"),
            State("rm-input-supunit", "value"),
            State("rm-input-supqty", "value"),
            State("rm-input-soh", "value"),
            State("rm-input-osoh", "value"),
            State("rm-input-sohv", "value"),
            State("rm-input-restock", "value"),
            State("rm-input-hazard", "value"),
            State("rm-input-condition", "value"),
            State("rm-input-msds", "value"),
            State("rm-input-active", "value"),
            State("rm-input-supplier", "value"),
            State("rm-modal-title", "children"),
            State("rm-table", "selected_rows"),
            State("rm-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_raw_material(
        n_clicks,
        desc1,
        desc2,
        search_key,
        search_ext,
        notes,
        xero_account,
        sg,
        purchase_cost,
        purchase_unit,
        usage_cost,
        usage_unit,
        deal_cost,
        sup_unit,
        sup_qty,
        soh,
        opening_soh,
        soh_value,
        restock_level,
        hazard,
        condition,
        msds_flag,
        active_flag,
        supplier_id,
        title,
        selected_rows,
        current_data,
    ):
        """Save or update raw material."""
        if not n_clicks:
            raise PreventUpdate

        if not desc1:
            print("Validation error: Description 1 is required")
            return no_update

        try:
            # Determine if this is edit mode
            is_edit = (
                title == "Edit Raw Material"
                and selected_rows
                and len(selected_rows) > 0
            )
            rm_id = None

            if is_edit:
                # Get the selected raw material to get its ID
                selected_rm = current_data[selected_rows[0]]
                rm_id = selected_rm.get("id")
                if not rm_id:
                    print("No ID found for selected raw material")
                    return no_update

            # Prepare payload with all fields
            payload = {
                "desc1": desc1,
                "desc2": desc2 or None,
                "search_key": search_key or None,
                "search_ext": search_ext or None,
                "sg": float(sg) if sg else None,
                "purchase_cost": float(purchase_cost) if purchase_cost else None,
                "purchase_unit": purchase_unit or None,
                "usage_cost": float(usage_cost) if usage_cost else None,
                "usage_unit": usage_unit or None,
                "deal_cost": float(deal_cost) if deal_cost else None,
                "sup_unit": sup_unit or None,
                "sup_qty": float(sup_qty) if sup_qty else None,
                "soh": float(soh) if soh else None,
                "opening_soh": float(opening_soh) if opening_soh else None,
                "soh_value": float(soh_value) if soh_value else None,
                "restock_level": float(restock_level) if restock_level else None,
                "hazard": hazard or None,
                "condition": condition or None,
                "msds_flag": msds_flag or None,
                "notes": notes or None,
                "xero_account": xero_account or None,
                "active_flag": active_flag or "A",
            }

            if is_edit:
                # Update - use the UUID from existing record
                response = make_api_request("PUT", f"/raw-materials/{rm_id}", payload)
            else:
                # Create new - need to get next available code
                # Fetch all raw materials to find next code
                all_raw_materials = make_api_request("GET", "/raw-materials/")
                if "error" in all_raw_materials:
                    print("Error fetching existing raw materials")
                    return no_update

                existing_codes = [
                    int(rm.get("code", 0)) for rm in all_raw_materials if rm.get("code")
                ]
                next_code = max(existing_codes, default=0) + 1 if existing_codes else 1

                # Add code to payload
                payload["code"] = next_code
                response = make_api_request("POST", "/raw-materials/", payload)

            # Check for error response
            if "error" in response:
                print(f"Failed to save: {response.get('error')}")
                return no_update

            # Add supplier if provided
            if supplier_id:
                # For new materials, get ID from response
                new_rm_id = response.get("id") if isinstance(response, dict) else rm_id

                if not new_rm_id:
                    # Try to get from the response
                    all_rms = make_api_request("GET", "/raw-materials/")
                    if all_rms and "error" not in all_rms:
                        # Find the newly created one
                        created_rm = all_rms[-1] if all_rms else None
                        new_rm_id = created_rm.get("id") if created_rm else None

                if new_rm_id:
                    # For edit mode, remove old suppliers first
                    if is_edit:
                        # Get existing suppliers
                        existing_suppliers = make_api_request(
                            "GET", f"/raw-materials/{new_rm_id}/suppliers"
                        )
                        if "error" not in existing_suppliers and isinstance(
                            existing_suppliers, list
                        ):
                            for old_supplier in existing_suppliers:
                                old_sup_id = old_supplier.get("id")
                                if old_sup_id and old_sup_id != supplier_id:
                                    # Remove old supplier
                                    make_api_request(
                                        "DELETE",
                                        f"/raw-materials/{new_rm_id}/suppliers/{old_sup_id}",
                                    )

                    # Add new supplier
                    supplier_payload = {"supplier_id": supplier_id}
                    supplier_response = make_api_request(
                        "POST",
                        f"/raw-materials/{new_rm_id}/suppliers",
                        supplier_payload,
                    )
                    if "error" in supplier_response:
                        print(
                            f"Failed to add supplier: {supplier_response.get('error')}"
                        )

            # Return empty list to avoid refetch
            # The page will refresh naturally or user can manually refresh
            return []

        except Exception as e:
            print(f"Exception saving raw material: {str(e)}")
            import traceback

            traceback.print_exc()
            return no_update

    # Load suppliers when modal opens
    @app.callback(
        [
            Output("rm-input-supplier", "options"),
            Output("rm-input-supplier", "value", allow_duplicate=True),
        ],
        [Input("rm-modal", "is_open")],
        [
            State("rm-table", "selected_rows"),
            State("rm-table", "data"),
            State("rm-modal-title", "children"),
        ],
        prevent_initial_call=True,
    )
    def load_suppliers(is_open, selected_rows, data, title):
        """Load suppliers for the dropdown and set current supplier."""
        if not is_open:
            raise PreventUpdate

        try:
            response = make_api_request("GET", "/suppliers/")

            if "error" in response:
                print(f"Error loading suppliers: {response.get('error')}")
                return [], None

            options = [
                {"label": s.get("name", ""), "value": s.get("id")} for s in response
            ]

            # Load current supplier if in edit mode
            supplier_value = None
            if title == "Edit Raw Material" and selected_rows and data:
                rm = data[selected_rows[0]]
                rm_id = rm.get("id")

                if rm_id:
                    suppliers_response = make_api_request(
                        "GET", f"/raw-materials/{rm_id}/suppliers"
                    )
                    if (
                        "error" not in suppliers_response
                        and isinstance(suppliers_response, list)
                        and len(suppliers_response) > 0
                    ):
                        supplier_value = suppliers_response[0].get("id")

            return options, supplier_value

        except Exception as e:
            print(f"Exception loading suppliers: {str(e)}")
            return [], None
