"""CRUD callbacks for excise rates."""

from datetime import datetime

import dash
from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate


def register_excise_rates_callbacks(app, make_api_request):
    """Register all excise rates CRUD callbacks."""

    # Toggle edit/delete buttons based on selection
    @app.callback(
        [
            Output("edit-excise-rate-btn", "disabled"),
            Output("delete-excise-rate-btn", "disabled"),
        ],
        [Input("excise-rates-table", "selected_rows")],
    )
    def toggle_action_buttons(selected_rows):
        disabled = not selected_rows or len(selected_rows) == 0
        return disabled, disabled

    # Load excise rates table
    @app.callback(
        Output("excise-rates-table", "data"),
        [
            Input("main-tabs", "active_tab"),
            Input("settings-tabs", "active_tab"),
            Input("excise-rates-refresh", "n_clicks"),
        ],
    )
    def load_excise_rates_table(main_tab, settings_tab, refresh_clicks):
        """Load excise rates table when settings tab is activated and excise-rates sub-tab is active."""
        if main_tab != "settings" or settings_tab != "excise-rates":
            return []

        try:
            response = make_api_request("GET", "/excise-rates/")
            if "error" in response:
                return []

            rates = response if isinstance(response, list) else []

            # Sort rates by date_active_from descending (most recent first)
            # Then calculate effective periods
            try:
                rates_with_dates = []
                for rate in rates:
                    if "date_active_from" in rate:
                        try:
                            dt = datetime.fromisoformat(
                                rate["date_active_from"].replace("Z", "+00:00")
                            )
                            rates_with_dates.append((dt, rate))
                        except (ValueError, TypeError):
                            rates_with_dates.append((datetime.min, rate))
                    else:
                        rates_with_dates.append((datetime.min, rate))

                # Sort by date descending
                rates_with_dates.sort(key=lambda x: x[0], reverse=True)

                # Calculate effective periods
                for i, (date_from, rate) in enumerate(rates_with_dates):
                    # Format date_active_from
                    rate["date_active_from"] = date_from.strftime("%Y-%m-%d")

                    # Calculate effective period
                    if i < len(rates_with_dates) - 1:
                        # There's a next rate, so this one is effective until that date
                        next_date = rates_with_dates[i + 1][0]
                        effective_period = f"{date_from.strftime('%Y-%m-%d')} to {next_date.strftime('%Y-%m-%d')}"
                    else:
                        # This is the most recent rate, effective indefinitely
                        effective_period = f"{date_from.strftime('%Y-%m-%d')} onwards"

                    rate["effective_period"] = effective_period

                    # Format other fields
                    if "rate_per_l_abv" in rate and rate["rate_per_l_abv"]:
                        try:
                            rate["rate_per_l_abv"] = float(rate["rate_per_l_abv"])
                        except (ValueError, TypeError):
                            pass
                    if "created_at" in rate:
                        try:
                            dt = datetime.fromisoformat(
                                rate["created_at"].replace("Z", "+00:00")
                            )
                            rate["created_at"] = dt.strftime("%Y-%m-%d %H:%M")
                        except (ValueError, TypeError):
                            pass
                    if "is_active" in rate:
                        rate["is_active"] = "Yes" if rate["is_active"] else "No"

                # Return sorted rates
                rates = [rate for _, rate in rates_with_dates]
            except Exception as e:
                print(f"Error formatting excise rates: {e}")
                # Fallback: format without effective period calculation
                for rate in rates:
                    if "date_active_from" in rate:
                        try:
                            dt = datetime.fromisoformat(
                                rate["date_active_from"].replace("Z", "+00:00")
                            )
                            rate["date_active_from"] = dt.strftime("%Y-%m-%d")
                            rate["effective_period"] = (
                                f"{dt.strftime('%Y-%m-%d')} onwards"
                            )
                        except (ValueError, TypeError):
                            rate["effective_period"] = "N/A"
                    if "rate_per_l_abv" in rate and rate["rate_per_l_abv"]:
                        try:
                            rate["rate_per_l_abv"] = float(rate["rate_per_l_abv"])
                        except (ValueError, TypeError):
                            pass
                    if "created_at" in rate:
                        try:
                            dt = datetime.fromisoformat(
                                rate["created_at"].replace("Z", "+00:00")
                            )
                            rate["created_at"] = dt.strftime("%Y-%m-%d %H:%M")
                        except (ValueError, TypeError):
                            pass
                    if "is_active" in rate:
                        rate["is_active"] = "Yes" if rate["is_active"] else "No"

            return rates
        except Exception as e:
            print(f"Error loading excise rates: {e}")
            return []

    # Open modal for add/edit and populate form
    @app.callback(
        [
            Output("excise-rate-form-modal", "is_open", allow_duplicate=True),
            Output("excise-rate-modal-title", "children", allow_duplicate=True),
            Output("excise-rate-date", "date", allow_duplicate=True),
            Output("excise-rate-rate", "value", allow_duplicate=True),
            Output("excise-rate-description", "value", allow_duplicate=True),
            Output("excise-rate-is-active", "value", allow_duplicate=True),
            Output("excise-rate-form-hidden", "children", allow_duplicate=True),
        ],
        [
            Input("add-excise-rate-btn", "n_clicks"),
            Input("edit-excise-rate-btn", "n_clicks"),
        ],
        [
            State("excise-rates-table", "selected_rows"),
            State("excise-rates-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def open_excise_rate_modal(add_clicks, edit_clicks, selected_rows, data):
        """Open modal for add or edit and populate form data."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "add-excise-rate-btn":
            # Add mode - clear form
            return [True, "Add Excise Rate", None, None, "", True, ""]

        elif button_id == "edit-excise-rate-btn":
            if not selected_rows or not data:
                raise PreventUpdate

            rate = data[selected_rows[0]]

            # Parse date for DatePicker
            date_str = rate.get("date_active_from", "")
            date_value = None
            if date_str:
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    date_value = dt.strftime("%Y-%m-%d")
                except (ValueError, TypeError):
                    try:
                        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        date_value = dt.strftime("%Y-%m-%d")
                    except (ValueError, TypeError):
                        pass

            # Extract numeric value
            rate_value = rate.get("rate_per_l_abv", "")
            if rate_value:
                try:
                    if isinstance(rate_value, str):
                        rate_value = rate_value.replace("$", "").strip()
                    rate_value = float(rate_value)
                except (ValueError, TypeError):
                    rate_value = None

            return (
                True,  # is_open
                "Edit Excise Rate",  # title
                date_value,  # date
                rate_value,  # rate
                rate.get("description", ""),  # description
                rate.get("is_active", True),  # is_active
                rate.get("id"),  # Hidden field - rate ID
            )

        raise PreventUpdate

    # Save excise rate (create or update)
    @app.callback(
        [
            Output("excise-rate-form-modal", "is_open", allow_duplicate=True),
            Output("excise-rate-modal-title", "children", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
            Output("excise-rates-table", "data", allow_duplicate=True),
        ],
        [Input("save-excise-rate-btn", "n_clicks")],
        [
            State("excise-rate-date", "date"),
            State("excise-rate-rate", "value"),
            State("excise-rate-description", "value"),
            State("excise-rate-is-active", "value"),
            State("excise-rate-form-hidden", "children"),
        ],
        prevent_initial_call=True,
    )
    def save_excise_rate(
        n_clicks, date_active, rate_value, description, is_active, rate_id
    ):
        """Save excise rate - create or update based on hidden state."""
        if not n_clicks:
            raise PreventUpdate

        # Validate required fields
        if not date_active or rate_value is None:
            return [
                False,
                "Add Excise Rate",
                True,
                "Error",
                "Date Active From and Rate are required",
                no_update,
            ]

        # Prepare rate data
        # Format date as ISO 8601 without timezone (matching API expectations)
        # Convert rate_value to float first, then string for Decimal parsing
        try:
            rate_float = float(rate_value) if rate_value is not None else None
        except (ValueError, TypeError):
            return [
                True,
                "Error",
                True,
                "Error",
                "Invalid rate value. Please enter a valid number.",
                no_update,
            ]

        rate_data = {
            "date_active_from": f"{date_active}T00:00:00",
            "rate_per_l_abv": str(rate_float),  # Pydantic will parse string to Decimal
            "description": description.strip() if description else None,
            "is_active": bool(is_active) if is_active is not None else True,
        }

        print(
            f"DEBUG: Saving excise rate with data: {rate_data}, rate_id: {rate_id}"
        )  # Debug output

        try:
            if rate_id and rate_id.strip():  # Update existing
                response = make_api_request(
                    "PUT", f"/excise-rates/{rate_id}", rate_data
                )
                if "error" in response:
                    error_msg = response.get("error", "Unknown error")
                    if isinstance(error_msg, str):
                        try:
                            import json

                            error_dict = json.loads(error_msg)
                            error_msg = error_dict.get("message", error_msg)
                        except (ValueError, TypeError):
                            pass
                    return [
                        True,
                        "Error",
                        True,
                        "Error",
                        f"Failed to update excise rate: {error_msg}",
                        no_update,
                    ]
                message = "Excise rate updated successfully"
            else:  # Create new
                response = make_api_request("POST", "/excise-rates/", rate_data)
                if "error" in response:
                    error_msg = response.get("error", "Unknown error")
                    if isinstance(error_msg, str):
                        try:
                            import json

                            error_dict = json.loads(error_msg)
                            error_msg = error_dict.get("message", error_msg)
                        except (ValueError, TypeError):
                            pass
                    print(f"API Error Response: {response}")  # Debug output
                    return [
                        True,
                        "Error",
                        True,
                        "Error",
                        f"Failed to create excise rate: {error_msg}",
                        no_update,
                    ]
                message = "Excise rate created successfully"

            # Reload table after successful save
            print("DEBUG: Save successful, reloading table...")  # Debug output
            rates_response = make_api_request("GET", "/excise-rates/")
            if "error" in rates_response:
                print(f"DEBUG: Error reloading table: {rates_response['error']}")
                rates = []
            else:
                rates = rates_response if isinstance(rates_response, list) else []
                print(f"DEBUG: Reloaded {len(rates)} rates")

            # Format dates and rates for display (same logic as load_excise_rates_table)
            try:
                rates_with_dates = []
                for rate in rates:
                    if "date_active_from" in rate:
                        try:
                            dt = datetime.fromisoformat(
                                rate["date_active_from"].replace("Z", "+00:00")
                            )
                            rates_with_dates.append((dt, rate))
                        except (ValueError, TypeError):
                            rates_with_dates.append((datetime.min, rate))
                    else:
                        rates_with_dates.append((datetime.min, rate))

                # Sort by date descending
                rates_with_dates.sort(key=lambda x: x[0], reverse=True)

                # Calculate effective periods
                for i, (date_from, rate) in enumerate(rates_with_dates):
                    rate["date_active_from"] = date_from.strftime("%Y-%m-%d")

                    if i < len(rates_with_dates) - 1:
                        next_date = rates_with_dates[i + 1][0]
                        effective_period = f"{date_from.strftime('%Y-%m-%d')} to {next_date.strftime('%Y-%m-%d')}"
                    else:
                        effective_period = f"{date_from.strftime('%Y-%m-%d')} onwards"

                    rate["effective_period"] = effective_period

                    if "rate_per_l_abv" in rate and rate["rate_per_l_abv"]:
                        try:
                            rate["rate_per_l_abv"] = float(rate["rate_per_l_abv"])
                        except (ValueError, TypeError):
                            pass
                    if "created_at" in rate:
                        try:
                            dt = datetime.fromisoformat(
                                rate["created_at"].replace("Z", "+00:00")
                            )
                            rate["created_at"] = dt.strftime("%Y-%m-%d %H:%M")
                        except (ValueError, TypeError):
                            pass
                    if "is_active" in rate:
                        rate["is_active"] = "Yes" if rate["is_active"] else "No"

                rates = [rate for _, rate in rates_with_dates]
            except Exception as e:
                print(f"Error formatting excise rates after save: {e}")
                # Fallback formatting
                for rate in rates:
                    if "date_active_from" in rate:
                        try:
                            dt = datetime.fromisoformat(
                                rate["date_active_from"].replace("Z", "+00:00")
                            )
                            rate["date_active_from"] = dt.strftime("%Y-%m-%d")
                            rate["effective_period"] = (
                                f"{dt.strftime('%Y-%m-%d')} onwards"
                            )
                        except (ValueError, TypeError):
                            rate["effective_period"] = "N/A"
                    if "rate_per_l_abv" in rate and rate["rate_per_l_abv"]:
                        try:
                            rate["rate_per_l_abv"] = float(rate["rate_per_l_abv"])
                        except (ValueError, TypeError):
                            pass
                    if "created_at" in rate:
                        try:
                            dt = datetime.fromisoformat(
                                rate["created_at"].replace("Z", "+00:00")
                            )
                            rate["created_at"] = dt.strftime("%Y-%m-%d %H:%M")
                        except (ValueError, TypeError):
                            pass
                    if "is_active" in rate:
                        rate["is_active"] = "Yes" if rate["is_active"] else "No"

            return [False, "Add Excise Rate", True, "Success", message, rates]

        except Exception as e:
            return [
                True,
                "Error",
                True,
                "Error",
                f"Failed to save excise rate: {str(e)}",
                no_update,
            ]

    # Cancel button
    @app.callback(
        Output("excise-rate-form-modal", "is_open", allow_duplicate=True),
        [Input("cancel-excise-rate-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def cancel_excise_rate_form(n_clicks):
        """Close modal on cancel."""
        if n_clicks:
            return False
        raise PreventUpdate

    # Delete excise rate
    @app.callback(
        [
            Output("excise-rates-table", "data", allow_duplicate=True),
            Output("toast", "is_open", allow_duplicate=True),
            Output("toast", "header", allow_duplicate=True),
            Output("toast", "children", allow_duplicate=True),
        ],
        [Input("delete-excise-rate-btn", "n_clicks")],
        [
            State("excise-rates-table", "selected_rows"),
            State("excise-rates-table", "data"),
        ],
        prevent_initial_call=True,
    )
    def delete_excise_rate(n_clicks, selected_rows, data):
        """Delete selected excise rate."""
        if not n_clicks or not selected_rows or not data:
            raise PreventUpdate

        rate = data[selected_rows[0]]
        rate_id = rate.get("id")

        if not rate_id:
            return no_update, True, "Error", "Excise rate ID not found"

        try:
            response = make_api_request("DELETE", f"/excise-rates/{rate_id}")
            if "error" in response:
                return (
                    no_update,
                    True,
                    "Error",
                    f"Failed to delete excise rate: {response['error']}",
                )

            # Reload table
            rates_response = make_api_request("GET", "/excise-rates/")
            rates = rates_response if isinstance(rates_response, list) else []

            # Format dates and rates for display (same logic as load_excise_rates_table)
            try:
                rates_with_dates = []
                for rate in rates:
                    if "date_active_from" in rate:
                        try:
                            dt = datetime.fromisoformat(
                                rate["date_active_from"].replace("Z", "+00:00")
                            )
                            rates_with_dates.append((dt, rate))
                        except (ValueError, TypeError):
                            rates_with_dates.append((datetime.min, rate))
                    else:
                        rates_with_dates.append((datetime.min, rate))

                rates_with_dates.sort(key=lambda x: x[0], reverse=True)

                for i, (date_from, rate) in enumerate(rates_with_dates):
                    rate["date_active_from"] = date_from.strftime("%Y-%m-%d")

                    if i < len(rates_with_dates) - 1:
                        next_date = rates_with_dates[i + 1][0]
                        effective_period = f"{date_from.strftime('%Y-%m-%d')} to {next_date.strftime('%Y-%m-%d')}"
                    else:
                        effective_period = f"{date_from.strftime('%Y-%m-%d')} onwards"

                    rate["effective_period"] = effective_period

                    if "rate_per_l_abv" in rate and rate["rate_per_l_abv"]:
                        try:
                            rate["rate_per_l_abv"] = float(rate["rate_per_l_abv"])
                        except (ValueError, TypeError):
                            pass
                    if "created_at" in rate:
                        try:
                            dt = datetime.fromisoformat(
                                rate["created_at"].replace("Z", "+00:00")
                            )
                            rate["created_at"] = dt.strftime("%Y-%m-%d %H:%M")
                        except (ValueError, TypeError):
                            pass
                    if "is_active" in rate:
                        rate["is_active"] = "Yes" if rate["is_active"] else "No"

                rates = [rate for _, rate in rates_with_dates]
            except Exception as e:
                print(f"Error formatting excise rates after delete: {e}")
                # Fallback formatting
                for rate in rates:
                    if "date_active_from" in rate:
                        try:
                            dt = datetime.fromisoformat(
                                rate["date_active_from"].replace("Z", "+00:00")
                            )
                            rate["date_active_from"] = dt.strftime("%Y-%m-%d")
                            rate["effective_period"] = (
                                f"{dt.strftime('%Y-%m-%d')} onwards"
                            )
                        except (ValueError, TypeError):
                            rate["effective_period"] = "N/A"
                    if "rate_per_l_abv" in rate and rate["rate_per_l_abv"]:
                        try:
                            rate["rate_per_l_abv"] = float(rate["rate_per_l_abv"])
                        except (ValueError, TypeError):
                            pass
                    if "created_at" in rate:
                        try:
                            dt = datetime.fromisoformat(
                                rate["created_at"].replace("Z", "+00:00")
                            )
                            rate["created_at"] = dt.strftime("%Y-%m-%d %H:%M")
                        except (ValueError, TypeError):
                            pass
                    if "is_active" in rate:
                        rate["is_active"] = "Yes" if rate["is_active"] else "No"

            return rates, True, "Success", "Excise rate deleted successfully"

        except Exception as e:
            return no_update, True, "Error", f"Failed to delete excise rate: {str(e)}"
