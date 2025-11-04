"""CRUD callbacks for units page."""

import dash
from dash import Input, Output, State
from dash.exceptions import PreventUpdate


def register_units_callbacks(app, make_api_request):
    """Register all units CRUD callbacks."""

    # Toggle edit/delete buttons based on selection
    @app.callback(
        [Output("edit-unit-btn", "disabled"), Output("delete-unit-btn", "disabled")],
        [Input("units-table", "selected_rows")],
    )
    def toggle_action_buttons(selected_rows):
        disabled = not selected_rows or len(selected_rows) == 0
        return disabled, disabled

    # Load units table
    @app.callback(
        Output("units-table", "data"),
        [
            Input("main-tabs", "active_tab"),
            Input("settings-tabs", "active_tab"),
            Input("units-refresh", "n_clicks"),
        ],
    )
    def load_units_table(main_tab, settings_tab, refresh_clicks):
        """Load units table when settings tab is activated and units sub-tab is active."""
        if main_tab != "settings" or settings_tab != "units":
            return []

        try:
            response = make_api_request("GET", "/units/")
            if "error" in response:
                return []

            units = response if isinstance(response, list) else []

            # Format data for table
            for unit in units:
                if "is_active" in unit:
                    unit["is_active"] = "Yes" if unit["is_active"] else "No"

            return units
        except Exception as e:
            print(f"Error loading units: {e}")
            return []

    # Open modal for add/edit and populate form
    @app.callback(
        [
            Output("unit-form-modal", "is_open", allow_duplicate=True),
            Output("unit-modal-title", "children", allow_duplicate=True),
            Output("unit-code", "value", allow_duplicate=True),
            Output("unit-name", "value", allow_duplicate=True),
            Output("unit-symbol", "value", allow_duplicate=True),
            Output("unit-type", "value", allow_duplicate=True),
            Output("unit-description", "value", allow_duplicate=True),
            Output("unit-conversion-formula", "value", allow_duplicate=True),
            Output("unit-is-active", "value", allow_duplicate=True),
            Output("unit-form-hidden", "children", allow_duplicate=True),
        ],
        [Input("add-unit-btn", "n_clicks"), Input("edit-unit-btn", "n_clicks")],
        [State("units-table", "selected_rows"), State("units-table", "data")],
        prevent_initial_call=True,
    )
    def open_unit_modal(add_clicks, edit_clicks, selected_rows, data):
        """Open modal for add or edit and populate form data."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "add-unit-btn":
            # Add mode - clear form
            return [True, "Add Unit", "", "", "", None, "", "", True, ""]

        elif button_id == "edit-unit-btn":
            if not selected_rows or not data:
                raise PreventUpdate

            unit = data[selected_rows[0]]

            return (
                True,  # is_open
                "Edit Unit",  # title
                unit.get("code", ""),
                unit.get("name", ""),
                unit.get("symbol", ""),
                unit.get("unit_type", ""),
                unit.get("description", ""),
                unit.get("conversion_formula", ""),
                (
                    unit.get("is_active") == "Yes"
                    if isinstance(unit.get("is_active"), str)
                    else unit.get("is_active", True)
                ),
                unit.get("id"),  # Hidden field - unit ID
            )

        raise PreventUpdate

    # Save unit (create or update)
    @app.callback(
        [
            Output("unit-form-modal", "is_open", allow_duplicate=True),
            Output("unit-modal-title", "children", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
            Output("units-table", "data", allow_duplicate=True),
        ],
        [Input("save-unit-btn", "n_clicks")],
        [
            State("unit-code", "value"),
            State("unit-name", "value"),
            State("unit-symbol", "value"),
            State("unit-type", "value"),
            State("unit-description", "value"),
            State("unit-conversion-formula", "value"),
            State("unit-is-active", "value"),
            State("unit-form-hidden", "children"),
        ],
        prevent_initial_call=True,
    )
    def save_unit(
        n_clicks,
        code,
        name,
        symbol,
        unit_type,
        description,
        conversion_formula,
        is_active,
        unit_id,
    ):
        """Save unit - create or update based on hidden state."""
        if not n_clicks:
            raise PreventUpdate

        # Validate required fields
        if not code or not name:
            return [
                True,
                "Error",
                True,
                "Error",
                "Code and Name are required",
                dash.no_update,
            ]

        # Prepare unit data
        unit_data = {
            "code": code.strip().upper(),
            "name": name.strip(),
            "symbol": symbol.strip() if symbol else None,
            "unit_type": unit_type if unit_type else None,
            "description": description.strip() if description else None,
            "conversion_formula": (
                conversion_formula.strip() if conversion_formula else None
            ),
            "is_active": is_active if is_active is not None else True,
        }

        try:
            if unit_id:  # Update existing
                response = make_api_request("PUT", f"/units/{unit_id}", unit_data)
                if "error" in response:
                    return [
                        True,
                        "Error",
                        True,
                        "Error",
                        f"Failed to update unit: {response['error']}",
                        dash.no_update,
                    ]
                message = f"Unit '{code}' updated successfully"
            else:  # Create new
                response = make_api_request("POST", "/units/", unit_data)
                if "error" in response:
                    return [
                        True,
                        "Error",
                        True,
                        "Error",
                        f"Failed to create unit: {response['error']}",
                        dash.no_update,
                    ]
                message = f"Unit '{code}' created successfully"

            # Reload table
            units_response = make_api_request("GET", "/units/")
            units = units_response if isinstance(units_response, list) else []

            # Format data for table
            for unit in units:
                if "is_active" in unit:
                    unit["is_active"] = "Yes" if unit["is_active"] else "No"

            return [False, "Add Unit", True, "Success", message, units]

        except Exception as e:
            return [
                True,
                "Error",
                True,
                "Error",
                f"Failed to save unit: {str(e)}",
                dash.no_update,
            ]

    # Cancel button
    @app.callback(
        Output("unit-form-modal", "is_open", allow_duplicate=True),
        [Input("cancel-unit-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def cancel_unit_form(n_clicks):
        """Close modal on cancel."""
        if n_clicks:
            return False
        raise PreventUpdate

    # Delete unit
    @app.callback(
        [
            Output("units-table", "data", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
        ],
        [Input("delete-unit-btn", "n_clicks")],
        [State("units-table", "selected_rows"), State("units-table", "data")],
        prevent_initial_call=True,
    )
    def delete_unit(n_clicks, selected_rows, data):
        """Delete selected unit."""
        if not n_clicks or not selected_rows or not data:
            raise PreventUpdate

        unit = data[selected_rows[0]]
        unit_id = unit.get("id")
        unit_code = unit.get("code", "Unknown")

        if not unit_id:
            return dash.no_update, True, "Error", "Unit ID not found"

        try:
            response = make_api_request("DELETE", f"/units/{unit_id}")
            if "error" in response:
                return (
                    dash.no_update,
                    True,
                    "Error",
                    f"Failed to delete unit: {response['error']}",
                )

            # Reload table
            units_response = make_api_request("GET", "/units/")
            units = units_response if isinstance(units_response, list) else []

            # Format data for table
            for unit in units:
                if "is_active" in unit:
                    unit["is_active"] = "Yes" if unit["is_active"] else "No"

            return units, True, "Success", f"Unit '{unit_code}' deleted successfully"

        except Exception as e:
            return dash.no_update, True, "Error", f"Failed to delete unit: {str(e)}"
