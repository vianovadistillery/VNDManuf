"""CRUD callbacks for purchase formats page."""

import dash
from dash import Input, Output, State
from dash.exceptions import PreventUpdate


def register_purchase_formats_callbacks(app, make_api_request):
    """Register all purchase formats CRUD callbacks."""

    # Toggle edit/delete buttons based on selection
    @app.callback(
        [
            Output("edit-purchase-format-btn", "disabled"),
            Output("delete-purchase-format-btn", "disabled"),
        ],
        [Input("purchase-formats-table", "selected_rows")],
    )
    def toggle_action_buttons(selected_rows):
        disabled = not selected_rows or len(selected_rows) == 0
        return disabled, disabled

    # Load purchase formats table
    @app.callback(
        Output("purchase-formats-table", "data"),
        [
            Input("main-tabs", "active_tab"),
            Input("settings-tabs", "active_tab"),
            Input("purchase-formats-refresh", "n_clicks"),
        ],
    )
    def load_purchase_formats_table(main_tab, settings_tab, refresh_clicks):
        """Load purchase formats table when settings tab is activated and purchase-formats sub-tab is active."""
        if main_tab != "settings" or settings_tab != "purchase-formats":
            return []

        try:
            response = make_api_request("GET", "/purchase-formats/")
            if "error" in response:
                return []

            formats = response if isinstance(response, list) else []

            # Format data for table
            for fmt in formats:
                if "is_active" in fmt:
                    fmt["is_active"] = "Yes" if fmt["is_active"] else "No"

            return formats
        except Exception as e:
            print(f"Error loading purchase formats: {e}")
            return []

    # Open modal for add/edit and populate form
    @app.callback(
        [
            Output("purchase-format-form-modal", "is_open", allow_duplicate=True),
            Output("purchase-format-modal-title", "children", allow_duplicate=True),
            Output("purchase-format-code", "value", allow_duplicate=True),
            Output("purchase-format-name", "value", allow_duplicate=True),
            Output("purchase-format-description", "value", allow_duplicate=True),
            Output("purchase-format-is-active", "value", allow_duplicate=True),
            Output("purchase-format-form-hidden", "children", allow_duplicate=True),
        ],
        [
            Input("add-purchase-format-btn", "n_clicks"),
            Input("edit-purchase-format-btn", "n_clicks"),
        ],
        [
            State("purchase-formats-table", "selected_rows"),
            State("purchase-formats-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def open_purchase_format_modal(add_clicks, edit_clicks, selected_rows, data):
        """Open modal for add or edit and populate form data."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "add-purchase-format-btn":
            # Add mode - clear form
            return [True, "Add Purchase Format", "", "", "", True, ""]

        elif button_id == "edit-purchase-format-btn":
            if not selected_rows or not data:
                raise PreventUpdate

            fmt = data[selected_rows[0]]

            return (
                True,  # is_open
                "Edit Purchase Format",  # title
                fmt.get("code", ""),
                fmt.get("name", ""),
                fmt.get("description", ""),
                (
                    fmt.get("is_active") == "Yes"
                    if isinstance(fmt.get("is_active"), str)
                    else fmt.get("is_active", True)
                ),
                fmt.get("id"),  # Hidden field - format ID
            )

        raise PreventUpdate

    # Save purchase format (create or update)
    @app.callback(
        [
            Output("purchase-format-form-modal", "is_open", allow_duplicate=True),
            Output("purchase-format-modal-title", "children", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
            Output("purchase-formats-table", "data", allow_duplicate=True),
        ],
        [Input("save-purchase-format-btn", "n_clicks")],
        [
            State("purchase-format-code", "value"),
            State("purchase-format-name", "value"),
            State("purchase-format-description", "value"),
            State("purchase-format-is-active", "value"),
            State("purchase-format-form-hidden", "children"),
        ],
        prevent_initial_call=True,
    )
    def save_purchase_format(n_clicks, code, name, description, is_active, format_id):
        """Save purchase format - create or update based on hidden state."""
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

        # Prepare format data
        format_data = {
            "code": code.strip().upper(),
            "name": name.strip(),
            "description": description.strip() if description else None,
            "is_active": is_active if is_active is not None else True,
        }

        try:
            if format_id:  # Update existing
                response = make_api_request(
                    "PUT", f"/purchase-formats/{format_id}", format_data
                )
                if "error" in response:
                    return [
                        True,
                        "Error",
                        True,
                        "Error",
                        f"Failed to update purchase format: {response['error']}",
                        dash.no_update,
                    ]
                message = f"Purchase format '{code}' updated successfully"
            else:  # Create new
                response = make_api_request("POST", "/purchase-formats/", format_data)
                if "error" in response:
                    return [
                        True,
                        "Error",
                        True,
                        "Error",
                        f"Failed to create purchase format: {response['error']}",
                        dash.no_update,
                    ]
                message = f"Purchase format '{code}' created successfully"

            # Reload table
            formats_response = make_api_request("GET", "/purchase-formats/")
            formats = formats_response if isinstance(formats_response, list) else []

            # Format data for table
            for fmt in formats:
                if "is_active" in fmt:
                    fmt["is_active"] = "Yes" if fmt["is_active"] else "No"

            return [False, "Add Purchase Format", True, "Success", message, formats]

        except Exception as e:
            return [
                True,
                "Error",
                True,
                "Error",
                f"Failed to save purchase format: {str(e)}",
                dash.no_update,
            ]

    # Cancel button
    @app.callback(
        Output("purchase-format-form-modal", "is_open", allow_duplicate=True),
        [Input("cancel-purchase-format-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def cancel_purchase_format_form(n_clicks):
        """Close modal on cancel."""
        if n_clicks:
            return False
        raise PreventUpdate

    # Delete purchase format
    @app.callback(
        [
            Output("purchase-formats-table", "data", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
        ],
        [Input("delete-purchase-format-btn", "n_clicks")],
        [
            State("purchase-formats-table", "selected_rows"),
            State("purchase-formats-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def delete_purchase_format(n_clicks, selected_rows, data):
        """Delete selected purchase format."""
        if not n_clicks or not selected_rows or not data:
            raise PreventUpdate

        fmt = data[selected_rows[0]]
        format_id = fmt.get("id")
        format_code = fmt.get("code", "Unknown")

        if not format_id:
            return dash.no_update, True, "Error", "Purchase format ID not found"

        try:
            response = make_api_request("DELETE", f"/purchase-formats/{format_id}")
            if "error" in response:
                return (
                    dash.no_update,
                    True,
                    "Error",
                    f"Failed to delete purchase format: {response['error']}",
                )

            # Reload table
            formats_response = make_api_request("GET", "/purchase-formats/")
            formats = formats_response if isinstance(formats_response, list) else []

            # Format data for table
            for fmt in formats:
                if "is_active" in fmt:
                    fmt["is_active"] = "Yes" if fmt["is_active"] else "No"

            return (
                formats,
                True,
                "Success",
                f"Purchase format '{format_code}' deleted successfully",
            )

        except Exception as e:
            return (
                dash.no_update,
                True,
                "Error",
                f"Failed to delete purchase format: {str(e)}",
            )
