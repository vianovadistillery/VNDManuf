"""CRUD callbacks for work areas page."""

import dash
from dash import Input, Output, State
from dash.exceptions import PreventUpdate


def register_work_areas_callbacks(app, make_api_request):
    """Register all work areas CRUD callbacks."""

    # Toggle edit/delete buttons based on selection
    @app.callback(
        [
            Output("edit-work-area-btn", "disabled"),
            Output("delete-work-area-btn", "disabled"),
        ],
        [Input("work-areas-table", "selected_rows")],
    )
    def toggle_action_buttons(selected_rows):
        disabled = not selected_rows or len(selected_rows) == 0
        return disabled, disabled

    # Load work areas table
    @app.callback(
        Output("work-areas-table", "data"),
        [
            Input("main-tabs", "active_tab"),
            Input("settings-tabs", "active_tab"),
            Input("work-areas-refresh", "n_clicks"),
        ],
    )
    def load_work_areas_table(main_tab, settings_tab, refresh_clicks):
        """Load work areas table when settings tab is activated and work-areas sub-tab is active."""
        if main_tab != "settings" or settings_tab != "work-areas":
            return []

        try:
            response = make_api_request("GET", "/work-areas/")
            if "error" in response:
                return []

            work_areas = response if isinstance(response, list) else []

            # Format data for table
            for wa in work_areas:
                if "is_active" in wa:
                    wa["is_active"] = "Yes" if wa["is_active"] else "No"

            return work_areas
        except Exception as e:
            print(f"Error loading work areas: {e}")
            # Return empty list if API doesn't exist yet
            return []

    # Open modal for add/edit and populate form
    @app.callback(
        [
            Output("work-area-form-modal", "is_open", allow_duplicate=True),
            Output("work-area-modal-title", "children", allow_duplicate=True),
            Output("work-area-code", "value", allow_duplicate=True),
            Output("work-area-name", "value", allow_duplicate=True),
            Output("work-area-description", "value", allow_duplicate=True),
            Output("work-area-is-active", "value", allow_duplicate=True),
            Output("work-area-form-hidden", "children", allow_duplicate=True),
        ],
        [
            Input("add-work-area-btn", "n_clicks"),
            Input("edit-work-area-btn", "n_clicks"),
        ],
        [State("work-areas-table", "selected_rows"), State("work-areas-table", "data")],
        prevent_initial_call=True,
    )
    def open_work_area_modal(add_clicks, edit_clicks, selected_rows, data):
        """Open modal for add or edit and populate form data."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "add-work-area-btn":
            # Add mode - clear form
            return [True, "Add Work Area", "", "", "", True, ""]

        elif button_id == "edit-work-area-btn":
            if not selected_rows or not data:
                raise PreventUpdate

            work_area = data[selected_rows[0]]

            return (
                True,  # is_open
                "Edit Work Area",  # title
                work_area.get("code", ""),
                work_area.get("name", ""),
                work_area.get("description", ""),
                (
                    work_area.get("is_active") == "Yes"
                    if isinstance(work_area.get("is_active"), str)
                    else work_area.get("is_active", True)
                ),
                work_area.get("id", ""),  # Store ID in hidden field
            )

        raise PreventUpdate

    # Save work area
    @app.callback(
        [
            Output("work-area-form-modal", "is_open", allow_duplicate=True),
            Output("work-areas-table", "data", allow_duplicate=True),
        ],
        [Input("save-work-area-btn", "n_clicks")],
        [
            State("work-area-form-hidden", "children"),
            State("work-area-code", "value"),
            State("work-area-name", "value"),
            State("work-area-description", "value"),
            State("work-area-is-active", "value"),
        ],
        prevent_initial_call=True,
    )
    def save_work_area(n_clicks, work_area_id, code, name, description, is_active):
        """Save work area (create or update)."""
        if not n_clicks:
            raise PreventUpdate

        if not code or not name:
            return [True, dash.no_update]  # Keep modal open if validation fails

        try:
            payload = {
                "code": code,
                "name": name,
                "description": description or "",
                "is_active": is_active if is_active is not None else True,
            }

            if work_area_id:
                # Update existing
                response = make_api_request(
                    "PUT", f"/work-areas/{work_area_id}", payload
                )
            else:
                # Create new
                response = make_api_request("POST", "/work-areas/", payload)

            if "error" in response:
                print(f"Error saving work area: {response.get('error')}")
                return [True, dash.no_update]  # Keep modal open on error

            # Reload table
            table_data = make_api_request("GET", "/work-areas/")
            if "error" not in table_data:
                work_areas = table_data if isinstance(table_data, list) else []
                for wa in work_areas:
                    if "is_active" in wa:
                        wa["is_active"] = "Yes" if wa["is_active"] else "No"
                return [False, work_areas]  # Close modal and update table

            return [False, dash.no_update]
        except Exception as e:
            print(f"Error saving work area: {e}")
            return [True, dash.no_update]  # Keep modal open on error

    # Delete work area
    @app.callback(
        Output("work-areas-table", "data", allow_duplicate=True),
        [Input("delete-work-area-btn", "n_clicks")],
        [State("work-areas-table", "selected_rows"), State("work-areas-table", "data")],
        prevent_initial_call=True,
    )
    def delete_work_area(n_clicks, selected_rows, data):
        """Delete selected work area."""
        if not n_clicks or not selected_rows or not data:
            raise PreventUpdate

        try:
            work_area = data[selected_rows[0]]
            work_area_id = work_area.get("id")

            if not work_area_id:
                return dash.no_update

            response = make_api_request("DELETE", f"/work-areas/{work_area_id}")

            if "error" in response:
                print(f"Error deleting work area: {response.get('error')}")
                return dash.no_update

            # Reload table
            table_data = make_api_request("GET", "/work-areas/")
            if "error" not in table_data:
                work_areas = table_data if isinstance(table_data, list) else []
                for wa in work_areas:
                    if "is_active" in wa:
                        wa["is_active"] = "Yes" if wa["is_active"] else "No"
                return work_areas

            return dash.no_update
        except Exception as e:
            print(f"Error deleting work area: {e}")
            return dash.no_update

    # Close modal
    @app.callback(
        Output("work-area-form-modal", "is_open", allow_duplicate=True),
        [Input("cancel-work-area-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def close_work_area_modal(n_clicks):
        """Close work area modal."""
        if n_clicks:
            return False
        raise PreventUpdate
