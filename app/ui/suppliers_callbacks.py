"""CRUD callbacks for suppliers page."""

import dash
from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate


def register_suppliers_callbacks(app, make_api_request):
    """Register all suppliers CRUD callbacks."""

    # Toggle edit/delete buttons based on selection
    @app.callback(
        [
            Output("suppliers-edit-btn", "disabled"),
            Output("suppliers-delete-btn", "disabled"),
        ],
        [Input("suppliers-table", "selected_rows")],
    )
    def toggle_action_buttons(selected_rows):
        disabled = not selected_rows or len(selected_rows) == 0
        return disabled, disabled

    # Load suppliers data
    @app.callback(
        Output("suppliers-table", "data"),
        [
            Input("suppliers-search-btn", "n_clicks"),
            Input("suppliers-clear-btn", "n_clicks"),
            Input("suppliers-refresh-btn", "n_clicks"),
            Input("main-tabs", "active_tab"),
        ],
        [
            State("suppliers-search-filter", "value"),
            State("suppliers-active-filter", "value"),
        ],
        prevent_initial_call=False,
    )
    def load_suppliers(
        n_clicks_search,
        n_clicks_clear,
        n_clicks_refresh,
        active_tab,
        search_text,
        active_filter,
    ):
        """Load suppliers from API."""
        # Only load when suppliers tab is active
        if active_tab != "suppliers":
            raise PreventUpdate

        try:
            # Build query params
            params = {}

            # Determine what triggered this callback
            ctx = dash.callback_context
            if not ctx.triggered:
                # Initial load - load all data without filters
                params = {}
            else:
                triggered_id = ctx.triggered[0]["prop_id"]

                # If clear button or refresh button was clicked, load all data without filters
                if triggered_id in [
                    "suppliers-clear-btn.n_clicks",
                    "suppliers-refresh-btn.n_clicks",
                    "main-tabs.active_tab",
                ]:
                    params = {}
                else:
                    # Use filters for search
                    if search_text:
                        params["name"] = search_text  # Search by name

                    # Handle active filter
                    if (
                        active_filter
                        and isinstance(active_filter, list)
                        and "active" in active_filter
                    ):
                        params["is_active"] = True

            response = make_api_request("GET", "/suppliers/", data=params)

            # Handle error response
            if "error" in response:
                print(f"Error loading suppliers: {response.get('error')}")
                return []

            # API returns a list directly
            return response if isinstance(response, list) else []

        except Exception as e:
            print(f"Exception loading suppliers: {e}")
            return []

    # Open add/edit modal
    @app.callback(
        [
            Output("suppliers-modal", "is_open", allow_duplicate=True),
            Output("suppliers-modal-title", "children", allow_duplicate=True),
            Output("suppliers-form-id-hidden", "children", allow_duplicate=True),
            Output("suppliers-form-name", "value", allow_duplicate=True),
            Output("suppliers-form-contact", "value", allow_duplicate=True),
            Output("suppliers-form-email", "value", allow_duplicate=True),
            Output("suppliers-form-phone", "value", allow_duplicate=True),
            Output("suppliers-form-address", "value", allow_duplicate=True),
            Output("suppliers-form-xero-id", "value", allow_duplicate=True),
            Output("suppliers-form-active", "value", allow_duplicate=True),
        ],
        [
            Input("suppliers-add-btn", "n_clicks"),
            Input("suppliers-edit-btn", "n_clicks"),
        ],
        [State("suppliers-table", "selected_rows"), State("suppliers-table", "data")],
        prevent_initial_call=True,
    )
    def open_suppliers_modal(add_clicks, edit_clicks, selected_rows, data):
        """Open modal for add or edit."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "suppliers-add-btn":
            # Add mode - clear form
            return [
                True,
                "Add Supplier",
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                True,
            ]

        elif button_id == "suppliers-edit-btn":
            if not selected_rows or not data:
                return [False, "", None, None, None, None, None, None, None, None]

            supplier = data[selected_rows[0]]

            return [
                True,  # is_open
                "Edit Supplier",  # title
                supplier.get("id"),  # hidden ID
                supplier.get("name", ""),
                supplier.get("contact_person", ""),
                supplier.get("email", ""),
                supplier.get("phone", ""),
                supplier.get("address", ""),
                supplier.get("xero_id", ""),
                supplier.get("is_active", True),
            ]

        raise PreventUpdate

    # Close modal
    @app.callback(
        Output("suppliers-modal", "is_open", allow_duplicate=True),
        [
            Input("suppliers-modal-cancel", "n_clicks"),
            Input("suppliers-modal-save", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def close_suppliers_modal(cancel_clicks, save_clicks):
        """Close modal when cancel or save is clicked."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        return False

    # Save supplier
    @app.callback(
        [
            Output("suppliers-table", "data", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
        ],
        [Input("suppliers-modal-save", "n_clicks")],
        [
            State("suppliers-form-name", "value"),
            State("suppliers-form-contact", "value"),
            State("suppliers-form-email", "value"),
            State("suppliers-form-phone", "value"),
            State("suppliers-form-address", "value"),
            State("suppliers-form-xero-id", "value"),
            State("suppliers-form-active", "value"),
            State("suppliers-modal-title", "children"),
            State("suppliers-form-id-hidden", "children"),
        ],
        prevent_initial_call=True,
    )
    def save_supplier(
        n_clicks,
        code,
        name,
        contact,
        email,
        phone,
        address,
        xero_id,
        is_active,
        title,
        supplier_id,
    ):
        """Save or update supplier."""
        if not n_clicks:
            raise PreventUpdate

        # Validate required fields
        if not name:
            return no_update, True, "Error", "Name is required"

        try:
            # Determine if this is edit mode
            is_edit = title == "Edit Supplier" and supplier_id is not None

            if is_edit:
                # Update - don't include code, API doesn't accept it for updates
                payload = {
                    "name": name,
                    "contact_person": contact or None,
                    "email": email or None,
                    "phone": phone or None,
                    "address": address or None,
                    "xero_id": xero_id or None,
                    "is_active": is_active if is_active is not None else True,
                }
                response = make_api_request("PUT", f"/suppliers/{supplier_id}", payload)
            else:
                # Create new - code is auto-generated as UUID
                payload = {
                    "name": name,
                    "contact_person": contact or None,
                    "email": email or None,
                    "phone": phone or None,
                    "address": address or None,
                    "xero_id": xero_id or None,
                    "is_active": is_active if is_active is not None else True,
                }
                response = make_api_request("POST", "/suppliers/", payload)

            # Check for error response
            if "error" in response:
                return no_update, True, "Error", response.get("error")

            # Reload data
            reload_response = make_api_request("GET", "/suppliers/")
            if "error" in reload_response:
                return (
                    no_update,
                    True,
                    "Error",
                    f"Error reloading: {reload_response.get('error')}",
                )

            # API returns list directly
            new_data = reload_response if isinstance(reload_response, list) else []

            success_msg = (
                f"Supplier {name} {'updated' if is_edit else 'created'} successfully"
            )
            return new_data, True, "Success", success_msg

        except Exception as e:
            return no_update, True, "Error", f"Exception saving supplier: {str(e)}"

    # Delete supplier confirmation
    @app.callback(
        [
            Output("suppliers-delete-name", "children"),
            Output("suppliers-delete-modal", "is_open"),
        ],
        [
            Input("suppliers-delete-btn", "n_clicks"),
            Input("suppliers-delete-confirm", "n_clicks"),
            Input("suppliers-delete-cancel", "n_clicks"),
        ],
        [State("suppliers-table", "selected_rows"), State("suppliers-table", "data")],
        prevent_initial_call=True,
    )
    def toggle_delete_supplier_modal(
        delete_clicks, confirm_clicks, cancel_clicks, selected_rows, data
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return "", False

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "suppliers-delete-btn" and selected_rows and data:
            supplier = data[selected_rows[0]]
            supplier_name = supplier.get("name", "Unknown")
            return supplier_name, True
        elif button_id == "suppliers-delete-cancel":
            return "", False
        elif button_id == "suppliers-delete-confirm":
            return "", False

        return "", False

    # Actual delete
    @app.callback(
        [
            Output("suppliers-table", "data", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
        ],
        [Input("suppliers-delete-confirm", "n_clicks")],
        [State("suppliers-table", "selected_rows"), State("suppliers-table", "data")],
        prevent_initial_call=True,
    )
    def delete_supplier(n_clicks, selected_rows, data):
        if not n_clicks or not selected_rows or not data:
            raise PreventUpdate

        supplier = data[selected_rows[0]]
        supplier_id = supplier.get("id")
        supplier_name = supplier.get("name")

        try:
            make_api_request("DELETE", f"/suppliers/{supplier_id}")

            # Reload data from API
            reload_response = make_api_request("GET", "/suppliers/")
            if "error" in reload_response:
                new_data = [row for i, row in enumerate(data) if i not in selected_rows]
            else:
                new_data = reload_response if isinstance(reload_response, list) else []

            return (
                new_data,
                True,
                "Success",
                f"Supplier {supplier_name} deleted successfully",
            )

        except Exception as e:
            return no_update, True, "Error", f"Failed to delete supplier: {str(e)}"
