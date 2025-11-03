"""CRUD callbacks for quality test definitions."""

import dash
from dash import Input, Output, State
from dash.exceptions import PreventUpdate


def register_quality_tests_callbacks(app, make_api_request):
    """Register all quality test definitions CRUD callbacks."""

    # Toggle edit/delete buttons based on selection
    @app.callback(
        [
            Output("edit-quality-test-btn", "disabled"),
            Output("delete-quality-test-btn", "disabled"),
        ],
        [Input("quality-tests-table", "selected_rows")],
    )
    def toggle_action_buttons(selected_rows):
        disabled = not selected_rows or len(selected_rows) == 0
        return disabled, disabled

    # Load quality tests table
    @app.callback(
        Output("quality-tests-table", "data"),
        [
            Input("main-tabs", "active_tab"),
            Input("quality-tests-refresh", "n_clicks"),
            Input("settings-tabs", "active_tab"),
        ],
    )
    def load_quality_tests_table(active_tab, refresh_clicks, settings_tab):
        """Load quality tests table when settings tab is activated and quality-tests sub-tab is active."""
        if active_tab != "settings" or settings_tab != "quality-tests":
            return []

        try:
            response = make_api_request("GET", "/quality-tests/")
            if "error" in response:
                return []

            tests = response if isinstance(response, list) else []

            # Format data for table
            for test in tests:
                if "is_active" in test:
                    test["is_active"] = "Yes" if test["is_active"] else "No"

            return tests
        except Exception as e:
            print(f"Error loading quality tests: {e}")
            return []

    # Open modal for add/edit and populate form
    @app.callback(
        [
            Output("quality-test-form-modal", "is_open", allow_duplicate=True),
            Output("quality-test-modal-title", "children", allow_duplicate=True),
            Output("quality-test-code", "value", allow_duplicate=True),
            Output("quality-test-name", "value", allow_duplicate=True),
            Output("quality-test-type", "value", allow_duplicate=True),
            Output("quality-test-unit", "value", allow_duplicate=True),
            Output("quality-test-min-value", "value", allow_duplicate=True),
            Output("quality-test-target-value", "value", allow_duplicate=True),
            Output("quality-test-max-value", "value", allow_duplicate=True),
            Output("quality-test-description", "value", allow_duplicate=True),
            Output("quality-test-is-active", "value", allow_duplicate=True),
            Output("quality-test-form-hidden", "children", allow_duplicate=True),
        ],
        [
            Input("add-quality-test-btn", "n_clicks"),
            Input("edit-quality-test-btn", "n_clicks"),
        ],
        [
            State("quality-tests-table", "selected_rows"),
            State("quality-tests-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def open_quality_test_modal(add_clicks, edit_clicks, selected_rows, data):
        """Open modal for add or edit and populate form data."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "add-quality-test-btn":
            # Add mode - clear form
            return [
                True,
                "Add Quality Test",
                "",
                "",
                None,
                "",
                None,
                None,
                None,
                "",
                True,
                "",
            ]

        elif button_id == "edit-quality-test-btn":
            if not selected_rows or not data:
                raise PreventUpdate

            test = data[selected_rows[0]]

            return (
                True,  # is_open
                "Edit Quality Test",  # title
                test.get("code", ""),
                test.get("name", ""),
                test.get("test_type", ""),
                test.get("unit", ""),
                test.get("min_value"),
                test.get("target_value"),
                test.get("max_value"),
                test.get("description", ""),
                test.get("is_active") == "Yes"
                if isinstance(test.get("is_active"), str)
                else test.get("is_active", True),
                test.get("id"),  # Hidden field - test ID
            )

        raise PreventUpdate

    # Save quality test (create or update)
    @app.callback(
        [
            Output("quality-test-form-modal", "is_open", allow_duplicate=True),
            Output("quality-test-modal-title", "children", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
            Output("quality-tests-table", "data", allow_duplicate=True),
        ],
        [Input("save-quality-test-btn", "n_clicks")],
        [
            State("quality-test-code", "value"),
            State("quality-test-name", "value"),
            State("quality-test-type", "value"),
            State("quality-test-unit", "value"),
            State("quality-test-min-value", "value"),
            State("quality-test-target-value", "value"),
            State("quality-test-max-value", "value"),
            State("quality-test-description", "value"),
            State("quality-test-is-active", "value"),
            State("quality-test-form-hidden", "children"),
        ],
        prevent_initial_call=True,
    )
    def save_quality_test(
        n_clicks,
        code,
        name,
        test_type,
        unit,
        min_value,
        target_value,
        max_value,
        description,
        is_active,
        test_id,
    ):
        """Save quality test - create or update based on hidden state."""
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

        # Prepare test data
        test_data = {
            "code": code.strip().upper(),
            "name": name.strip(),
            "test_type": test_type if test_type else None,
            "unit": unit.strip() if unit else None,
            "min_value": float(min_value) if min_value is not None else None,
            "target_value": float(target_value) if target_value is not None else None,
            "max_value": float(max_value) if max_value is not None else None,
            "description": description.strip() if description else None,
            "is_active": is_active if is_active is not None else True,
        }

        try:
            if test_id:  # Update existing
                response = make_api_request(
                    "PUT", f"/quality-tests/{test_id}", test_data
                )
                if "error" in response:
                    return [
                        True,
                        "Error",
                        True,
                        "Error",
                        f"Failed to update quality test: {response['error']}",
                        dash.no_update,
                    ]
                message = f"Quality test '{code}' updated successfully"
            else:  # Create new
                response = make_api_request("POST", "/quality-tests/", test_data)
                if "error" in response:
                    return [
                        True,
                        "Error",
                        True,
                        "Error",
                        f"Failed to create quality test: {response['error']}",
                        dash.no_update,
                    ]
                message = f"Quality test '{code}' created successfully"

            # Reload table
            tests_response = make_api_request("GET", "/quality-tests/")
            tests = tests_response if isinstance(tests_response, list) else []

            # Format data for table
            for test in tests:
                if "is_active" in test:
                    test["is_active"] = "Yes" if test["is_active"] else "No"

            return [False, "Add Quality Test", True, "Success", message, tests]

        except Exception as e:
            return [
                True,
                "Error",
                True,
                "Error",
                f"Failed to save quality test: {str(e)}",
                dash.no_update,
            ]

    # Cancel button
    @app.callback(
        Output("quality-test-form-modal", "is_open", allow_duplicate=True),
        [Input("cancel-quality-test-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def cancel_quality_test_form(n_clicks):
        """Close modal on cancel."""
        if n_clicks:
            return False
        raise PreventUpdate

    # Delete quality test
    @app.callback(
        [
            Output("quality-tests-table", "data", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
        ],
        [Input("delete-quality-test-btn", "n_clicks")],
        [
            State("quality-tests-table", "selected_rows"),
            State("quality-tests-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def delete_quality_test(n_clicks, selected_rows, data):
        """Delete selected quality test."""
        if not n_clicks or not selected_rows or not data:
            raise PreventUpdate

        test = data[selected_rows[0]]
        test_id = test.get("id")
        test_code = test.get("code", "Unknown")

        if not test_id:
            return dash.no_update, True, "Error", "Quality test ID not found"

        try:
            response = make_api_request("DELETE", f"/quality-tests/{test_id}")
            if "error" in response:
                return (
                    dash.no_update,
                    True,
                    "Error",
                    f"Failed to delete quality test: {response['error']}",
                )

            # Reload table
            tests_response = make_api_request("GET", "/quality-tests/")
            tests = tests_response if isinstance(tests_response, list) else []

            # Format data for table
            for test in tests:
                if "is_active" in test:
                    test["is_active"] = "Yes" if test["is_active"] else "No"

            return (
                tests,
                True,
                "Success",
                f"Quality test '{test_code}' deleted successfully",
            )

        except Exception as e:
            return (
                dash.no_update,
                True,
                "Error",
                f"Failed to delete quality test: {str(e)}",
            )
